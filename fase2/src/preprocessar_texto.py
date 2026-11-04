"""Adiciona marcadores contextuais antes da vetorização textual."""

import re

from contexto_sintomas import analisar_expressoes, normalizar


FAMILIAS = {
    "sintoma_toracico": ("dor no peito", "dor no torax", "pressao no peito", "aperto no peito", "aperto no torax"),
    "dificuldade_respiratoria": ("falta de ar", "dificuldade para respirar", "sem ar"),
    "suor_frio": ("suor frio", "suando frio", "transpiracao fria", "suor gelado"),
    "palpitacoes": ("palpitacoes", "coracao acelerado", "batimentos irregulares"),
    "tontura_ou_desmaio": ("tontura", "sensacao de desmaio", "desmaio", "perdi a consciencia"),
}

PADROES_CONTEXTO = {
    "contexto_recuperacao_completa": (
        r"\b(?:passou completamente|volt(?:ei|ou) ao normal|normalizou|cessou|nao voltou|estou bem|me sinto normal)\b",
        r"\b(?:recuperei|recuperou) (?:o folego )?(?:completamente|totalmente)\b",
    ),
    "contexto_persistencia_ou_piora": (
        r"\b(?:nao passa|nao passou|nao melhora|nao melhorou|nao cede|continua|persistente|piorando|aumentando)\b",
    ),
    "contexto_apos_esforco": (
        r"\b(?:depois|apos) (?:da|do|de)? ?(?:corrida|treino|exercicio|academia|caminhada)\b",
        r"\bao (?:correr|subir|pedalar)\b",
    ),
    "contexto_em_repouso": (
        r"\b(?:em repouso|mesmo parado|mesmo sentado|sem esforco)\b",
    ),
    "contexto_relato_de_terceiro": (
        r"\b(?:minha|meu) (?:mae|pai|irma|irmao|avo|avó|marido|esposa)\b",
        r"\b(?:foi|e) (?:da|do) (?:minha|meu|outra pessoa)\b",
    ),
}


def preparar_texto(texto):
    """Mantém o texto e acrescenta marcadores de contexto reconhecível."""
    texto_normalizado = normalizar(texto)
    marcadores = []
    for familia, expressoes in FAMILIAS.items():
        analise = analisar_expressoes(texto_normalizado, expressoes)
        if analise["negadas"]:
            marcadores.append(f"neg_{familia}")
        if analise["dupla_negacao"]:
            marcadores.append(f"dupla_negacao_{familia}")
        if analise["contraditorias"]:
            marcadores.append(f"contradicao_{familia}")
    if re.search(r"\brespiro normalmente\b", texto_normalizado):
        marcadores.append("neg_dificuldade_respiratoria")
    for marcador, padroes in PADROES_CONTEXTO.items():
        if any(re.search(padrao, texto_normalizado) for padrao in padroes):
            marcadores.append(marcador)
    return re.sub(r"\s+", " ", " ".join([texto_normalizado, *sorted(set(marcadores))])).strip()
