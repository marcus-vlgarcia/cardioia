// Configuração sem dados sensíveis para executar a demonstração no Wokwi.
// Para usar HiveMQ Cloud, altere MQTT_HOST, MQTT_PORT, MQTT_USAR_TLS,
// MQTT_USUARIO e MQTT_SENHA localmente. Não envie credenciais ao Git.

#pragma once

#define WIFI_SSID "Wokwi-GUEST"
#define WIFI_SENHA ""

// Broker público apenas para a demonstração acadêmica inicial.
#define MQTT_HOST "broker.hivemq.com"
#define MQTT_PORT 1883
#define MQTT_USAR_TLS 0
#define MQTT_USUARIO ""
#define MQTT_SENHA ""
// Para MQTT_USAR_TLS=true, informe o PEM da autoridade certificadora do broker.
#define MQTT_CERTIFICADO_RAIZ nullptr

#define MQTT_TOPICO_TELEMETRIA "cardioia/pulseia/v1/telemetria"
#define MQTT_CLIENTE_ID "cardioia-pulseia-esp32-001"
#define ID_PACIENTE "PACIENTE_DEMO_001"
