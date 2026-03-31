#region base projeto
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor, QPalette, QIcon, QPixmap
from PySide6.QtWidgets import *
import sys
from pathlib import Path
# Adiciona o diretório raiz do projeto ao path e permite usar partes/modulos dcleare outras pastas do projeto
if getattr(sys, 'frozen', False):
    root = Path(sys._MEIPASS)
else:
    root = Path(__file__).parent.parent

sys.path.insert(0, str(root))
from data.Inventario import Inventario,InventarioFuncionalidade,Itens #criar init.py para reconhecer modulo
#configuração para compilar em executavel
def resource_path(relative_path):
    base = getattr(sys, '_MEIPASS', Path(__file__).parent.parent.parent)
    return str(Path(base) / relative_path)
#configurando base da gui
app = QApplication(sys.argv)
paleta = QPalette()
PaletaCores = {
    "fundo": "#002F48",
    "TopoInventario": "#080d3f",
    "botao": "#080d3f",
    "houver":"#0a1370",
    "ativo": "#2636e4",
    "texto": "#ffffff"
}
paleta.setColor(QPalette.ColorRole.Window, QColor(PaletaCores["fundo"]))
app.setPalette(paleta)
#stylesheet do app
app.setStyleSheet(f"""
                  QLabel{{
                  color: #ffffff;
                  }}
                  QPushButton {{
                  background-color: {PaletaCores['botao']};color: {PaletaCores['texto']
                  }}}
                  QCheckBox::indicator {{
                    width: 18px;
                    height: 18px;
                    border: 2px solid {PaletaCores['botao']};
                    border-radius: 3px;
                    background-color: {PaletaCores['botao']};
                    image: url({resource_path('app/ui/imgs/check-nao.png')});
                    }}
                  QCheckBox::indicator:checked {{
                    background-color: {PaletaCores['texto']};
                    border: 2px solid {PaletaCores['texto']};
                    image: url({resource_path('app/ui/imgs/check-ok.png')});
    }}
""")#trocar icon
Imagens = {
    "capacete": "imagens/capacete.png"
}
#endregion base projeto
#region gerenciador interfaces graficas
class GerenciadorJanelas(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("sistema de inventario")
        self.setWindowIcon(QIcon(resource_path("app/ui/imgs/ideia_de_logo_app_JA.png")))
        self.HistoricoNavegacao = []
        self.stacked = QStackedWidget()
        self.Inventario = InventarioUi(Voltar=self.Voltar, Historico=self.IrHistorico, Gerenciar=self.IrGerenciarInventario)
        self.Historico = HistoricoUi(Inventario=self.IrInventario, Gerenciar=self.IrGerenciarInventario)
        self.GerenciarInventario = GerenciadorInventario(Historico=self.IrHistorico, Inventario=self.IrInventario)
        self.stacked.addWidget(self.Inventario)
        self.stacked.addWidget(self.Historico)
        self.stacked.addWidget(self.GerenciarInventario)

        # definir Layout
        Layout = QVBoxLayout(self)
        Layout.setContentsMargins(0, 0, 0, 0)
        Layout.addWidget(self.stacked)

        # tela inicial
        self.stacked.setCurrentWidget(self.Inventario)
    def IrPara(self, Widget):
        TelaAtual = self.stacked.currentWidget()
        if TelaAtual != Widget:  # Só adiciona se for uma tela diferente
            self.HistoricoNavegacao.append(TelaAtual)
        self.stacked.setCurrentWidget(Widget)
    def IrHistorico(self):
        self.IrPara(self.Historico)
    def IrInventario(self):
        self.Inventario.AtualizarListaItens()#recarregar o db sempre
        self.IrPara(self.Inventario)
    def IrGerenciarInventario(self, Tipo):
        self.GerenciarInventario.AtualizarTipo(Tipo)
        self.IrPara(self.GerenciarInventario)
    def Voltar(self):
        # Volta para a última tela no histórico
        TelaAnterior = self.HistoricoNavegacao.pop()
        self.stacked.setCurrentWidget(TelaAnterior)
#endregion gerenciador interfaces graficas
#region main ui
class InventarioUi(QWidget):
    def __init__(self, Voltar, Historico, Gerenciar):
        super().__init__()
        #topo ui
        TopoLayout = QHBoxLayout()
        AddItem = QPushButton("Adicionar do inventario")
        AddItem.clicked.connect(lambda: Gerenciar("add"))
        RemItem = QPushButton("Remover do inventario")
        RemItem.clicked.connect(lambda: Gerenciar("rem"))
        EditItem = QPushButton("Editar o inventario")
        EditItem.clicked.connect(lambda: Gerenciar("edit"))
        HistoricoBotao = QPushButton("Historico")
        HistoricoBotao.clicked.connect(Historico)
        TopoLayout.addWidget(AddItem)
        TopoLayout.addWidget(RemItem)
        TopoLayout.addWidget(EditItem)
        TopoLayout.addWidget(HistoricoBotao)

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
        ScrollArea = QScrollArea()
        ScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        ScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        ScrollArea.setWidgetResizable(True)
        ScrollArea.setFixedHeight(5 * 80)  # ~ 5 linhas
        self.ListaItensLayout = QVBoxLayout(self.ScrollContent)
        self.ListaItensLayout.setSpacing(10)
        self.ListaItensLayout.setContentsMargins(0, 0, 0, 0)
        DbItens = InventarioFuncionalidade().ItensTotais()
        for Item in DbItens:
              Linha = self.CriarLinhaItem(Item)
              Linha.setFixedHeight(78)  # altura fixa por linha
              self.ListaItensLayout.addWidget(Linha)
        self.ListaItensLayout.addStretch()  # empurra itens pro topo
        self.ScrollContent.setLayout(self.ListaItensLayout)
        ScrollArea.setWidget(self.ScrollContent)
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
        InventarioBaseLayout.addWidget(ScrollArea)
        InventarioBaseLayout.addWidget(ItemContainer)
        InventarioCentroLayout.addLayout(IdentificacaoLayout)
        BaseLayout = QVBoxLayout()
        BaseLayout.addLayout(TopoLayout)
        BaseLayout.addLayout(InventarioBaseLayout)
        self.setLayout(BaseLayout)
        #garantir atualizar a lista
        self.AtualizarListaItens()

    def AtualizarListaItens(self):
        while self.ListaItensLayout.count():
            Item = self.ListaItensLayout.takeAt(0)
            if Item.widget():
                Item.widget().deleteLater()

        DbItens = InventarioFuncionalidade().ItensTotais()

        for Item in DbItens:
            Linha = self.CriarLinhaItem(Item)
            Linha.setFixedHeight(78)
            self.ListaItensLayout.addWidget(Linha)

        self.ListaItensLayout.addStretch()

    def AtualizarListaFiltrado(self, Filtro):
        while self.ListaItensLayout.count():
            Item = self.ListaItensLayout.takeAt(0)
            if Item.widget():
                Item.widget().deleteLater()
        if Filtro:
            DbItens = InventarioFuncionalidade().pesquisar(Filtro)
        else:
            DbItens = InventarioFuncionalidade().ItensTotais()

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
        Layout.addWidget(Col(Item.usos_formatado, COL_USOS))
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

        return ItemContainer
#endregion main ui
#region historico
class HistoricoUi(QWidget):
    def __init__(self, Inventario, Gerenciar):
        super().__init__()
        HistoricoBaseLayout = QVBoxLayout()
        VoltarBotao = QPushButton("Inventario")
        VoltarBotao.clicked.connect(Inventario)
        TopoLayout = QHBoxLayout()
        AddItem  = QPushButton("Adicionar do inventario")
        AddItem.clicked.connect(lambda: Gerenciar("add"))
        RemItem  = QPushButton("Remover do inventario")
        RemItem.clicked.connect(lambda: Gerenciar("rem"))
        EditItem = QPushButton("Editar o inventario")
        EditItem.clicked.connect(lambda: Gerenciar("edit"))
        TopoLayout.addWidget(VoltarBotao)
        TopoLayout.addWidget(AddItem)
        TopoLayout.addWidget(RemItem)
        TopoLayout.addWidget(EditItem)

        HisTopoLay = QVBoxLayout()
        FundoTopo = QWidget()
        FundoTopo.setStyleSheet("background-color: #005B8C; color: #ffffff;")
        FundoTopo.setAutoFillBackground(True)
        HistoricoTopoLayout = QHBoxLayout(FundoTopo)
        HistoricoTopoLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        HistoricoTopoLayout.setContentsMargins(8, 4, 8, 4)
        HistoricoTopoLayout.addSpacing(10)
        COL_IMG      = 60
        COL_IDENT    = 80
        COL_DONO     = 120
        COL_ATUAL    = 80
        COL_ANTERIOR = 100
        def HeaderLabel(Text, Width):
            Lbl = QLabel(Text)
            Lbl.setFixedWidth(Width)
            Lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            return Lbl
        HistoricoTopoLayout.addWidget(HeaderLabel("", COL_IMG))           # espaço da imagem
        HistoricoTopoLayout.addWidget(HeaderLabel("Identificação", COL_IDENT))
        HistoricoTopoLayout.addWidget(HeaderLabel("Dono",          COL_DONO))
        HistoricoTopoLayout.addWidget(HeaderLabel("versão anterior",     COL_ANTERIOR))
        HistoricoTopoLayout.addWidget(HeaderLabel("versão atual",  COL_ATUAL))
        HistoricoTopoLayout.addWidget(HeaderLabel("Reverter",  COL_ATUAL))
        HisTopoLay.addWidget(FundoTopo)

        self.ScrollContent = QWidget()
        ScrollArea = QScrollArea()
        ScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        ScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        ScrollArea.setWidgetResizable(True)
        ScrollArea.setFixedHeight(5 * 80)
        self.ListaItensLayout = QVBoxLayout(self.ScrollContent)
        self.ListaItensLayout.setSpacing(10)
        self.ListaItensLayout.setContentsMargins(0, 0, 0, 0)

        DbItens = InventarioFuncionalidade().ItensHistorico()
        for Item in DbItens:
            Linha = self.CriarLinhaItem(Item)
            Linha.setFixedHeight(78)
            self.ListaItensLayout.addWidget(Linha)
        self.ListaItensLayout.addStretch()
        self.ScrollContent.setLayout(self.ListaItensLayout)
        ScrollArea.setWidget(self.ScrollContent)
        HistoricoBaseLayout.addLayout(HisTopoLay)
        HistoricoBaseLayout.addWidget(ScrollArea)

        BaseLayout = QVBoxLayout()
        BaseLayout.addLayout(TopoLayout)
        BaseLayout.addLayout(HistoricoBaseLayout)
        self.setLayout(BaseLayout)

    def CriarLinhaItem(self, Item) -> QWidget:
        COL_ID       = 120
        COL_TIPO     = 120
        COL_ANTERIOR = 200
        COL_ATUAL    = 100
        COL_CB       = 80

        Container = QWidget()
        Container.setStyleSheet("background-color: #D9D9D9; color: #000000;")
        Layout = QHBoxLayout(Container)
        Layout.setContentsMargins(8, 4, 8, 4)
        Layout.setSpacing(8)

        def Col(Text, Width):
            Lbl = QLabel(str(Text) if Text else "—")
            Lbl.setFixedWidth(Width)
            Lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            Lbl.setWordWrap(True)
            return Lbl

        Layout.addWidget(Col(f"Item #{Item.IdItemAlterado}", COL_ID))
        Layout.addWidget(Col(Item.TiposAlteracao,             COL_TIPO))
        Layout.addWidget(Col(Item.VersaoAnterior,             COL_ANTERIOR))
        Layout.addWidget(Col(Item.VersaoAtual,                COL_ATUAL))

        # checkbox direto no Layout, não via Col()
        CbContainer = QWidget()
        CbContainer.setFixedWidth(COL_CB)
        CbLay = QHBoxLayout(CbContainer)
        CbLay.setContentsMargins(0, 0, 0, 0)
        Reverter = QCheckBox()
        #trocar para foi alterado
        Reverter.setChecked(Item.revertido or False)
        Reverter.clicked.connect(lambda Checked, Id=Item.id: InventarioFuncionalidade().ReverterItem(Id, Checked))
        CbLay.addWidget(Reverter, alignment=Qt.AlignmentFlag.AlignCenter)
        Layout.addWidget(CbContainer)

        return Container
#endregion historico
#region gerenciador de inventario
class GerenciadorInventario(QWidget):
    def __init__(self, Inventario, Historico):
        super().__init__()
        self.IrInventario = Inventario
        self.IrHistorico = Historico

        # botões fixos do topo
        self.InventarioBotao = QPushButton("Inventário")
        self.BtnAdd = QPushButton("Adicionar")
        self.BtnRem = QPushButton("Remover")
        self.BtnEdit = QPushButton("Editar")
        self.BtnHistorico = QPushButton("Historico")

        self.InventarioBotao.clicked.connect(self.IrInventario)
        self.BtnHistorico.clicked.connect(self.IrHistorico)
        self.BtnAdd.clicked.connect(lambda: self.AtualizarTipo("add"))
        self.BtnRem.clicked.connect(lambda: self.AtualizarTipo("rem"))
        self.BtnEdit.clicked.connect(lambda: self.AtualizarTipo("edit"))

        TopoLayout = QHBoxLayout()
        TopoLayout.addWidget(self.InventarioBotao)
        TopoLayout.addWidget(self.BtnAdd)
        TopoLayout.addWidget(self.BtnRem)
        TopoLayout.addWidget(self.BtnEdit)
        TopoLayout.addWidget(self.BtnHistorico)

        # área de conteúdo dinâmico
        self.Conteudo = QWidget()
        self.ConteudoLayout = QHBoxLayout(self.Conteudo)

        BaseLayout = QVBoxLayout()
        BaseLayout.addLayout(TopoLayout)
        BaseLayout.addWidget(self.Conteudo)
        self.setLayout(BaseLayout)

    #permitir a troca sem criar outras classes
    def _LimparConteudo(self):
        while self.ConteudoLayout.count():
            Item = self.ConteudoLayout.takeAt(0)
            if Item.widget():
                Item.widget().deleteLater()
            elif Item.layout():
                self._LimparLayout(Item.layout())

    def _LimparLayout(self, Layout):
        while Layout.count():
            Item = Layout.takeAt(0)
            if Item.widget():
                Item.widget().deleteLater()
            elif Item.layout():
                self._LimparLayout(Item.layout())

    def Add(self):
        self._LimparConteudo()

        Form = QWidget()
        FormLayout = QFormLayout(Form)
        FormLayout.setSpacing(10)

        self.InputCa = QLineEdit()
        self.InputTipo = QComboBox()#select do pyside
        self.InputTipo.addItems(["capacete","luva","cinto","bota", "alabarte", "manquito", "oculos", "protetor auricolar", "colete refletivo"])#array para cada item
        self.InputDono = QLineEdit()
        self.InputUsos = QLineEdit()
        self.InputDevolucao = QDateEdit()
        self.InputDevolucao.setCalendarPopup(True)
        self.InputDevolucao.setDate(QDate.currentDate())
        self.InputDescarte = QDateEdit()
        self.InputDescarte.setCalendarPopup(True)
        self.InputDescarte.setDate(QDate.currentDate())

        FormLayout.addRow("CA:", self.InputCa)
        FormLayout.addRow("Tipo de EPI:", self.InputTipo)
        FormLayout.addRow("Responsável:", self.InputDono)
        FormLayout.addRow("Usos:", self.InputUsos)
        FormLayout.addRow("Data devolução:", self.InputDevolucao)
        FormLayout.addRow("Data descarte:", self.InputDescarte)

        BtnConfirmar = QPushButton("Adicionar item")
        BtnConfirmar.clicked.connect(self.ConfirmarAdd)
        FormLayout.addRow(BtnConfirmar)

        self.ConteudoLayout.addWidget(Form)

        #data para descarte e devolução
    def ConfirmarAdd(self):
        DataDev = self.InputDevolucao.date().toPython()
        DataDesc = self.InputDescarte.date().toPython()

        InventarioFuncionalidade().AddItem(
            ca=self.InputCa.text(),
            tipo_epi=self.InputTipo.currentText(),
            dono=self.InputDono.text(),
            usos=self.InputUsos.text(),
            data_descarte=str(DataDesc),
            data_devolucao=str(DataDev)
        )
        self.IrInventario()

    def Rem(self):
        self._LimparConteudo()
        #"select de funcionario"
        self.ListaFuncionario = QComboBox() #itera de
        DbListaFuncionarios = InventarioFuncionalidade().RemListaFuncionarios()
        self.ListaFuncionario.addItems([f"ID: {Id} nome: {Nome} " for Id, Nome in DbListaFuncionarios])
        self.ConteudoLayout.addWidget(self.ListaFuncionario)
        RemBotao = QPushButton("remover item")
        RemBotao.clicked.connect(self.ConfirmarRem)
        self.ConteudoLayout.addWidget(RemBotao)

    def ConfirmarRem(self):
        Texto = self.ListaFuncionario.currentText()
        ItemId = int(Texto.split("ID: ")[1].split(" ")[0])  # extrai o id do texto
        InventarioFuncionalidade().RemItem(ItemId)
        self.IrInventario()

    def Edit(self):
        self._LimparConteudo()
        self.EditUi = QVBoxLayout()
        Selecionar = QWidget()
        SelecionarLayout = QFormLayout(Selecionar)
        #"select de funcionario"
        self.ListaFuncionario = QComboBox()
        DbListaFuncionarios = InventarioFuncionalidade().RemListaFuncionarios()
        self.ListaFuncionario.addItems(
            [f"ID: {Id} nome: {Nome}" for Id, Nome in DbListaFuncionarios]
        )
        SelecionarBotao = QPushButton("Selecionar")
        SelecionarBotao.clicked.connect(self.SelecionarEdicao)
        EditBotao = QPushButton("Editar")
        EditBotao.clicked.connect(self.ConfirmarEdicao)
        SelecionarLayout.addRow("Funcionário:", self.ListaFuncionario)
        SelecionarLayout.addRow(SelecionarBotao)
        self.EditUi.addWidget(Selecionar)
        #parte escondida até Selecionar
        self.Form = QWidget()
        self.Form.hide()
        self.EditUi.addWidget(self.Form)
        self.FormLayout = QFormLayout(self.Form)
        self.FormLayout.setSpacing(10)

        self.InputCa = QLineEdit()
        self.InputTipo = QComboBox()#select do pyside
        self.InputTipo.addItems(["capacete","luva","cinto","bota", "alabarte", "manquito", "oculos", "protetor auricolar", "colete refletivo"])#array para cada item
        self.InputDono = QLineEdit()
        self.InputUsos = QLineEdit()
        self.InputDevolucao = QDateEdit()
        self.InputDevolucao.setCalendarPopup(True)
        self.InputDevolucao.setDate(QDate.currentDate())
        self.InputDescarte = QDateEdit()
        self.InputDescarte.setCalendarPopup(True)
        self.InputDescarte.setDate(QDate.currentDate())

        self.FormLayout.addRow("CA:", self.InputCa)
        self.FormLayout.addRow("Tipo de EPI:", self.InputTipo)
        self.FormLayout.addRow("Responsável:", self.InputDono)
        self.FormLayout.addRow("Usos:", self.InputUsos)
        self.FormLayout.addRow("Data devolução:", self.InputDevolucao)
        self.FormLayout.addRow("Data descarte:", self.InputDescarte)
        #
        self.EditUi.addWidget(EditBotao)
        self.ConteudoLayout.addLayout(self.EditUi)

    def SelecionarEdicao(self):
        Texto = self.ListaFuncionario.currentText()
        ItemId = int(Texto.split("ID: ")[1].split(" ")[0])
        Item = InventarioFuncionalidade().SelFuncionario(ItemId)
        if Item:
            self.InputCa.setText(Item.Ca)
            self.InputTipo.setCurrentText(Item.TipoEpi)
            self.InputDono.setText(Item.Dono)
            self.InputUsos.setText(Item.usos_formatado)
        self.Form.show()

    def ConfirmarEdicao(self):
        Texto = self.ListaFuncionario.currentText()
        self.ItemIdEdicao = int(Texto.split("ID: ")[1].split(" ")[0])
        InventarioFuncionalidade().EditItem(
            self.ItemIdEdicao,
            self.InputCa.text(),
            self.InputTipo.currentText(),
            self.InputDono.text(),
            self.InputUsos.text().split(","),
            str(self.InputDevolucao.date().toPython()),
            str(self.InputDescarte.date().toPython())
        )
        self.IrInventario()

    def AtualizarTipo(self, Tipo):
        # reseta visibilidade
        for Btn in [self.BtnAdd, self.BtnRem, self.BtnEdit]:
            Btn.setVisible(True)
        Acoes   = {"add": self.Add,    "rem": self.Rem,    "edit": self.Edit}
        Esconder = {"add": self.BtnAdd, "rem": self.BtnRem, "edit": self.BtnEdit}
        if Tipo in Acoes:
            Esconder[Tipo].setVisible(False)
            Acoes[Tipo]()  #chama tela especifica
#endregion gerenciador de inventario
#iniciando janela
Window = GerenciadorJanelas()
Window.show()
sys.exit(app.exec())