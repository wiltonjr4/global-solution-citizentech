# Decisões técnicas e lógica do protótipo

## Por que usar Python textual em vez de interface web?

O desafio da FIAP restringe a implementação aos fundamentos das fases 1–3. Uma interface textual permite demonstrar entrada, saída, condicionais e estruturas de dados sem frameworks, dependências, banco externo ou riscos de indisponibilidade da rede. Ela reduz a complexidade e torna as regras diretamente observáveis.

## Onde os dados ficam?

Os exemplos originais ficam em dois CSVs UTF-8 separados por `;`. A biblioteca padrão `csv` lê e escreve linhas como dicionários. O arquivo de ocorrências reserva campo de ID, bairro, categoria, descrição, localidade, dia de abertura, situação e, quando aplicável, dia de conclusão. O histórico contém ID, dia do evento, situação anterior, nova situação e observação. Não há coleta de dados pessoais.

Quando houver uma alteração válida, novos CSVs locais são gerados para salvar o estado. A restauração elimina somente estes arquivos locais e mantém a base original inalterada. Ao reiniciar, os dados simulados podem ser recuperados.

## Por que essas estruturas?

| Estrutura | Exemplo | Papel |
|---|---|---|
| Lista | `ocorrencias` | Entrada e percurso em ordem de registro |
| Fila | `fila` | Triagem FIFO das ocorrências abertas na ordem dos cadastros |
| Pilha | `pilha` | Histórico com consulta do evento mais recente primeiro (LIFO) |
| Dicionário | `indice["003"]` | Busca pontual pelo código |
| Dicionário de dicionários | `hierarquia[bairro][categoria]` | Agrupamento bairro → categoria → códigos |
| Matriz (lista de listas) | `matriz[linha][coluna]` | Cruzamento quantitativo categoria × situação |

A função `reorganizar()` recalcula estruturas auxiliares após cada cadastro ou mudança, suficiente para 12 registros simulados. Essa decisão privilegia correção e simplicidade em vez de otimizações inadequadas para o escopo.

## Decisões e condições

1. **Cadastro:** ID gerado automaticamente; todos os campos obrigatórios devem existir. `not campo_A or not campo_B` rejeita se algum estiver vazio. O ID `013`, embora inválido, não é reutilizado, preservando rastreabilidade da rejeição.
2. **Busca:** `indice.get(id)` retorna o registro, ou `None`; a interface informa claramente que o código não existe.
3. **Filtros:** `(not categoria or coincide_categoria) and (not status or coincide_status)` faz os dois critérios valerem em conjunto, aceitando entradas vazias como ausência de restrição.
4. **Transição:** só `aberta` → `em_analise` → `concluida`. A expressão com `or` entre os dois casos válidos rejeita outros movimentos. `concluida` precisa de um dia entre o último evento daquele código e o dia 30.
5. **Histórico:** uma atualização válida adiciona um evento; eventos anteriores permanecem. A importação confere se o encadeamento faz sentido; assim, dados corrompidos não são aceitos silenciosamente.
6. **Indicadores:** somente registros válidos entram em contagens e médias; laços e aritmética simples, sem algoritmos de aprendizado de máquina.

## Complexidade didática

A busca por identificador usa dicionário (acesso usualmente constante em condições normais), enquanto a criação de índices, agrupamentos e contagens percorre a lista (`n` registros). A matriz tem tamanho fixo de 4 linhas × 3 colunas. A reconstrução simples é apropriada ao pequeno conjunto simulado.

## Possíveis evoluções após a entrega

Validação de experiências com usuários, armazenamento em banco, autenticação, perfis, trilha de auditoria formal, medidas de segurança e interface acessível mais completa.
