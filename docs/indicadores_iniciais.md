# Indicadores iniciais e interpretação

**Base:** `data/ocorrencias_iniciais.csv` (12 registros válidos, 1 inválido excluído) e `data/historico_inicial.csv` (11 eventos). Referência temporal fictícia: dia 30. Nenhuma informação é real.

## Contagem por situação

| Situação | Quantidade | Cálculo | Proporção |
|---|---:|---|---:|
| Aberta | 4 | 4 / 12 × 100 | 33,3% |
| Em análise | 5 | 5 / 12 × 100 | 41,7% |
| Concluída | 3 | 3 / 12 × 100 | 25,0% |
| **Total** | **12** | | **100,0%** (arredondado) |

## Categorias

Cada categoria (iluminação, acessibilidade, limpeza e conservação) possui **3 registros**, ou **25%** do total válido. A base foi deliberadamente equilibrada para assegurar exemplos nas quatro categorias, sem sugerir uma necessidade real predominante.

## Matriz categoria × situação

| Categoria | Aberta | Em análise | Concluída | Total |
|---|---:|---:|---:|---:|
| Iluminação | 1 | 1 | 1 | 3 |
| Acessibilidade | 1 | 1 | 1 | 3 |
| Limpeza | 1 | 2 | 0 | 3 |
| Conservação | 1 | 1 | 1 | 3 |

## Indicadores adicionais

**Pendências:** 4 abertas + 5 em análise = **9**, ou **75,0%** do conjunto simulado.

**Dias para a conclusão (registros 002, 004, 009):** `[15−2, 20−4, 24−9] = [13, 16, 15]`. Média = `(13+16+15)/3 = 14,666...`, exibida como **14,7 dias simulados**.

**Dias acumulados das pendências no dia 30:** `[29, 27, 25, 24, 23, 22, 19, 18, 17]`; soma `204`; média `204/9 = 22,666...`, exibida como **22,7 dias simulados**. Essa média **não é** tempo de conclusão nem tempo prometido de atendimento.

## Leitura dos resultados

O conjunto fictício demonstra todas as categorias na mesma proporção, porém a maioria das solicitações permanece pendente. Em um cenário ilustrativo, isso ajuda a argumentar que um painel de acompanhamento fornece transparência e permite olhar além do volume bruto de novos registros. Como não existe coleta real, a análise **não retrata nenhuma comunidade de fato**.
