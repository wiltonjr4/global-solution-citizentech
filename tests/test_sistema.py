"""Testes sem dependencias externas: python -m unittest discover -s tests -v"""
import copy
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("sistema", RAIZ / "src" / "sistema.py")
sistema = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sistema)


class TestesGlobalSolution(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.raiz = Path(self.tmp.name)
        (self.raiz / "data").mkdir()
        for nome in ("ocorrencias_iniciais.csv", "historico_inicial.csv"):
            shutil.copyfile(RAIZ / "data" / nome, self.raiz / "data" / nome)
        self.s = sistema.carregar_sistema(self.raiz)

    def tearDown(self):
        self.tmp.cleanup()

    def test_carga_minima_e_rejeicao(self):
        self.assertEqual(len(self.s["ocorrencias"]), 12)
        self.assertEqual(len(self.s["historico"]), 11)
        self.assertEqual(len(self.s["inconsistencias"]), 1)
        self.assertEqual(self.s["inconsistencias"][0]["id"], "013")
        self.assertIn("categoria desconhecida ou ausente", self.s["inconsistencias"][0]["motivos"])

    def test_busca_por_id(self):
        self.assertEqual(sistema.consultar(self.s, "009")["status"], "concluida")
        self.assertIsNone(sistema.consultar(self.s, "999"))

    def test_cadastro_gera_codigo_sem_reutilizar_rejeitado(self):
        novo, erros = sistema.cadastrar(self.s, "limpeza", "Solicitação simulada", "Praça", "Vila Esperança", 21)
        self.assertEqual(erros, [])
        self.assertEqual(novo["id"], "014")
        self.assertEqual(len(self.s["ocorrencias"]), 13)
        self.assertIn("014", self.s["fila"])

    def test_cadastro_categoria_invalida(self):
        registro, erros = sistema.cadastrar(self.s, "transporte", "Ponto danificado", "Praça", "Vila", 11)
        self.assertIsNone(registro)
        self.assertIn("categoria desconhecida ou ausente", erros)

    def test_cadastro_sem_campos_obrigatorios(self):
        registro, erros = sistema.cadastrar(self.s, "limpeza", "", "", "", 11)
        self.assertIsNone(registro)
        self.assertTrue(any("obrigatório" in e for e in erros))

    def test_cadastro_data_invalida(self):
        registro, erros = sistema.cadastrar(self.s, "limpeza", "Lixo na praça", "Praça", "Vila", 35)
        self.assertIsNone(registro)
        self.assertTrue(any("dia de abertura" in e for e in erros))

    def test_rejeita_id_duplicado(self):
        registro = copy.copy(self.s["ocorrencias"][0])
        self.assertIn("ID já cadastrado", sistema.validar_ocorrencia(registro, self.s["indice"]))

    def test_filtro_categoria_e_status(self):
        filtrados = sistema.filtrar(self.s, "iluminacao", "aberta")
        self.assertEqual([x["id"] for x in filtrados], ["005"])
        with self.assertRaises(ValueError):
            sistema.filtrar(self.s, "educacao", "")

    def test_fila_fifo_de_abertas(self):
        self.assertEqual(self.s["fila"], ["003", "005", "008", "010"])
        ok, _ = sistema.atualizar(self.s, "003", "em_analise", 20)
        self.assertTrue(ok)
        self.assertEqual(self.s["fila"], ["005", "008", "010"])

    def test_pilha_lifo_das_atualizacoes(self):
        ok, _ = sistema.atualizar(self.s, "003", "em_analise", 20)
        self.assertTrue(ok)
        self.assertEqual(self.s["pilha"][-1]["id"], "003")
        self.assertEqual(self.s["pilha"][-1]["status_novo"], "em_analise")

    def test_impede_pular_status(self):
        ok, mensagem = sistema.atualizar(self.s, "003", "concluida", 20)
        self.assertFalse(ok)
        self.assertIn("Transição inválida", mensagem)
        self.assertEqual(len(self.s["historico"]), 11)

    def test_impede_status_desconhecido(self):
        ok, _ = sistema.atualizar(self.s, "003", "em_execucao", 20)
        self.assertFalse(ok)

    def test_impede_regressao_e_conclusao_com_data_anterior(self):
        ok, _ = sistema.atualizar(self.s, "002", "aberta", 25)
        self.assertFalse(ok)
        ok, mensagem = sistema.atualizar(self.s, "001", "concluida", 2)
        self.assertFalse(ok)
        self.assertIn("Dia inválido", mensagem)

    def test_atualiza_e_registra_dia_conclusao(self):
        ok, _ = sistema.atualizar(self.s, "001", "concluida", 28, "Teste funcional")
        self.assertTrue(ok)
        self.assertEqual(self.s["indice"]["001"]["dia_conclusao"], "28")
        self.assertEqual(self.s["matriz"][0], [1, 0, 2])
        self.assertEqual(len(self.s["historico"]), 12)

    def test_hierarquia_e_matriz(self):
        self.assertIn("Vila Esperança", self.s["hierarquia"])
        self.assertIn("001", self.s["hierarquia"]["Vila Esperança"]["iluminacao"])
        self.assertEqual(self.s["matriz"], [[1, 1, 1], [1, 1, 1], [1, 2, 0], [1, 1, 1]])
        self.assertEqual(sum(sum(linha) for linha in self.s["matriz"]), 12)

    def test_indicadores_e_formulas(self):
        indicadores = sistema.indicadores(self.s)
        self.assertEqual(indicadores["pendentes"], 9)
        self.assertEqual(indicadores["pct_categorias"]["limpeza"], 25.0)
        self.assertEqual(indicadores["pct_situacoes"]["em_analise"], 41.7)
        self.assertEqual(indicadores["dias_conclusao"], [13, 16, 15])
        self.assertEqual(indicadores["tempo_medio_conclusao"], 14.7)
        self.assertEqual(indicadores["tempo_medio_pendencia"], 22.7)

    def test_salvar_e_reabrir_sem_perder_alteracoes(self):
        novo, _ = sistema.cadastrar(self.s, "limpeza", "Lixo acumulado", "Praça Leste", "Vila", 22)
        sistema.atualizar(self.s, "003", "em_analise", 23)
        sistema.salvar(self.s)
        reaberto = sistema.carregar_sistema(self.raiz)
        self.assertEqual(len(reaberto["ocorrencias"]), 13)
        self.assertEqual(reaberto["indice"][novo["id"]]["status"], "aberta")
        self.assertEqual(reaberto["indice"]["003"]["status"], "em_analise")
        self.assertEqual(len(reaberto["historico"]), 12)

    def test_arquivo_historico_incoerente_e_rejeitado(self):
        arquivo = self.raiz / "data" / "historico_inicial.csv"
        conteudo = arquivo.read_text(encoding="utf-8")
        arquivo.write_text(conteudo.replace("001;4;aberta;em_analise", "001;4;aberta;concluida"), encoding="utf-8")
        with self.assertRaises(ValueError):
            sistema.carregar_sistema(self.raiz)

    def test_resumo_cli_independente_do_diretorio_atual(self):
        # Executa uma copia isolada do projeto: o teste nao depende de dados
        # locais que o usuario tenha alterado ao usar o aplicativo.
        pasta_src = self.raiz / "src"
        pasta_src.mkdir()
        script = pasta_src / "sistema.py"
        shutil.copyfile(RAIZ / "src" / "sistema.py", script)
        pasta_externa = self.raiz / "diretorio_externo"
        pasta_externa.mkdir()

        # Padroniza a saida do Python filho como UTF-8, inclusive quando o
        # Windows utiliza cp1252 para saidas redirecionadas.
        ambiente = {**os.environ, "PYTHONIOENCODING": "utf-8"}
        processo = subprocess.run(
            [sys.executable, str(script), "--resumo"],
            cwd=pasta_externa, capture_output=True, text=True,
            encoding="utf-8", env=ambiente
        )
        self.assertEqual(processo.returncode, 0, processo.stderr)
        self.assertIn("Registros válidos: 12", processo.stdout)
        self.assertIn("Matriz", processo.stdout)

    def test_divisao_por_zero_sem_registros(self):
        vazio = {"ocorrencias": [], "historico": [], "inconsistencias": [], "raiz": self.raiz}
        sistema.reorganizar(vazio)
        metricas = sistema.indicadores(vazio)
        self.assertEqual(metricas["pct_situacoes"]["aberta"], 0)
        self.assertIsNone(metricas["tempo_medio_conclusao"])
        self.assertEqual(metricas["pendentes"], 0)


if __name__ == "__main__":
    unittest.main()
