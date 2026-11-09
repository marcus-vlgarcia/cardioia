# Fase 4 · Coração em Imagens

Protótipo acadêmico para classificar radiografias de tórax conforme a presença
do rótulo de cardiomegalia na base pública ChestMNIST. O protótipo usa imagens
da base em uma demonstração simulada. Os exames de origem são reais, e os
rótulos vieram de relatórios radiológicos processados automaticamente.

| Entregável | Arquivo |
| --- | --- |
| Pré-processamento | [Notebook 01](notebooks/01_preprocessamento.ipynb) · [Abrir no Colab](https://colab.research.google.com/github/marcus-vlgarcia/cardioia/blob/fase4/fase4/notebooks/01_preprocessamento.ipynb) |
| Relatório de preparação | [PDF](output/pdf/relatorio_preprocessamento.pdf) |
| CNN do zero e Transfer Learning | [Notebook 02](notebooks/02_treinamento_avaliacao.ipynb) · [Abrir no Colab](https://colab.research.google.com/github/marcus-vlgarcia/cardioia/blob/fase4/fase4/notebooks/02_treinamento_avaliacao.ipynb) |
| Evidências das métricas | [Comparativo](resultados/metricas.png) · [Matrizes](resultados/matrizes_confusao.png) · [Curva precisão × recall](resultados/curva_precisao_recall.png) |
| Protótipo interativo | [Notebook 03](notebooks/03_prototipo.ipynb) · [Abrir no Colab](https://colab.research.google.com/github/marcus-vlgarcia/cardioia/blob/fase4/fase4/notebooks/03_prototipo.ipynb) |

## Como executar

Abra um notebook no Google Colab pela opção **Arquivo → Abrir notebook →
GitHub**. Selecione este repositório e a branch da Fase 4. Execute as células em
ordem. Para treinar novamente no Notebook 02, habilite uma GPU no Colab e altere
`REPETIR_TREINO` para `True`. Os resultados e pesos desta execução já estão
versionados para consulta.

Para executar o treinamento localmente, a partir da raiz do repositório:

```bash
python -m pip install -r fase4/requirements.txt
python fase4/src/treinar.py
python fase4/src/verificar.py
```

O pipeline usa `curl` para baixar cerca de 402 MB de imagens do Zenodo e
verifica o arquivo com o checksum oficial. Os pesos ImageNet da ResNet18 são
baixados e verificados na primeira execução.
O protótipo inclui seis imagens do teste, sorteadas com semente fixa, três por
rótulo. Ele carrega apenas esses exemplos e os pesos necessários para inferência.
O avaliador pode escolher o exame e o modelo e comparar a previsão com a referência. Os escores dos modelos dependem do treinamento
e dos limiares escolhidos na validação. Sua interpretação é didática.

## Dados e avaliação

Usamos a coluna de cardiomegalia da ChestMNIST 64 × 64. O pipeline converte
as radiografias para RGB, redimensiona para 56 × 56 e normaliza os valores.
Na ResNet18 também é aplicada a normalização do ImageNet. Aumentos leves de
rotação, deslocamento, escala e intensidade são aplicados somente no treino,
preservando a orientação do exame.

| Partição | Exames | Com rótulo de cardiomegalia |
| --- | ---: | ---: |
| Treino | 9.750 | 1.950 |
| Validação | 7.997 | 179 |
| Teste reservado da revisão | 14.432 | 392 |

A partição de treino usa quatro negativos por positivo. A validação parte de
8.000 exames sorteados na partição oficial. O teste da revisão usa o restante
da partição oficial, após excluir os 8.000 índices sorteados na primeira
avaliação e cópias exatas dessas imagens. A deduplicação por SHA-256 também
remove cópias dentro e entre partições. O NPZ não disponibiliza identificadores
para auditar a separação por paciente. Preservamos a separação da fonte.

A CNN simples começa com pesos aleatórios. A ResNet18 parte de pesos ImageNet
e ajusta o último bloco e a saída, mantendo os primeiros blocos fixos.
Ambos recebem os mesmos exames. A melhor época é selecionada por *Average
Precision* na validação, e o limiar é escolhido pelo F1 positivo nessa mesma
partição. O teste fica reservado para medir os resultados dessa configuração.
Os pesos e limiares do commit inicial `cb3cc82` foram reaplicados ao mesmo
teste da revisão para permitir uma comparação direta.

| Modelo no mesmo teste | Acurácia | Acurácia balanceada | Precisão positiva | Recall positivo | F1 positivo | AP |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Classe majoritária | 97,28% | 50,00% | 0% | 0% | 0% | 0,027 |
| CNN inicial | 95,35% | 63,39% | 22,70% | 29,59% | 25,69% | 0,180 |
| **CNN revisada** | 94,91% | **66,26%** | 22,60% | **35,97%** | **27,76%** | **0,212** |
| ResNet18 inicial | 92,75% | 56,47% | 8,92% | 18,11% | 11,95% | 0,061 |
| **ResNet18 ajustada** | 92,36% | **63,34%** | **13,25%** | **32,65%** | **18,85%** | **0,116** |

A CNN revisada encontrou 141 dos 392 exames com rótulo, ante 116 na versão
inicial. O ganho de 25 acertos positivos veio acompanhado de 88 falsos
positivos adicionais. A ResNet18 ajustada encontrou 128, ante 71, e teve
113 falsos positivos adicionais. A acurácia global caiu nos dois modelos
porque os negativos predominam no teste. A acurácia balanceada dá o mesmo
peso ao recall de cada classe. O desempenho ainda é limitado, como mostram
os 251 falsos negativos da CNN revisada.

Cada linha de [predições de teste](resultados/predicoes_teste.csv) informa
o índice oficial do exame, seu rótulo e os escores dos quatro modelos.
O [registro de métricas](resultados/metricas.json) traz as métricas por classe,
os limiares e o histórico de validação.

A ausência do rótulo significa apenas que a base não registra cardiomegalia
para aquele exame. A resolução reduzida, os rótulos extraídos automaticamente
e o uso de uma única base limitam a interpretação. A comparação é interna e
os resultados servem para o exercício acadêmico.

Fontes: [MedMNIST](https://medmnist.com/), [metadados oficiais e licença CC BY 4.0](https://github.com/MedMNIST/MedMNIST/blob/main/medmnist/info.py),
[distribuição Zenodo](https://zenodo.org/records/10519652) e
[pesos ResNet18 do Torchvision](https://docs.pytorch.org/vision/stable/models/generated/torchvision.models.resnet18.html).

## Checklist do enunciado

- [x] Dataset público de radiografias, com fonte e licença.
- [x] Conversão para RGB, redimensionamento, normalização e partições
  de treino, validação e teste.
- [x] Notebook de pré-processamento para Colab e relatório de uma página.
- [x] CNN treinada do zero e Transfer Learning com ajuste parcial da ResNet18.
- [x] Notebook com treinamento, resultados, acurácia, matriz de confusão,
  precisão, recall e F1 por classe.
- [x] Capturas das métricas e notebook interativo para apresentar a classificação.

A composição do grupo PulseIA está registrada no [README principal](../README.md).
