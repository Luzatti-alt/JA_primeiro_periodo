#region base projeto
from PySide6 import QtGui
from PySide6.QtCore import Qt, QDate, QTimer, QPoint
from PySide6.QtGui import QColor, QPalette, QIcon, QPixmap, QPainter, QPen, QColor, QFont
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
                  background-color: {PaletaCores['botao']};
                  color: {PaletaCores['texto']};
                  }}
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
        self.ReverterNavegacao = []
        self.stacked = QStackedWidget()
        self.Login = Login(Inventario=self.IrInventario,CriarConta=self.IrCriarConta)
        self.CriarConta = CriarConta(Login=self.IrLogin)
        self.Inventario = InventarioUi(Historico=self.IrHistorico,Reverter=self.IrReverter, Gerenciar=self.IrGerenciarInventario)
        self.Reverter = ReverterUi(Historico=self.IrHistorico,Inventario=self.IrInventario, Gerenciar=self.IrGerenciarInventario)
        self.Historico = HistoricoUi(Reverter=self.IrReverter,Inventario=self.IrInventario, Gerenciar=self.IrGerenciarInventario)
        self.GerenciarInventario = GerenciadorInventario(Historico=self.IrHistorico,Reverter=self.IrReverter, Inventario=self.IrInventario)
        self.stacked.addWidget(self.Login)
        self.stacked.addWidget(self.CriarConta)
        self.stacked.addWidget(self.Inventario)
        self.stacked.addWidget(self.Reverter)
        self.stacked.addWidget(self.Historico)
        self.stacked.addWidget(self.GerenciarInventario)

        # definir Layout
        Layout = QVBoxLayout(self)
        Layout.setContentsMargins(0, 0, 0, 0)
        Layout.addWidget(self.stacked)

        # tela inicial
        self.stacked.setCurrentWidget(self.Login)
    def IrPara(self, Widget):
        TelaAtual = self.stacked.currentWidget()
        if TelaAtual != Widget:  # Só adiciona se for uma tela diferente
            self.ReverterNavegacao.append(TelaAtual)
        self.stacked.setCurrentWidget(Widget)
    def IrLogin(self):
        self.IrPara(self.Login)
    def IrCriarConta(self):
        self.IrPara(self.CriarConta)
    def IrReverter(self):
        self.IrPara(self.Reverter)
    def IrHistorico(self):
        self.IrPara(self.Historico)
    def IrInventario(self):
        self.IrPara(self.Inventario)
        self.Inventario.AtualizarListaItens()#recarregar o db sempre, aqui so para não ter a impressão de lag
    def IrGerenciarInventario(self, Tipo):
        self.GerenciarInventario.AtualizarTipo(Tipo)
        self.IrPara(self.GerenciarInventario)
#endregion gerenciador interfaces graficas
#region Conta
class Login(QWidget):
    SEQUENCIA_SECRETA = ["img", "img", "img"]  # clicar 3x no logo abre CriarConta
    def __init__(self,Inventario,CriarConta):
        super().__init__()
        self.IrInventario = Inventario
        self.IrCriarConta = CriarConta
        self.HistoricoClick = []
        Layout = QVBoxLayout()
        Layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont("Arial", 20)
        Logo = QHBoxLayout()
        self.imgLogo = QPushButton("IMG")  # ← QPushButton, não QLabel
        self.imgLogo.setFont(font)
        self.imgLogo.setFlat(True)  # parece label visualmente
        self.imgLogo.setStyleSheet("border: none; background: transparent;")
        self.imgLogo.clicked.connect(lambda: self.Registrar("img"))
        self.TextoLogo = QLabel("Sistema PLACEHOARDER")
        self.TextoLogo.setFont(font)
        Logo.addWidget(self.imgLogo)
        Logo.addWidget(self.TextoLogo)
        Layout.addLayout(Logo)

        self.Username = QLineEdit()
        self.Username.setPlaceholderText("Usuário")
        Layout.addWidget(self.Username)

        self.Senha = QLineEdit()
        self.Senha.setPlaceholderText("Senha")
        self.Senha.setEchoMode(QLineEdit.EchoMode.Password)
        Layout.addWidget(self.Senha)

        self.LblErro = QLabel("")
        self.LblErro.setStyleSheet("color: #ff4444;")
        Layout.addWidget(self.LblErro)

        LogarBotao = QPushButton("Logar")
        LogarBotao.clicked.connect(self.Logar)
        Layout.addWidget(LogarBotao)

        self.setLayout(Layout)

    def Logar(self):
        usuario = self.Username.text().strip()
        senha = self.Senha.text().strip()

        if not usuario or not senha:
            self.LblErro.setText("Preencha todos os campos.")
            return

        conta = Contas.login(usuario,senha)
        if conta:
            self.LblErro.setText("")
            self.IrInventario()
        else:
            self.LblErro.setText("Usuário ou senha incorretos.")


    def Registrar(self, Nome):
        self.HistoricoClick.append(Nome)
        self.HistoricoClick = self.HistoricoClick[-len(self.SEQUENCIA_SECRETA):]
        if self.HistoricoClick == self.SEQUENCIA_SECRETA:
            self.HistoricoClick = []
            self.IrCriarConta()

#este so ira aparecer se for apertado uma parte especifica de botoes
class CriarConta(QWidget):
    def __init__(self, Login):
        super().__init__()
        self.IrLogin = Login

        Layout = QVBoxLayout()
        Layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.InputUsuario = QLineEdit()
        self.InputUsuario.setPlaceholderText("Usuário")
        Layout.addWidget(self.InputUsuario)

        self.InputSenha = QLineEdit()
        self.InputSenha.setPlaceholderText("Senha")
        self.InputSenha.setEchoMode(QLineEdit.EchoMode.Password)
        Layout.addWidget(self.InputSenha)

        self.InputCargo = QComboBox()
        self.InputCargo.addItems(["admin", "operador"])
        Layout.addWidget(self.InputCargo)

        self.LblErro = QLabel("")
        self.LblErro.setStyleSheet("color: #ff4444;")
        Layout.addWidget(self.LblErro)

        BtnCriar = QPushButton("Criar conta")
        BtnCriar.clicked.connect(self.cadastrar)
        Layout.addWidget(BtnCriar)

        self.setLayout(Layout)
    def cadastrar(self):
        self.IrLogin()
        Contas.Cadastrar(self.InputUsuario.text(),self.InputSenha.text(),self.InputCargo.currentText())

#endregion Conta
#region main ui
class InventarioUi(QWidget):
    PAGE_SIZE = 30

    def __init__(self,Historico, Reverter, Gerenciar):
        super().__init__()

        #optimização da query e melhoria da experiencia do usuario
        self._offset = 0          # quantos itens já carregados
        self._total = 0           # total no banco
        self._carregando = False  # evita chamadas duplicadas
        self._filtro_ativo = ""   # guarda pesquisa atual

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
        TopoLayout.addWidget(AddItem)
        TopoLayout.addWidget(RemItem)
        TopoLayout.addWidget(EditItem)
        TopoLayout.addWidget(ReverterBotao)
        TopoLayout.addWidget(BtnHistorico)

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
        self.ScrollArea.verticalScrollBar().valueChanged.connect(self._OnScroll)
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
        QTimer.singleShot(500, self._AlertasVencimento)

    def _AlertasVencimento(self):
        alertas = GerenciadorTemporal().ConferirValDev()
        atrasados = [a for a in alertas if a[1] == "atrasado"]
        if atrasados:
            QMessageBox.warning(self, "Atenção", f"{len(atrasados)} item(s) com devolução atrasada!")

    def AtualizarListaItens(self):
        """Reseta a lista e carrega a primeira página (60 itens)."""
        self._filtro_ativo = ""
        self._offset = 0
        self._total = InventarioFuncionalidade().TotalItens()
        self._carregando = False

        self.setUpdatesEnabled(False)

        # limpa widgets existentes mantendo o stretch no final
        while self.ListaItensLayout.count():
            Item = self.ListaItensLayout.takeAt(0)
            if Item.widget():
                Item.widget().deleteLater()

        self._CarregarPagina()
        self.ListaItensLayout.addStretch()
        self.setUpdatesEnabled(True)

    def _CarregarPagina(self):
        """Carrega mais PAGE_SIZE itens a partir do offset atual."""
        if self._carregando:
            return
        if self._filtro_ativo:
            return  # pesquisa já carregou tudo
        if self._offset >= self._total:
            return  # não há mais itens

        self._carregando = True

        # remove o stretch antes de adicionar novos widgets
        Ultimo = self.ListaItensLayout.itemAt(self.ListaItensLayout.count() - 1)
        if Ultimo and Ultimo.spacerItem():
            self.ListaItensLayout.removeItem(Ultimo)

        Novos = InventarioFuncionalidade().ItensPaginados(
            offset=self._offset,
            limit=self.PAGE_SIZE
        )
        for Item in Novos:
            Linha = self.CriarLinhaItem(Item)
            Linha.setFixedHeight(78)
            self.ListaItensLayout.addWidget(Linha)

        self._offset += len(Novos)
        self.ListaItensLayout.addStretch()
        self._carregando = False

    def _OnScroll(self, Valor):
        """Dispara carregamento quando scroll chega perto do fim."""
        Barra = self.ScrollArea.verticalScrollBar()
        if Valor >= Barra.maximum() - 50:
            # usa QTimer para não bloquear o evento de scroll
            QTimer.singleShot(0, self._CarregarPagina)

    def AtualizarListaFiltrado(self, Filtro):
        """Pesquisa: carrega todos os resultados filtrados de uma vez."""
        while self.ListaItensLayout.count():
            Item = self.ListaItensLayout.takeAt(0)
            if Item.widget():
                Item.widget().deleteLater()

        self._filtro_ativo = Filtro

        if Filtro:
            DbItens = InventarioFuncionalidade().pesquisar(Filtro)
        else:
            # sem filtro: volta para lazy loading normal
            self._filtro_ativo = ""
            self._offset = 0
            self._total = InventarioFuncionalidade().TotalItens()
            DbItens = InventarioFuncionalidade().ItensPaginados(offset=0, limit=self.PAGE_SIZE)
            self._offset = len(DbItens)

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
#region Historico
class HistoricoUi(QWidget):
    def __init__(self,Reverter, Inventario, Gerenciar):
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
        ReverterBotao = QPushButton("Reverter")
        ReverterBotao.clicked.connect(Reverter)
        TopoLayout.addWidget(VoltarBotao)
        TopoLayout.addWidget(AddItem)
        TopoLayout.addWidget(RemItem)
        TopoLayout.addWidget(EditItem)
        TopoLayout.addWidget(ReverterBotao)

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
        HisTopoLay.addWidget(FundoTopo)

        self.ScrollContent = QWidget()
        ScrollArea = QScrollArea()
        ScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        ScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        ScrollArea.setWidgetResizable(True)
        ScrollArea.setFixedHeight(5 * 120)
        self.ListaItensLayout = QVBoxLayout(self.ScrollContent)
        self.ListaItensLayout.setSpacing(20)
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
    def formatar_dict_texto(self,d):
        if not d:
            return "—"

        nomes_amigaveis = {
            "Ca": "CA",
            "TipoEpi": "Tipo",
            "Dono": "Responsável",
            "Usos": "Usos",
            "DataDevolucao": "Devolução",
            "DataDescarte": "Validade"
        }

        linhas = []
        for chave, valor in d.items():
            nome = nomes_amigaveis.get(chave, chave)

            # tratar lista (ex: usos)
            if isinstance(valor, list):
                valor = ", ".join(valor)

            linhas.append(f"{nome}: {valor}")

        return "\n".join(linhas)
    def AtualizarHistorico(self):
        while self.ListaItensLayout.count():
            item = self.ListaItensLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        DbItens = InventarioFuncionalidade().ItensHistorico()

        for Item in DbItens:
            Linha = self.CriarLinhaItem(Item)
            Linha.setFixedHeight(78)
            self.ListaItensLayout.addWidget(Linha)

        self.ListaItensLayout.addStretch()
    def HistoricoEAtualizar(self, Id, Checked):
        InventarioFuncionalidade().HistoricoItem(Id, Checked)
        self.AtualizarHistorico()
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
        Layout.addWidget(Col(self.formatar_dict_texto(Item.VersaoAnterior), COL_ANTERIOR))
        Layout.addWidget(Col(self.formatar_dict_texto(Item.VersaoAtual), COL_ATUAL))

        return Container
#endregion Historico
#region Reverter
class ReverterUi(QWidget):
    def __init__(self,Historico, Inventario, Gerenciar):
        super().__init__()
        ReverterBaseLayout = QVBoxLayout()
        VoltarBotao = QPushButton("Inventario")
        VoltarBotao.clicked.connect(Inventario)
        TopoLayout = QHBoxLayout()
        AddItem  = QPushButton("Adicionar do inventario")
        AddItem.clicked.connect(lambda: Gerenciar("add"))
        RemItem  = QPushButton("Remover do inventario")
        RemItem.clicked.connect(lambda: Gerenciar("rem"))
        EditItem = QPushButton("Editar o inventario")
        EditItem.clicked.connect(lambda: Gerenciar("edit"))
        BtnHistorico = QPushButton("Historico")
        BtnHistorico.clicked.connect(Historico)
        
        TopoLayout.addWidget(VoltarBotao)
        TopoLayout.addWidget(AddItem)
        TopoLayout.addWidget(RemItem)
        TopoLayout.addWidget(EditItem)
        TopoLayout.addWidget(BtnHistorico)

        HisTopoLay = QVBoxLayout()
        FundoTopo = QWidget()
        FundoTopo.setStyleSheet("background-color: #005B8C; color: #ffffff;")
        FundoTopo.setAutoFillBackground(True)
        ReverterTopoLayout = QHBoxLayout(FundoTopo)
        ReverterTopoLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ReverterTopoLayout.setContentsMargins(8, 4, 8, 4)
        ReverterTopoLayout.addSpacing(10)
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
        ReverterTopoLayout.addWidget(HeaderLabel("", COL_IMG))           # espaço da imagem
        ReverterTopoLayout.addWidget(HeaderLabel("Identificação", COL_IDENT))
        ReverterTopoLayout.addWidget(HeaderLabel("Dono",          COL_DONO))
        ReverterTopoLayout.addWidget(HeaderLabel("versão anterior",     COL_ANTERIOR))
        ReverterTopoLayout.addWidget(HeaderLabel("versão atual",  COL_ATUAL))
        ReverterTopoLayout.addWidget(HeaderLabel("Reverter",  COL_ATUAL))
        HisTopoLay.addWidget(FundoTopo)

        self.ScrollContent = QWidget()
        ScrollArea = QScrollArea()
        ScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        ScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        ScrollArea.setWidgetResizable(True)
        ScrollArea.setFixedHeight(5 * 120)
        self.ListaItensLayout = QVBoxLayout(self.ScrollContent)
        self.ListaItensLayout.setSpacing(20)
        self.ListaItensLayout.setContentsMargins(0, 0, 0, 0)

        DbItens = InventarioFuncionalidade().ItensReverter()
        for Item in DbItens:
            Linha = self.CriarLinhaItem(Item)
            Linha.setFixedHeight(78)
            self.ListaItensLayout.addWidget(Linha)
        self.ListaItensLayout.addStretch()
        self.ScrollContent.setLayout(self.ListaItensLayout)
        ScrollArea.setWidget(self.ScrollContent)
        ReverterBaseLayout.addLayout(HisTopoLay)
        ReverterBaseLayout.addWidget(ScrollArea)

        BaseLayout = QVBoxLayout()
        BaseLayout.addLayout(TopoLayout)
        BaseLayout.addLayout(ReverterBaseLayout)
        self.setLayout(BaseLayout)
    def formatar_dict_texto(self,d):
        if not d:
            return "—"

        nomes_amigaveis = {
            "Ca": "CA",
            "TipoEpi": "Tipo",
            "Dono": "Responsável",
            "Usos": "Usos",
            "DataDevolucao": "Devolução",
            "DataDescarte": "Validade"
        }

        linhas = []
        for chave, valor in d.items():
            nome = nomes_amigaveis.get(chave, chave)

            # tratar lista (ex: usos)
            if isinstance(valor, list):
                valor = ", ".join(valor)

            linhas.append(f"{nome}: {valor}")

        return "\n".join(linhas)
    def AtualizarReverter(self):
        while self.ListaItensLayout.count():
            item = self.ListaItensLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        DbItens = InventarioFuncionalidade().ItensReverter()

        for Item in DbItens:
            Linha = self.CriarLinhaItem(Item)
            Linha.setFixedHeight(78)
            self.ListaItensLayout.addWidget(Linha)

        self.ListaItensLayout.addStretch()
    def ReverterEAtualizar(self, Id, Checked):
        InventarioFuncionalidade().ReverterItem(Id, Checked)
        self.AtualizarReverter()
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
        Layout.addWidget(Col(self.formatar_dict_texto(Item.VersaoAnterior), COL_ANTERIOR))
        Layout.addWidget(Col(self.formatar_dict_texto(Item.VersaoAtual), COL_ATUAL))

        # checkbox direto no Layout, não via Col()
        CbContainer = QWidget()
        CbContainer.setFixedWidth(COL_CB)
        CbLay = QHBoxLayout(CbContainer)
        CbLay.setContentsMargins(0, 0, 0, 0)
        Reverter = QCheckBox()
        #trocar para foi alterado
        Reverter.setChecked(Item.revertido or False)
        Reverter.clicked.connect(
            lambda Checked, Id=Item.id: self.ReverterEAtualizar(Id, Checked)
            )
        CbLay.addWidget(Reverter, alignment=Qt.AlignmentFlag.AlignCenter)
        Layout.addWidget(CbContainer)

        return Container
#endregion Reverter
#region assinatura
class AssinaturaWidget(QWidget):
    #qwidget onde tera a assinatura
 
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(800, 150)
        self._canvas = QPixmap(800,350)
        self._canvas.fill(QColor("#ffffff"))
        self._ultimo_ponto = QPoint()
        self._desenhando = False
 
        # borda visual para indicar a área
        self.setStyleSheet("border: 2px solid #005B8C; background-color: #ffffff;")
 
    #eventos de mouse
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._desenhando = True
            self._ultimo_ponto = event.position().toPoint()
 
    def mouseMoveEvent(self, event):
        if self._desenhando:
            painter = QPainter(self._canvas)
            pen = QPen(QColor("#000000"), 2, Qt.PenStyle.SolidLine,
                       Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            painter.drawLine(self._ultimo_ponto, event.position().toPoint())
            painter.end()
            self._ultimo_ponto = event.position().toPoint()
            self.update()
 
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._desenhando = False
 
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self._canvas)
 
    #extras
    def limpar(self):
        self._canvas.fill(QColor("#ffffff"))
        self.update()
 
    def vazio(self) -> bool:#se não tiver nenhum pixel na tela
        img = self._canvas.toImage()
        for y in range(img.height()):
            for x in range(img.width()):
                if QColor(img.pixel(x, y)).lightness() < 200:
                    return False
        return True
 
    def pixmap(self) -> QPixmap:
        return self._canvas.copy()

#endregion assinatura
#region gerenciador de inventario
class GerenciadorInventario(QWidget):
    def __init__(self,Historico, Inventario, Reverter):
        super().__init__()
        self.IrInventario = Inventario
        self.IrReverter = Reverter

        # botões fixos do topo
        self.InventarioBotao = QPushButton("Inventário")
        self.BtnAdd = QPushButton("Adicionar")
        self.BtnRem = QPushButton("Remover")
        self.BtnEdit = QPushButton("Editar")
        self.BtnReverter = QPushButton("Reverter")
        self.BtnHistorico = QPushButton("Historico")
        self.BtnHistorico.clicked.connect(Historico)

        self.InventarioBotao.clicked.connect(self.IrInventario)
        self.BtnReverter.clicked.connect(self.IrReverter)
        self.BtnAdd.clicked.connect(lambda: self.AtualizarTipo("add"))
        self.BtnRem.clicked.connect(lambda: self.AtualizarTipo("rem"))
        self.BtnEdit.clicked.connect(lambda: self.AtualizarTipo("edit"))

        TopoLayout = QHBoxLayout()
        TopoLayout.addWidget(self.InventarioBotao)
        TopoLayout.addWidget(self.BtnAdd)
        TopoLayout.addWidget(self.BtnRem)
        TopoLayout.addWidget(self.BtnEdit)
        TopoLayout.addWidget(self.BtnReverter)
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

        AssinaturaLay = QVBoxLayout()
        lbl = QLabel("Assinatura do Funcionario:")
        lbl.setStyleSheet("color: #ffffff; border: none;")
        AssinaturaLay.addWidget(lbl)
 
        self.area = AssinaturaWidget()
        AssinaturaLay.addWidget(self.area)
 
        btn_limpar = QPushButton("Limpar assinatura")
        btn_limpar.clicked.connect(self.area.limpar)
        AssinaturaLay.addWidget(btn_limpar)
        FormLayout.addRow(AssinaturaLay)

        BtnConfirmar = QPushButton("Adicionar item")
        BtnConfirmar.clicked.connect(self.ConfirmarAdd)
        FormLayout.addRow(BtnConfirmar)

        self.ConteudoLayout.addWidget(Form)
 
        def pixmap(self) -> QPixmap:
            return self.area.pixmap()
 
        def vazio(self) -> bool:
            return self.area.vazio()
 
        def limpar(self):
            self.area.limpar()

        #data para descarte e devolução
    def ConfirmarAdd(self):
        if not self.InputCa.text() or not self.InputDono.text():
            return #trocar para uma caixa de alert
        DataDev = self.InputDevolucao.date().toPython()
        DataDesc = self.InputDescarte.date().toPython()

        InventarioFuncionalidade().AddItem(
            ca=self.InputCa.text(),
            tipo_epi=self.InputTipo.currentText(),
            dono=self.InputDono.text(),
            usos=[uso.strip() for uso in self.InputUsos.text().split(",")],
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
        if self.ListaFuncionario.count() == 0:
            return
        Texto = self.ListaFuncionario.currentText()
        ItemId = int(Texto.split("ID: ")[1].split(" ")[0])# extrai o id do texto
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
            [uso.strip() for uso in self.InputUsos.text().split(",")],
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