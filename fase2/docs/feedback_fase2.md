# Evolução após o feedback da Fase 2

| Recomendação recebida | Mudança realizada | Limite que permanece |
| --- | --- | --- |
| Ampliar a diversidade | Base principal ampliada de 288 para 1.112 frases; além das 576 variações anteriores, foram escritos 120 casos individuais com mais contextos, coloquialismos e erros ortográficos. | Os exemplos continuam simulados e sem pacientes independentes. |
| Melhorar negações complexas | Tratamento de dupla negação, contraste e sinalização de contradições, com testes automatizados e normalização de alguns erros de escrita. | Não há compreensão completa da linguagem. |
| Aumentar o teste final | Teste passou de 24 para 264 frases; agora há 80 frases inéditas e 20 pares inéditos em auditorias separadas. | O teste de 264 já foi observado; as auditorias novas também foram escritas no projeto. |
| Investigar os dois falsos positivos | B69 foi analisado por contribuição de termos e preservado na regressão; agora as duas frases são classificadas corretamente. | Corrigir um cenário conhecido não prova generalização. |
| Usar avaliação externa | Mantido conjunto de 32 cenários baseados em Ministério da Saúde e OMS; novas auditorias trazem mais 120 frases com fontes dos padrões de sintomas documentadas. | A coleta por autores e revisores externos ainda precisa ser realizada. |
| Diferenciar leve e grave | Mantidos 16 pares anteriores e criados 20 pares inéditos; o modelo ampliado teve 93,8% nos pares anteriores e 97,5% nos novos. | Houve um falso negativo entre os pares novos; o modelo anterior teve o mesmo resultado neles. |
| Expandir análise de vieses | Auditoria com 48 casos pareados por sexo referido e faixa etária, com métricas por grupo. | O teste é sintético e não comprova fairness populacional. |
| Incorporar validação especializada | Criada ficha para as 83 associações, com fontes, parecer, identificação e data do revisor. | A validação profissional está pendente e não foi simulada. |
| Interpretar probabilidades | Conjunto exclusivo de calibração, curva de confiabilidade, Brier score, log loss e aviso de que confiança não é risco clínico. | A calibração usa 88 frases simuladas e não é clínica. |

Esta revisão prioriza evidência e rastreabilidade. Por isso, novos erros foram
mantidos nos resultados em vez de ajustar o teste para obter uma nota maior.
