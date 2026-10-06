# Avaliação do classificador

## Base e separação dos conjuntos

A base contém 288 frases simuladas, organizadas em 144 cenários com duas
paráfrases. São 208 frases de treino, 24 de teste final e 56 de regressão. As
duas frases do mesmo cenário ficam sempre no mesmo conjunto.

Os testes analisados nas versões anteriores foram preservados como regressão:
os grupos A51–A60, B51–B60 e os oito grupos do teste inicial. Eles não entram
no treino, mas seus resultados não são evidência independente porque seus erros
já orientaram a revisão. O teste final é formado pelos grupos A67–A72 e B67–B72.

## Configuração e limiar escolhidos no treino

O classificador usa TF-IDF e Regressão Logística. Antes de consultar o teste
final, a validação cruzada por cenário comparou quatro configurações: n-gramas
(1,2) ou (1,3), com C=1 ou C=4. A seleção por F1 macro escolheu bigramas e C=4.
As acurácias das quatro divisões foram 96,15%, 92,31%, 96,15% e 92,31%, com média
de 94,23%. Esses valores ajudam a escolher o modelo, mas podem ser otimistas.

Também marcamos cinco negações comuns antes da vetorização, como “não sinto dor
no peito” e “sem falta de ar”. O procedimento é limitado: não compreende toda a
estrutura da frase, ironia, dupla negação ou relato indireto complexo.

O limiar de decisão foi escolhido por previsões fora da divisão no treino:

| Limiar para alto risco | Precisão alto risco | Recall alto risco | Falsos negativos | Falsos positivos |
| ---: | ---: | ---: | ---: | ---: |
| 0,35 | 77,61% | 100% | 0 | 30 |
| 0,40 | 81,60% | 98,08% | 2 | 23 |
| 0,45 | 87,18% | 98,08% | 2 | 15 |
| 0,50 | 91,82% | 97,12% | 3 | 9 |

Para esta simulação de triagem, foi selecionado 0,35: é o menor limiar com
precisão de alto risco acima de 75% e o maior recall. Isso privilegia evitar
falsos negativos e, como consequência, pode aumentar falsos positivos.

O código prioriza recall, depois F1 macro e, em caso de empate, o menor limiar
entre os elegíveis. Se nenhum atingir a precisão mínima, usa 0,50 e informa a
ressalva. As probabilidades não foram calibradas clinicamente. Como a escolha de
parâmetros e limiar reutiliza divisões do treino, esses resultados podem ser
otimistas; são critérios de desenvolvimento, não uma avaliação independente.

## Resultado no teste final

| Medida | Resultado |
| --- | ---: |
| Acurácia | 91,7% (22/24) |
| Baseline | 50% |
| Precisão de alto risco | 85,7% |
| Recall de alto risco | 100% |
| F1 de alto risco | 0,923 |
| Falsos negativos | 0 |
| Falsos positivos | 2 |

A matriz de confusão tem 10 acertos de baixo risco, dois falsos positivos,
nenhum falso negativo e 12 acertos de alto risco. Os dois falsos positivos são
as paráfrases do cenário B69: suor após exercício que cessou com descanso. O
erro sugere uma associação lexical com o suor, apesar do contexto de recuperação;
essa interpretação é uma hipótese, não uma explicação causal validada.

O resultado é promissor para o exercício, mas o teste tem somente 12 cenários e
cada erro altera a acurácia em 4,17 pontos percentuais. Todos os exemplos são
sintéticos e produzidos no mesmo projeto. A métrica não representa desempenho
clínico nem valida uso em atendimento.

A revisão de outubro reexecutou a configuração existente, sem trocar os exemplos,
os rótulos ou os parâmetros para elevar a pontuação. O teste já foi observado no
desenvolvimento anterior, portanto sua reprodução não constitui um novo teste
independente. A próxima melhoria orientada por esses erros exigirá outra avaliação.

## Regressão e desafios

O conjunto de regressão teve 48 acertos em 56 frases (85,7%). Os 12 desafios
adicionais tiveram 12 acertos, inclusive os exemplos de negação que antes eram
classificados como alto risco. A revisão combinou ampliação de cenários, marcação
de negações e mudança de limiar; o experimento não isola a contribuição de cada
mudança. Ainda há falhas em frases mais longas ou fora do vocabulário da base.

Os arquivos `predicoes_teste.csv`, `predicoes_regressao.csv` e
`resultados_desafios.csv` guardam cada previsão. `comparacao_limiares.csv`
mostra a escolha do limiar e `metricas.json` registra a seed, versões, hashes e
métricas da execução.

## Continuidade planejada

O teste final atual deve permanecer sem alterações enquanto esta versão existir.
Se seus erros forem usados para treinar outra revisão, ele será apenas regressão
e um novo conjunto reservado ou externo deverá ser criado. Para fases futuras,
o grupo pretende buscar revisão clínica independente dos rótulos, diversidade
de linguagem e dados, avaliação externa e critérios explícitos para o custo de
falsos negativos e falsos positivos.
