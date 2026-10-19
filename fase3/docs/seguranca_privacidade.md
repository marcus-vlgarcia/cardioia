# Segurança, privacidade e limites

O CardioIA nesta fase é uma simulação didática. As mensagens usam valores do
DHT22 e pulsos inseridos manualmente; o identificador do payload é fictício.
Nenhuma leitura deve ser entendida como prontuário, sinal vital validado ou
diagnóstico.

## Decisões adotadas

- Não há dados pessoais, nomes, documentos, localização ou registros clínicos
  no payload demonstrativo.
- O broker público serve somente para testar telemetria fictícia. Ele não é
  apropriado para informações de saúde.
- A configuração para broker Cloud prevê TLS e o programa bloqueia uma conexão
  TLS sem certificado raiz configurado.
- Senhas e certificados reais não estão versionados. O arquivo de exemplo usa
  marcadores, e os valores devem ser mantidos fora do Git.
- A fila local é limitada a 1.000 leituras e informa quando descarta a mais
  antiga. Essa decisão evita esgotamento de memória, mas deixa explícita a
  limitação do histórico em quedas longas.

## Riscos e evolução necessária

Em um produto real, seria necessário usar autenticação individual por
dispositivo, autorização por tópico, criptografia em trânsito e em repouso,
rotação de segredos, logs de auditoria, política de retenção e controle de
acesso. Também seria necessário minimizar dados, obter base legal apropriada e
seguir a LGPD, além de avaliar os riscos operacionais e clínicos.

Os limiares de 38 °C e 120 BPM existem apenas para acionar a interface da
demonstração. Eles não são uma triagem e não substituem avaliação profissional.
Alarmes de um sistema de saúde real requerem sensores validados, contexto do
paciente, protocolos assistenciais, testes de segurança e validação clínica.
