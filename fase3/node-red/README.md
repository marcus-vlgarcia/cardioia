# Dashboard Node-RED — PulseIA

O arquivo `flows_cardioia.json` recebe as mensagens do tópico
`cardioia/pulseia/v1/telemetria`, interpreta o JSON e cria:

- gráfico de BPM;
- gauge de temperatura;
- gauge de umidade;
- texto de alerta para BPM maior ou igual a 120 e temperatura maior ou igual a 38 °C;
- indicador com o estado da fila local do ESP32;
- painel Debug com o JSON recebido.

## Importação

1. Instale o Node-RED e abra `http://localhost:1880`.
2. Em **Menu → Manage palette → Install**, instale `node-red-dashboard`.
3. Em **Menu → Import**, selecione `flows_cardioia.json` e confirme a importação.
4. Abra o nó **HiveMQ público - demonstração** e mantenha o host
   `broker.hivemq.com`, a porta `1883` e o tópico configurado no ESP32.
5. Clique em **Deploy** e abra `http://localhost:1880/ui`.

Para usar HiveMQ Cloud, substitua o broker por seu host, porta 8883, TLS e as
credenciais criadas no serviço. Não exporte senhas no fluxo que será enviado ao
GitHub.

## Evidências para a entrega

Faça ao menos três capturas:

1. Circuito em execução no Wokwi e Monitor Serial publicando JSON.
2. Dashboard com o gráfico, os gauges e o estado normal.
3. Dashboard com alerta: altere o DHT22 para 38 °C ou gere pulsos suficientes
   para atingir 120 BPM.

Inclua também uma captura da fila local: acione o botão `ONLINE/OFFLINE`, aguarde
duas leituras, reative a conectividade e mostre no Serial a sincronização.
