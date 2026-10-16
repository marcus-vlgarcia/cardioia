# Protocolo para uma avaliação independente futura

## Por que ainda é necessária

O conjunto `avaliacao_externa.csv` é separado do treino e baseado em fontes
públicas, mas foi redigido dentro do próprio projeto. Por isso, ele reduz
vazamento de desenvolvimento, porém não atende sozinho ao conceito mais forte de
avaliação independente.

## Procedimento proposto

1. Convidar pelo menos uma pessoa que não tenha visto a base de treino para
   escrever relatos em linguagem natural, sem copiar os exemplos do projeto.
2. Solicitar início, sintomas, evolução e impacto na rotina, sem informar quais
   palavras o classificador costuma usar.
3. Encaminhar os relatos, sem a previsão do modelo, a dois profissionais de
   saúde para classificação independente de urgência.
4. Resolver divergências por consenso e guardar identificação, data e versão do
   protocolo adotado.
5. Executar o modelo uma única vez nesse conjunto e relatar todos os erros, sem
   reescrever os exemplos.
6. Se o conjunto orientar mudanças no modelo, movê-lo para regressão e criar
   outro teste independente.

Relatos reais exigem autorização, anonimização e avaliação ética. Até que esse
processo seja concluído, o projeto não declara validação clínica ou externa
independente.

Como referência metodológica, o trabalho [RepVig](https://doi.org/10.1038/s41598-024-83844-z)
discute amostragem representativa de vinhetas e revisão independente do nível de
triagem por profissionais. O protocolo acima adapta esses princípios ao tamanho
e ao caráter acadêmico do CardioIA.
