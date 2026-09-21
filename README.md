# Multiagents — Papéis e Responsabilidades em Sistemas Multi-Agente

Exemplos práticos em Python sobre como modelar, validar e diagnosticar papéis e
responsabilidades em times de agentes de IA, usando um cenário único de
**Sistema de Atendimento Inteligente (SAI)** como fio condutor.

## Sobre

Este repositório reúne scripts de estudo que exploram dois problemas comuns no
design de sistemas multi-agente:

- **Quem é responsável por quê** — e o que acontece quando isso não está claro.
- **Quais padrões indicam um time de agentes mal desenhado** (papéis
  redundantes, agentes "faz-tudo", ferramentas duplicadas, over-engineering).

Cada script é executável de forma independente e imprime a análise diretamente
no terminal usando [`rich`](https://github.com/Textualize/rich).

## Estrutura

| Arquivo | Descrição |
|---|---|
| [`02_raci_matrix.py`](./02_raci_matrix.py) | Matriz RACI adaptada para agentes: modela `Responsible / Accountable / Consulted / Informed` por atividade, valida regras de consistência (ex: exatamente 1 Accountable por atividade) e gera um diagnóstico automático de riscos (sobrecarga, silos de informação, coordenação excessiva). |
| [`03_anti_patterns.py`](./03_anti_patterns.py) | Detector de anti-padrões em times de agentes: identifica papéis redundantes, agentes sobrecarregados, agentes sem ferramentas, ferramentas compartilhadas, over-engineering e inputs órfãos, comparando um time bem definido com um time problemático. |

## Requisitos

- Python 3.10+
- Dependências em [`requirements.txt`](./requirements.txt) (`pydantic`, `rich`)

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Como executar

```bash
python 02_raci_matrix.py
python 03_anti_patterns.py
```

## Conceitos abordados

- Modelagem de responsabilidades com **Matriz RACI** aplicada a agentes de IA
- Validação de invariantes de design com `pydantic` (`model_validator`)
- Detecção heurística de anti-padrões de arquitetura multi-agente
- Visualização de dados no terminal com `rich` (tabelas, painéis, texto estilizado)

## Licença

Distribuído sob a licença MIT. Veja [`LICENSE`](./LICENSE) para mais detalhes.
