# Roteiro de execução e evidências

## 1. Sensores e leitura

1. Inicie a simulação Wokwi e abra o Monitor Serial em 115200 baud.
2. Mostre o DHT22 e os botões `PULSO` e `ONLINE/OFFLINE` no circuito.
3. Pressione `PULSO` algumas vezes e aguarde a janela de dez segundos.
4. Registre no Serial as linhas `[SENSOR]` com temperatura, umidade e BPM.

## 2. Resiliência offline

1. Pressione `ONLINE/OFFLINE` para desativar a rede.
2. Aguarde duas ou mais leituras; o Serial deve mostrar que a fila cresce.
3. Reative a rede pelo mesmo botão.
4. Registre as linhas `[MQTT] Publicado` e a mensagem de fila sincronizada.

## 3. MQTT e dashboard

1. Importe `node-red/flows_cardioia.json` no Node-RED e faça Deploy.
2. Use os nós de teste normal e alerta para conferir o layout; não registre
   esses testes como prova de MQTT.
3. Abra `/ui` e mostre o gráfico BPM, gauges e texto de fila recebendo dados do
   ESP32, com o nó MQTT exibindo estado conectado.
4. Ajuste o DHT22 para pelo menos 38 °C ou simule pulsos para atingir 120 BPM.
5. Capture o texto de alerta no dashboard e o JSON correspondente no Debug.

## Evidências a anexar

- Link público do projeto Wokwi, depois de publicado pelo grupo.
- Captura do circuito e do Monitor Serial.
- Captura da fila offline antes e depois da sincronização.
- Captura do dashboard normal.
- Captura do dashboard em alerta.
- Relatórios `relatorio_edge.md` e `relatorio_mqtt_dashboard.md` exportados em
  PDF, se a plataforma de entrega solicitar arquivos em PDF.
