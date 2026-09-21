"""
aula2 — Papéis de Agentes e Modelagem de Responsabilidades
Arquivo 03: Detector de Anti-Padrões

Cenário: Sistema de Atendimento Inteligente (SAI)
Demonstra como detectar anti-padrões comuns em times de agentes:
papéis redundantes, responsabilidades difusas, over-engineering.

Execução: python 03_anti_patterns.py
"""

# ============================================================
# 0. IMPORTS
# ============================================================

from enum import Enum

from pydantic import BaseModel, Field
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()


# ============================================================
# 1. MODELS
# ============================================================

class Severidade(str, Enum):
    CRÍTICO = "CRÍTICO"
    AVISO = "AVISO"
    DICA = "DICA"


class AntiPadrão(BaseModel):
    """Um anti-padrão detectado no time de agentes."""
    nome: str
    severidade: Severidade
    descrição: str
    agentes_afetados: list[str]
    recomendação: str


class PapelSimplificado(BaseModel):
    """Versão simplificada do papel para análise de anti-padrões."""
    nome: str
    descrição_curta: str
    responsabilidades: list[str]  # Lista de verbos/ações
    ferramentas: list[str]
    inputs: list[str]
    outputs: list[str]


# ============================================================
# 2. DETECTOR DE ANTI-PADRÕES
# ============================================================

def detectar_anti_padrões(papéis: list[PapelSimplificado]) -> list[AntiPadrão]:
    """Analisa uma lista de papéis e detecta anti-padrões."""
    problemas: list[AntiPadrão] = []

    # --- Anti-padrão 1: Redundância de papéis ---
    # Dois agentes com responsabilidades muito parecidas
    for i, p1 in enumerate(papéis):
        for p2 in papéis[i + 1:]:
            resp_comuns = set(p1.responsabilidades) & set(p2.responsabilidades)
            overlap = len(resp_comuns) / max(len(p1.responsabilidades), len(p2.responsabilidades), 1)
            if overlap >= 0.5:
                problemas.append(AntiPadrão(
                    nome="Papéis Redundantes",
                    severidade=Severidade.CRÍTICO,
                    descrição=(
                        f"'{p1.nome}' e '{p2.nome}' compartilham "
                        f"{len(resp_comuns)} responsabilidades ({overlap:.0%} de overlap). "
                        f"Responsabilidades em comum: {', '.join(resp_comuns)}"
                    ),
                    agentes_afetados=[p1.nome, p2.nome],
                    recomendação="Consolide em um único agente ou especialize as fronteiras.",
                ))

    # --- Anti-padrão 2: Agente faz-tudo ---
    # Agente com muitas responsabilidades
    for p in papéis:
        if len(p.responsabilidades) > 4:
            problemas.append(AntiPadrão(
                nome="Agente Faz-Tudo",
                severidade=Severidade.CRÍTICO,
                descrição=(
                    f"'{p.nome}' tem {len(p.responsabilidades)} responsabilidades. "
                    "Agentes com mais de 4 responsabilidades perdem foco e qualidade."
                ),
                agentes_afetados=[p.nome],
                recomendação="Divida em 2+ agentes especializados.",
            ))

    # --- Anti-padrão 3: Agente sem ferramentas ---
    for p in papéis:
        if not p.ferramentas:
            problemas.append(AntiPadrão(
                nome="Agente Desarmado",
                severidade=Severidade.AVISO,
                descrição=(
                    f"'{p.nome}' não tem ferramentas. "
                    "Se não precisa de ferramentas, provavelmente não precisa ser um agente."
                ),
                agentes_afetados=[p.nome],
                recomendação="Adicione ferramentas ou converta em um step de prompt simples.",
            ))

    # --- Anti-padrão 4: Ferramentas duplicadas ---
    tool_owners: dict[str, list[str]] = {}
    for p in papéis:
        for t in p.ferramentas:
            tool_owners.setdefault(t, []).append(p.nome)

    for tool, owners in tool_owners.items():
        if len(owners) > 1:
            problemas.append(AntiPadrão(
                nome="Ferramenta Compartilhada",
                severidade=Severidade.AVISO,
                descrição=(
                    f"Ferramenta '{tool}' é usada por {len(owners)} agentes: "
                    f"{', '.join(owners)}. Risco de conflito e acoplamento."
                ),
                agentes_afetados=owners,
                recomendação="Avalie se cada agente realmente precisa dessa ferramenta.",
            ))

    # --- Anti-padrão 5: Over-engineering ---
    if len(papéis) > 6:
        problemas.append(AntiPadrão(
            nome="Over-Engineering",
            severidade=Severidade.AVISO,
            descrição=(
                f"Time com {len(papéis)} agentes. "
                "Times grandes aumentam custo de coordenação e latência. "
                "Pergunte: 'um agente com boas ferramentas resolve?'"
            ),
            agentes_afetados=[p.nome for p in papéis],
            recomendação="Comece com 3-5 agentes. Adicione mais só quando necessário.",
        ))

    # --- Anti-padrão 6: Output não conecta com input ---
    todos_outputs = set()
    for p in papéis:
        todos_outputs.update(p.outputs)

    for p in papéis:
        for inp in p.inputs:
            # Verifica se algum outro agente produz esse input
            if inp not in todos_outputs and inp not in [
                "Texto do ticket do cliente",  # Inputs externos são OK
                "Dados do CRM",
                "Input externo",
            ]:
                problemas.append(AntiPadrão(
                    nome="Input Órfão",
                    severidade=Severidade.DICA,
                    descrição=(
                        f"'{p.nome}' espera input '{inp}' "
                        "mas nenhum outro agente produz esse output."
                    ),
                    agentes_afetados=[p.nome],
                    recomendação="Verifique se esse input vem de fonte externa ou está faltando um agente.",
                ))

    return problemas


# ============================================================
# 3. CENÁRIOS — Time bom vs time com problemas
# ============================================================

def time_sai_bem_definido() -> list[PapelSimplificado]:
    """Time SAI bem projetado."""
    return [
        PapelSimplificado(
            nome="Triador",
            descrição_curta="Classifica tickets por categoria e urgência.",
            responsabilidades=["classificar", "priorizar"],
            ferramentas=["ClassificadorTicket", "BuscaHistórico"],
            inputs=["Texto do ticket do cliente"],
            outputs=["categoria", "urgência", "resumo"],
        ),
        PapelSimplificado(
            nome="Especialista Técnico",
            descrição_curta="Resolve problemas técnicos com base de conhecimento.",
            responsabilidades=["diagnosticar", "resolver"],
            ferramentas=["BuscaDocumentação", "ConsultaLogs"],
            inputs=["categoria", "resumo"],
            outputs=["diagnóstico", "solução", "confidence"],
        ),
        PapelSimplificado(
            nome="Redator",
            descrição_curta="Transforma diagnósticos em respostas claras.",
            responsabilidades=["redigir", "formatar"],
            ferramentas=["TemplateRespostas"],
            inputs=["diagnóstico", "solução"],
            outputs=["resposta_final", "resumo_interno"],
        ),
        PapelSimplificado(
            nome="Supervisor",
            descrição_curta="Coordena o time e escalona casos críticos.",
            responsabilidades=["monitorar", "escalonar", "aprovar"],
            ferramentas=["PainelMétricas", "NotificaçãoHumano"],
            inputs=["confidence", "métricas"],
            outputs=["decisão", "relatório"],
        ),
    ]


def time_com_anti_padrões() -> list[PapelSimplificado]:
    """Time com anti-padrões propositais para demonstração."""
    return [
        PapelSimplificado(
            nome="Analisador Geral",
            descrição_curta="Faz triagem, análise e diagnóstico.",
            responsabilidades=[
                "classificar", "priorizar", "diagnosticar",
                "resolver", "escalonar",  # 5 responsabilidades = faz-tudo
            ],
            ferramentas=["ClassificadorTicket", "BuscaDocumentação", "ConsultaLogs"],
            inputs=["Texto do ticket do cliente"],
            outputs=["diagnóstico", "solução"],
        ),
        PapelSimplificado(
            nome="Diagnosticador",
            descrição_curta="Diagnostica problemas técnicos.",
            responsabilidades=["diagnosticar", "resolver"],  # Overlap com Analisador
            ferramentas=["BuscaDocumentação", "ConsultaLogs"],  # Ferramentas duplicadas
            inputs=["resumo_ticket"],
            outputs=["diagnóstico", "solução"],
        ),
        PapelSimplificado(
            nome="Respondedor",
            descrição_curta="Monta a resposta pro cliente.",
            responsabilidades=["redigir"],
            ferramentas=[],  # Sem ferramentas!
            inputs=["diagnóstico"],
            outputs=["resposta_final"],
        ),
        PapelSimplificado(
            nome="Logger",
            descrição_curta="Registra tudo que acontece.",
            responsabilidades=["logar"],
            ferramentas=[],  # Sem ferramentas — deveria ser um step, não um agente
            inputs=["eventos"],
            outputs=["log"],
        ),
    ]


# ============================================================
# 4. VISUALIZAÇÃO
# ============================================================

def exibir_resultado(
    nome_time: str,
    papéis: list[PapelSimplificado],
    problemas: list[AntiPadrão],
) -> None:
    """Exibe resultado da análise de anti-padrões."""

    # Tabela do time
    table = Table(title=f"👥 Time: {nome_time}", show_lines=True)
    table.add_column("Agente", style="bold", width=20)
    table.add_column("Responsabilidades", width=30)
    table.add_column("Tools", justify="center", width=8)
    table.add_column("Inputs", width=20)
    table.add_column("Outputs", width=20)

    for p in papéis:
        table.add_row(
            p.nome,
            ", ".join(p.responsabilidades),
            str(len(p.ferramentas)),
            ", ".join(p.inputs[:2]),
            ", ".join(p.outputs[:2]),
        )

    console.print(table)

    # Problemas encontrados
    if not problemas:
        console.print(Panel(
            "[green]✓ Nenhum anti-padrão detectado. Time bem definido.[/green]",
            border_style="green",
        ))
        return

    cor_sev = {
        Severidade.CRÍTICO: "red",
        Severidade.AVISO: "yellow",
        Severidade.DICA: "blue",
    }
    ícone_sev = {
        Severidade.CRÍTICO: "🔴",
        Severidade.AVISO: "🟡",
        Severidade.DICA: "🔵",
    }

    for prob in problemas:
        cor = cor_sev[prob.severidade]
        ícone = ícone_sev[prob.severidade]
        console.print(Panel(
            f"[{cor}]{prob.descrição}[/{cor}]\n\n"
            f"[bold]Agentes:[/bold] {', '.join(prob.agentes_afetados)}\n"
            f"[bold]Recomendação:[/bold] {prob.recomendação}",
            title=f"{ícone} [{cor}]{prob.severidade.value}: {prob.nome}[/{cor}]",
            border_style=cor,
            padding=(0, 2),
        ))

    # Resumo
    resumo = Table(title="📊 Resumo", show_lines=True)
    resumo.add_column("Severidade", width=12)
    resumo.add_column("Quantidade", justify="center", width=12)
    for sev in Severidade:
        count = len([p for p in problemas if p.severidade == sev])
        if count:
            cor = cor_sev[sev]
            resumo.add_row(
                Text(sev.value, style=cor),
                Text(str(count), style=f"bold {cor}"),
            )
    console.print(resumo)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    console.print(Panel(
        "[bold]aula2 — Detector de Anti-Padrões em Times de Agentes[/bold]\n"
        "Cenário: Sistema de Atendimento Inteligente (SAI)\n"
        "Arquivo: 03_anti_patterns.py",
        border_style="cyan",
    ))

    # Time 1: Bem definido
    console.print("\n[bold green]═══ Cenário 1: Time Bem Definido ═══[/bold green]\n")
    time_bom = time_sai_bem_definido()
    problemas_bom = detectar_anti_padrões(time_bom)
    exibir_resultado("SAI — Bem Definido", time_bom, problemas_bom)

    # Time 2: Com anti-padrões
    console.print("\n[bold red]═══ Cenário 2: Time Com Anti-Padrões ═══[/bold red]\n")
    time_ruim = time_com_anti_padrões()
    problemas_ruim = detectar_anti_padrões(time_ruim)
    exibir_resultado("SAI — Com Problemas", time_ruim, problemas_ruim)

    console.print(
        "\n[dim]Os mesmos padrões de detecção se aplicam a qualquer sistema multi-agente, "
        "não apenas atendimento.[/dim]"
    )
