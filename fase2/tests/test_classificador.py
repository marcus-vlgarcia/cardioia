"""Verifica a interpretação do sinal dos coeficientes do classificador."""

import sys
import unittest
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from avaliar_classificador import explicar_frase  # noqa: E402


class TestExplicacao(unittest.TestCase):
    def test_termos_favor_alto_risco_respeitam_ordem_das_classes(self):
        modelo = Pipeline([
            ("tfidf", TfidfVectorizer()),
            ("classificador", LogisticRegression()),
        ])
        modelo.fit(["alarme forte", "alarme urgente", "calmo leve", "calmo normal"],
                   ["alto risco", "alto risco", "baixo risco", "baixo risco"])
        a_favor, contra = explicar_frase(modelo, "alarme calmo", limite=10)
        self.assertIn("alarme", a_favor)
        self.assertIn("calmo", contra)


if __name__ == "__main__":
    unittest.main()
