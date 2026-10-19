# Checklist do enunciado e evidências

Este quadro relaciona cada requisito da Fase 3 à evidência presente no projeto.
Ele foi atualizado após a demonstração integrada realizada em 19/10/2026.

| Requisito | Situação | Evidência |
| --- | --- | --- |
| ESP32 no Wokwi | Atendido e demonstrado | [Projeto público](https://wokwi.com/projects/478351016184515585), `diagram.json` e `wokwi.toml` |
| DHT22 para temperatura e umidade | Atendido | DHT22 no circuito e leitura em `main.cpp` |
| Segundo sensor de livre escolha | Atendido | Botão `PULSO`, contagem em janela e cálculo de BPM |
| Conectividade simulada por variável booleana | Atendido | `conectividadeAtiva` e botão `ONLINE/OFFLINE` |
| Envio pelo Serial quando conectado | Atendido | Payload JSON impresso com o prefixo `[SERIAL]` |
| Coleta contínua sem conexão | Atendido | Toda amostra entra primeiro na fila circular |
| Sincronização após retorno da rede | Atendido | Publicação em ordem e remoção após aceitação local |
| Estratégia de armazenamento limitado | Atendido | 1.000 amostras; cerca de 83 minutos; substituição da mais antiga |
| Link público Wokwi | Atendido | [Projeto público](https://wokwi.com/projects/478351016184515585) e link no README |
| Código C++ comentado | Atendido | `esp32-cardioia/src/main.cpp` |
| Relatório Edge de pelo menos uma página | Atendido | Markdown em `docs/` e PDF de 2 páginas em `output/pdf/` |
| Envio MQTT para broker | Atendido e demonstrado | Wokwi publicou no HiveMQ público; Node-RED recebeu telemetria no tópico configurado |
| Gráfico de sinal vital | Atendido | Gráfico temporal de BPM no fluxo Node-RED |
| Gauge de outro parâmetro | Atendido | Gauges de temperatura e umidade |
| Alerta automático | Atendido | BPM >= 120 ou temperatura simulada >= 38 °C |
| Export ou prints do dashboard | Atendido pelo export; capturas recomendadas | `node-red/flows_cardioia.json` e roteiro de capturas |
| Relatório MQTT/dashboard de pelo menos duas páginas | Atendido | Markdown em `docs/` e PDF de 2 páginas em `output/pdf/` |
| Grafana Cloud | Não realizado; opcional | Node-RED atende integralmente ao item obrigatório |

## Complementos alinhados à proposta

- contador sequencial de amostras e de descartes;
- cliente MQTT com identificador derivado do ESP32 para reduzir colisões;
- validação do payload no Node-RED antes de atualizar a interface;
- dois casos de teste no próprio fluxo: leitura normal e leitura em alerta;
- configuração local de credenciais ignorada pelo Git;
- bloqueio da conexão TLS sem certificado raiz;
- verificador automático da estrutura da Fase 3;
- compilação real do firmware, com consumo de RAM e flash registrado;
- documento separado sobre segurança, privacidade e limites clínicos.
- registro datado da execução ponta a ponta, distinguindo telemetria real do
  simulador e testes locais de interface.

## Próximo passo recomendado

Salvar as capturas reais indicadas em `evidencias/` e registrá-las em um
commit. Elas não substituem o export já entregue, mas oferecem evidência visual
direta de sensores, fila offline, sincronização, painel normal e alerta.
