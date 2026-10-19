# Validação técnica local

Verificação realizada em 19/10/2026 antes da execução visual no Wokwi.

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

A função JavaScript exportada no fluxo também foi executada isoladamente com
quatro cenários: leitura normal, leitura em alerta, salto de sequência e payload
inválido. Os quatro comportamentos esperados foram confirmados.

O verificador geral `python scripts/verificar_entrega.py` também terminou sem
erros para as Fases 1, 2 e 3.

## Limite desta validação

A compilação prova que o firmware pode ser construído, mas não substitui a
execução no simulador. O link público do Wokwi, a conexão com o broker, a
recepção no Node-RED e as capturas do dashboard continuam dependendo do teste
integrado realizado pelo grupo.
