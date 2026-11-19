# Neighborhood Action Dashboard | CitizenTech

**Global Solution 2026.2 · FIAP · Ciência da Computação · Fases 1–3**  
**Projeto:** protótipo textual de acompanhamento de ocorrências comunitárias  
**Equipe:** projeto individual  
**Integrante:** Wilton Bezerra Campos Junior.  
**Vídeo da apresentação:** https://youtu.be/BFyIqpfMGu0

> **Natureza do projeto:** todos os bairros, registros, datas e eventos aqui apresentados são *fictícios*. A aplicação não registra chamados reais, não consulta órgãos públicos e não prevê prazos de atendimento.

## 1. Problema, comunidade e propósito

Em muitas comunidades, problemas cotidianos, como iluminação pública insuficiente, pisos sem acessibilidade, resíduos acumulados e conservação de espaços de convivência, são relatados de modo disperso. Isso dificulta visualizar pendências e acompanhar sua evolução.

O **Neighborhood Action Dashboard** organiza esses relatos em um painel comunitário simulado. A demonstração utiliza dois bairros **inteiramente fictícios**, Vila Esperança e Jardim Horizonte, e localidades genéricas, como Praça das Flores e Parque do Sol. Moradores, lideranças comunitárias e equipes de apoio são o público que poderia se beneficiar de uma solução real, desde que ela fosse posteriormente adaptada e governada de forma adequada.

**Objetivo educacional:** aplicar Python básico, condicionais, laços, listas, filas, pilhas, dicionários, hierarquia e matrizes a um problema social compreensível, com indicadores matemáticos simples e regras explícitas.

## 2. Funcionalidades entregues

- Cadastrar ocorrências, com ID automático, categoria validada, descrição, bairro, localidade genérica e dia simulado.
- Listar todas as ocorrências com identificação e situação atual.
- Consultar por ID, filtrar por categoria, por situação ou pelos dois critérios simultaneamente.
- Atualizar o status na sequência **Aberta → Em análise → Concluída**, registrando dia e observação no histórico.
- Consultar a fila FIFO de registros ainda não examinados e a pilha LIFO dos eventos mais recentes.
- Explorar hierarquia `bairro → categoria → IDs` e matriz `categoria × situação`.
- Calcular quantidades, percentuais, pendências e tempos médios simulados, com fórmulas visíveis.
- Detectar um registro de entrada inconsistente sem afetar a análise dos registros válidos.
- Persistir cadastros e atualizações em arquivos CSV **locais**, preservando os exemplos originais para novos testes.
- Executar **20 testes automatizados** com a biblioteca padrão do Python.

## 3. Como executar

**Requisito:** Python 3.8 ou superior. Não é necessário instalar dependências ou conectar à internet.

Abra um terminal na **pasta do projeto que contém `src/` e `data/`**:

```bash
python src/sistema.py
```

Se o Windows não reconhecer `python`, tente `py -3 src/sistema.py`.

Comandos úteis:

```bash
python src/sistema.py --resumo   # Mostra a validação e os indicadores sem abrir o menu
python src/sistema.py --reset    # Apaga apenas o estado local e restaura os dados iniciais
python -m unittest discover -s tests -v   # Executa os 20 testes automatizados
```

> Atenção: `--reset` restaura os dados iniciais **removendo apenas os arquivos locais gerados pelo uso**; não altera os CSVs originais. O sistema utiliza o *dia 30* como referência inteiramente simulada, não a data do computador.

> **Compatibilidade Windows:** a suíte de testes configura UTF-8 no subprocesso que verifica `--resumo`, evitando conflitos com codificações regionais (como cp1252). Os testes trabalham com dados temporários isolados e não alteram o histórico salvo no uso normal da aplicação.

### Menu do sistema

```text
  1. Listar ocorrências
  2. Consultar por ID
  3. Filtrar por categoria e/ou situação
  4. Cadastrar ocorrência
  5. Atualizar situação
  6. Painel de indicadores
  7. Histórico recente (pilha)
  8. Fila de abertas e hierarquia
  9. Relatório de validação
  0. Sair
```

## 4. Formato e validação dos dados

Arquivos originais em `data/`:

- `ocorrencias_iniciais.csv`: 13 linhas de dados, sendo **12 registros válidos e 1 rejeitado intencionalmente**.
- `historico_inicial.csv`: **11 eventos simulados** de acompanhamento de status.

O CSV utiliza **UTF-8, cabeçalho e ponto e vírgula (`;`)** como separador. Cada ocorrência tem os campos:

| Campo | Obrigatório? | Regra |
|---|---|---|
| `id` | Sim | Código único de três algarismos, como `001` |
| `bairro` | Sim | Nome fictício/genérico |
| `categoria` | Sim | `iluminacao`, `acessibilidade`, `limpeza`, `conservacao` |
| `descricao` | Sim | Breve descrição, com pelo menos cinco caracteres |
| `localidade` | Sim | Local comunitário genérico, sem endereço residencial |
| `dia_abertura` | Sim | Dia fictício de 1 a 30 |
| `status` | Sim | `aberta`, `em_analise`, `concluida` |
| `dia_conclusao` | Condicional | Obrigatório para `concluida`; vazio nos outros casos |

**Significado dos status:**

- **Aberta:** demanda registrada, ainda sem análise; permanece na fila de triagem.
- **Em análise:** triagem registrada no histórico; a demanda segue pendente.
- **Concluída:** conclusão **fictícia** registrada, com dia de conclusão informado.

### Tratamento do erro obrigatório

A linha de ID **013** contém o campo `categoria` vazio. A função `validar_ocorrencia()` detecta esse problema com condições booleanas, registra os motivos em `inconsistencias`, **impede a inclusão da linha na lista de registros válidos** e emite o relatório de validação na opção `9`. O ID rejeitado também fica reservado, portanto o primeiro novo cadastro recebe o ID `014`.

O histórico é conferido quanto a IDs existentes, ordem temporal e transições válidas. Caso os dados locais sejam incoerentes, uma mensagem orienta a restauração. A aplicação não corrige ou inventa silenciosamente dados incompletos.

## 5. Estruturas de dados e motivos de escolha

| Estrutura | Aplicação real no código | Justificativa |
|---|---|---|
| **Lista** | `ocorrencias` | Conjunto principal, ordem dos cadastros e iteração em buscas e cálculos. |
| **Fila FIFO** | `fila` | IDs das demandas ainda `aberta`, pela ordem em que aparecem na lista de registros; o primeiro cadastrado vem primeiro. |
| **Pilha LIFO** | `pilha` | Guarda eventos de acompanhamento na ordem de registro, facilitando exibir o evento mais recente primeiro. |
| **Dicionário** | `indice` | Localiza uma ocorrência diretamente pelo código; evita percorrer a lista inteira para consultas por ID. |
| **Hierarquia** | `hierarquia` | Organiza `bairro → categoria → IDs`, favorecendo a navegação temática e territorial. |
| **Matriz** | `matriz` | Lista de listas 4 × 3, com cruzamento de categorias e situações, útil para o resumo numérico. |

Essas estruturas são reconstruídas pela função `reorganizar()` após alterações válidas, garantindo que busca, fila, árvore e matriz reflitam o mesmo conjunto de dados. A pilha é baseada na lista de eventos acumulados.

## 6. Regras lógicas e expressões booleanas

As decisões do sistema dependem de condições com **`if` / `elif` / `else`** e os operadores booleanos **`and` / `or` / `not`**:

```python
# Regra 1: OR. Um único campo essencial vazio torna o cadastro inválido.
if not codigo or not bairro or not categoria or not descricao or not local or not dia_texto or not status:
    erros.append("existe campo obrigatório vazio")

# Regra 2: AND + NOT. ID existente não pode ser reutilizado.
if codigo and codigo in existentes and not registro.get("permitir_duplicado", False):
    erros.append("ID já cadastrado")

# Regra 3: AND + NOT. Cada filtro é opcional; com dois filtros, ambos devem coincidir.
if (not categoria or registro["categoria"] == categoria) and (not status or registro["status"] == status):
    resultado.append(registro)
```

Na atualização, a transição só é permitida de `aberta` para `em_analise`, ou de `em_analise` para `concluida`. O sistema impede saltar etapas, repetir a mesma situação, reabrir uma ocorrência concluída e atribuir datas anteriores ao evento anterior. Cada mensagem informa o resultado de uma condição específica e seu motivo.

## 7. Indicadores, cálculos e interpretação

**Base original validada, antes de qualquer cadastro ou alteração local:**

| Categoria | Aberta | Em análise | Concluída | Total | Proporção |
|---|---:|---:|---:|---:|---:|
| Iluminação | 1 | 1 | 1 | 3 | 25,0% |
| Acessibilidade | 1 | 1 | 1 | 3 | 25,0% |
| Limpeza | 1 | 2 | 0 | 3 | 25,0% |
| Conservação | 1 | 1 | 1 | 3 | 25,0% |
| **Total** | **4** | **5** | **3** | **12** | **100,0%** |

**Fórmulas:**

- Proporção de cada grupo: `(quantidade do grupo ÷ total válido) × 100`.
- Pendências: `quantidade de abertas + quantidade em análise = 4 + 5 = 9` (**75,0%** do total).
- Dias para concluir cada ocorrência: `dia_conclusao − dia_abertura`.
- Média até conclusão: `(13 + 16 + 15) ÷ 3 = 14,7 dias simulados` (arredondado).
- Tempo pendente no dia 30: `30 − dia_abertura`, só para as demandas não concluídas. Média inicial: **22,7 dias simulados**.

**Interpretação:** os problemas se distribuem igualmente entre as quatro categorias na amostra fictícia. Entretanto, 9 de 12 demandas permanecem pendentes, indicando a utilidade de um acompanhamento organizado. O número é **ilustrativo** e não pode ser generalizado para um bairro real nem interpretado como indicador de desempenho de uma prefeitura.

A aplicação mostra **os dados de origem de cada média**, o cálculo e o resultado na opção 6. O uso de laços e operações aritméticas foi deliberado; não utilizamos bibliotecas analíticas avançadas.

## 8. Exemplo de uso demonstrável

1. Execute `python src/sistema.py --reset`, seguido de `python src/sistema.py`.
2. Opção `1`: lista as 12 ocorrências válidas. A opção `9` identifica o registro rejeitado `013`.
3. Opção `2`: consulte `003` (limpeza, aberta, Jardim Horizonte).
4. Opção `3`: selecione a categoria `iluminacao` e a situação `aberta`. O resultado inicial é `005`.
5. Opção `5`: atualize `003` para **Em análise**, no **dia 20**. Um evento será incluído no histórico.
6. Opção `4`: cadastre uma nova ocorrência fictícia, por exemplo, categoria `limpeza`, bairro `Vila Esperança`, local `Praça das Palmeiras`, descrição `Resíduos no espaço coletivo`, dia `22`. O ID gerado será `014`.
7. Opção `6`: visualize os indicadores recalculados e a nova matriz. Opção `7`: confira a atualização no histórico.
8. Opção `0`: saia. Ao abrir novamente, os novos registros e status estarão preservados em CSVs locais.

## 9. Acessibilidade, inclusão, privacidade e ética

- **Acessibilidade:** menu textual, opções numeradas, mensagens diretas, tabelas com cabeçalhos e informações que não dependem apenas de cores. Funciona sem mouse nem recursos gráficos.
- **Inclusão:** quatro categorias acessíveis à comunidade, incluindo barreiras de mobilidade, e linguagem de fácil interpretação. Um produto real exigiria testes com usuários diversos e adaptações adicionais.
- **Privacidade:** dados inteiramente fictícios, locais genéricos e ausência de campos para nomes, telefones, documentos ou endereços residenciais. Nenhum envio para servidores externos.
- **Responsabilidade:** status simulados **não representam atendimento oficial**, não demonstram solução de problemas reais e não devem embasar decisões públicas.

## 10. Estrutura do projeto

```text
global-solution-citizentech/
├── README.md
├── .gitignore
├── src/
│   └── sistema.py
├── data/
│   ├── ocorrencias_iniciais.csv
│   └── historico_inicial.csv
├── docs/
│   ├── indicadores_iniciais.md
│   ├── decisoes_tecnicas
│   ├── uso_ia.md
│   └── saida_exemplo.txt
└── tests/
    └── test_sistema.py
```

Os arquivos `data/estado_local.csv` e `data/historico_local.csv` são criados automaticamente ao alterar o sistema, não entram no Git e não substituem os dados de demonstração versionados.

## 11. Testes, documentação e uso de IA

Execute `python -m unittest discover -s tests -v`. Os **20 testes automatizados** cobrem a leitura, os cálculos, os filtros, o tratamento de inconsistências, as transições, as estruturas e a persistência.

A participação de IA na elaboração da solução e dos testes está explicitada em [`docs/uso_ia.md`](docs/uso_ia.md). A versão final do trabalho exige que o estudante revise, compreenda, demonstre e consiga justificar o código.

## 12. Conclusões, limitações e aprendizados

O protótipo demonstra que fundamentos introdutórios de Ciência da Computação conseguem organizar informações comunitárias e produzir indicadores transparentes sem frameworks, APIs ou serviços externos. O tratamento de inconsistências evita distorções e a combinação de estruturas tem papéis claros: localizar, agrupar, priorizar e resumir.

**Limitações:** escala pequena e simulada; somente um usuário local; sem autenticação, controle multiusuário, verificação de campo, consentimento real ou integração pública. A fila representa ordem de registro, não prioridade técnica, urgência ou prazo legal. Datas são fictícias. Em fases posteriores, podem ser estudadas persistência mais robusta, testes de usabilidade, acessibilidade aprofundada, visualizações e proteção de dados, **sem presumir que tais recursos façam parte da entrega atual**.

**Aprendizados centrais:** leitura e validação de CSV, condições booleanas, estruturas de dados, busca, estados válidos, rastreabilidade e transformação de registros em indicadores interpretáveis.
