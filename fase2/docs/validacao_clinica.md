# Protocolo de validação clínica

## Situação atual

O grupo realizou uma triagem documental das 83 associações do mapa, usando
fontes públicas de saúde. Isso melhora a rastreabilidade, mas não substitui uma
revisão clínica. A coluna `validacao_especialista` de
`data/revisao_clinica.csv` está preenchida como `pendente`.

## Como concluir a validação especializada

Um profissional habilitado e sem participação na criação inicial deve revisar
cada associação e registrar:

1. nome, profissão e registro profissional;
2. data da revisão;
3. parecer: `aprovada`, `ajustar` ou `remover`;
4. observação sobre contexto, gravidade e diagnósticos diferenciais;
5. fonte clínica adicional, quando necessária.

Também deve revisar os critérios de `alto risco` e `baixo risco`, com atenção às
consequências de falsos negativos e falsos positivos. Alterações aprovadas devem
gerar uma nova versão do mapa e dos rótulos; o conjunto usado na avaliação atual
deve permanecer preservado para rastreabilidade.

## O que a validação não significa

Mesmo após a revisão, o protótipo continuará sendo acadêmico. Validação de uma
tabela não equivale a validação de um dispositivo médico, estudo prospectivo,
aprovação regulatória ou autorização de uso em atendimento.
