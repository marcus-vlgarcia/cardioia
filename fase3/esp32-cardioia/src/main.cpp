/*
 * CardioIA PulseIA - Fase 3
 * ESP32 + DHT22 + botão de pulso + MQTT.
 *
 * O Wokwi não preserva SPIFFS entre execuções. Por isso, esta versão usa uma
 * fila circular em memória, visível no Monitor Serial, para demonstrar a
 * resiliência offline. Em hardware real, a mesma fila pode ser gravada em
 * SPIFFS ou cartão SD antes de cada sincronização.
 */

#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <atomic>
#include <esp_timer.h>
#include <sys/time.h>
#include "config.h"

constexpr uint8_t PINO_DHT = 15;
constexpr uint8_t PINO_PULSO = 18;
constexpr uint8_t PINO_REDE = 19;
constexpr uint8_t PINO_LED_REDE = 2;
constexpr uint32_t INTERVALO_LEITURA_MS = 5000;
constexpr uint32_t JANELA_BPM_MS = 10000;
constexpr uint32_t INTERVALO_RECONEXAO_WIFI_MS = 5000;
constexpr uint16_t LIMITE_TEMPERATURA_ALERTA = 38;
constexpr uint16_t LIMITE_BPM_ALERTA = 120;
constexpr uint16_t TAMANHO_BUFFER_MQTT = 512;

// Capacidade equivalente a cerca de 83 minutos de leituras a cada 5 segundos.
// Quando cheia, a amostra mais antiga é substituída para preservar o dado atual.
constexpr uint16_t MAX_AMOSTRAS_OFFLINE = 1000;

DHT dht(PINO_DHT, DHT22);
#if MQTT_USAR_TLS
WiFiClientSecure clienteMqtt;
#else
WiFiClient clienteMqtt;
#endif
PubSubClient mqtt(clienteMqtt);

struct Amostra {
  uint32_t sequencia;
  uint64_t instanteMs;
  float temperatura;
  float umidade;
  uint16_t bpm;
  bool alerta;
  bool coletadaOffline;
};

Amostra fila[MAX_AMOSTRAS_OFFLINE];
uint16_t inicioFila = 0;
uint16_t tamanhoFila = 0;
uint32_t amostrasDescartadas = 0;
uint32_t proximaSequencia = 1;

std::atomic<bool> conectividadeAtiva{true};
std::atomic<bool> mqttDisponivel{false};
portMUX_TYPE travaFila = portMUX_INITIALIZER_UNLOCKED;
portMUX_TYPE travaPulso = portMUX_INITIALIZER_UNLOCKED;
bool ultimoEstadoRede = HIGH;
uint64_t ultimoCliquePulsoUs = 0;
uint32_t ultimoCliqueRede = 0;
uint64_t inicioJanelaBpmUs = 0;
uint32_t ultimaLeitura = 0;
uint32_t ultimaTentativaWifi = 0;
uint16_t pulsosNaJanela = 0;
uint16_t bpmAtual = 0;

void registrarNoSerial(const char* evento) {
  portENTER_CRITICAL(&travaFila);
  const auto pendentes = tamanhoFila;
  const auto descartadas = amostrasDescartadas;
  portEXIT_CRITICAL(&travaFila);
  Serial.printf("[EDGE] %s | fila=%u | descartadas=%lu | rede=%s\n", evento,
                pendentes, static_cast<unsigned long>(descartadas),
                conectividadeAtiva ? "habilitada" : "offline simulada");
}

void adicionarNaFila(const Amostra& amostra) {
  portENTER_CRITICAL(&travaFila);
  if (tamanhoFila == MAX_AMOSTRAS_OFFLINE) {
    inicioFila = (inicioFila + 1) % MAX_AMOSTRAS_OFFLINE;
    tamanhoFila--;
    amostrasDescartadas++;
  }
  const uint16_t posicao = (inicioFila + tamanhoFila) % MAX_AMOSTRAS_OFFLINE;
  fila[posicao] = amostra;
  tamanhoFila++;
  portEXIT_CRITICAL(&travaFila);
}

bool montarPayload(const Amostra& amostra, uint16_t pendentes, uint32_t descartadas,
                   char* destino, size_t tamanhoDestino) {
  const uint64_t idadeMs = esp_timer_get_time() / 1000 - amostra.instanteMs;
  timeval agora{};
  gettimeofday(&agora, nullptr);
  char instanteUtc[24] = "null";
  if (agora.tv_sec >= 1704067200) {  // Relógio sincronizado, a partir de 2024.
    const uint64_t utcMs = static_cast<uint64_t>(agora.tv_sec) * 1000 + agora.tv_usec / 1000;
    snprintf(instanteUtc, sizeof(instanteUtc), "%llu",
             static_cast<unsigned long long>(utcMs - idadeMs));
  }
  char temperatura[16] = "null", umidade[16] = "null";
  if (isfinite(amostra.temperatura)) snprintf(temperatura, sizeof(temperatura), "%.2f", amostra.temperatura);
  if (isfinite(amostra.umidade)) snprintf(umidade, sizeof(umidade), "%.2f", amostra.umidade);
  const bool recuperada = amostra.coletadaOffline || idadeMs >= INTERVALO_LEITURA_MS;
  const int escrito = snprintf(
      destino, tamanhoDestino,
      "{\"projeto\":\"CardioIA\",\"paciente_id\":\"%s\",\"sequencia\":%lu,"
      "\"instante_ms\":%llu,\"idade_ms\":%llu,\"coletada_em_ms\":%s,\"recuperada\":%s,"
      "\"temperatura_c\":%s,\"umidade_pct\":%s,\"bpm\":%u,"
      "\"pulso_detectado\":%s,\"alerta\":%s,\"fila_offline\":%u,"
      "\"amostras_descartadas\":%lu,\"origem\":\"edge_esp32\"}",
      ID_PACIENTE, static_cast<unsigned long>(amostra.sequencia),
      static_cast<unsigned long long>(amostra.instanteMs),
      static_cast<unsigned long long>(idadeMs), instanteUtc, recuperada ? "true" : "false",
      temperatura, umidade, amostra.bpm, amostra.bpm > 0 ? "true" : "false",
      amostra.alerta ? "true" : "false", pendentes, static_cast<unsigned long>(descartadas));
  return escrito > 0 && static_cast<size_t>(escrito) < tamanhoDestino;
}

bool publicar(const Amostra& amostra, uint16_t pendentes, uint32_t descartadas) {
  char payload[448];
  if (!montarPayload(amostra, pendentes, descartadas, payload, sizeof(payload))) {
    Serial.println("[MQTT] Erro ao montar JSON.");
    return false;
  }
  const bool enviado = mqtt.publish(MQTT_TOPICO_TELEMETRIA, payload);
  Serial.print("[SERIAL] ");
  Serial.println(payload);
  Serial.printf("[MQTT] %s: %s\n", enviado ? "Publicado" : "Falha ao publicar", payload);
  return enviado;
}

bool conectarMqtt() {
  if (!conectividadeAtiva || WiFi.status() != WL_CONNECTED) return false;
  if (mqtt.connected()) return true;
#if MQTT_USAR_TLS
  if (MQTT_CERTIFICADO_RAIZ == nullptr) {
    Serial.println("[MQTT] Conexão TLS bloqueada: certificado raiz não configurado.");
    return false;
  }
#endif

  Serial.printf("[MQTT] Conectando em %s:%d...\n", MQTT_HOST, MQTT_PORT);
  char idCliente[64];
  const uint64_t chipId = ESP.getEfuseMac();
  snprintf(idCliente, sizeof(idCliente), "%s-%04llX", MQTT_CLIENTE_PREFIXO,
           static_cast<unsigned long long>(chipId & 0xFFFF));
  const bool conectado = strlen(MQTT_USUARIO) == 0
      ? mqtt.connect(idCliente)
      : mqtt.connect(idCliente, MQTT_USUARIO, MQTT_SENHA);
  if (!conectado) Serial.printf("[MQTT] Estado de conexão: %d\n", mqtt.state());
  return conectado;
}

void conectarWifiSeNecessario() {
  if (!conectividadeAtiva || WiFi.status() == WL_CONNECTED) return;
  if (ultimaTentativaWifi != 0 &&
      millis() - ultimaTentativaWifi < INTERVALO_RECONEXAO_WIFI_MS) return;
  ultimaTentativaWifi = millis();
  Serial.printf("[WIFI] Conectando à rede %s...\n", WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_SENHA, WIFI_CANAL);
}

void sincronizarPendentes() {
  portENTER_CRITICAL(&travaFila);
  if (tamanhoFila == 0) {
    portEXIT_CRITICAL(&travaFila);
    return;
  }
  const Amostra pendente = fila[inicioFila];
  const uint16_t restantes = tamanhoFila - 1;
  const uint32_t descartadas = amostrasDescartadas;
  portEXIT_CRITICAL(&travaFila);

  // A aquisição pode inserir ou descartar amostras durante o envio.
  const bool enviada = publicar(pendente, restantes, descartadas);
  portENTER_CRITICAL(&travaFila);
  if (fila[inicioFila].sequencia == pendente.sequencia) {
    if (enviada) {
      inicioFila = (inicioFila + 1) % MAX_AMOSTRAS_OFFLINE;
      tamanhoFila--;
    } else {
      fila[inicioFila].coletadaOffline = true;
    }
  }
  const bool vazia = tamanhoFila == 0;
  portEXIT_CRITICAL(&travaFila);
  if (vazia) registrarNoSerial("Fila enviada e limpa após aceitação local das publicações MQTT");
}

void atualizarLed() {
  static uint32_t ultimaMudanca = 0;
  static bool estado = false;
  const bool conectado = conectividadeAtiva && mqtt.connected();
  if (conectado) {
    digitalWrite(PINO_LED_REDE, HIGH);
    return;
  }
  if (millis() - ultimaMudanca >= 350) {
    estado = !estado;
    digitalWrite(PINO_LED_REDE, estado);
    ultimaMudanca = millis();
  }
}

void IRAM_ATTR contarPulso() {
  const uint64_t agora = esp_timer_get_time();
  portENTER_CRITICAL_ISR(&travaPulso);
  if (ultimoCliquePulsoUs == 0 || agora - ultimoCliquePulsoUs > 120000) {
    pulsosNaJanela++;
    ultimoCliquePulsoUs = agora;
  }
  portEXIT_CRITICAL_ISR(&travaPulso);
}

constexpr uint16_t calcularBpm(uint16_t pulsos, uint64_t duracaoUs) {
  return (pulsos * 60000000ULL + duracaoUs / 2) / duracaoUs;
}

static_assert(calcularBpm(12, 10000000) == 72, "Janela de dez segundos");
static_assert(calcularBpm(12, 12000000) == 60, "Janela de doze segundos");

void atualizarBpm() {
  if (esp_timer_get_time() - inicioJanelaBpmUs < JANELA_BPM_MS * 1000ULL) return;
  portENTER_CRITICAL(&travaPulso);
  const uint64_t agora = esp_timer_get_time();
  const uint64_t duracaoUs = agora - inicioJanelaBpmUs;
  const uint16_t pulsos = pulsosNaJanela;
  pulsosNaJanela = 0;
  inicioJanelaBpmUs = agora;
  portEXIT_CRITICAL(&travaPulso);
  bpmAtual = calcularBpm(pulsos, duracaoUs);
}

void tratarBotaoRede() {
  const bool estado = digitalRead(PINO_REDE);
  if (ultimoEstadoRede == HIGH && estado == LOW && millis() - ultimoCliqueRede > 250) {
    conectividadeAtiva = !conectividadeAtiva;
    ultimoCliqueRede = millis();
  }
  ultimoEstadoRede = estado;
}

void coletarEProcessar() {
  const uint64_t instanteMs = esp_timer_get_time() / 1000;
  const float temperatura = dht.readTemperature();
  const float umidade = dht.readHumidity();
  const Amostra amostra = {
      proximaSequencia++, instanteMs, temperatura, umidade, bpmAtual,
      (isfinite(temperatura) && temperatura >= LIMITE_TEMPERATURA_ALERTA) ||
          bpmAtual >= LIMITE_BPM_ALERTA,
      !conectividadeAtiva || !mqttDisponivel};
  adicionarNaFila(amostra);
}

void tarefaRede(void*) {
  bool modoAnterior = true;
  bool relogioConfigurado = false;
  uint32_t ultimaTentativaMqtt = millis() - INTERVALO_RECONEXAO_WIFI_MS;
  uint32_t ultimoRegistroOffline = millis();
  for (;;) {
    const bool online = conectividadeAtiva;
    if (online != modoAnterior) {
      if (!online) {
        mqttDisponivel = false;
        mqtt.disconnect();
        WiFi.disconnect();
        registrarNoSerial("Modo offline ativado: leituras serão mantidas na fila local");
      } else {
        registrarNoSerial("Modo online ativado: iniciando sincronização de pendências");
      }
      modoAnterior = online;
    }

    if (online) {
      conectarWifiSeNecessario();
      if (!relogioConfigurado && WiFi.status() == WL_CONNECTED) {
        configTime(0, 0, "pool.ntp.org");
        relogioConfigurado = true;
      }
      if (!mqtt.connected()) {
        mqttDisponivel = false;
        if (millis() - ultimaTentativaMqtt >= INTERVALO_RECONEXAO_WIFI_MS) {
          ultimaTentativaMqtt = millis();
          conectarMqtt();
        }
      }
      mqttDisponivel = conectividadeAtiva && mqtt.loop();
      if (mqttDisponivel) sincronizarPendentes();
    } else if (millis() - ultimoRegistroOffline >= INTERVALO_LEITURA_MS) {
      ultimoRegistroOffline = millis();
      registrarNoSerial("Coleta offline");
    }
    atualizarLed();
    // Um envio por iteração, sem manter a fila travada durante a rede.
    vTaskDelay(pdMS_TO_TICKS(20));
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(PINO_PULSO, INPUT_PULLUP);
  pinMode(PINO_REDE, INPUT_PULLUP);
  pinMode(PINO_LED_REDE, OUTPUT);
  dht.begin();

#if MQTT_USAR_TLS
  if (MQTT_CERTIFICADO_RAIZ == nullptr) {
    Serial.println("[MQTT] TLS sem certificado de autoridade: configure MQTT_CERTIFICADO_RAIZ antes de publicar.");
  } else {
    clienteMqtt.setCACert(MQTT_CERTIFICADO_RAIZ);
  }
#endif
  mqtt.setServer(MQTT_HOST, MQTT_PORT);
  mqtt.setBufferSize(TAMANHO_BUFFER_MQTT);
  mqtt.setKeepAlive(30);
  inicioJanelaBpmUs = esp_timer_get_time();
  attachInterrupt(digitalPinToInterrupt(PINO_PULSO), contarPulso, FALLING);
  if (xTaskCreate(tarefaRede, "cardioia-rede", 8192, nullptr, 1, nullptr) != pdPASS) {
    Serial.println("[EDGE] Falha ao iniciar tarefa de rede; aquisição local permanece ativa.");
  }
  Serial.println("[CARDIOIA] Monitor vestível iniciado. Botão PULSO registra batida; botão ONLINE/OFFLINE alterna conectividade.");
}

void loop() {
  tratarBotaoRede();
  atualizarBpm();

  if (millis() - ultimaLeitura >= INTERVALO_LEITURA_MS) {
    ultimaLeitura = millis();
    coletarEProcessar();
  }
  delay(1);
}
