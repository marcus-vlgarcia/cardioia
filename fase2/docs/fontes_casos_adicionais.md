# Fontes dos casos adicionais

Os 120 relatos de `data/casos_adicionais.csv`, as 80 frases de
`data/auditoria_nova.csv` e os 20 pares de `data/auditoria_contrastiva.csv`
foram elaborados com apoio de IA para este experimento. A coluna
`fonte_id` aponta para a fonte que orientou o **padrão de sintomas ou o
diagnóstico diferencial**; a frase e o rótulo não foram retirados literalmente
da página. Consulta realizada em 18/10/2026.

| Identificador | Fonte | Aspecto usado |
| --- | --- | --- |
| `INFARTO` | [Ministério da Saúde: infarto](https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/i/infarto) | Dor ou desconforto torácico, irradiação, suor frio, palidez, falta de ar e apresentações menos específicas. |
| `DOR` | [Linha de Cuidado: dor torácica](https://linhasdecuidado.saude.gov.br/portal/dor-toracica/sou-paciente/) | Início, persistência, irradiação e sintomas associados de alerta. |
| `AVC` | [Ministério da Saúde: AVC](https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/a/avc/avc/) | Alteração súbita da fala, da visão e da força em um lado do corpo. |
| `IC` | [Linha de Cuidado: insuficiência cardíaca](https://linhasdecuidado.saude.gov.br/portal/insuficiencia-cardiaca-%28IC%29-no-adulto/sou-paciente) | Falta de ar ao deitar, cansaço e inchaço. |
| `ARR` | [Secretaria da Saúde do Ceará: arritmia](https://www.ce.gov.br/saude/2019/11/06/arritmia-cardiaca-conheca-mais-sobre-a-doenca-e-saiba-como-trata-la-corretamente/) | Palpitações acompanhadas de tontura, falta de ar ou sensação de desmaio. |
| `TROMBOSE` | [Ministério da Saúde: trombose](https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/t/trombose) e [Linha de Cuidado: avaliação da dor torácica](https://linhasdecuidado.saude.gov.br/portal/dor-toracica/unidade-de-pronto-atendimento/avaliacao-conduta/) | Falta de ar súbita, dor ao respirar e contexto de cirurgia ou imobilização. |
| `DIF` | [Linha de Cuidado: planejamento assistencial da dor torácica](https://linhasdecuidado.saude.gov.br/portal/dor-toracica/unidade-de-atencao-primaria/planejamento-assistencial/) | Diferenças possíveis entre dor da parede torácica, refluxo e situações potencialmente graves. |

O rótulo `baixo risco` representa somente a comparação didática entre relatos
explicitamente leves ou resolvidos e relatos com sinais de alerta. Nenhuma das
fontes certifica que uma pessoa real com aquela frase está fora de perigo.
Alguns casos podem ter mais de uma interpretação clínica; a revisão por
profissional de saúde continua pendente. O conjunto `auditoria_nova.csv` é
separado do treinamento e não é uma validação clínica externa: foi redigido no
mesmo processo de elaboração e seus rótulos também são didáticos.
