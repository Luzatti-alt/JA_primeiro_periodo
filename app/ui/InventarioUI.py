#region base projeto
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap
from datetime import date #alertar conforme a data
from PySide6.QtWidgets import *
import sys
from pathlib import Path
# Adiciona o diretório raiz do projeto ao path e permite usar partes/modulos dcleare outras pastas do projeto
if getattr(sys, 'frozen', False):
    root = Path(sys._MEIPASS)
else:
    root = Path(__file__).parent.parent

sys.path.insert(0, str(root))
from data.Inventario import Inventario,InventarioFuncionalidade,Itens, Contas, GerenciadorTemporal #criar init.py para reconhecer modulo
#temp
from data.Inventario import session

def resource_path(relative_path):
    base = getattr(sys, '_MEIPASS', Path(__file__).parent.parent)
    return str(Path(base) / relative_path)
#endregion base projeto

class InventarioUi(QWidget):
    PAGESIZE = 30

    def __init__(self,Historico, Reverter, Gerenciar,Dashboard):
        super().__init__()

        #optimização da query e melhoria da experiencia do usuario
        self.Offset = 0          # quantos itens já carregados
        self.Total = 0           # total no banco
        self.Carregando = False  # evita chamadas duplicadas
        self.filtroAtivo = ""   # guarda pesquisa atual

        #topo ui
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
        TopoLayout.addWidget(AddItem)
        TopoLayout.addWidget(RemItem)
        TopoLayout.addWidget(EditItem)
        TopoLayout.addWidget(ReverterBotao)
        TopoLayout.addWidget(BtnHistorico)
        TopoLayout.addWidget(BtnDashboard)

        #inventario na ui

        InvTopoLay = QVBoxLayout()
        # Inventario no topo
        FundoTopo = QWidget()
        FundoTopo.setStyleSheet("background-color: #005B8C; color: #ffffff;")
        FundoTopo.setAutoFillBackground(True)
        InventarioTopoLayout = QHBoxLayout(FundoTopo)
        InventarioTopoLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        InventarioTopoLayout.setContentsMargins(8, 4, 8, 4)
        InventarioTopoLayout.addSpacing(10)

        #tentativa de alinhar texto e img com o texto do topo
        COL_IMG    = 60
        COL_IDENT  = 80
        COL_ID     = 30
        COL_DONO   = 120
        COL_COD    = 80
        COL_USOS   = 140
        COL_DEVO   = 100
        COL_DESC   = 80
        COL_CB     = 60
        def HeaderLabel(Text, Width):
            Lbl = QLabel(Text)
            Lbl.setFixedWidth(Width)
            Lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            return Lbl
        InventarioTopoLayout.addWidget(HeaderLabel("", COL_IMG))           # espaço da imagem
        InventarioTopoLayout.addWidget(HeaderLabel("Identificação", COL_IDENT))
        InventarioTopoLayout.addWidget(HeaderLabel("ID",          COL_ID))#conversao necessaria int -> str
        InventarioTopoLayout.addWidget(HeaderLabel("Dono",          COL_DONO))
        InventarioTopoLayout.addWidget(HeaderLabel("Código único",  COL_COD))
        InventarioTopoLayout.addWidget(HeaderLabel("Usos",          COL_USOS))
        InventarioTopoLayout.addWidget(HeaderLabel("Devolução",     COL_DEVO))
        InventarioTopoLayout.addWidget(HeaderLabel("Validade",      COL_DESC))
        InventarioTopoLayout.addWidget(HeaderLabel("Descartado",    COL_CB))
        InvTopoLay.addWidget(FundoTopo)

        InventarioBaseLayout = QVBoxLayout()
        #iterando esse Layout para cada item no db
        ItemContainer = QWidget()
        ItemLinhaLayout = QHBoxLayout(ItemContainer)
        InventarioCentroLayout = QHBoxLayout()
        IdentificacaoLayout = QVBoxLayout()

        self.ScrollContent = QWidget()
        self.ScrollArea = QScrollArea()
        self.ScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.ScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.ScrollArea.setWidgetResizable(True)
        self.ScrollArea.setFixedHeight(5 * 80)  # ~ 5 linhas
        self.ListaItensLayout = QVBoxLayout(self.ScrollContent)
        self.ListaItensLayout.setSpacing(10)
        self.ListaItensLayout.setContentsMargins(0, 0, 0, 0)
        self.ListaItensLayout.addStretch()
        self.ScrollContent.setLayout(self.ListaItensLayout)
        self.ScrollArea.setWidget(self.ScrollContent)
        # detectar scroll chegando ao fim → carregar mais itens
        self.ScrollArea.verticalScrollBar().valueChanged.connect(self.OnScroll)
        #barra de pesquisa
        PesquisaLayout = QHBoxLayout()
        InputPesquisa = QLineEdit()
        PesquisaLayout.addWidget(InputPesquisa)
        PesquisarBotao = QPushButton("pesquisar")
        PesquisarBotao.clicked.connect(lambda: self.AtualizarListaFiltrado(InputPesquisa.text()))#pesquisar e recarregar
        PesquisaLayout.addWidget(PesquisarBotao)
        #stylesheet nos Layout
        #add Layout na tela
        InventarioBaseLayout.addLayout(InvTopoLay)
        InventarioBaseLayout.addLayout(PesquisaLayout)
        InventarioBaseLayout.addWidget(self.ScrollArea)
        InventarioBaseLayout.addWidget(ItemContainer)
        InventarioCentroLayout.addLayout(IdentificacaoLayout)
        BaseLayout = QVBoxLayout()
        BaseLayout.addLayout(TopoLayout)
        BaseLayout.addLayout(InventarioBaseLayout)
        self.setLayout(BaseLayout)
        #garantir atualizar a lista
        self.AtualizarListaItens()

    def AlertasVencimento(self):
        alertas = GerenciadorTemporal().ConferirValDev()
        atrasados = [a for a in alertas if a[1] == "atrasado"]
        if atrasados:
            QMessageBox.warning(self, "Atenção", f"{len(atrasados)} item(s) com devolução atrasada!")

    def AtualizarListaItens(self):
        """Reseta a lista e carrega a primeira página (60 itens)."""
        self.filtroAtivo = ""
        self.Offset = 0
        self.Total = InventarioFuncionalidade().TotalItens()
        self.Carregando = False

        self.setUpdatesEnabled(False)

        # limpa widgets existentes mantendo o stretch no final
        while self.ListaItensLayout.count():
            Item = self.ListaItensLayout.takeAt(0)
            if Item.widget():
                Item.widget().deleteLater()

        self.CarregarPagina()
        self.ListaItensLayout.addStretch()
        self.setUpdatesEnabled(True)

    def CarregarPagina(self):
        """Carrega mais PAGESIZE itens a partir do offset atual."""
        if self.Carregando:
            return
        if self.filtroAtivo:
            return  # pesquisa já carregou tudo
        if self.Offset >= self.Total:
            return  # não há mais itens

        self.Carregando = True

        # remove o stretch antes de adicionar novos widgets
        Ultimo = self.ListaItensLayout.itemAt(self.ListaItensLayout.count() - 1)
        if Ultimo and Ultimo.spacerItem():
            self.ListaItensLayout.removeItem(Ultimo)

        Novos = InventarioFuncionalidade().ItensPaginados(
            offset=self.Offset,
            limit=self.PAGESIZE
        )
        for Item in Novos:
            Linha = self.CriarLinhaItem(Item)
            Linha.setFixedHeight(78)
            self.ListaItensLayout.addWidget(Linha)

        self.Offset += len(Novos)
        self.ListaItensLayout.addStretch()
        self.Carregando = False

    def OnScroll(self, Valor):
        """Dispara carregamento quando scroll chega perto do fim."""
        Barra = self.ScrollArea.verticalScrollBar()
        if Valor >= Barra.maximum() - 50:
            # usa QTimer para não bloquear o evento de scroll
            QTimer.singleShot(0, self.CarregarPagina)

    def AtualizarListaFiltrado(self, Filtro):
        """Pesquisa: carrega todos os resultados filtrados de uma vez."""
        while self.ListaItensLayout.count():
            Item = self.ListaItensLayout.takeAt(0)
            if Item.widget():
                Item.widget().deleteLater()

        self.filtroAtivo = Filtro

        if Filtro:
            DbItens = InventarioFuncionalidade().pesquisar(Filtro)
        else:
            # sem filtro: volta para lazy loading normal
            self.filtroAtivo = ""
            self.Offset = 0
            self.Total = InventarioFuncionalidade().TotalItens()
            DbItens = InventarioFuncionalidade().ItensPaginados(offset=0, limit=self.PAGESIZE)
            self.Offset = len(DbItens)

        for Item in DbItens:
            Linha = self.CriarLinhaItem(Item)
            Linha.setFixedHeight(78)
            self.ListaItensLayout.addWidget(Linha)

        self.ListaItensLayout.addStretch()

    def CriarLinhaItem(self, Item) -> QWidget:
        COL_IMG    = 60
        COL_IDENT  = 80
        COL_ID     = 30
        COL_DONO   = 120
        COL_COD    = 80
        COL_USOS   = 140
        COL_DEVO   = 100
        COL_DESC   = 80
        COL_CB     = 60
        ItemContainer = QWidget()
        ItemContainer.setStyleSheet("background-color: #D9D9D9; color: #000000;")
        Layout = QHBoxLayout(ItemContainer)
        Layout.setContentsMargins(8, 4, 8, 4)
        Layout.setSpacing(0)

        # imagem
        ImgLabel = QLabel()
        ImgLabel.setPixmap(QPixmap(resource_path('app/ui/imgs/capacete-icon.png')))
        ImgLabel.setScaledContents(True)
        ImgLabel.setFixedSize(48, 60)
        ImgLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ColImgWidget = QWidget()
        ColImgWidget.setFixedWidth(COL_IMG)
        ColImgLay = QHBoxLayout(ColImgWidget)
        ColImgLay.setContentsMargins(0,0,0,0)
        ColImgLay.addWidget(ImgLabel, alignment=Qt.AlignmentFlag.AlignCenter)
        Layout.addWidget(ColImgWidget)

        # identificação
        Ident = QWidget()
        Ident.setFixedWidth(COL_IDENT)
        IdentLay = QVBoxLayout(Ident)
        IdentLay.setContentsMargins(0,0,0,0)
        IdentLay.setSpacing(2)
        IdentLay.addWidget(QLabel(Item.TipoEpi))
        IdentLay.addWidget(QLabel(f"CA: {Item.Ca}"))
        IdentLay.addWidget(QLabel(f"Cód: {Item.CodUnico}"))
        Layout.addWidget(Ident)

        # colunas simples
        def Col(Text, Width, Align=Qt.AlignmentFlag.AlignCenter):
            Lbl = QLabel(Text)
            Lbl.setFixedWidth(Width)
            Lbl.setAlignment(Align)
            Lbl.setWordWrap(True)
            return Lbl

        Layout.addWidget(Col(str(Item.id), COL_ID))#conversao necessaria int -> str
        Layout.addWidget(Col(Item.Dono, COL_DONO))
        Layout.addWidget(Col(Item.CodUnico, COL_COD))
        Layout.addWidget(Col(Item.Usosformatado, COL_USOS))
        Layout.addWidget(Col(Item.DataDevolucao, COL_DEVO))
        Layout.addWidget(Col(Item.DataDescarte, COL_DESC))

        # checkbox centralizado
        CbContainer = QWidget()
        CbContainer.setFixedWidth(COL_CB)
        CbLay = QHBoxLayout(CbContainer)
        CbLay.setContentsMargins(0,0,0,0)
        Cb = QCheckBox()
        Cb.setChecked(Item.Descartado or False)
        Cb.clicked.connect(lambda Checked, Id=Item.id: InventarioFuncionalidade().descartearItem(Id, Checked))
        CbLay.addWidget(Cb, alignment=Qt.AlignmentFlag.AlignCenter)
        Layout.addWidget(CbContainer)

        #gerenciar conforme data
        try:
            devolucao = date.fromisoformat(Item.DataDevolucao)
            dias = (devolucao - date.today()).days
            if dias < 0:
                ItemContainer.setStyleSheet("background-color: #8B0000; color: #ffffff;")  # vermelho
            elif dias <= 7:
                ItemContainer.setStyleSheet("background-color: #8B6000; color: #ffffff;")  # amarelo
        except (ValueError, TypeError):
            pass

        return ItemContainer
#endregion main ui