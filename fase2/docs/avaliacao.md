# Avaliação do classificador — revisão pós-feedback

## Separação e método

A base contém 992 frases sintéticas, 496 por classe. As 416 frases da revisão
anterior foram mantidas; 576 frases foram criadas de 48 situações-base, com
duas redações e seis variações por situação. Assim, o número de frases não
representa o número de pacientes ou de casos independentes. Cada família de
situações fica integralmente em uma partição. O teste anterior, já conhecido,
foi movido para regressão.

| Conjunto | Frases | Grupos de duas redações | Uso |
| --- | ---: | ---: | --- |
| Treino | 496 | 248 | seleção e ajuste do classificador |
| Calibração | 88 | 44 | ajuste sigmoide das probabilidades |
| Teste final | 264 | 132 | avaliação reservada; 22 famílias novas |
| Regressão | 144 | 72 | casos conhecidos de versões anteriores |

Comparamos TF-IDF de palavras (unigramas/bigramas e unigramas até trigramas)
e uma combinação de palavras e sequências de caracteres, útil para investigar
erros de escrita. A busca de parâmetros e a validação cruzada com quatro
partições foram feitas **somente no treino**, agrupadas por família. O melhor
F1 macro nessa validação escolheu palavras com `C=8`; a opção com caracteres
foi testada, mas não venceu. O teste final não foi usado para escolher modelo,
limiar ou exemplos de treinamento.

## Resultado principal

| Medida | Resultado |
| --- | ---: |
| Acurácia | 89,0% (235/264) |
| Referência majoritária | 50,0% |
| Precisão de alto risco | 84,6% |
| Recall de alto risco | 95,5% |
| F1 macro | 0,890 |
| Falsos negativos | 6 |
| Falsos positivos | 23 |

A matriz de confusão registra 109 acertos e 23 erros entre frases de baixo
risco, e 126 acertos e seis erros entre as de alto risco. A acurácia global
permaneceu próxima da revisão anterior (89,1% em 64 frases), apesar da base
maior. Isso não é evidência de desempenho clínico. Como as frases são variações
de poucos enredos redigidos pela equipe, métricas por frase podem superestimar
generalização. A validação cruzada no treino também foi mais otimista que o
teste final; os modelos ainda podem aproveitar padrões repetidos de redação.

No teste há 44 frases com erros ortográficos e 44 coloquiais, cada subconjunto
com 88,6% de acurácia. Há também variações diretas, temporais, de rotina e
hesitantes. A tabela completa está em `outputs/metricas_variacoes.csv`. Os
erros ortográficos testados são controlados; não demonstram resistência a
qualquer erro de digitação ou dialeto.

## Erros e avaliações complementares

Os dois falsos positivos do cenário histórico `B69`, sobre suor após academia
com recuperação, foram preservados no conjunto de regressão e agora são
classificados como baixo risco. O arquivo `outputs/investigacao_erros.csv`
registra os erros atuais e termos que favorecem cada classe. São contribuições
matemáticas do modelo, não explicações clínicas. Há falsos positivos em relatos
de azia resolvida e falsos negativos em algumas formas de falta de ar ao deitar;
o contexto ainda não é compreendido de maneira confiável.

| Avaliação | Frases | Acurácia | Recall alto risco | Limite |
| --- | ---: | ---: | ---: | --- |
| Baseada em fontes externas | 32 | 96,9% | 100% | frases redigidas para o projeto, sem rótulo clínico validado |
| Pares de gravidade | 32 | 90,6% | 100% | três falsos positivos |
| Regressão | 144 | 95,8% | 97,2% | casos conhecidos, não independentes |
| Subgrupos sintéticos | 48 | 100% | 100% | não comprova equidade populacional |

O ganho nos conjuntos complementares não deve ser confundido com evolução
comprovada em pacientes reais. Frases externas têm fonte documental, mas foram
escritas pela própria equipe. É necessário coletar relatos independentes,
legalmente utilizáveis e revisados por profissionais para avaliar generalização.

## Probabilidades e próximos testes

A calibração sigmoide foi ajustada em 88 frases separadas. No teste, o Brier
score passou de 0,096 para 0,070 e o log loss de 0,342 para 0,254. Valores
menores são melhores nesses indicadores para esta amostra, mas uma saída de
0,80 **não significa 80% de risco clínico**: faltam sinais vitais, exames,
prevalência, revisão especializada e validação prospectiva.

Para melhorar o sistema sem viciar o teste, a próxima iteração deve obter
novos relatos independentes e rótulos revisados, estudar os erros por família
e por subgrupo e reservar um novo teste antes de qualquer ajuste. Aumentar
frases derivadas dos mesmos exemplos ou ajustar o código após olhar os erros
do teste atual pode elevar a métrica sem melhorar a generalização.
