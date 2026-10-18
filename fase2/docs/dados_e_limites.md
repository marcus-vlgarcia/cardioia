# Dados, fontes e limites

## O que é simulado

Os dez relatos obrigatórios, as 1.112 frases da base principal, os desafios, os
pares de gravidade e a auditoria de subgrupos são exemplos simulados. Não são
prontuários, transcrições ou registros de atendimento. O balanceamento de 556
frases por classe foi escolhido para o exercício e não representa prevalência.

As 576 frases adicionadas nesta ampliação combinam duas redações de 48 situações
com seis formas de relato: direto, temporal, cotidiano, coloquial, hesitante e
com erro ortográfico controlado. As 128 frases da revisão anterior já traziam
relato de terceiros, esforço, recuperação, persistência, negações duplas e
contradições. Os 120 casos seguintes foram escritos como situações individuais
com linguagem cotidiana e pistas de gravidade variadas. Ainda há autoria
compartilhada e vocabulário repetido; 1.112 frases não equivalem a 1.112
pacientes. O teste histórico de 264 frases deriva de apenas 22 famílias de
situações. Há também 80 frases e 20 pares novos fora da base principal.

## Avaliação baseada em fontes externas

`avaliacao_externa.csv` contém 32 cenários escritos para teste a partir de
orientações públicas. Cada linha guarda URL e justificativa. O arquivo não foi
usado para treinar, escolher configuração ou calibrar o modelo. Essa separação
reduz a influência direta da base de treino, mas não transforma os rótulos em
padrão-ouro clínico e não torna as frases relatos reais.

Fontes principais, consultadas em 16/10/2026:

- [Ministério da Saúde — Infarto](https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/i/infarto)
- [Linha de Cuidado — manejo inicial da dor torácica](https://linhasdecuidado.saude.gov.br/portal/dor-toracica/unidade-de-atencao-primaria/manejo-inicial/)
- [Linha de Cuidado — avaliação e conduta](https://linhasdecuidado.saude.gov.br/portal/dor-toracica/unidade-de-pronto-atendimento/avaliacao-conduta/)
- [OMS — doenças cardiovasculares](https://www.who.int/health-topics/cardiovascular-diseases)

## Critério dos rótulos

- `alto risco`: combinação didática de sinais agudos ou persistentes que, nas
  fontes consultadas, demanda atenção imediata.
- `baixo risco`: descrição explicitamente leve, localizada ou completamente
  resolvida no exemplo, sem combinação de alertas. O rótulo não exclui doença e
  não significa que uma pessoa real possa dispensar avaliação.
- `grupo`: identifica duas redações do mesmo cenário; `familia` reúne também
  as seis variações. A partição é feita por família para reduzir vazamento.

Os rótulos não vêm do alvo numérico artificial da Fase 1 e não são produzidos
pelo extrator de sintomas.

Os novos arquivos `casos_adicionais.csv`, `auditoria_nova.csv` e
`auditoria_contrastiva.csv` guardam um identificador de fonte por cenário.
As fontes orientam os padrões de sintomas, mas não fornecem rótulos individuais
nem substituem revisão especializada. Consulte
[fontes_casos_adicionais.md](fontes_casos_adicionais.md).

## Negações e contradições

O extrator separa trechos por pontuação e contraste, diferencia negação simples
de alguns padrões de dupla negação e registra três listas: sintomas afirmados,
negados e contraditórios. Quando o mesmo sintoma aparece afirmado e negado, a
contradição fica visível na saída. Para não perder um possível alerta, a menção
afirmada continua disponível para o mapa.

O classificador recebe marcadores de negação, dupla negação, contradição,
recuperação, persistência, esforço, repouso e relato de terceiros. As regras não
resolvem ironia, ambiguidade, correferência, todos os tempos verbais ou todas as
formas regionais do português.

## Vieses

A auditoria usa 12 cenários em quatro versões, combinando sexo referido e faixa
etária, totalizando 48 frases. Mede acurácia, recall e falsos positivos por grupo.
Nesta amostra pareada, os resultados foram iguais. Isso mostra apenas que as
trocas testadas não alteraram as previsões nesses casos.

Não há dados suficientes para avaliar raça/cor, deficiência, escolaridade,
território, renda, identidade de gênero, acesso ao sistema de saúde ou diferenças
de prevalência. Também não há pacientes reais ou desfechos clínicos. Portanto,
o projeto não demonstra equidade entre populações.

## Validação clínica

As 83 linhas do mapa possuem fonte documental e campos para revisão profissional
em `revisao_clinica.csv`. A validação por especialista permanece explicitamente
pendente. O procedimento necessário está em `validacao_clinica.md`. Nenhum texto
do projeto deve afirmar que a tabela foi validada clinicamente antes desse passo.
