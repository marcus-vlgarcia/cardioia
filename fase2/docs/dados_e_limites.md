# Origem dos dados e limites

## Construção dos arquivos

Os 10 relatos, as 288 frases rotuladas e os 12 casos de desafio foram escritos
para esta simulação acadêmica. Não são prontuários, downloads de relatos reais
ou registros de atendimento. Os textos institucionais da Fase 1 continuam
preservados, mas não foram transformados em exemplos rotulados de pacientes.

O mapa contém 83 pares de expressões e 14 grupos de possíveis condições. Ele
registra combinações distintas que podem apontar para mais de uma hipótese, como
dor no peito relacionada a síndrome coronariana, angina, pericardite, miocardite,
dissecção de aorta, refluxo ou dor musculoesquelética. Inclui ainda insuficiência
cardíaca, arritmias, valvulopatias, cardiomiopatia por estresse, alterações de
pressão arterial, tromboembolismo pulmonar e ansiedade. É uma tabela de
associações didáticas, não uma ontologia clínica formal ou uma lista exaustiva.
A ocorrência de um par não confirma a condição, e a ausência de correspondência
não exclui doença. Os 10 relatos incluem início, sintomas e impacto na rotina.
A opção interativa formula um décimo primeiro relato a partir de três respostas
curtas, sem alterar os dez exemplos. A análise da execução fica em um CSV local
separado; cada envio também é acrescentado ao histórico `relatos_interativos.csv`.
Os dois arquivos interativos são ignorados pelo Git.

## Critérios dos rótulos

- `alto risco`: cenário simulado com sintomas agudos preocupantes, como dor
  torácica persistente com suor frio, dificuldade respiratória importante ou
  perda de consciência.
- `baixo risco`: descrição explicitamente leve ou resolvida, sem sinais de
  alerta relatados no exemplo. Não significa ausência de doença ou dispensa de
  avaliação médica.
- `grupo`: cenário de origem das duas paráfrases; não é atributo preditor.
- `esperado` em `desafios.csv`: rótulo didático para observar comportamento em
  exemplos adicionais; não é padrão-ouro médico.

Os rótulos não foram validados por profissionais da saúde. Eles não são derivados
da coluna `doenca_cardiaca` da Fase 1, nem atribuídos pelo extrator. Balanceamento
de classes foi uma escolha de construção, não uma estimativa de prevalência.

## Limitações concretas

1. As duas frases de cada cenário são dependentes. Por isso, a divisão e a
   validação cruzada mantêm os grupos juntos.
2. Há 144 cenários: 104 de treino, 12 de teste final e 28 de regressão. O teste
   final tem 24 frases; um erro altera a acurácia em 4,17 pontos percentuais.
3. Queixas não cardíacas leves predominam em parte da classe de baixo risco.
   O modelo pode aprender diferença de vocabulário em vez de gravidade.
4. O pré-processamento marca cinco negações frequentes, mas não resolve ironia,
   dupla negação, relatos indiretos complexos, erros ortográficos ou sintomas
   atípicos. Palavras como “leve”, “forte” e “repouso” ainda podem dominar decisões.
5. O extrator trata apenas negação simples até pontuação ou contraste. Uma frase
   longa com negações e afirmações misturadas pode produzir erro. Ele exige os
   dois sintomas da linha e devolve todas as associações compatíveis.
6. A base não representa uma população por sexo, idade, raça ou região.
   Trocar identidade mantendo sintomas é um teste de sensibilidade, não uma
   avaliação suficiente de fairness.

## Ampliação da base textual

A revisão preserva as 80 frases originais e acrescenta 208 em 104 novos cenários.
Inclui negações, contraste com sinais de alerta, relatos de terceiros, escrita
informal, recuperação após esforço e sintomas de intensidade diferente. As classes
continuam balanceadas por construção (144 frases cada).

Os testes que já foram analisados, A51–A60, B51–B60 e os oito grupos do teste
inicial, permanecem fora do treino como regressão. O manifesto `data/particoes.csv`
fixa como teste final os grupos A67–A72 e B67–B72. A seleção de parâmetros e do
limiar usa apenas previsões dentro do treino. Os 12 desafios também são regressão.

As paráfrases são próximas e há temas e expressões semelhantes entre grupos.
A autoria compartilhada e a escolha manual dos cenários limitam a independência
da avaliação. Muitas queixas leves ainda não são cardíacas. Não há representação
de prevalência ou revisão clínica independente. Nenhuma regra manual foi usada
para corrigir os rótulos previstos pelo modelo.

Se os erros do teste final atual orientarem uma próxima revisão, ele também deverá
ser reclassificado como regressão. A próxima versão precisa de uma nova avaliação
reservada ou externa, além de revisão clínica independente dos rótulos.

Consulta complementar em 11/09/2026: [Ministério da Saúde — Infarto](https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/i/infarto)
e [Scikit-learn — GridSearchCV](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GridSearchCV.html).

## Fontes consultadas na versão inicial

Acesso em 08/09/2026. As fontes abaixo orientam a contextualização dos sintomas;
não validam o mapa nem os rótulos produzidos para o exercício.

- Síndrome coronariana aguda/infarto: [Ministério da Saúde — Infarto](https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/i/infarto).
- Insuficiência cardíaca: [Ministério da Saúde — orientações ao paciente](https://linhasdecuidado.saude.gov.br/portal/insuficiencia-cardiaca-%28IC%29-no-adulto/sou-paciente).
- Angina: [Biblioteca Virtual em Saúde — Angina](https://bvsms.saude.gov.br/angina/).
- Arritmias: [Secretaria da Saúde do Ceará — sintomas e cuidados](https://www.ce.gov.br/saude/2019/11/06/arritmia-cardiaca-conheca-mais-sobre-a-doenca-e-saiba-como-trata-la-corretamente/).
- Dor torácica, pericardite e dissecção de aorta: [Linha de Cuidado — avaliação e conduta](https://linhasdecuidado.saude.gov.br/portal/dor-toracica/unidade-hospitalar/avaliacao-conduta/).
- Valvulopatias: [Secretaria de Saúde de Alagoas — estenose aórtica](https://www.saude.al.gov.br/medico-do-hospital-do-coracao-alagoano-alerta-para-sintomas-da-estenose-aortica/).
- Cardiomiopatia por estresse: [Biblioteca Virtual em Saúde — síndrome do coração partido](https://bvsms.saude.gov.br/sindrome-do-coracao-partido/).
- Tromboembolismo pulmonar: [Ministério da Saúde — trombose](https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/t/trombose).
- Método: [Scikit-learn — prevenção de vazamento de dados](https://scikit-learn.org/stable/common_pitfalls.html).

A base numérica e os ECGs da Fase 1 permanecem disponíveis para continuidade
do projeto, com suas limitações documentadas em `docs/auditoria_dados_fase1.md`.
