# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
  <a href="https://www.fiap.com.br/"><img src="assets/logo-fiap.png" alt="FIAP - Faculdade de Informática e Administração Paulista" border="0" width="40%" height="40%"></a>
</p>

# CardioIA — PulseIA

## Fase 2 — Diagnóstico Automatizado: IA no Estetoscópio Digital

O módulo da Fase 2 associa sintomas a possíveis condições e classifica frases
simuladas em `baixo risco` ou `alto risco`. As explicações e arquivos da Fase 1
continuam abaixo como registro da preparação dos dados.

| Entregável da Fase 2 | Acesso |
| --- | --- |
| 10 relatos completos | [relatos_sintomas.txt](fase2/data/relatos_sintomas.txt) |
| Mapa de conhecimento com 83 associações | [mapa_conhecimento.csv](fase2/data/mapa_conhecimento.csv) |
| Código Python de extração | [extrair_sintomas.py](fase2/src/extrair_sintomas.py) |
| Base simulada com 288 frases rotuladas | [frases_risco.csv](fase2/data/frases_risco.csv) |
| Notebook executado: TF-IDF, treinamento e avaliação | [classificador_risco.ipynb](fase2/notebooks/classificador_risco.ipynb) |
| Instalação e execução | [Guia da Fase 2](fase2/README.md) |
| Resultados e análise dos erros | [Análise da avaliação](fase2/docs/avaliacao.md) |
| Fontes, critérios dos rótulos e vieses | [Dados e limites](fase2/docs/dados_e_limites.md) |

### Vídeo de demonstração

[Assista ao vídeo de demonstração da Fase 2](https://youtu.be/L3uZMKG7ZUc)
(3min07s, YouTube não listado).

### Resultados da Fase 2

Após ampliar a base para 288 frases, o modelo usa 208 para treino, 24 para teste
final e 56 dos testes já analisados como regressão. A configuração e o limiar de
triagem foram escolhidos somente no treino. No teste final, atingiu **91,7% (22/24)**,
contra 50% do baseline, com recall de alto risco de 100%, nenhum falso negativo e
dois falsos positivos. O conjunto é pequeno e sintético; a [avaliação completa](fase2/docs/avaliacao.md)
registra as limitações, os erros e os próximos passos.

![Matriz de confusão do teste](fase2/outputs/matriz_confusao.png)

### Complementos e revisão de entrega

Além do mínimo solicitado, a Fase 2 inclui o mapa ampliado, coleta interativa
com três perguntas, histórico local, tratamento de negações, comparação de
configurações e limiares, testes de regressão e análise de sensibilidade textual
à identidade. Esses experimentos não validam uso clínico ou fairness demográfica.

As duas fases podem ser verificadas sem alterar seus dados com
`python scripts/verificar_entrega.py`: o script confere as quantidades, os hashes
das imagens, a separação dos cenários e a consistência dos resultados e notebook.
Os detalhes de execução estão no [README da Fase 2](fase2/README.md).

## Fase 1 — Batimentos de Dados

## Grupo - PulseIA

## 👨‍🎓 Integrantes

- Erik Criscuolo
- [Marcus Vinícius Loureiro Garcia](https://www.linkedin.com/in/marcusvlgarcia/)
- [Sidney William de Paula Dias](https://www.linkedin.com/in/sidneywilliamdepaula/)

## 👩‍🏫 Professores

### Tutor

- [Leonardo Ruiz Orabona](https://www.linkedin.com/in/leonardoorabona/)

### Coordenador

- [André Godoi Chiovato](https://www.linkedin.com/in/andregodoichiovato/)

## 📜 Descrição

Este repositório reúne as bases preparadas para a primeira fase do projeto
CardioIA, desenvolvido no curso de Inteligência Artificial da FIAP. A
proposta é organizar dados que podem ser usados nas próximas etapas do projeto,
envolvendo análise numérica, Processamento de Linguagem Natural (NLP) e Visão
Computacional.

Nesta fase, o foco foi preparar os dados, registrar as fontes e discutir os
limites do seu uso. Nenhum arquivo deste repositório deve ser usado para
diagnóstico ou atendimento em saúde.

## Evolução após a avaliação da Fase 1

Após a avaliação da Fase 1, o projeto recebeu uma atualização de transparência
e governança para orientar as próximas etapas. A revisão não altera os dados
entregues nem os apresenta como dados clínicos: ela torna explícitas as
limitações que precisam ser consideradas antes de qualquer experimento de
Machine Learning.

- foi incluída uma auditoria quantitativa da base numérica, com a distribuição
  de sexo, idade, variável-alvo, diabetes, tabagismo e outros fatores;
- a construção artificial de `doenca_cardiaca` foi documentada como uma regra
  didática que pode ser reaprendida por um modelo;
- o uso de `sexo` nessa regra foi destacado como possível fonte de associação
  artificial e ponto de atenção em avaliações de fairness;
- o conjunto visual passou a explicitar que possui 100 arquivos derivados de
  apenas 10 registros de origem, e não 100 exames independentes;
- a análise de anomalias em ECG permanece descrita como possibilidade futura,
  pois não há rótulos clínicos por segmento neste conjunto.

Os detalhes, os números da auditoria e as ações planejadas estão em
[`docs/auditoria_dados_fase1.md`](docs/auditoria_dados_fase1.md) e
[`docs/feedback_fase1.md`](docs/feedback_fase1.md).

## 📁 Estrutura de pastas

As pastas abaixo foram organizadas de acordo com o tipo de dado e sua função no
projeto: `data` contém o dataset numérico, `assets` reúne os textos e imagens,
`docs` registra o dicionário de dados e as fontes, e `scripts` guarda os códigos
de reprodução e geração dos materiais.

```
cardioia/
├── fase2/
│   ├── data/                     # Relatos, mapa e frases rotuladas
│   ├── docs/                     # Fontes e avaliação
│   ├── notebooks/                # Classificador executado
│   ├── outputs/                  # Resultados reproduzíveis
│   ├── src/                      # Extração e execução
│   ├── tests/                    # Casos de teste do extrator
│   └── README.md
├── data/numeric/
│   └── dataset_pacientes_cardiacos.csv
├── assets/
│   ├── textos/
│   │   ├── hipertensao_arterial_ministerio_saude.txt
│   │   └── infarto_agudo_miocardio_ministerio_saude.txt
│   └── imagens/ecg_mitbih/
│       ├── train/                 # 70 imagens
│       ├── validation/            # 20 imagens
│       ├── test/                  # 10 imagens
│       ├── manifesto_imagens.csv
│       ├── README.md
│       └── link_externo.txt
├── docs/
│   ├── dicionario_de_dados.md
│   ├── auditoria_dados_fase1.md
│   ├── feedback_fase1.md
│   └── fontes.md
├── scripts/
│   ├── gerar_dataset_numerico.py
│   ├── auditar_dados_fase1.py
│   ├── verificar_entrega.py
│   └── gerar_imagens_ecg.py
├── requirements.txt
└── README.md
```

## Parte 1 — Dados numéricos

O arquivo `data/numeric/dataset_pacientes_cardiacos.csv` contém **300 registros
simulados**, acima do mínimo de 100 linhas solicitado na atividade. Os dados
foram gerados por um script do próprio projeto, com valores plausíveis dentro de
faixas usadas em exemplos de saúde cardiovascular. Portanto, não representam
pacientes reais, não contêm dados pessoais e servem apenas para fins acadêmicos.
O arquivo também pode ser acessado diretamente na
[pasta de dados numéricos do Google Drive](https://drive.google.com/drive/u/0/folders/1w0OrNUyqomzj2sH7Ti0DWEU0AYtmiaph).

Optou-se pela simulação mesmo existindo bases públicas, como a
[Heart Disease, da UCI](https://uci-ics-mlr-prod.aws.uci.edu/dataset/45/heart%2Bdisease),
que reúne 303 registros anonimizados com variáveis cardiovasculares. Para esta
etapa, a base simulada permite apresentar claramente como os dados foram gerados,
reproduzir o arquivo e evitar o tratamento de informações de saúde de pessoas
reais. Além disso, uma base pública pode ter coleta antiga, poucas observações ou
codificações próprias; já bases clínicas mais detalhadas normalmente exigem
credenciamento, termo de uso e cuidados adicionais de privacidade. A escolha não
torna os dados simulados mais adequados para uso médico: ela apenas é mais
apropriada e transparente para o objetivo didático desta fase.

As definições, unidades e codificações de todas as colunas estão em
[`docs/dicionario_de_dados.md`](docs/dicionario_de_dados.md). Para uma aplicação
de IA voltada à saúde, as variáveis abaixo seriam as mais relevantes neste
conjunto:

| Grupo de variáveis | Por que é relevante para a análise |
| --- | --- |
| Idade e sexo | Ajudam a caracterizar o perfil da população e estão associados a diferentes padrões de risco cardiovascular. |
| Pressão arterial em repouso e colesterol | São medidas frequentemente acompanhadas na prevenção de hipertensão e aterosclerose. |
| Tipo de dor no peito e angina por esforço | Registram sinais relatados pelo paciente que podem apoiar a identificação de padrões de sintomas. |
| Frequência cardíaca máxima, ECG em repouso, `oldpeak` e inclinação do segmento ST | Representam informações relacionadas ao esforço e ao traçado cardíaco, úteis para comparar perfis no conjunto. |
| Diabetes, tabagismo, IMC e histórico familiar | Reúnem fatores de risco que podem ser combinados em análises de associação e classificação. |
| `doenca_cardiaca` | É a variável-alvo didática, isto é, a coluna que um exercício de classificação supervisionada tentaria estimar. |

O conjunto permite praticar organização de dados, estatística descritiva e
classificação supervisionada. Como os valores são simulados e as relações entre
as colunas foram simplificadas, qualquer resultado obtido nele não tem valor
clínico nem pode ser generalizado para uma população real.

Em especial, `doenca_cardiaca` foi gerada a partir de uma regra probabilística
do próprio script, usando idade, sexo, colesterol, pressão arterial, angina,
`oldpeak`, tipo de dor, número de vasos, histórico familiar, tabagismo e
diabetes. Assim, um modelo treinado com essas mesmas colunas pode obter bom
desempenho apenas por reaprender uma relação definida pelo gerador. Esse uso é
válido para demonstrar o fluxo técnico de uma classificação, mas suas métricas
não devem ser interpretadas como evidência clínica. A distribuição observada e
as associações do conjunto estão registradas na
[auditoria dos dados](docs/auditoria_dados_fase1.md).

## Parte 2 — Dados textuais

Foram extraídos dois textos em português sobre saúde cardiovascular:

- `hipertensao_arterial_ministerio_saude.txt`, com excerto literal da página do
  Ministério da Saúde sobre hipertensão;
- `infarto_agudo_miocardio_ministerio_saude.txt`, com excerto literal da página
  do Ministério da Saúde sobre infarto.

Os conteúdos principais das páginas foram convertidos para `.txt`, sem menus ou
elementos de navegação. Cada arquivo informa a fonte, a URL, a data de acesso e
a licença, deixando claro que o texto não é um resumo produzido pelo grupo. Os
textos permitem exemplos de análise de linguagem natural, como mostra a tabela a
seguir:

| Possível análise de NLP | Aplicação nos textos | Relevância para o projeto |
| --- | --- | --- |
| Extração de entidades e palavras-chave | Localizar termos como sintomas, fatores de risco, exames e tratamentos. | Facilita a organização de informações importantes em um conteúdo extenso. |
| Classificação de tópicos | Diferenciar trechos sobre hipertensão, infarto, prevenção ou atendimento de urgência. | Pode apoiar a separação automática de conteúdos por assunto. |
| Busca semântica | Encontrar passagens relacionadas a uma dúvida, mesmo quando a pergunta usa palavras diferentes do texto. | É útil para recuperar informações em materiais educativos de saúde. |
| Análise de sentimentos | Avaliar a presença de linguagem de alerta, prevenção ou orientação. | Ajuda a discutir limites da técnica: estes textos são informativos, então não substituem relatos reais de pacientes. |

Essas análises são relevantes porque podem apoiar a consulta e a organização de
materiais de educação em saúde. Em um projeto real, seria necessário validar as
respostas com profissionais da área e deixar claro que o sistema não realiza
diagnóstico. As fontes completas constam em [`docs/fontes.md`](docs/fontes.md).

## Parte 3 — Dados visuais

O conjunto visual principal contém **100 imagens PNG de ECG** derivadas da
[MIT-BIH Arrhythmia Database](https://physionet.org/content/mitdb/1.0.0/), do
PhysioNet. Os sinais públicos da base foram convertidos em imagens de traçados
eletrocardiográficos para permitir exercícios com arquivos visuais. São imagens
reais de exames da fonte indicada, e não imagens sintéticas. Elas estão no
repositório e também na
[pasta de imagens de ECG do Google Drive](https://drive.google.com/drive/u/0/folders/1B6aVJphAdL24uQbI_EgVwcXJlrEOKW9g).

As imagens foram separadas por registro para evitar que segmentos de um mesmo
registro apareçam em mais de um conjunto. Essa organização reduz o risco de um
modelo avaliar, no teste, um traçado muito parecido com outro já visto no treino:

| Conjunto | Registros | Imagens |
| --- | --- | ---: |
| Treino | 100 a 106 | 70 |
| Validação | 107 e 108 | 20 |
| Teste | 109 | 10 |

O arquivo `manifesto_imagens.csv` registra a origem, o intervalo de tempo, as
derivações, o conjunto e o hash de cada imagem. Trata-se de material de estudo:
as imagens não substituem exames, nem possuem rótulo clínico por segmento.

As possibilidades de análise por Visão Computacional incluem:

| Possível análise de VC | Aplicação nas imagens de ECG | Importância para IA em saúde |
| --- | --- | --- |
| Pré-processamento e identificação de traçado | Recortar a região útil do exame, reduzir ruídos visuais e localizar a linha do sinal. | Padroniza a entrada antes de uma análise automática. |
| Detecção de padrões e bordas | Identificar o desenho do traçado, picos e mudanças de inclinação ao longo do ECG. | Mostra como características visuais podem ser transformadas em dados para comparação. |
| Exploração de possíveis anomalias | Procurar traçados que se diferenciem do padrão predominante, sem atribuir diagnóstico. | Pode orientar estudos futuros de apoio à revisão de grandes volumes de exames. |
| Classificação de imagens | Em uma etapa futura, associar padrões a classes clínicas previamente rotuladas. | Ilustra o potencial de modelos que auxiliem profissionais na priorização de exames. |

Essas aplicações podem agilizar a organização e a revisão de exames, mas não
substituem a interpretação de profissionais de saúde. Como este conjunto não
traz rótulos clínicos por imagem, ele é adequado para exploração visual e
preparo de dados; uma classificação médica exigiria rótulos confiáveis,
validação clínica e avaliação de vieses antes de qualquer uso real.

Embora existam 100 arquivos, eles foram produzidos a partir de 10 registros de
origem da MIT-BIH, com dez segmentos por registro. Portanto, o total de imagens
não equivale a 100 pacientes ou 100 exames independentes. A separação por
registro continua sendo importante para evitar vazamento entre treino, validação
e teste, mas a diversidade clínica do conjunto é limitada e precisará ser
ampliada em etapas futuras.

## Acesso aos dados

Além deste repositório, os arquivos da atividade estão disponíveis em pasta
pública para consulta e correção:

[Pasta pública do Google Drive](https://drive.google.com/drive/folders/18jSV0Aq45kVY0TAm7l7XCqzQAQevBpnI?usp=sharing)

A pasta foi indicada para consulta dos arquivos completos. Ela deve permanecer
com permissão de leitura para qualquer pessoa com o link até a correção da atividade.

## Governança, privacidade e vieses

Os dados numéricos são sintéticos, o que evita o uso de informações pessoais e
de prontuários. As imagens são dados públicos do PhysioNet e mantêm a atribuição
à fonte. Ainda assim, as três bases têm limitações:

- o dataset numérico foi criado com distribuições simplificadas; a auditoria
  mostra, por exemplo, 64,7% de registros masculinos e uma variável-alvo
  construída pelo próprio gerador. O uso de sexo no score exige atenção em
  qualquer comparação futura entre grupos;
- os textos são informativos e não representam conversas ou prontuários de
  pacientes;
- a MIT-BIH é uma base histórica, com população e contexto de coleta próprios;
  além disso, as 100 imagens vêm de somente 10 registros de origem.

Por isso, qualquer modelo treinado com esses arquivos deve ser tratado como
exercício acadêmico. Antes de uso real, seriam necessários dados representativos,
validação, revisão ética e medidas de segurança compatíveis com a LGPD.

Nas próximas etapas, a equipe irá reportar distribuição dos dados, divisão entre
treino e teste, métricas por classe e possíveis distorções observadas. Essas
verificações não eliminam os limites da base, mas evitam que eles fiquem ocultos
na interpretação dos resultados.

## 🔧 Como executar o código

Os scripts não são necessários para abrir os dados entregues, mas foram mantidos
para mostrar como a base simulada pode ser reproduzida ou ampliada.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Gerar novamente o dataset numérico

```bash
python3 scripts/gerar_dataset_numerico.py
```

O comando recria o arquivo principal com 300 registros e uma semente fixa. Para
gerar uma base separada com mais registros:

```bash
python3 scripts/gerar_dataset_numerico.py -n 500 -o data/numeric/dataset_ampliado.csv
```

Também é possível acrescentar novos registros ao arquivo existente. Nesse modo,
os identificadores continuam a numeração já presente no arquivo:

```bash
python3 scripts/gerar_dataset_numerico.py -n 100 -m anexar
```

### Gerar imagens sintéticas de ECG

As imagens usadas na entrega são as 100 imagens reais do MIT-BIH. O script abaixo
gera traçados sintéticos apenas como material complementar de estudo, sem alterar
o conjunto real:

```bash
python3 scripts/gerar_imagens_ecg.py -n 100
```

Por padrão, os arquivos são criados em `assets/imagens/ecg_sintetico/`. Para
usar outra pasta:

```bash
python3 scripts/gerar_imagens_ecg.py -n 30 -o assets/imagens/exemplos_sinteticos
```

As imagens sintéticas não devem ser apresentadas como exames reais e não fazem
parte das 100 imagens usadas para cumprir o requisito da atividade.

## Referências

As referências completas estão em [`docs/fontes.md`](docs/fontes.md). As fontes
incluem o Ministério da Saúde para os textos e o PhysioNet para as imagens de
ECG.

## 🗃 Histórico de lançamentos

- `0.2.1` — 07/10/2026: revisão de integridade e execução; proteção dos relatos
  interativos, validação do histórico, compatibilidade das dependências e correção
  do gerador sintético complementar. Teste reservado reproduzido sem ajuste de
  dados ou parâmetros. Vídeo de demonstração publicado.
- `0.2.0` — 08/09/2026: implementação das duas partes da Fase 2, notebook
  executado, análise de erros e demonstração preparada; publicação no YouTube
  pendente.
- `0.1.1` — 08/09/2026: atualização de governança e auditoria em resposta à
  avaliação da Fase 1.
- `0.1.0` — 02/09/2026: organização e entrega das bases numérica, textual e
  visual da Fase 1.

## 📋 Licença

<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1" alt="Creative Commons"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1" alt="Attribution">

[MODELO GIT FIAP](https://github.com/agodoi/template) por [Fiap](https://fiap.com.br/) está licenciado sobre [Attribution 4.0 International](http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1).

As fontes e as condições de uso dos dados utilizados no projeto estão registradas em [`docs/fontes.md`](docs/fontes.md).
