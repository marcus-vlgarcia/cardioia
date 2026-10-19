# Checklist do enunciado e evidências

Este quadro relaciona cada requisito da Fase 3 à evidência presente no projeto.
Itens que dependem de serviços externos só podem ser concluídos após a execução
e publicação pelo grupo.

| Requisito | Situação | Evidência |
| --- | --- | --- |
| ESP32 no Wokwi | Implementado; falta publicar o link | `esp32-cardioia/diagram.json` e `wokwi.toml` |
| DHT22 para temperatura e umidade | Atendido | DHT22 no circuito e leitura em `main.cpp` |
| Segundo sensor de livre escolha | Atendido | Botão `PULSO`, contagem em janela e cálculo de BPM |
| Conectividade simulada por variável booleana | Atendido | `conectividadeAtiva` e botão `ONLINE/OFFLINE` |
| Envio pelo Serial quando conectado | Atendido | Payload JSON impresso com o prefixo `[SERIAL]` |
| Coleta contínua sem conexão | Atendido | Toda amostra entra primeiro na fila circular |
| Sincronização após retorno da rede | Atendido | Publicação em ordem e remoção após aceitação local |
| Estratégia de armazenamento limitado | Atendido | 1.000 amostras; cerca de 83 minutos; substituição da mais antiga |
| Link público Wokwi | Pendente de ação externa | Publicar na conta do grupo e atualizar o README |
| Código C++ comentado | Atendido | `esp32-cardioia/src/main.cpp` |
| Relatório Edge de pelo menos uma página | Atendido | Markdown em `docs/` e PDF de 2 páginas em `output/pdf/` |
| Envio MQTT para broker | Implementado; evidência visual pendente | PubSubClient, broker público demonstrativo e configuração Cloud/TLS |
| Gráfico de sinal vital | Atendido | Gráfico temporal de BPM no fluxo Node-RED |
| Gauge de outro parâmetro | Atendido | Gauges de temperatura e umidade |
| Alerta automático | Atendido | BPM >= 120 ou temperatura simulada >= 38 °C |
| Export ou prints do dashboard | Export atendido; prints pendentes | `node-red/flows_cardioia.json` e roteiro de capturas |
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

## O que ainda precisa ser feito pelo grupo

1. Executar o circuito e confirmar a publicação no broker escolhido.
2. Publicar o projeto no Wokwi e substituir o marcador pelo link público.
3. Importar o fluxo no Node-RED e produzir as capturas indicadas no roteiro.
4. Registrar no README o broker utilizado na demonstração, sem expor senha.
