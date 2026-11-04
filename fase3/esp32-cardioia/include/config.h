#pragma once

// config.local.h é ignorado pelo Git e tem prioridade quando existe.
#if __has_include("config.local.h")
#include "config.local.h"
#else

// Configuração sem dados sensíveis para executar a demonstração no Wokwi.
#define WIFI_SSID "Wokwi-GUEST"
#define WIFI_SENHA ""
#define WIFI_CANAL 6

// Broker público apenas para a demonstração acadêmica inicial.
#define MQTT_HOST "broker.hivemq.com"
#define MQTT_PORT 1883
#define MQTT_USAR_TLS 0
#define MQTT_USUARIO ""
#define MQTT_SENHA ""
// Para MQTT_USAR_TLS=true, informe o PEM da autoridade certificadora do broker.
#define MQTT_CERTIFICADO_RAIZ nullptr

#define MQTT_TOPICO_TELEMETRIA "cardioia/pulseia/v1/telemetria"
#define MQTT_CLIENTE_PREFIXO "cardioia-pulseia"
#define ID_PACIENTE "PACIENTE_DEMO_001"

#endif
