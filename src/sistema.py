"""Global Solution 2026.2 - Neighborhood Action Dashboard.

Sistema textual e didatico em Python, com estruturas de dados introdutorias.
Execute a partir da raiz do projeto: python src/sistema.py
"""

import csv
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CATEGORIAS = ("iluminacao", "acessibilidade", "limpeza", "conservacao")
SITUACOES = ("aberta", "em_analise", "concluida")
ROTULOS = {
    "iluminacao": "Iluminação",
    "acessibilidade": "Acessibilidade",
    "limpeza": "Limpeza",
    "conservacao": "Conservação",
    "aberta": "Aberta",
    "em_analise": "Em análise",
    "concluida": "Concluída",
}
DIA_ATUAL = 30  # Marco temporal ficticio, nao corresponde ao calendario real.
CAMPOS_OCORRENCIAS = (
    "id", "bairro", "categoria", "descricao", "localidade", "dia_abertura",
    "status", "dia_conclusao"
)
CAMPOS_HISTORICO = ("id", "dia_evento", "status_anterior", "status_novo", "observacao")


def rotulo(codigo):
    return ROTULOS.get(codigo, codigo)


def validar_ocorrencia(registro, existentes):
    """Retorna lista de motivos; sem bibliotecas de validacao externas."""
    erros = []
    codigo = str(registro.get("id", "")).strip()
    bairro = str(registro.get("bairro", "")).strip()
    categoria = str(registro.get("categoria", "")).strip()
    descricao = str(registro.get("descricao", "")).strip()
    local = str(registro.get("localidade", "")).strip()
    status = str(registro.get("status", "")).strip()
    dia_texto = str(registro.get("dia_abertura", "")).strip()
    conclusao_texto = str(registro.get("dia_conclusao", "")).strip()

    # OR: basta um campo obrigatorio vazio para reprovar.
    if not codigo or not bairro or not categoria or not descricao or not local or not dia_texto or not status:
        erros.append("existe campo obrigatório vazio")
    if not codigo.isdigit() or len(codigo) != 3:
        erros.append("ID deve conter exatamente três algarismos")
    # AND + NOT: um identificador nao pode estar reservado na tabela de consulta.
    if codigo and codigo in existentes and not registro.get("permitir_duplicado", False):
        erros.append("ID já cadastrado")
    if categoria not in CATEGORIAS:
        erros.append("categoria desconhecida ou ausente")
    if status not in SITUACOES:
        erros.append("situação desconhecida ou ausente")
    if descricao and len(descricao) < 5:
        erros.append("descrição deve ter pelo menos cinco caracteres")
    if not dia_texto.isdigit() or not 1 <= int(dia_texto) <= DIA_ATUAL:
        erros.append("dia de abertura deve ser de 1 a 30")

    # IF / ELIF / ELSE: o campo de conclusao depende da situacao.
    if status == "concluida":
        if not conclusao_texto.isdigit():
            erros.append("concluída precisa informar dia de conclusão")
        elif dia_texto.isdigit() and not int(dia_texto) <= int(conclusao_texto) <= DIA_ATUAL:
            erros.append("dia de conclusão fora do período simulado")
    elif status in ("aberta", "em_analise"):
        if conclusao_texto:
            erros.append("ocorrência pendente não pode ter dia de conclusão")
    else:
        # Uma mensagem específica sobre a situacao ja foi inserida acima.
        pass
    return erros


def ler_csv(caminho):
    with caminho.open("r", encoding="utf-8-sig", newline="") as arquivo:
        return list(csv.DictReader(arquivo, delimiter=";"))


def escrever_csv(caminho, campos, linhas):
    with caminho.open("w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=campos, delimiter=";", extrasaction="ignore")
        escritor.writeheader()
        escritor.writerows(linhas)


def reorganizar(sistema):
    """Reconstrói indice, fila FIFO, pilha LIFO, hierarquia e matriz."""
    registros = sistema["ocorrencias"]  # Lista: armazenamento principal e percurso.
    sistema["indice"] = {r["id"]: r for r in registros}  # Dicionario: busca por ID.
    sistema["fila"] = [r["id"] for r in registros if r["status"] == "aberta"]
    # Fila FIFO: mantém a ordem de cadastro no conjunto, não a ordem das datas fictícias.
    sistema["pilha"] = sistema["historico"].copy()  # Pilha: ultimo evento no topo.
    arvore = {}
    for registro in registros:
        bairro = registro["bairro"]
        categoria = registro["categoria"]
        if bairro not in arvore:
            arvore[bairro] = {}
        if categoria not in arvore[bairro]:
            arvore[bairro][categoria] = []
        arvore[bairro][categoria].append(registro["id"])
    sistema["hierarquia"] = arvore
    matriz = [[0 for _ in SITUACOES] for _ in CATEGORIAS]
    for registro in registros:
        i = CATEGORIAS.index(registro["categoria"])
        j = SITUACOES.index(registro["status"])
        matriz[i][j] += 1
    sistema["matriz"] = matriz


def verificar_historico(registros, eventos):
    """Confere sequencia de eventos e coerencia com os status atuais."""
    indice = {r["id"]: r for r in registros}
    situacao_reconstruida = {codigo: "aberta" for codigo in indice}
    ultimo_dia = {codigo: int(r["dia_abertura"]) for codigo, r in indice.items()}
    for posicao, evento in enumerate(eventos, start=1):
        codigo = evento["id"]
        anterior, novo = evento["status_anterior"], evento["status_novo"]
        dia_texto = evento["dia_evento"]
        if codigo not in indice:
            raise ValueError(f"Histórico linha {posicao}: ID inexistente {codigo}")
        if not dia_texto.isdigit() or not ultimo_dia[codigo] <= int(dia_texto) <= DIA_ATUAL:
            raise ValueError(f"Histórico linha {posicao}: dia incoerente")
        permitido = (anterior == "aberta" and novo == "em_analise") or (
            anterior == "em_analise" and novo == "concluida"
        )
        if not permitido or situacao_reconstruida[codigo] != anterior:
            raise ValueError(f"Histórico linha {posicao}: transição incoerente")
        situacao_reconstruida[codigo] = novo
        ultimo_dia[codigo] = int(dia_texto)
        if novo == "concluida" and indice[codigo]["dia_conclusao"] != dia_texto:
            raise ValueError(f"Histórico linha {posicao}: conclusão diferente do registro")
    for codigo, registro in indice.items():
        if situacao_reconstruida[codigo] != registro["status"]:
            raise ValueError(f"Histórico: situação final inconsistente para {codigo}")


def carregar_sistema(raiz=RAIZ):
    raiz = Path(raiz)
    arquivo_estado = raiz / "data" / "estado_local.csv"
    arquivo_eventos_local = raiz / "data" / "historico_local.csv"
    existe_estado = arquivo_estado.exists()
    existe_historico = arquivo_eventos_local.exists()
    if existe_estado != existe_historico:
        raise ValueError("Estado local incompleto. Use --reset para voltar aos dados iniciais.")
    arquivo_ocorrencias = arquivo_estado if existe_estado else raiz / "data" / "ocorrencias_iniciais.csv"
    arquivo_historico = arquivo_eventos_local if existe_historico else raiz / "data" / "historico_inicial.csv"
    validos, inconsistencias, indice = [], [], {}
    for linha, registro in enumerate(ler_csv(arquivo_ocorrencias), start=2):
        motivos = validar_ocorrencia(registro, indice)
        if motivos:
            inconsistencias.append({"linha": linha, "id": registro.get("id", ""), "motivos": motivos})
        else:
            validos.append(registro)
            indice[registro["id"]] = registro
    historico = ler_csv(arquivo_historico)
    verificar_historico(validos, historico)
    sistema = {"ocorrencias": validos, "historico": historico, "inconsistencias": inconsistencias,
               "raiz": raiz}
    reorganizar(sistema)
    return sistema


def salvar(sistema):
    diretorio = sistema["raiz"] / "data"
    diretorio.mkdir(parents=True, exist_ok=True)
    # Arquivos gerados localmente ficam fora do Git (ver .gitignore).
    escrever_csv(diretorio / "estado_local.csv", CAMPOS_OCORRENCIAS, sistema["ocorrencias"])
    escrever_csv(diretorio / "historico_local.csv", CAMPOS_HISTORICO, sistema["historico"])


def cadastrar(sistema, categoria, descricao, localidade, bairro, dia_abertura):
    numeros = [int(r["id"]) for r in sistema["ocorrencias"]]
    # IDs de registros rejeitados também ficam reservados para evitar confusão de auditoria.
    numeros += [int(e["id"]) for e in sistema["inconsistencias"] if str(e["id"]).isdigit()]
    proximo = (max(numeros) + 1) if numeros else 1
    if proximo > 999:
        return None, ["limite de 999 identificadores atingido"]
    registro = {"id": f"{proximo:03d}", "bairro": bairro.strip(), "categoria": categoria.strip(),
                "descricao": descricao.strip(), "localidade": localidade.strip(),
                "dia_abertura": str(dia_abertura).strip(), "status": "aberta", "dia_conclusao": ""}
    erros = validar_ocorrencia(registro, sistema["indice"])
    if erros:
        return None, erros
    sistema["ocorrencias"].append(registro)
    reorganizar(sistema)
    return registro, []


def consultar(sistema, codigo):
    return sistema["indice"].get(str(codigo).strip())


def filtrar(sistema, categoria="", status=""):
    if (categoria and categoria not in CATEGORIAS) or (status and status not in SITUACOES):
        raise ValueError("Filtro desconhecido. Use uma categoria e situação padronizadas.")
    resultado = []
    for registro in sistema["ocorrencias"]:
        # AND + NOT: campo vazio significa sem filtro, campo preenchido deve coincidir.
        if (not categoria or registro["categoria"] == categoria) and (
            not status or registro["status"] == status
        ):
            resultado.append(registro)
    return resultado


def atualizar(sistema, codigo, novo_status, dia_evento, observacao=""):
    registro = consultar(sistema, codigo)
    if registro is None:
        return False, "Ocorrência não encontrada."
    if novo_status not in SITUACOES:
        return False, "Situação inválida. Escolha uma das opções oferecidas."
    anterior = registro["status"]
    if novo_status == anterior:
        return False, "Não houve alteração: a situação já é essa."
    # Proíbe saltar etapas ou reabrir registros concluídos.
    if not ((anterior == "aberta" and novo_status == "em_analise") or
            (anterior == "em_analise" and novo_status == "concluida")):
        return False, "Transição inválida: use Aberta > Em análise > Concluída."
    dia_texto = str(dia_evento).strip()
    if not dia_texto.isdigit():
        return False, "O dia simulado precisa ser um número inteiro."
    dia = int(dia_texto)
    dias_do_registro = [int(r["dia_evento"]) for r in sistema["historico"] if r["id"] == registro["id"]]
    ultimo = max(dias_do_registro) if dias_do_registro else int(registro["dia_abertura"])
    if not ultimo <= dia <= DIA_ATUAL:
        return False, f"Dia inválido: use de {ultimo} até {DIA_ATUAL}."
    registro["status"] = novo_status
    if novo_status == "concluida":
        registro["dia_conclusao"] = str(dia)
    sistema["historico"].append({"id": registro["id"], "dia_evento": str(dia),
                                "status_anterior": anterior, "status_novo": novo_status,
                                "observacao": observacao.strip() or "Acompanhamento simulado"})
    reorganizar(sistema)
    return True, f"Ocorrência {codigo}: {rotulo(anterior)} > {rotulo(novo_status)} (dia {dia})."


def indicadores(sistema):
    total = len(sistema["ocorrencias"])
    categorias = {chave: 0 for chave in CATEGORIAS}
    situacoes = {chave: 0 for chave in SITUACOES}
    concluidas_dias = []
    pendentes_dias = []
    for registro in sistema["ocorrencias"]:
        categorias[registro["categoria"]] += 1
        situacoes[registro["status"]] += 1
        if registro["status"] == "concluida":
            concluidas_dias.append(int(registro["dia_conclusao"]) - int(registro["dia_abertura"]))
        else:
            pendentes_dias.append(DIA_ATUAL - int(registro["dia_abertura"]))
    def proporcoes(valores):
        return {k: round((v / total) * 100, 1) if total else 0.0 for k, v in valores.items()}
    return {"total": total, "categorias": categorias, "situacoes": situacoes,
            "pct_categorias": proporcoes(categorias), "pct_situacoes": proporcoes(situacoes),
            "pendentes": len(pendentes_dias),
            "tempo_medio_conclusao": round(sum(concluidas_dias) / len(concluidas_dias), 1)
            if concluidas_dias else None,
            "tempo_medio_pendencia": round(sum(pendentes_dias) / len(pendentes_dias), 1)
            if pendentes_dias else None,
            "dias_conclusao": concluidas_dias, "dias_pendencia": pendentes_dias}


def tabela(registros):
    if not registros:
        print("Nenhuma ocorrência corresponde à consulta.")
        return
    print(f"{'ID':<5} {'CATEGORIA':<17} {'BAIRRO / LOCALIDADE':<38} {'SITUAÇÃO'}")
    print("-" * 85)
    for registro in registros:
        lugar = f"{registro['bairro']} / {registro['localidade']}"
        print(f"{registro['id']:<5} {rotulo(registro['categoria']):<17} {lugar[:37]:<38} {rotulo(registro['status'])}")
    print(f"Total listado: {len(registros)}")


def imprimir_indicadores(sistema):
    d = indicadores(sistema)
    print("\n=== PAINEL DE INDICADORES | DADOS SIMULADOS ===")
    print(f"Registros válidos: {d['total']} | Pendentes: {d['pendentes']} | Dia de referência: {DIA_ATUAL}")
    print("\nPor categoria (quantidade / proporção):")
    for chave in CATEGORIAS:
        print(f"  {rotulo(chave):<18} {d['categorias'][chave]:>2}  ({d['pct_categorias'][chave]:>5.1f}%)")
    print("\nPor situação (quantidade / proporção):")
    for chave in SITUACOES:
        print(f"  {rotulo(chave):<18} {d['situacoes'][chave]:>2}  ({d['pct_situacoes'][chave]:>5.1f}%)")
    print("\nMatriz: linhas = categorias; colunas = aberta / em análise / concluída")
    print(f"{'Categoria':<18} {'Aberta':>7} {'Análise':>8} {'Concluída':>11} {'Total':>7}")
    for posicao, chave in enumerate(CATEGORIAS):
        valores = sistema["matriz"][posicao]
        print(f"{rotulo(chave):<18} {valores[0]:>7} {valores[1]:>8} {valores[2]:>11} {sum(valores):>7}")
    print("\nFórmulas e dados de origem:")
    print("  Proporção (%) = (quantidade do grupo / total válido) x 100")
    print(f"  Pendentes = {d['situacoes']['aberta']} abertas + {d['situacoes']['em_analise']} em análise = {d['pendentes']}")
    if d["tempo_medio_conclusao"] is not None:
        print(f"  Dias até conclusão = {d['dias_conclusao']} | Média = {d['tempo_medio_conclusao']:.1f} dias")
    else:
        print("  Média de conclusão: sem ocorrências concluídas.")
    if d["tempo_medio_pendencia"] is not None:
        print(f"  Dias pendentes no dia {DIA_ATUAL} = {d['dias_pendencia']} | Média = {d['tempo_medio_pendencia']:.1f} dias")
    else:
        print("  Média de pendência: sem ocorrências pendentes.")
    print("\nLeitura dos dados:")
    maior = max(d["categorias"].values(), default=0)
    mais_frequentes = [rotulo(k) for k, v in d["categorias"].items() if v == maior and v > 0]
    if not mais_frequentes:
        print("  Ainda não há dados suficientes para interpretar prioridades.")
    elif len(mais_frequentes) == len(CATEGORIAS):
        print("  O conjunto fictício está distribuído igualmente entre as quatro categorias.")
    else:
        print("  Categoria(s) mais frequente(s): " + ", ".join(mais_frequentes) + ".")
    print(f"  {d['pendentes']} demanda(s) permanecem pendentes; isso indica necessidade de acompanhamento simulado.")
    print("  Não representa diagnóstico real nem prazo de atendimento público.")


def mostrar_historico(sistema, codigo=""):
    eventos = [e for e in sistema["pilha"] if not codigo or e["id"] == codigo]
    if not eventos:
        print("Nenhum evento encontrado.")
        return
    print("\nÚltimos eventos (pilha: LIFO):")
    for evento in reversed(eventos[-10:]):
        print(f"  Dia {evento['dia_evento']:>2} | ID {evento['id']} | "
              f"{rotulo(evento['status_anterior'])} > {rotulo(evento['status_novo'])} | {evento['observacao']}")


def mostrar_fila(sistema):
    print("\nFila de registros ainda não examinados (FIFO):")
    if not sistema["fila"]:
        print("  Não há ocorrências abertas.")
    for posicao, codigo in enumerate(sistema["fila"], start=1):
        item = sistema["indice"][codigo]
        print(f"  {posicao}. ID {codigo} | abertura dia {item['dia_abertura']} | {rotulo(item['categoria'])}")


def mostrar_hierarquia(sistema):
    print("\nHierarquia: bairro > categoria > IDs")
    for bairro, grupos in sorted(sistema["hierarquia"].items()):
        print("  " + bairro)
        for categoria, ids in grupos.items():
            print("    " + rotulo(categoria) + ": " + ", ".join(ids))


def mostrar_inconsistencias(sistema):
    print("\nRegistros rejeitados na leitura (não entram nos cálculos):")
    if not sistema["inconsistencias"]:
        print("  Nenhum. A base local atualmente carregada está validada.")
    for item in sistema["inconsistencias"]:
        print(f"  Linha {item['linha']}, ID {item['id']}: " + "; ".join(item["motivos"]))


def menu():
    print("\n" + "=" * 57)
    print(" NEIGHBORHOOD ACTION DASHBOARD | CITIZENTECH 2026.2")
    print(" Simulação educativa, sem registro de dados pessoais")
    print("=" * 57)
    print("  1. Listar ocorrências")
    print("  2. Consultar por ID")
    print("  3. Filtrar por categoria e/ou situação")
    print("  4. Cadastrar ocorrência")
    print("  5. Atualizar situação")
    print("  6. Painel de indicadores")
    print("  7. Histórico recente (pilha)")
    print("  8. Fila de abertas e hierarquia")
    print("  9. Relatório de validação")
    print("  0. Sair")


def escolher(opcoes, titulo, permitir_vazio=False):
    print(titulo)
    for indice, opcao in enumerate(opcoes, start=1):
        print(f"  {indice}. {rotulo(opcao)}")
    texto = input("Escolha o número" + (" (Enter = todos)" if permitir_vazio else "") + ": ").strip()
    if permitir_vazio and not texto:
        return ""
    if not texto.isdigit() or not 1 <= int(texto) <= len(opcoes):
        print("Opção inválida.")
        return None
    return opcoes[int(texto) - 1]


def executar(sistema):
    print("Dados simulados carregados. Digite 6 para visualizar os indicadores.")
    if sistema["inconsistencias"]:
        print(f"Validação: {len(sistema['inconsistencias'])} registro(s) inconsistente(s) rejeitado(s). Veja opção 9.")
    while True:
        menu()
        opcao = input("Opção: ").strip()
        if opcao == "0":
            print("Encerrado. Alterações válidas foram salvas localmente.")
            return
        elif opcao == "1":
            tabela(sistema["ocorrencias"])
        elif opcao == "2":
            codigo = input("Informe o código (ex.: 001): ").strip()
            registro = consultar(sistema, codigo)
            if registro:
                tabela([registro])
                print(f"Descrição: {registro['descricao']} | Abertura: dia {registro['dia_abertura']}")
            else:
                print("Ocorrência não encontrada.")
        elif opcao == "3":
            categoria = escolher(CATEGORIAS, "Categoria:", permitir_vazio=True)
            if categoria is None:
                continue
            status = escolher(SITUACOES, "Situação:", permitir_vazio=True)
            if status is None:
                continue
            tabela(filtrar(sistema, categoria, status))
        elif opcao == "4":
            categoria = escolher(CATEGORIAS, "Categoria:")
            if categoria is None:
                continue
            bairro = input("Bairro genérico (ex.: Vila Esperança): ")
            local = input("Localidade genérica (sem endereço pessoal): ")
            descricao = input("Descrição breve: ")
            dia = input("Dia simulado de abertura (1 a 30): ")
            registro, erros = cadastrar(sistema, categoria, descricao, local, bairro, dia)
            if erros:
                print("Cadastro recusado: " + "; ".join(erros))
            else:
                salvar(sistema)
                print(f"Cadastro realizado: ID {registro['id']} (situação Aberta).")
        elif opcao == "5":
            codigo = input("ID que deseja atualizar: ").strip()
            if not consultar(sistema, codigo):
                print("Ocorrência não encontrada.")
                continue
            status = escolher(SITUACOES, "Nova situação:")
            if status is None:
                continue
            dia = input("Dia simulado do evento (1 a 30): ")
            nota = input("Observação breve (opcional, sem dados pessoais): ")
            sucesso, mensagem = atualizar(sistema, codigo, status, dia, nota)
            if sucesso:
                salvar(sistema)
            print(mensagem)
        elif opcao == "6":
            imprimir_indicadores(sistema)
        elif opcao == "7":
            mostrar_historico(sistema, input("Filtrar ID (Enter para todos): ").strip())
        elif opcao == "8":
            mostrar_fila(sistema)
            mostrar_hierarquia(sistema)
        elif opcao == "9":
            mostrar_inconsistencias(sistema)
        else:
            print("Opção inválida. Escolha de 0 a 9.")


def main():
    if "--reset" in sys.argv:
        for nome in ("estado_local.csv", "historico_local.csv"):
            (RAIZ / "data" / nome).unlink(missing_ok=True)
        print("Dados locais restaurados. O próximo início usará os arquivos fictícios originais.")
        return
    try:
        sistema = carregar_sistema()
        if "--resumo" in sys.argv:
            mostrar_inconsistencias(sistema)
            imprimir_indicadores(sistema)
        else:
            executar(sistema)
    except (OSError, ValueError, KeyError) as erro:
        print("Erro na carga ou gravação dos dados: " + str(erro))
        sys.exit(1)
    except (EOFError, KeyboardInterrupt):
        print("\nExecução encerrada.")


if __name__ == "__main__":
    main()
