# Avaliação do classificador — revisão pós-feedback

## Separação dos dados

A base principal contém 416 frases simuladas, 208 por classe, organizadas em
208 cenários com duas paráfrases. As paráfrases nunca são separadas entre os
conjuntos.

| Conjunto | Frases | Cenários | Uso |
| --- | ---: | ---: | --- |
| Treino | 256 | 128 | seleção e ajuste do TF-IDF e da Regressão Logística |
| Calibração | 16 | 8 | calibração sigmoide das probabilidades |
| Teste final | 64 | 32 | avaliação interna da revisão |
| Regressão | 80 | 40 | preserva testes e erros já vistos nas versões anteriores |

O teste final cresceu de 24 para 64 frases. Além dele, há 32 exemplos derivados
de fontes públicas, 32 frases em pares de gravidade e 48 variações sintéticas de
sexo referido e faixa etária. Nenhum desses três conjuntos entra no treino, na
seleção de parâmetros ou na calibração.

## Resultado principal

O modelo selecionado usa unigramas e bigramas, `C=4` e sem peso adicional de
classe. No teste final ampliado, obteve:

| Medida | Resultado |
| --- | ---: |
| Acurácia | 89,1% (57/64) |
| Baseline | 50,0% |
| Precisão de alto risco | 85,7% |
| Recall de alto risco | 93,8% |
| F1 macro | 0,890 |
| Falsos negativos | 2 |
| Falsos positivos | 5 |

A matriz de confusão tem 27 acertos e cinco erros de baixo risco, além de 30
acertos e dois erros de alto risco. O resultado é inferior aos 91,7% da entrega
avaliada, mas se apoia em um teste maior e mais difícil. Isso oferece uma visão
mais realista das limitações do classificador.

## Investigação dos falsos positivos anteriores

As duas frases do cenário `B69` descrevem suor após academia com recuperação.
Na entrega avaliada, ambas foram classificadas incorretamente como alto risco.
Elas foram movidas para regressão, pois os erros já eram conhecidos. A revisão
incluiu exemplos de recuperação após esforço e marcadores contextuais de esforço
e recuperação. As duas frases agora são classificadas como baixo risco, com
probabilidades de alto risco de aproximadamente 0,23 e 0,19.

O arquivo `outputs/investigacao_erros.csv` também mostra as contribuições locais
dos termos. Elas explicam o cálculo do modelo linear, não estabelecem causa
clínica. Os novos erros revelam que expressões como “após”, “normal” ou uma
negação podem receber pesos inadequados dependendo do vocabulário do treino.

## Avaliações complementares

| Avaliação | Casos | Acurácia | Recall alto risco | Observação |
| --- | ---: | ---: | ---: | --- |
| Externa, baseada em fontes | 32 | 84,4% | 100% | cinco falsos positivos; não é padrão-ouro clínico |
| Pares de gravidade | 32 | 84,4% | 100% | mostra dificuldade com linguagem semelhante em contextos diferentes |
| Regressão | 80 | 96,3% | 100% | inclui exemplos já observados; não é teste independente |
| Subgrupos sintéticos | 48 | 100% | 100% | ausência de diferença neste teste não comprova fairness |

Os pares de gravidade foram criados para comparar frases com temas parecidos,
mas com persistência, recuperação, repouso e intensidade diferentes. Cinco
frases leves ou resolvidas ainda foram classificadas como alto risco. Portanto,
o modelo reduziu um erro conhecido, mas continua dependente de atalhos lexicais.

## Probabilidades

A calibração sigmoide foi ajustada em 16 frases separadas. No teste, o Brier
score passou de 0,127 para 0,105 e o log loss de 0,425 para 0,340. Valores menores
são melhores nesses dois indicadores, mas a amostra é pequena. A curva de
calibração está em `outputs/curva_calibracao.png`.

Uma saída de 0,80 significa apenas maior confiança do classificador dentro deste
conjunto. Não significa “80% de chance clínica” de agravamento, não incorpora
sinais vitais, exames, prevalência ou avaliação profissional e não deve orientar
atendimento.

## Limite de independência

As frases externas foram redigidas a partir de orientações do Ministério da
Saúde e da OMS e mantidas fora do desenvolvimento. Elas não são relatos reais
nem exemplos fornecidos por avaliadores independentes. Uma avaliação externa
forte ainda exige corpus licenciado, população definida e rótulos revisados por
profissionais que não participaram da construção do modelo.
