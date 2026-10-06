"""Casos que evitam associações silenciosamente incorretas no extrator."""
import sys
import tempfile
import unittest
import csv
from unittest.mock import patch
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
from extrair_sintomas import analisar, expressoes_mais_especificas, ler_mapa, montar_frase, salvar_historico
from preprocessar_texto import preparar_texto
from extrair_sintomas import main


class TestExtracao(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mapa = ler_mapa(RAIZ / "data/mapa_conhecimento.csv")

    def test_acento_e_caixa(self):
        self.assertIn("coronariana", analisar("APERTO NO TÓRAX e falta de ar", self.mapa)["associacoes"])

    def test_negacao(self):
        self.assertEqual(analisar("Não sinto dor no peito nem suor frio.", self.mapa)["sintomas"], "")

    def test_contraste(self):
        self.assertIn("arritmia", analisar("Não sinto dor no peito, mas tenho palpitações e tontura", self.mapa)["associacoes"])

    def test_sintoma_isolado(self):
        self.assertIn("insuficiente", analisar("Tenho falta de ar", self.mapa)["associacoes"])

    def test_desconhecido(self):
        self.assertIn("insuficiente", analisar("Meu joelho está estalando", self.mapa)["associacoes"])

    def test_varias_associacoes(self):
        resultado = analisar("Dor no peito e suor frio. Palpitações e tontura.", self.mapa)
        self.assertIn("coronariana", resultado["associacoes"])
        self.assertIn("arritmia", resultado["associacoes"])

    def test_mapa_ampliado_e_ambiguo(self):
        self.assertGreaterEqual(len(self.mapa), 80)
        resultado = analisar("Tenho dor no peito, suor frio, palpitações e tontura.", self.mapa)
        self.assertIn("coronariana", resultado["associacoes"])
        self.assertIn("arritmia", resultado["associacoes"])

    def test_montar_frase_com_tres_respostas(self):
        frase = montar_frase("há dois dias", "sinto dor no peito e suor frio", "parei de caminhar")
        self.assertEqual(frase, "Há dois dias, sinto dor no peito e suor frio, e parei de caminhar.")

    def test_exibe_expressao_mais_especifica(self):
        exibidas = expressoes_mais_especificas(["cansaco", "cansaco ao esforco"])
        self.assertEqual(exibidas, ["cansaco ao esforco"])

    def test_dez_relatos(self):
        frases = (RAIZ / "data/relatos_sintomas.txt").read_text().splitlines()
        self.assertEqual(len(frases), 10)
        for frase in frases:
            self.assertNotIn("insuficiente", analisar(frase, self.mapa)["associacoes"])

    def test_marcacao_de_negacao_para_o_classificador(self):
        texto = preparar_texto("Não sinto dor no peito nem suor frio; respiro normalmente.")
        self.assertIn("neg_sintoma_toracico", texto)
        self.assertIn("neg_suor_frio", texto)
        self.assertIn("neg_dificuldade_respiratoria", texto)

    def test_duas_negacoes_na_mesma_frase(self):
        texto = preparar_texto("Não tenho falta de ar nem dor no peito.")
        self.assertIn("neg_dificuldade_respiratoria", texto)
        self.assertIn("neg_sintoma_toracico", texto)

    def test_contraste_e_preservado_no_preprocessamento(self):
        texto = preparar_texto("Não tenho falta de ar, mas sinto dor no peito forte.")
        self.assertIn("neg_dificuldade_respiratoria", texto)
        self.assertIn("dor no peito forte", texto)

    def test_historico_interativo_acrescenta_resultados(self):
        resultado = analisar("Há dois dias sinto dor no peito e suor frio, e parei de caminhar.", self.mapa)
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "historico.csv"
            salvar_historico(resultado, caminho)
            salvar_historico(resultado, caminho)
            with caminho.open(encoding="utf-8", newline="") as arquivo:
                linhas = list(csv.DictReader(arquivo))
        self.assertEqual(len(linhas), 2)
        self.assertIn("coronariana", linhas[0]["associacoes"])

    def test_historico_incompativel_e_preservado(self):
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "historico.csv"
            caminho.write_text("outra_coluna\nvalor\n", encoding="utf-8")
            antes = caminho.read_bytes()
            with self.assertRaises(ValueError):
                salvar_historico(analisar("palpitações e tontura", self.mapa), caminho)
            self.assertEqual(caminho.read_bytes(), antes)

    def test_interativo_preserva_relatorios_originais(self):
        with tempfile.TemporaryDirectory() as diretorio:
            raiz = Path(diretorio)
            (raiz / "outputs").mkdir()
            original = raiz / "outputs/diagnosticos_sugeridos.csv"
            original.write_text("resultado original\n", encoding="utf-8")
            argumentos = ["extrair_sintomas.py", "--interativo", "--frases",
                str(RAIZ / "data/relatos_sintomas.txt"), "--mapa",
                str(RAIZ / "data/mapa_conhecimento.csv")]
            with patch("extrair_sintomas.RAIZ", raiz), patch("sys.argv", argumentos), \
                 patch("extrair_sintomas.coletar_relato_interativo",
                       return_value="Há dois dias sinto dor no peito e suor frio."), \
                 patch("builtins.print"):
                main()
            self.assertEqual(original.read_text(), "resultado original\n")
            with (raiz / "outputs/diagnosticos_interativos.csv").open(newline="") as arquivo:
                self.assertEqual(len(list(csv.DictReader(arquivo))), 11)
            with (raiz / "outputs/relatos_interativos.csv").open(newline="") as arquivo:
                self.assertEqual(len(list(csv.DictReader(arquivo))), 1)


if __name__ == "__main__":
    unittest.main()
