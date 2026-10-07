# PulseIA — Fase 2

## Diagnóstico Automatizado — IA no Estetoscópio Digital

O módulo possui duas partes independentes: associação de sintomas a possíveis
condições por regras e classificação de frases em alto ou baixo risco com
TF-IDF e Regressão Logística. O projeto é uma simulação acadêmica de apoio à
triagem; não realiza diagnóstico médico.

## Entregáveis

| Critério do enunciado | Arquivo |
| --- | --- |
| 10 relatos completos de sintomas | [relatos_sintomas.txt](data/relatos_sintomas.txt) |
| Mapa de conhecimento | [mapa_conhecimento.csv](data/mapa_conhecimento.csv) — 83 associações possíveis |
| Código de extração funcional | [extrair_sintomas.py](src/extrair_sintomas.py) |
| Base de frases e rótulos | [frases_risco.csv](data/frases_risco.csv) — 288 frases, 144 por classe |
| Partições fixas por cenário | [particoes.csv](data/particoes.csv) — treino, teste final e regressão |
| Notebook com TF-IDF, treinamento e avaliação | [classificador_risco.ipynb](notebooks/classificador_risco.ipynb) |
| Resultados da extração | [diagnosticos_sugeridos.csv](outputs/diagnosticos_sugeridos.csv) |
| Avaliação do modelo | [metricas.json](outputs/metricas.json) e [predicoes_teste.csv](outputs/predicoes_teste.csv) |
| Governança e fontes | [dados_e_limites.md](docs/dados_e_limites.md) |
| Demonstração em vídeo | [Vídeo de demonstração](https://youtu.be/L3uZMKG7ZUc) (3min07s, YouTube não listado). |

## Execução

Na raiz do repositório, com Python 3.13:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r fase2/requirements.txt
python fase2/src/extrair_sintomas.py
python fase2/src/executar_notebook.py
python -m unittest discover -s fase2/tests -v
python scripts/verificar_entrega.py
```

O primeiro script lê o `.txt` e o mapa e salva as dez associações. É possível
usar outros arquivos com `--frases`, `--mapa` e `--saida`. Para demonstrar um
novo relato, execute `python fase2/src/extrair_sintomas.py --interativo`: três
campos pedem sintomas, impacto na rotina e tempo de início. O programa formula
a frase no padrão dos relatos. No modo interativo, os dez exemplos e o novo relato
são analisados em `fase2/outputs/diagnosticos_interativos.csv`, sem sobrescrever
`diagnosticos_sugeridos.csv` ou o arquivo original com os dez exemplos. Cada envio também é
guardado, junto com sintomas e possíveis associações, em
`fase2/outputs/relatos_interativos.csv`. Esse histórico fica apenas na máquina
que executou o programa e, assim como a saída interativa, é ignorado pelo Git.
O histórico acumula os envios; a saída interativa é recriada em cada execução.
É possível usar `--historico` e `--saida` para escolher outros caminhos locais,
desde que separados dos arquivos de entrada e entre si. Use exemplos simulados
na demonstração. O segundo executa
todas as células e salva o notebook com tabelas e gráficos, além dos arquivos
em `outputs`. Também é possível abrir o notebook no VS Code ou Jupyter usando
o mesmo ambiente e executar todas as células em ordem.

## Como funciona

O extrator normaliza acentos e maiúsculas, procura expressões inteiras e verifica
negação simples. Cada linha do mapa exige os dois sintomas. Não havendo um par
compatível, retorna “Associação insuficiente no mapa”. O mapa foi ampliado para
registrar mais de uma possibilidade para sintomas parecidos. Um relato pode
receber mais de uma associação; nenhuma delas é um diagnóstico confirmado.

### Parte 1 — mapa de conhecimento ampliado

O arquivo segue as três colunas propostas no enunciado: `sintoma_1`, `sintoma_2`
e `doenca_associada`. Cada linha exige a presença das duas expressões. Repetir um
sintoma em linhas diferentes permite apresentar hipóteses distintas para uma mesma
queixa, como dor no peito relacionada a síndrome coronariana, angina, pericardite,
miocardite, refluxo ou dor musculoesquelética. O mapa contém 83 associações em 14
grupos de possibilidades. Ele é uma estrutura didática, não uma lista exaustiva
nem uma ferramenta de diagnóstico.

### Parte 2 — classificação de risco

O classificador usa 208 frases de treino, 24 do teste final e 56 de regressão.
As partições são fixadas por cenário e as paráfrases ficam juntas. O TF-IDF é
ajustado apenas no treino. Antes da avaliação, a validação cruzada escolhe entre
quatro configurações pelo F1 macro e compara quatro limiares de decisão. A versão
selecionada atingiu 91,7% (22/24) no teste final, com recall de alto risco de 100%
e dois falsos positivos. A comparação e os erros estão em [avaliacao.md](docs/avaliacao.md).

O notebook apresenta acurácia, precisão, recall e F1 por classe, matriz de
confusão, baseline e erros individuais. Também inspeciona termos aprendidos e
testa os 12 desafios antigos como regressão. Todos os rótulos são simulados. A análise detalhada
de limitações inclui vieses lexicais e a falta de representatividade demográfica.

## Próxima melhoria registrada

Se uma nova revisão for feita, os 24 exemplos do teste final atual devem passar
para regressão e uma nova avaliação reservada deverá ser criada. Os próximos
passos incluem revisão clínica independente dos rótulos, relatos reais autorizados
e anonimizados, maior diversidade de linguagem e avaliação externa. A expansão da
base atual não equivale a validação clínica.

## Continuidade da Fase 1

A auditoria da Fase 1 orientou a divisão por grupos, a identificação explícita
dos rótulos sintéticos e a análise de erros. A variável numérica artificial não
é usada como alvo deste classificador textual. O portal e a MLP são atividades
opcionais posteriores.
