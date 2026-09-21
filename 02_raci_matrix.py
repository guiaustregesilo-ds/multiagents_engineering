"""

Papéis de Agentes e Modelagem de Responsabilidade
Matriz RACI adaptada para agents

Cenário:
Sistema de Atendimento Inteligente - SAI
Demonstra como modelar responsabilidades com Matriz RACI,
Detectar inconsistência e visualizar a distribuição.

R = Responsible ( Quem FAZ a tarefa )
A = Accountable ( Quem RESPONDE pelo resultado )
C = Consulted ( Quem é CONSULTADO antes da decisão )
I = Informed ( Quem é INFORMADO depois da execução )

Execution = python 02_raci_matrix.py

"""

## ---------------------------
# 00. IMPORTS
## ---------------------------

from enum   import Enum
from typing import Optional

from pydantic     import BaseModel, Field, model_validator
from rich.console import Console
from rich.panel   import Panel
from rich.table   import Table
from rich.text    import Text

console = Console()

## ---------------------------
# 1. MODELS
## ---------------------------

class RACI(str, Enum):
    R = "R"  # Responsible — faz a tarefa
    A = "A"  # Accountable — responde pelo resultado
    C = "C"  # Consulted — consultado antes
    I = "I"  # Informed — informado depois


class AtividadeRACI(BaseModel):
    """Uma atividade com atribuições RACI por agente."""
    atividade: str
    atribuições: dict[str, RACI] = Field(
        description="Mapa agente → papel RACI"
    )

    @model_validator(mode="after")
    def validar_raci(self):
        roles = list(self.atribuições.values())

        # Regra 1: Toda atividade DEVE ter exatamente 1 Accountable
        accountables = [a for a, r in self.atribuições.items() if r == RACI.A]
        if len(accountables) == 0:
            raise ValueError(
                f"Atividade '{self.atividade}': nenhum Accountable definido. "
                "Quem responde se der errado?"
            )
        if len(accountables) > 1:
            raise ValueError(
                f"Atividade '{self.atividade}': {len(accountables)} Accountables "
                f"({', '.join(accountables)}). Só pode ter 1."
            )

        # Regra 2: Toda atividade DEVE ter pelo menos 1 Responsible
        responsibles = [a for a, r in self.atribuições.items() if r == RACI.R]
        if len(responsibles) == 0:
            raise ValueError(
                f"Atividade '{self.atividade}': nenhum Responsible. "
                "Quem faz o trabalho?"
            )

        return self


class MatrizRACI(BaseModel):
    """Matriz RACI completa de um sistema multi-agente."""
    nome_sistema: str
    agentes: list[str]
    atividades: list[AtividadeRACI]

    def diagnosticar(self) -> list[str]:
        """Analisa a matriz e retorna lista de avisos."""
        avisos = []

        # Análise por agente
        for agente in self.agentes:
            roles_agente = []
            for ativ in self.atividades:
                if agente in ativ.atribuições:
                    roles_agente.append((ativ.atividade, ativ.atribuições[agente]))

            # Aviso: agente sem nenhuma atribuição
            if not roles_agente:
                avisos.append(
                    f"⚠️  '{agente}' não tem nenhuma atribuição. Agente desnecessário?"
                )

            # Aviso: agente é R em muitas atividades (sobrecarga)
            responsabilidades = [a for a, r in roles_agente if r == RACI.R]
            if len(responsabilidades) > 3:
                avisos.append(
                    f"⚠️  '{agente}' é Responsible em {len(responsabilidades)} atividades. "
                    "Risco de sobrecarga — considere dividir."
                )

            # Aviso: agente é R mas nunca é C ou I (isolado)
            consultado_ou_informado = [
                a for a, r in roles_agente if r in (RACI.C, RACI.I)
            ]
            if responsabilidades and not consultado_ou_informado:
                avisos.append(
                    f"💡 '{agente}' executa mas nunca é consultado/informado "
                    "em outras atividades. Possível silo de informação."
                )

        # Análise por atividade
        for ativ in self.atividades:
            envolvidos = len(ativ.atribuições)
            if envolvidos > 4:
                avisos.append(
                    f"⚠️  Atividade '{ativ.atividade}': {envolvidos} agentes envolvidos. "
                    "Coordenação excessiva?"
                )

        return avisos


# ============================================================
# 2. CENÁRIO SAI — Matriz RACI do atendimento
# ============================================================

def criar_matriz_sai() -> MatrizRACI:
    """Cria a Matriz RACI do Sistema de Atendimento Inteligente."""

    agentes = [
        "Triador",
        "Esp. Técnico",
        "Esp. Comercial",
        "Redator",
        "Supervisor",
    ]

    atividades = [
        AtividadeRACI(
            atividade="Classificar ticket",
            atribuições={
                "Triador": RACI.R,
                "Supervisor": RACI.A,
            },
        ),
        AtividadeRACI(
            atividade="Diagnosticar problema técnico",
            atribuições={
                "Esp. Técnico": RACI.R,
                "Triador": RACI.C,
                "Supervisor": RACI.A,
                "Redator": RACI.I,
            },
        ),
        AtividadeRACI(
            atividade="Resolver questão comercial",
            atribuições={
                "Esp. Comercial": RACI.R,
                "Triador": RACI.C,
                "Supervisor": RACI.A,
                "Redator": RACI.I,
            },
        ),
        AtividadeRACI(
            atividade="Redigir resposta ao cliente",
            atribuições={
                "Redator": RACI.R,
                "Supervisor": RACI.A,
                "Esp. Técnico": RACI.C,
            },
        ),
        AtividadeRACI(
            atividade="Escalonar para humano",
            atribuições={
                "Supervisor": RACI.R,
                "Triador": RACI.I,
                "Redator": RACI.I,
                "Esp. Técnico": RACI.A,  # Propositalmente errado para demo
            },
        ),
        AtividadeRACI(
            atividade="Monitorar SLA",
            atribuições={
                "Supervisor": RACI.A,
                "Triador": RACI.R,     # Triador reporta métricas de tempo
            },
        ),
    ]

    return MatrizRACI(
        nome_sistema="Sistema de Atendimento Inteligente (SAI)",
        agentes=agentes,
        atividades=atividades,
    )


# ============================================================
# 3. VISUALIZAÇÃO
# ============================================================

def exibir_matriz(matriz: MatrizRACI) -> None:
    """Exibe a Matriz RACI como tabela rica."""
    table = Table(
        title=f"📊 Matriz RACI — {matriz.nome_sistema}",
        show_lines=True,
    )
    table.add_column("Atividade", style="bold white", width=30)

    for agente in matriz.agentes:
        table.add_column(agente, justify="center", width=14)

    cor_raci = {
        RACI.R: "bold green",
        RACI.A: "bold red",
        RACI.C: "yellow",
        RACI.I: "dim",
    }

    for ativ in matriz.atividades:
        row = [ativ.atividade]
        for agente in matriz.agentes:
            if agente in ativ.atribuições:
                raci = ativ.atribuições[agente]
                row.append(Text(raci.value, style=cor_raci[raci]))
            else:
                row.append(Text("—", style="dim"))
        table.add_row(*row)

    # Legenda
    table.add_section()
    table.add_row(
        "[dim]Legenda[/dim]",
        *[Text("") for _ in matriz.agentes],
    )

    console.print(table)
    console.print(
        "[dim]R = Responsible (faz) | A = Accountable (responde) | "
        "C = Consulted (antes) | I = Informed (depois)[/dim]\n"
    )


def exibir_diagnóstico(matriz: MatrizRACI) -> None:
    """Executa e exibe o diagnóstico da matriz."""
    avisos = matriz.diagnosticar()

    if avisos:
        console.print(Panel(
            "\n".join(avisos),
            title="[bold yellow]🔍 Diagnóstico da Matriz RACI[/bold yellow]",
            border_style="yellow",
            padding=(1, 2),
        ))
    else:
        console.print(Panel(
            "[green]Nenhum aviso. Matriz está consistente.[/green]",
            title="[bold green]✓ Diagnóstico OK[/bold green]",
            border_style="green",
        ))


def demo_validação_falha():
    """Demonstra validações que falham."""
    console.print("\n[bold red]═══ Demonstração: Violações RACI ═══[/bold red]\n")

    # Sem Accountable
    console.print("[yellow]Teste 1:[/yellow] Atividade sem Accountable...")
    try:
        AtividadeRACI(
            atividade="Responder ticket VIP",
            atribuições={
                "Redator": RACI.R,
                "Supervisor": RACI.A,
                "Triador": RACI.I,
            },
        )
    except Exception as e:
        console.print(f"  [red]✗ REJEITADO:[/red] {e}\n")

    # Dois Accountables
    console.print("[yellow]Teste 2:[/yellow] Atividade com 2 Accountables...")
    try:
        AtividadeRACI(
            atividade="Aprovar desconto",
            atribuições={
                "Esp. Comercial": RACI.A,
                "Redator": RACI.R,
            },
        )
    except Exception as e:
        console.print(f"  [red]✗ REJEITADO:[/red] {e}\n")

    # Sem Responsible
    console.print("[yellow]Teste 3:[/yellow] Atividade sem Responsible...")
    try:
        AtividadeRACI(
            atividade="Gerar relatório mensal",
            atribuições={
                "Supervisor": RACI.A,
                "Redator" : RACI.R,
                "Triador": RACI.I,
            },
        )
    except Exception as e:
        console.print(f"  [red]✗ REJEITADO:[/red] {e}\n")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    console.print(Panel(
        "[bold]aula2 — Matriz RACI para Sistemas Multi-Agente[/bold]\n"
        "Cenário: Sistema de Atendimento Inteligente (SAI)\n"
        "Arquivo: 02_raci_matrix.py",
        border_style="cyan",
    ))

    # Criar e exibir a matriz
    matriz = criar_matriz_sai()
    exibir_matriz(matriz)

    # Diagnóstico automático
    exibir_diagnóstico(matriz)

    # Demonstrar validações
    demo_validação_falha()

    console.print("[dim]Regra: 1 Accountable por atividade. Sempre. Sem exceção.[/dim]")