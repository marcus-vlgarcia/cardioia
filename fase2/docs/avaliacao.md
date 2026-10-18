# Avaliação do classificador após a ampliação

## Dados e separação

A base principal contém 1.112 frases sintéticas balanceadas, sendo 556 por
classe. A revisão anterior tinha 992 frases. Os 120 casos acrescentados agora
foram redigidos individualmente para incluir fala cotidiana, erros de escrita,
negações, apresentações menos típicas e situações leves e graves com palavras
parecidas. Eles foram colocados exclusivamente no treino. As fontes que
orientaram os cenários estão em [fontes_casos_adicionais.md](fontes_casos_adicionais.md).

| Partição | Frases | Grupos | Uso |
| --- | ---: | ---: | --- |
| Treino | 616 | 368 | seleção e ajuste do classificador |
| Calibração | 88 | 44 | ajuste sigmoide das probabilidades |
| Teste de 264 frases | 264 | 132 | acompanhamento histórico da revisão anterior |
| Regressão | 144 | 72 | casos conhecidos de versões mais antigas |

As variações de uma mesma situação permanecem na mesma partição. Os 120 casos
novos têm um grupo próprio por frase. As 264 frases de teste vêm de apenas 22
famílias de situações; esse conjunto já foi examinado na versão anterior e não
é mais uma medida inédita de desempenho.

Criamos ainda duas avaliações fora da base principal: `auditoria_nova.csv`
tem 80 frases individuais balanceadas; `auditoria_contrastiva.csv` tem 20 pares
de relatos leves e graves com vocabulário semelhante. Essas 120 frases não
entram no treino, na calibração nem na seleção de parâmetros. Foram elaboradas
com apoio de IA no mesmo projeto e seus rótulos são didáticos, sem validação
clínica.

## Como o modelo foi escolhido

Comparamos TF-IDF de palavras com unigramas e bigramas, palavras até
trigramas e uma combinação de palavras e caracteres. A validação cruzada
agrupada por família utilizou apenas o treino. O melhor F1 macro médio nessa
comparação foi 0,963, com unigramas/bigramas e Regressão Logística `C=8`.
A opção com caracteres foi avaliada, mas não venceu.

Para uma comparação direta, reproduzimos o modelo anterior com sua configuração
publicada, treinando-o somente nas 496 frases que compunham o treino antigo e
usando as mesmas 88 frases para calibração. O modelo ampliado foi treinado nas
616 frases. Ambos foram aplicados às duas auditorias novas.

## Resultados

| Avaliação | Modelo anterior | Modelo ampliado | Leitura |
| --- | ---: | ---: | --- |
| Conjunto conhecido de 264 frases | 89,0% (235/264) | 94,7% (250/264) | melhora no acompanhamento histórico |
| Auditoria nova de 80 frases | 97,5% (78/80) | 97,5% (78/80) | empate; dois falsos positivos em ambos |
| Vinte pares novos | 97,5% (39/40) | 97,5% (39/40) | empate; um falso negativo em ambos |

No conjunto conhecido, a matriz de confusão atual é `[[124, 8], [6, 126]]`
na ordem baixo/alto risco. Os falsos positivos caíram de 23 para oito; os
falsos negativos permaneceram em seis. A precisão de alto risco foi 94,0%, o
recall foi 95,5% e o F1 macro foi 0,947. O conjunto possui 44 frases com erro
ortográfico e 44 coloquiais; a acurácia foi 95,5% em cada tipo.

As auditorias novas somam 120 frases e tiveram 117 acertos nos dois modelos.
Os mesmos erros persistiram: uma frase sobre uma notícia de televisão e outra
sobre recuperar o fôlego após carregar compras foram classificadas como alto
risco; uma frase que combina pulso acelerado em repouso e quase desmaio foi
classificada como baixo risco. As previsões completas estão em
`outputs/predicoes_auditoria_nova.csv` e
`outputs/predicoes_auditoria_contrastiva.csv`. Esses erros não foram usados
para ajustar o modelo desta versão.

Os conjuntos complementares mais antigos também foram recalculados: 96,9% nas
32 frases baseadas em fontes públicas, 93,8% nos 32 pares de gravidade
anteriores e 97,9% na regressão de 144 frases. A auditoria sintética de
subgrupos permaneceu em 48/48; isso não demonstra equidade entre populações.

## O que a acurácia permite concluir

O aumento de 89,0% para 94,7% no conjunto conhecido mostra que as frases
adicionais ajudaram a lidar com situações semelhantes às dificuldades já
observadas. O empate nas duas auditorias novas não mostra ganho de
generalização. Mesmo 97,5% deve ser lido com cautela: são textos curtos,
escritos pela equipe, com rótulos artificiais e prevalência equilibrada por
construção. Nenhuma métrica estima a segurança em pacientes reais.

A calibração foi ajustada em 88 frases separadas. No conjunto histórico, o
Brier score caiu de 0,077 para 0,048 e o log loss de 0,290 para 0,172 após
calibração. Esses números medem a coerência das probabilidades com os rótulos
deste corpus; uma probabilidade de 0,80 não significa 80% de risco clínico.

O próximo ganho mensurável exige material com origem independente e revisão dos
rótulos. Enquanto isso não estiver disponível, os erros das auditorias podem
orientar novos experimentos, mas uma avaliação posterior precisará ser
reservada antes de novos ajustes. Não seria correto anunciar 94,7% como
acurácia clínica ou como melhora comprovada em dados inéditos.
