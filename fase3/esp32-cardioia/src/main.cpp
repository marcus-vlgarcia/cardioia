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
  uint32_t instanteMs;
  float temperatura;
  float umidade;
  uint16_t bpm;
  bool alerta;
};

Amostra fila[MAX_AMOSTRAS_OFFLINE];
uint16_t inicioFila = 0;
uint16_t tamanhoFila = 0;
uint32_t amostrasDescartadas = 0;
uint32_t proximaSequencia = 1;

bool conectividadeAtiva = true;
bool ultimoEstadoPulso = HIGH;
bool ultimoEstadoRede = HIGH;
uint32_t ultimoCliquePulso = 0;
uint32_t ultimoCliqueRede = 0;
uint32_t inicioJanelaBpm = 0;
uint32_t ultimaLeitura = 0;
uint32_t ultimaTentativaWifi = 0;
uint16_t pulsosNaJanela = 0;
uint16_t bpmAtual = 0;

void registrarNoSerial(const char* evento) {
  Serial.printf("[EDGE] %s | fila=%u | descartadas=%lu | rede=%s\n", evento,
                tamanhoFila, amostrasDescartadas,
                conectividadeAtiva ? "habilitada" : "offline simulada");
}

void adicionarNaFila(const Amostra& amostra) {
  if (tamanhoFila == MAX_AMOSTRAS_OFFLINE) {
    inicioFila = (inicioFila + 1) % MAX_AMOSTRAS_OFFLINE;
    tamanhoFila--;
    amostrasDescartadas++;
    Serial.println("[EDGE] Limite local atingido: amostra mais antiga substituída.");
  }
  const uint16_t posicao = (inicioFila + tamanhoFila) % MAX_AMOSTRAS_OFFLINE;
  fila[posicao] = amostra;
  tamanhoFila++;
}

bool montarPayload(const Amostra& amostra, char* destino, size_t tamanhoDestino) {
  // A mensagem atual ainda ocupa a cabeça da fila. O painel recebe a
  // quantidade que restará caso esta publicação seja aceita pelo cliente MQTT.
  const uint16_t pendentesAposEnvio = tamanhoFila > 0 ? tamanhoFila - 1 : 0;
  const int escrito = snprintf(
      destino, tamanhoDestino,
      "{\"projeto\":\"CardioIA\",\"paciente_id\":\"%s\",\"sequencia\":%lu,"
      "\"instante_ms\":%lu,"
      "\"temperatura_c\":%.2f,\"umidade_pct\":%.2f,\"bpm\":%u,"
      "\"pulso_detectado\":%s,\"alerta\":%s,\"fila_offline\":%u,"
      "\"amostras_descartadas\":%lu,\"origem\":\"edge_esp32\"}",
      ID_PACIENTE, static_cast<unsigned long>(amostra.sequencia),
      static_cast<unsigned long>(amostra.instanteMs), amostra.temperatura,
      amostra.umidade, amostra.bpm, amostra.bpm > 0 ? "true" : "false",
      amostra.alerta ? "true" : "false", pendentesAposEnvio,
      static_cast<unsigned long>(amostrasDescartadas));
  return escrito > 0 && static_cast<size_t>(escrito) < tamanhoDestino;
}

bool publicar(const Amostra& amostra) {
  char payload[320];
  if (!montarPayload(amostra, payload, sizeof(payload))) {
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
  if (!conectarMqtt()) return;
  while (tamanhoFila > 0) {
    const Amostra& pendente = fila[inicioFila];
    if (!publicar(pendente)) {
      registrarNoSerial("Sincronização interrompida; dado preservado localmente");
      return;
    }
    inicioFila = (inicioFila + 1) % MAX_AMOSTRAS_OFFLINE;
    tamanhoFila--;
  }
  registrarNoSerial("Fila enviada e limpa após aceitação local das publicações MQTT");
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

void tratarBotaoPulso() {
  const bool estado = digitalRead(PINO_PULSO);
  if (ultimoEstadoPulso == HIGH && estado == LOW && millis() - ultimoCliquePulso > 120) {
    pulsosNaJanela++;
    ultimoCliquePulso = millis();
    Serial.printf("[SENSOR] Pulso registrado. Pulsos na janela: %u\n", pulsosNaJanela);
  }
  ultimoEstadoPulso = estado;
}

void atualizarBpm() {
  if (millis() - inicioJanelaBpm < JANELA_BPM_MS) return;
  bpmAtual = pulsosNaJanela * (60000 / JANELA_BPM_MS);
  Serial.printf("[SENSOR] BPM calculado: %u\n", bpmAtual);
  pulsosNaJanela = 0;
  inicioJanelaBpm = millis();
}

void tratarBotaoRede() {
  const bool estado = digitalRead(PINO_REDE);
  if (ultimoEstadoRede == HIGH && estado == LOW && millis() - ultimoCliqueRede > 250) {
    conectividadeAtiva = !conectividadeAtiva;
    ultimoCliqueRede = millis();
    if (!conectividadeAtiva) {
      mqtt.disconnect();
      WiFi.disconnect();
      registrarNoSerial("Modo offline ativado: leituras serão mantidas na fila local");
    } else {
      registrarNoSerial("Modo online ativado: iniciando sincronização de pendências");
      conectarWifiSeNecessario();
    }
  }
  ultimoEstadoRede = estado;
}

void coletarEProcessar() {
  const float temperatura = dht.readTemperature();
  const float umidade = dht.readHumidity();
  if (isnan(temperatura) || isnan(umidade)) {
    Serial.println("[SENSOR] Falha na leitura do DHT22; nenhuma amostra foi gravada.");
    return;
  }

  const Amostra amostra = {
      proximaSequencia++, millis(), temperatura, umidade, bpmAtual,
      temperatura >= LIMITE_TEMPERATURA_ALERTA || bpmAtual >= LIMITE_BPM_ALERTA};
  adicionarNaFila(amostra);
  Serial.printf("[SENSOR] temp=%.1f C | umidade=%.1f %% | bpm=%u | alerta=%s\n",
                temperatura, umidade, bpmAtual, amostra.alerta ? "SIM" : "nao");
  sincronizarPendentes();
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
  inicioJanelaBpm = millis();
  conectarWifiSeNecessario();
  Serial.println("[CARDIOIA] Monitor vestível iniciado. Botão PULSO registra batida; botão ONLINE/OFFLINE alterna conectividade.");
}

void loop() {
  tratarBotaoPulso();
  tratarBotaoRede();
  atualizarBpm();
  conectarWifiSeNecessario();
  if (mqtt.connected()) mqtt.loop();
  atualizarLed();

  if (millis() - ultimaLeitura >= INTERVALO_LEITURA_MS) {
    ultimaLeitura = millis();
    coletarEProcessar();
  }
}
