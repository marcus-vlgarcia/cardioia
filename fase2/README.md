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
| Frases e rótulos | [frases_risco.csv](data/frases_risco.csv) — 416 frases, 208 por classe |
| Partições por cenário | [particoes.csv](data/particoes.csv) |
| Notebook TF-IDF e avaliação | [classificador_risco.ipynb](notebooks/classificador_risco.ipynb) |
| Vídeo da entrega avaliada | [YouTube não listado](https://youtu.be/L3uZMKG7ZUc) — 3min07s |

## Revisão após a avaliação

A entrega recebeu nota máxima e foi preservada na branch `fase2-entrega`. Esta
branch aplica todas as recomendações do professor antes do início da Fase 3.
O [quadro de mudanças](docs/feedback_fase2.md) relaciona cada recomendação à
implementação e ao limite que ainda permanece.

Principais acréscimos:

- base principal ampliada de 288 para 416 frases;
- teste final ampliado de 24 para 64 frases;
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

## Resultados da revisão

| Conjunto | Casos | Acurácia | Recall de alto risco |
| --- | ---: | ---: | ---: |
| Teste final ampliado | 64 | 89,1% | 93,8% |
| Avaliação baseada em fontes externas | 32 | 84,4% | 100% |
| Pares de gravidade | 32 | 84,4% | 100% |
| Regressão | 80 | 96,3% | 100% |

No teste final ocorreram dois falsos negativos e cinco falsos positivos. O teste
mais difícil reduziu a acurácia em relação à entrega avaliada, mas oferece uma
medida mais informativa. Os erros não foram escondidos nem usados para reescrever
o teste. A análise completa está em [avaliacao.md](docs/avaliacao.md).

![Matriz de confusão ampliada](outputs/matriz_confusao.png)

## Probabilidades e vieses

A probabilidade produzida é confiança estatística dentro desta base. Não é risco
clínico. A calibração usa somente 16 frases e serve para estudo; Brier score e
log loss não garantem segurança médica.

Os testes de subgrupos não encontraram diferença entre as variações testadas,
mas usam frases sintéticas pareadas. Eles não avaliam representatividade,
prevalência, raça/cor, território, renda ou desfechos de pacientes e não
demonstram fairness. Fontes e limitações estão em
[dados_e_limites.md](docs/dados_e_limites.md).
