# Validação técnica e demonstração integrada

As verificações locais e a demonstração integrada foram realizadas em
19/10/2026.

## Firmware

O projeto foi compilado com PlatformIO 6.2.0, plataforma Espressif32 6.12.0 e
framework Arduino para `esp32dev`. A compilação terminou sem erros.

| Recurso | Resultado da compilação |
| --- | --- |
| RAM estática estimada | 64.864 bytes de 327.680 bytes (19,8%) |
| Flash estimada | 752.197 bytes de 1.310.720 bytes (57,4%) |

A fila de 1.000 leituras está incluída nesse consumo de RAM. Há margem no
protótipo, mas a capacidade deve voltar a ser medida sempre que a estrutura da
amostra ou as bibliotecas forem alteradas.

## Arquivos e integração

O comando `python fase3/scripts/verificar_fase3.py` confirmou:

- presença do ESP32, DHT22 e botões no circuito;
- conexões mínimas do diagrama;
- implementação da fila limitada, MQTT e reconexão espaçada;
- consistência do tópico entre ESP32 e Node-RED;
- presença de gráfico, gauges, alerta e casos de teste no dashboard;
- existência e extensão mínima dos relatórios.

A função JavaScript exportada no fluxo também é exercitada por
`node fase3/scripts/testar_fluxo_nodered.js`, sem depender de Wokwi ou broker.
O teste cobre quatro cenários: leitura normal, leitura em alerta, salto de
sequência e payload inválido. Os quatro comportamentos esperados foram
confirmados.

O verificador geral `python scripts/verificar_entrega.py` também terminou sem
erros para as Fases 1, 2 e 3.

## Demonstração integrada

O projeto público do Wokwi foi executado com `Wokwi-GUEST`, o broker
`broker.hivemq.com:1883` e o tópico `cardioia/pulseia/v1/telemetria`. O Monitor
Serial registrou mensagens com o prefixo `[MQTT] Publicado`. Em paralelo, o
Node-RED se conectou ao mesmo tópico e mostrou as leituras recebidas no painel:
temperatura de 36,7 °C, umidade de 55%, BPM igual a 0 e fila Edge vazia. Isso
confirma o caminho completo Wokwi → MQTT → Node-RED. O fluxo e os valores
observados estão detalhados em [registro_execucao.md](registro_execucao.md).

O alerta também foi validado com o caso de teste explícito do fluxo: 126 BPM,
38,2 °C e três pendências na fila resultaram no texto `ALERTA SIMULADO`. Esse
teste confirma a regra de interface; não deve ser confundido com uma leitura
clínica nem com uma publicação física do sensor.

## Limites da validação

A compilação e a demonstração comprovam este protótipo acadêmico, não a
confiabilidade de um dispositivo médico. A captura do modo offline e da
sincronização após reconexão ainda deve ser adicionada à pasta `evidencias/`
para documentar visualmente esse cenário. Em produto real, seriam necessários
sensores validados, persistência física, confirmação de entrega pelo servidor,
TLS, autenticação e avaliação clínica.
