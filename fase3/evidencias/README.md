# Evidências da execução

As capturas registram a simulação realizada em 04/11/2026 com dados fictícios.
O DHT22 fornece temperatura e umidade simuladas, e os BPM resultam de toques no
botão de pulso. As imagens podem ser abertas na ordem abaixo:

1. [Circuito e leituras](01-wokwi-circuito-serial.png): ESP32, sensores,
   Monitor Serial e publicação MQTT.
2. [Modo offline](02-fila-offline.png): ativação do modo offline seguida de
   leituras. O `fila=0` exibido é do instante da ativação, antes dessas leituras.
3. [Retorno e publicação](03-sincronizacao-mqtt.png): reconexão e publicação
   com `fila_offline: 8`, estimativa de pendências após a mensagem mostrada.
4. [Fila sincronizada](03b-fila-sincronizada.png): registro posterior de
   publicação e fila vazia.
5. [Dashboard sem alerta](04-dashboard-normal.png): gráfico, medidores e
   estado do monitor com 60 BPM e 36,7 °C simulados.
6. [Dashboard em alerta](05-dashboard-alerta.png): alerta com temperatura
   simulada de 39,8 °C, acima do limite demonstrativo de 38 °C.

As mensagens MQTT usam QoS 0: a aceitação local registrada no Serial não
confirma armazenamento no broker. As capturas não representam dados clínicos.
