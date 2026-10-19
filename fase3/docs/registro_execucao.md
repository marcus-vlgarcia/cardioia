# Registro de execução integrada

## Objetivo do registro

Este documento registra o teste de ponta a ponta realizado em 19/10/2026 para
que a avaliação diferencie evidência de execução de recursos apenas previstos
no código. O teste usa exclusivamente valores simulados e o identificador
fictício `PACIENTE_DEMO_001`.

## Ambiente utilizado

| Componente | Configuração da demonstração |
| --- | --- |
| Simulador | [Wokwi — CardioIA Monitoramento IoT](https://wokwi.com/projects/478351016184515585) |
| Rede do simulador | `Wokwi-GUEST`, canal 6 |
| Broker MQTT | `broker.hivemq.com:1883`, sem credenciais |
| Tópico | `cardioia/pulseia/v1/telemetria` |
| Consumidor | Node-RED com `flows_cardioia.json` importado |
| Dashboard | Node-RED Dashboard clássico, rota local `/ui` |

## Resultado observado

1. O Wokwi iniciou o ESP32, leu o DHT22 e imprimiu mensagens JSON no Monitor
   Serial.
2. O firmware exibiu `[MQTT] Publicado` para amostras sequenciais do paciente
   demonstrativo.
3. O nó MQTT In do Node-RED permaneceu conectado ao broker e exibiu no painel
   Debug as mensagens de `PACIENTE_DEMO_001`.
4. O dashboard atualizou temperatura para 36,7 °C, umidade para 55%, BPM para
   0 e fila Edge para zero, com o estado visual sem alerta.

Esse resultado confirma a comunicação Wokwi → broker MQTT → Node-RED e a
atualização dos widgets a partir de telemetria do simulador, não de valores
digitados manualmente no painel.

## Teste de alerta e escopo

O fluxo também foi validado pelo seu nó de teste de alerta: o payload com
126 BPM, 38,2 °C e três pendências produziu o texto `ALERTA SIMULADO` e atualizou
os gauges. Esse é um teste deliberado de regra de interface; ele não constitui
diagnóstico, validação clínica ou evidência de que o DHT22 mede uma temperatura
corporal.

## Evidência visual a completar

As capturas devem ser feitas durante uma nova execução e salvas em
`fase3/evidencias/`, seguindo o [roteiro de evidências](roteiro_evidencias.md).
Em especial, ainda é importante registrar visualmente a fila crescendo no modo
offline e a sincronização posterior. Essa etapa complementa a demonstração sem
atribuir ao projeto uma persistência que o Wokwi não possui entre execuções.
