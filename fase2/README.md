# PulseIA — Fase 2

## Diagnóstico Automatizado — IA no Estetoscópio Digital

O módulo associa sintomas a possíveis condições por regras e classifica frases
simuladas em `alto risco` ou `baixo risco` com TF-IDF e Regressão Logística. É
um projeto acadêmico: não realiza diagnóstico nem orienta atendimento.

## Entregáveis originais

| Critério | Arquivo |
| --- | --- |
| 10 relatos completos | [relatos_sintomas.txt](data/relatos_sintomas.txt) |
| Mapa de conhecimento | [mapa_conhecimento.csv](data/mapa_conhecimento.csv) — 83 associações |
| Extração de sintomas | [extrair_sintomas.py](src/extrair_sintomas.py) |
| Frases e rótulos | [frases_risco.csv](data/frases_risco.csv) — 1.112 frases, 556 por classe |
| Partições por cenário | [particoes.csv](data/particoes.csv) |
| Notebook TF-IDF e avaliação | [classificador_risco.ipynb](notebooks/classificador_risco.ipynb) |
| Vídeo da entrega avaliada | [YouTube não listado](https://youtu.be/L3uZMKG7ZUc) — 3min07s |

## Revisão após a avaliação

A entrega recebeu nota máxima e foi preservada na branch `fase2-entrega`. Esta
branch aplica todas as recomendações do professor antes do início da Fase 3.
O [quadro de mudanças](docs/feedback_fase2.md) relaciona cada recomendação à
implementação e ao limite que ainda permanece.

Principais acréscimos:

- base principal ampliada de 288 para 1.112 frases, incluindo 576 variações da etapa anterior e 120 casos individuais novos;
- teste final ampliado de 24 para 264 frases, separadas por família de cenário;
- duas auditorias novas, com 80 frases variadas e 20 pares de gravidade;
- 32 cenários de avaliação baseados em fontes externas;
- 16 pares de manifestações leves e graves com linguagem semelhante;
- tratamento de dupla negação e sinalização de relatos contraditórios;
- investigação por termos dos erros, inclusive os dois falsos positivos antigos;
- auditoria com 48 variações sintéticas de sexo referido e faixa etária;
- calibração experimental das probabilidades e curva de confiabilidade;
- ficha de revisão clínica para todas as 83 associações.

A validação por profissional de saúde não foi inventada: ela continua marcada
como `pendente` em [revisao_clinica.csv](data/revisao_clinica.csv), com o
[procedimento de validação](docs/validacao_clinica.md) preparado. Pelo mesmo
motivo, a avaliação baseada em fontes não é chamada de independente; o
[protocolo para coleta externa](docs/avaliacao_independente.md) registra como
essa etapa deverá ser concluída sem vazamento.

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

`extrair_sintomas.py` lê os dez relatos, procura expressões do mapa e salva
`outputs/diagnosticos_sugeridos.csv`. A saída agora separa sintomas afirmados,
negados e contraditórios. Cada linha do mapa exige a presença dos dois sintomas;
uma frase pode receber mais de uma associação.

O modo interativo continua disponível:

```bash
python fase2/src/extrair_sintomas.py --interativo
```

Três campos coletam sintomas, impacto na rotina e tempo de início. O envio fica
em arquivos locais ignorados pelo Git, sem alterar os dez relatos obrigatórios.

`executar_notebook.py` executa todas as células e atualiza as tabelas e figuras.
Para reproduzir também os arquivos de avaliação diretamente:

```bash
python fase2/src/avaliar_classificador.py
```

O gerador `expandir_linguagem.py` recria as 576 frases adicionais e o manifesto
de partições a partir da base anterior e acrescenta os 120 casos de
`casos_adicionais.csv` somente ao treino. `criar_notebook.py` recria o notebook
didático antes de executá-lo. Os dois são determinísticos. As
[fontes dos casos novos](docs/fontes_casos_adicionais.md) estão registradas.

## Resultados da revisão

| Conjunto | Casos | Acurácia | Recall de alto risco |
| --- | ---: | ---: | ---: |
| Teste de 264 frases, agora histórico | 264 | 94,7% | 95,5% |
| Auditoria nova, modelo anterior / atual | 80 | 97,5% / 97,5% | 100% / 100% |
| Pares novos, modelo anterior / atual | 40 | 97,5% / 97,5% | 95% / 95% |
| Avaliação baseada em fontes externas | 32 | 96,9% | 100% |
| Pares de gravidade anteriores | 32 | 93,8% | 100% |
| Regressão | 144 | 97,9% | 100% |

No conjunto histórico de 264 frases ocorreram seis falsos negativos e oito
falsos positivos. A acurácia foi de 95,5% nas 44 frases com erros ortográficos
e nas 44 coloquiais. Nas auditorias novas, os modelos anterior e atual tiveram
os mesmos três erros: dois falsos positivos entre as 80 frases e um falso
negativo entre os 20 pares. Todos os exemplos e rótulos foram redigidos para o
projeto e não receberam validação clínica. A análise completa está em
[avaliacao.md](docs/avaliacao.md).

![Matriz de confusão ampliada](outputs/matriz_confusao.png)

## Probabilidades e vieses

A probabilidade produzida é confiança estatística dentro desta base. Não é risco
clínico. A calibração usa 88 frases reservadas e serve para estudo; Brier score e
log loss não garantem segurança médica.

Os testes de subgrupos não encontraram diferença entre as variações testadas,
mas usam frases sintéticas pareadas. Eles não avaliam representatividade,
prevalência, raça/cor, território, renda ou desfechos de pacientes e não
demonstram fairness. Fontes e limitações estão em
[dados_e_limites.md](docs/dados_e_limites.md).
