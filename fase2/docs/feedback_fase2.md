# Evolução após o feedback da Fase 2

| Recomendação recebida | Mudança realizada | Limite que permanece |
| --- | --- | --- |
| Ampliar a diversidade | Base principal ampliada de 288 para 992 frases; 576 relatos novos variam fala cotidiana, hesitação, tempo e erros ortográficos. | São variações de situações redigidas pela equipe, não pacientes independentes. |
| Melhorar negações complexas | Tratamento de dupla negação, contraste e sinalização de contradições, com testes automatizados e normalização de alguns erros de escrita. | Não há compreensão completa da linguagem. |
| Aumentar o teste final | Teste passou de 24 para 264 frases; versões anteriores foram para regressão. | As 264 frases derivam de apenas 22 famílias novas. |
| Investigar os dois falsos positivos | B69 foi analisado por contribuição de termos e preservado na regressão; agora as duas frases são classificadas corretamente. | Corrigir um cenário conhecido não prova generalização. |
| Usar avaliação externa | Criado conjunto separado com 32 cenários derivados de Ministério da Saúde e OMS, com fonte por linha, além de um protocolo para coleta independente. | A coleta por autores e revisores externos ainda precisa ser realizada. |
| Diferenciar leve e grave | Criados 16 pares contrastivos e marcadores de recuperação, persistência, esforço e repouso; a avaliação atual tem 90,6% de acurácia. | Permanecem três falsos positivos nos 32 exemplos pareados. |
| Expandir análise de vieses | Auditoria com 48 casos pareados por sexo referido e faixa etária, com métricas por grupo. | O teste é sintético e não comprova fairness populacional. |
| Incorporar validação especializada | Criada ficha para as 83 associações, com fontes, parecer, identificação e data do revisor. | A validação profissional está pendente e não foi simulada. |
| Interpretar probabilidades | Conjunto exclusivo de calibração, curva de confiabilidade, Brier score, log loss e aviso de que confiança não é risco clínico. | A calibração usa 88 frases simuladas e não é clínica. |

Esta revisão prioriza evidência e rastreabilidade. Por isso, novos erros foram
mantidos nos resultados em vez de ajustar o teste para obter uma nota maior.
