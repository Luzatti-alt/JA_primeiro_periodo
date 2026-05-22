#region base projeto
import sys
from pathlib import Path
from datetime import date

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QFrame, QScrollArea, QSizePolicy,
    QComboBox,
)

# matplotlib embutido no Qt
import matplotlib
matplotlib.use("QtAgg")  # backend Qt6
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

if getattr(sys, 'frozen', False):
    root = Path(sys._MEIPASS)
else:
    root = Path(__file__).parent.parent

sys.path.insert(0, str(root))
from data.Inventario import Contas, InventarioFuncionalidade
#endregion base projeto


CORES = {
    "bg":       "#1e1e2e",
    "surface":  "#2a2a3e",
    "borda":    "#3a3a5e",
    "primaria": "#7c6af7",
    "ok":       "#50fa7b",
    "alerta":   "#ffb86c",
    "perigo":   "#ff5555",
    "texto":    "#cdd6f4",
    "subtexto": "#6c7086",
}

# estilo geral de matplotlib alinhado com a paleta
plt.rcParams.update({
    "figure.facecolor":  CORES["surface"],
    "axes.facecolor":    CORES["surface"],
    "axes.edgecolor":    CORES["borda"],
    "axes.labelcolor":   CORES["texto"],
    "xtick.color":       CORES["subtexto"],
    "ytick.color":       CORES["subtexto"],
    "text.color":        CORES["texto"],
    "grid.color":        CORES["borda"],
    "grid.alpha":        0.4,
    "font.size":         9,
})

PALETA_GRAF = [
    CORES["primaria"], CORES["ok"], CORES["alerta"],
    CORES["perigo"], "#8be9fd", "#bd93f9", "#ff79c6",
]


class CartaoKPI(QFrame):
    """Cartão numérico simples para exibir um KPI."""
    def __init__(self, titulo: str, valor: str = "—", cor_valor: str = CORES["primaria"]):
        super().__init__()
        self.setStyleSheet(f"""
            QFrame {{
                background: {CORES['surface']};
                border: 1px solid {CORES['borda']};
                border-radius: 10px;
                padding: 8px;
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setSpacing(4)

        self._lbl_titulo = QLabel(titulo)
        self._lbl_titulo.setStyleSheet(f"color: {CORES['subtexto']}; font-size: 11px;")
        self._lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._lbl_valor = QLabel(valor)
        self._lbl_valor.setStyleSheet(
            f"color: {cor_valor}; font-size: 26px; font-weight: bold;"
        )
        self._lbl_valor.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self._lbl_titulo)
        layout.addWidget(self._lbl_valor)

    def atualizar(self, valor: str):
        self._lbl_valor.setText(valor)


class GraficoCanvas(FigureCanvas):
    #Canvas matplotlib reutilizável
    def __init__(self, largura=4, altura=3, dpi=90):
        self.fig = Figure(figsize=(largura, altura), dpi=dpi, tight_layout=True)
        super().__init__(self.fig)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)


class Dashboard(QWidget):
    """
    Contém os diferentes painéis de dashboard.
    Cada método *constrói e retorna* um QWidget pronto.
    """

    def __init__(self, inv_func: InventarioFuncionalidade):
        super().__init__()
        self.inv = inv_func

    # ── Geral ─────────────────────────────────────────────────────────────────
    def DashGeral(self) -> QWidget:
        """Visão geral: KPIs + gráfico de pizza por tipo + barras por dono."""
        dados = self.inv.DadosDashboard()

        container = QWidget()
        v = QVBoxLayout(container)
        v.setSpacing(12)

        # KPIs
        kpi_row = QHBoxLayout()
        self._kpi_ativos     = CartaoKPI("EPIs Ativos",     str(dados["total_ativos"]),     CORES["ok"])
        self._kpi_desc       = CartaoKPI("Descartados",     str(dados["total_descartados"]), CORES["alerta"])
        self._kpi_atrasos    = CartaoKPI("Atrasos",         str(sum(1 for _, s, _ in dados["atrasos"] if s == "atrasado")), CORES["perigo"])
        self._kpi_proximos   = CartaoKPI("Próx. devolução", str(sum(1 for _, s, _ in dados["atrasos"] if s == "proximo")), CORES["alerta"])
        self._kpi_mes        = CartaoKPI("Entregas no mês", str(dados["entregas_mes"]),      CORES["primaria"])
        for kpi in (self._kpi_ativos, self._kpi_desc, self._kpi_atrasos,
                    self._kpi_proximos, self._kpi_mes):
            kpi_row.addWidget(kpi)
        v.addLayout(kpi_row)

        # linha de gráficos
        graf_row = QHBoxLayout()

        # pizza – distribuição por tipo
        canvas_pizza = GraficoCanvas(4, 3)
        ax = canvas_pizza.fig.add_subplot(111)
        if dados["por_tipo"]:
            labels = list(dados["por_tipo"].keys())
            sizes  = list(dados["por_tipo"].values())
            ax.pie(sizes, labels=labels, autopct="%1.0f%%",
                   colors=PALETA_GRAF[:len(labels)],
                   startangle=90, wedgeprops={"edgecolor": CORES["bg"], "linewidth": 1.5})
            ax.set_title("EPIs por Tipo", pad=8)
        else:
            ax.text(0.5, 0.5, "Sem dados", ha="center", va="center")
            ax.set_title("EPIs por Tipo")
        graf_row.addWidget(canvas_pizza)

        # barras – top donas
        canvas_bar = GraficoCanvas(5, 3)
        ax2 = canvas_bar.fig.add_subplot(111)
        if dados["por_dono"]:
            donos   = list(dados["por_dono"].keys())[:8]
            quant   = [dados["por_dono"][d] for d in donos]
            barras  = ax2.barh(donos, quant, color=CORES["primaria"], height=0.55)
            ax2.bar_label(barras, padding=4, color=CORES["texto"])
            ax2.set_xlabel("Quantidade")
            ax2.set_title("EPIs por Funcionário (top 8)")
            ax2.invert_yaxis()
            ax2.grid(axis="x")
        else:
            ax2.text(0.5, 0.5, "Sem dados", ha="center", va="center")
            ax2.set_title("EPIs por Funcionário")
        graf_row.addWidget(canvas_bar)

        v.addLayout(graf_row)

        # barras – histórico 30 dias
        canvas_hist = GraficoCanvas(9, 2.5)
        ax3 = canvas_hist.fig.add_subplot(111)
        if dados["historico_30dias"]:
            tipos  = list(dados["historico_30dias"].keys())
            counts = list(dados["historico_30dias"].values())
            bars   = ax3.bar(tipos, counts,
                             color=PALETA_GRAF[:len(tipos)],
                             width=0.5, edgecolor=CORES["bg"])
            ax3.bar_label(bars, padding=3, color=CORES["texto"])
            ax3.set_title("Alterações nos últimos 30 dias")
            ax3.grid(axis="y")
        else:
            ax3.text(0.5, 0.5, "Nenhuma alteração nos últimos 30 dias",
                     ha="center", va="center")
            ax3.set_title("Alterações nos últimos 30 dias")
        v.addWidget(canvas_hist)

        return container

    # ── Atrasos ───────────────────────────────────────────────────────────────
    def DashAtrasos(self) -> QWidget:
        """Lista apenas os itens com devolução atrasada."""
        dados = self.inv.DadosDashboard()
        atrasados = [(item, dias) for item, status, dias in dados["atrasos"]
                     if status == "atrasado"]

        container = QWidget()
        v = QVBoxLayout(container)
        v.setSpacing(8)

        titulo = QLabel(f"⚠  Devoluções Atrasadas  ({len(atrasados)} itens)")
        titulo.setStyleSheet(f"color:{CORES['perigo']}; font-size:14px; font-weight:bold;")
        v.addWidget(titulo)

        if not atrasados:
            ok = QLabel("✔  Nenhum atraso registrado.")
            ok.setStyleSheet(f"color:{CORES['ok']}; font-size:13px;")
            ok.setAlignment(Qt.AlignmentFlag.AlignCenter)
            v.addWidget(ok)
            return container

        # gráfico de barras horizontais – dias de atraso
        canvas = GraficoCanvas(8, max(3, len(atrasados) * 0.45))
        ax = canvas.fig.add_subplot(111)
        nomes = [f"{i.Dono} — {i.TipoEpi}" for i, _ in atrasados]
        dias  = [d for _, d in atrasados]
        bars  = ax.barh(nomes, dias, color=CORES["perigo"], height=0.55)
        ax.bar_label(bars, fmt="%d dias", padding=4, color=CORES["texto"])
        ax.set_xlabel("Dias de atraso")
        ax.set_title("Atraso por item")
        ax.invert_yaxis()
        ax.grid(axis="x")
        v.addWidget(canvas)

        return container

    def DashPessoal(self, dono: str) -> QWidget:
        #Dashboard individual do funcionário: EPIs ativos, atrasos, descartados."""
        dados = self.inv.DadosDashPessoal(dono)

        container = QWidget()
        v = QVBoxLayout(container)
        v.setSpacing(10)

        titulo = QLabel(f"👤  {dono}")
        titulo.setStyleSheet(f"color:{CORES['primaria']}; font-size:14px; font-weight:bold;")
        v.addWidget(titulo)

        # KPIs individuais
        kpi_row = QHBoxLayout()
        kpi_row.addWidget(CartaoKPI("EPIs Ativos",    str(len(dados["ativos"])),      CORES["ok"]))
        kpi_row.addWidget(CartaoKPI("Descartados",    str(len(dados["descartados"])),  CORES["alerta"]))
        kpi_row.addWidget(CartaoKPI("Em Atraso",      str(len(dados["atrasos"])),      CORES["perigo"]))
        kpi_row.addWidget(CartaoKPI("Dentro do prazo",str(len(dados["em_dia"])),       CORES["primaria"]))
        v.addLayout(kpi_row)

        if not dados["ativos"]:
            v.addWidget(QLabel("Nenhum EPI ativo para este funcionário."))
            return container

        # pizza – status dos EPIs
        canvas = GraficoCanvas(4, 3)
        ax = canvas.fig.add_subplot(111)
        categorias = ["Em dia", "Atrasados", "Descartados"]
        valores    = [len(dados["em_dia"]), len(dados["atrasos"]), len(dados["descartados"])]
        cores_pie  = [CORES["ok"], CORES["perigo"], CORES["alerta"]]
        nao_zero   = [(c, v, cor) for c, v, cor in zip(categorias, valores, cores_pie) if v > 0]
        if nao_zero:
            ax.pie([x[1] for x in nao_zero],
                   labels=[x[0] for x in nao_zero],
                   autopct="%1.0f%%",
                   colors=[x[2] for x in nao_zero],
                   startangle=90,
                   wedgeprops={"edgecolor": CORES["bg"], "linewidth": 1.5})
        ax.set_title(f"Status dos EPIs — {dono}")
        v.addWidget(canvas)

        return container



class DashBoardUi(QWidget):
    def __init__(self,ControleFuncionarios, Historico, Reverter, Gerenciar, Inventario,
                 inv_func: InventarioFuncionalidade = None):
        super().__init__()
        self.setStyleSheet(f"background:{CORES['bg']}; color:{CORES['texto']};")
        self._inv_func = InventarioFuncionalidade()
        self._dashboard = Dashboard(self._inv_func)
        self._painel_atual = None
        FundoTopo = QWidget()
        FundoTopo.setStyleSheet("background-color: #005B8C; color: #ffffff;")
        FundoTopo.setAutoFillBackground(True)
        TopoLayout = QHBoxLayout(FundoTopo)
        TopoLayout.setSpacing(6)

        TopoLayout = QHBoxLayout()
        AddItem = QPushButton("Adicionar do inventario")
        AddItem.clicked.connect(lambda: Gerenciar("add"))
        RemItem = QPushButton("Remover do inventario")
        RemItem.clicked.connect(lambda: Gerenciar("rem"))
        EditItem = QPushButton("Editar o inventario")
        EditItem.clicked.connect(lambda: Gerenciar("edit"))
        ReverterBotao = QPushButton("Reverter")
        ReverterBotao.clicked.connect(Reverter)
        BtnHistorico = QPushButton("Historico")
        BtnHistorico.clicked.connect(Historico)
        BtnDashboard = QPushButton("Dashboards")
        BtnDashboard.clicked.connect(Dashboard)
        BtnControleFuncionarios = QPushButton("ControleFuncionarios")
        BtnControleFuncionarios.clicked.connect(ControleFuncionarios)


        DashBoardTopoLayout = QHBoxLayout(FundoTopo)
        #DashBoardTopoLayout.setAlignment(Qt.AlignTopoLayout.addWidget(AddItem))
        TopoLayout.addWidget(RemItem)
        TopoLayout.addWidget(EditItem)
        TopoLayout.addWidget(ReverterBotao)
        TopoLayout.addWidget(BtnHistorico)
        TopoLayout.addWidget(BtnDashboard)
        TopoLayout.addWidget(BtnControleFuncionarios)
        TopoLayout.addStretch()

        # abas de dashboard
        #TopoLayout.addWidget(_btn("Geral",        lambda: self._trocar_dash("geral"),   CORES["ok"]))
        #TopoLayout.addWidget(_btn("Atrasos",      lambda: self._trocar_dash("atrasos"), CORES["perigo"]))

        # seletor de funcionário
        self._combo_pessoal = QComboBox()
        self._combo_pessoal.setStyleSheet(f"""
            QComboBox {{
                background:{CORES['surface']}; color:{CORES['texto']};
                border:1px solid {CORES['borda']}; border-radius:6px;
                padding:4px 8px; font-size:12px; min-width:140px;
            }}
            QComboBox QAbstractItemView {{
                background:{CORES['surface']}; color:{CORES['texto']};
                selection-background-color:{CORES['primaria']};
            }}
        """)
        self._combo_pessoal.addItem("Nenhum funcionario selecionado")
        self._carregar_donos()
        self._combo_pessoal.currentTextChanged.connect(self._on_pessoal)
        TopoLayout.addWidget(self._combo_pessoal)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        base = QVBoxLayout(self)
        base.setContentsMargins(10, 10, 10, 10)
        base.setSpacing(8)
        base.addLayout(TopoLayout)
        base.addWidget(self._scroll)

        # abre o dashboard geral por padrão
        self._trocar_dash("geral")

        # atualiza o combo de donos periodicamente (caso itens sejam adicionados)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._carregar_donos)
        self._timer.start(30_000)  # 30 s

    
    def _carregar_donos(self):
        donos_atuais = set()
        for i in range(1, self._combo_pessoal.count()):
            donos_atuais.add(self._combo_pessoal.itemText(i))

        lista = self._inv_func.RemListaFuncionarios()
        novos = {dono for _, dono in lista} - donos_atuais
        for dono in sorted(novos):
            self._combo_pessoal.addItem(dono)

    def _trocar_dash(self, tipo: str, dono: str = ""):
        if tipo == "geral":
            widget = self._dashboard.DashGeral()
        elif tipo == "atrasos":
            widget = self._dashboard.DashAtrasos()
        elif tipo == "Nenhum funcionario selecionado" and dono:
            widget = self._dashboard.DashPessoal(dono)
        else:
            return
        self._scroll.setWidget(widget)

    def _on_pessoal(self, texto: str):
        if texto and texto != "Nenhum funcionario selecionado":
            self._trocar_dash("Nenhum funcionario selecionado", texto)

    # atualização forçada (chamar após qualquer CRUD)
    def atualizar(self):
        #usa dados recentes do banco.
        self._inv_func._cache_itens = None
        widget = self._scroll.widget()
        if widget:
            # descobre qual aba está aberta pelo título do widget filho (se houver)
            self._trocar_dash("geral")   # padrão seguro