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
| Evidências das métricas | [Comparativo](resultados/metricas.png) · [Matrizes](resultados/matrizes_confusao.png) |
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
```

O pipeline usa `curl` para baixar cerca de 402 MB de imagens do Zenodo e
verifica o arquivo com o checksum oficial. Os pesos ImageNet da ResNet18 são
baixados e verificados na primeira execução.
O protótipo permite escolher um exemplo da partição de teste e comparar as
predições com o rótulo da base. Os escores dos modelos dependem do treinamento
e dos limiares escolhidos na validação. Sua interpretação é didática.

## Dados e avaliação

Usamos a coluna de cardiomegalia da ChestMNIST 64 × 64, uma versão
pré-redimensionada do NIH ChestXray14. O pipeline converte as imagens para RGB,
redimensiona para 56 × 56 e normaliza os valores. Preservamos as partições
oficiais e amostramos dentro de cada uma com semente fixa. O treino inclui
os positivos disponíveis e dois negativos por positivo. Validação e teste
partem de amostras aleatórias de 8.000 exames cada, sem balanceamento por
classe. A deduplicação por SHA-256 deixou 5.850 imagens no treino, 7.997 na
validação e 7.998 no teste. O arquivo distribuído contém imagens e rótulos,
e usamos a separação da fonte como referência para os grupos de pacientes.

Os dois modelos recebem os mesmos exames. A CNN simples aprende todos os
pesos, enquanto a ResNet18 usa pesos do ImageNet com o extrator congelado e
treina uma camada de classificação. A melhor época é selecionada por AP
na validação. O limiar maximiza o F1 da classe positiva na validação e
permanece fixo no teste.

| Modelo | Acurácia | Precisão positiva | Recall positivo | F1 positivo | AP |
| --- | ---: | ---: | ---: | ---: | ---: |
| Classe majoritária | 97,62% | 0% | 0% | 0% | — |
| CNN do zero | 95,29% | 19,14% | 30,53% | 23,53% | 0,167 |
| ResNet18 pré-treinada | 93,31% | 6,55% | 13,68% | 8,86% | 0,054 |

A CNN simples identificou 58 dos 190 positivos no teste, e a ResNet18
identificou 26. A acurácia da classe majoritária é alta porque apenas 2,38%
das imagens do teste têm o rótulo positivo. O recall e os falsos positivos
das matrizes mostram que os dois modelos ainda erram com frequência.
Os resultados por classe e os históricos por época estão no
[registro de métricas](resultados/metricas.json).

A ausência do rótulo significa apenas que a base não registra cardiomegalia
para aquele exame. A resolução reduzida, os rótulos extraídos automaticamente
e o uso de uma única base limitam a interpretação. A comparação é interna e
os resultados servem para o exercício acadêmico.

Fontes: [MedMNIST](https://medmnist.com/), [metadados oficiais e licença CC BY 4.0](https://github.com/MedMNIST/MedMNIST/blob/main/medmnist/info.py),
[distribuição Zenodo](https://zenodo.org/records/10519652) e
[pesos ResNet18 do Torchvision](https://docs.pytorch.org/vision/stable/models/generated/torchvision.models.resnet18.html).
