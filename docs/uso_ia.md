# Registro de utilização de Inteligência Artificial

**Global Solution 2026.2 · Neighborhood Action Dashboard**

## Como a IA foi utilizada

Foi utilizada IA generativa como ferramenta de **apoio ao planejamento e desenvolvimento da solução**, incluindo organização dos requisitos do enunciado, estruturação do código introdutório em Python, elaboração de dados fictícios, elaboração/revisão da documentação e **desenvolvimento e execução de testes funcionais**.

A IA auxiliou na revisão de rotinas de cadastro, validação, busca, atualização de situações, manutenção de histórico e cálculo dos indicadores, além de sugerir cenários de erro e casos de teste para conferir o comportamento esperado.

Não foi utilizada IA como componente de execução do sistema: a aplicação final opera apenas com Python e dados CSV locais, sem chamadas a modelos de IA, APIs ou serviços externos.

## Como os resultados foram verificados

No ambiente de desenvolvimento foram executados os **20 testes automatizados**, utilizando `unittest` da biblioteca padrão do Python, todos aprovados. Também foi executado o comando `python src/sistema.py --resumo`, conferindo 12 registros válidos, 1 inválido rejeitado, os valores das matrizes, percentuais e tempos médios.

## Limitações e responsabilidades

Os dados foram criados para demonstração, sem representar fatos ou pessoas reais. As sugestões da IA foram avaliadas criticamente; O projeto é educacional e não se conecta a canais de atendimento público.
