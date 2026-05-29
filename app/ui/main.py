#region base projeto
from PySide6.QtCore import Qt,QTimer
from PySide6.QtGui import QColor, QPalette, QIcon
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QStackedWidget
import sys
from pathlib import Path

if getattr(sys, 'frozen', False):
    root = Path(sys._MEIPASS)
else:
    root = Path(__file__).parent.parent

sys.path.insert(0, str(root))

#modulos/ui especificas
from ui.ContasUI import Login, CriarConta, ExcluirContaUI
from ui.InventarioUI import InventarioUi
from ui.ReverterUI import ReverterUi
from ui.HistoricoUI import HistoricoUi
from ui.ControleInventarioUI import GerenciadorInventario
from ui.GerenciarFuncionarioUi import GerenciarFuncionariosUI
from ui.ControleFunc import ControleFuncionariosUI
from ui.DashBoardUI import Dashboard,DashBoardUi

def resource_path(relative_path: str) -> str:
    base = getattr(sys, '_MEIPASS', Path(__file__).parent.parent)
    return str(Path(base) / relative_path)
#endregion base projeto

#paelta global

CORES = {
    "fundo":         "#002F48",
    "TopoInventario":"#080d3f",
    "botao":         "#080d3f",
    "hover":         "#0a1370",
    "ativo":         "#2636e4",
    "texto":         "#ffffff",
}

def ConfigurarApp(app: QApplication) -> None:
    paleta = QPalette()

    check_nao = resource_path('app/ui/imgs/check-nao.png').replace("\\", "/")
    check_ok  = resource_path('app/ui/imgs/check-ok.png').replace("\\", "/")
    paleta.setColor(QPalette.ColorRole.Window, QColor(CORES["fundo"]))
    app.setPalette(paleta)

    app.setStyleSheet(f"""
        QLabel {{
            color: {CORES['texto']};
        }}
        QPushButton {{
            background-color: {CORES['botao']};
            color: {CORES['texto']};
        }}
        QPushButton:hover {{
            background-color: {CORES['hover']};
        }}
        QPushButton:pressed {{
            background-color: {CORES['ativo']};
        }}
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border: 2px solid {CORES['botao']};
            border-radius: 3px;
            background-color: {CORES['botao']};
            image: url({check_nao});
        }}
        QCheckBox::indicator:checked {{
            background-color: {CORES['texto']};
            border: 2px solid {CORES['texto']};
            image: url({check_ok});
        }}
    """)

# Gerenciador de janelas
class GerenciadorJanelas(QWidget):
    """
    Controla toda a navegação via QStackedWidget.
    - UserLogado é propriedade que permite gerenciar qual usuario fez o que.
    - Cada tela recebe apenas callables de navegação — nunca referências
      diretas a outras telas, evitando acoplamento circular.
    - IrPara() mantém pilha de histórico para Voltar() funcionar.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Inventário")
        self.setWindowIcon(QIcon(resource_path("app/ui/imgs/ideia_de_logo_app_JA.ico")))
        self.UserLogado: int | None = None   # substitui o global UserLogado
        self.HistoricoNav: list[QWidget] = []

        self.Stacked = QStackedWidget()
        self.AlertaExibido = False
        #telas
        self.Login            = Login(
            Inventario=self.IrInventario,
            CriarConta=self.IrCriarConta,
            Usuario=self.SetUser,        # callback para guardar o user logado
            ExcluirConta = self.IrExcluirConta
        )
        self.CriarConta      = CriarConta(Login=self.IrLogin)
        self.Inventario       = InventarioUi(
            Historico=self.IrHistorico,
            Reverter=self.IrReverter,
            Gerenciar=self.IrGerenciar,
            GerenciarFuncionarios = self.IrGerenciarFuncionarios,
            Usuario=self.GetUser,
            Dashboard= self.IrDashboard
        )
        
        self.Reverter         = ReverterUi(
            Historico=self.IrHistorico,
            Inventario=self.IrInventario,
            Gerenciar=self.IrGerenciar,
            Dashboard= self.IrDashboard,
            GerenciarFuncionarios = self.IrGerenciarFuncionarios,
            Usuario=self.GetUser,        # callback para ler user logado
        )
        self.Historico        = HistoricoUi(
            Reverter=self.IrReverter,
            Inventario=self.IrInventario,
            Gerenciar=self.IrGerenciar,
            GerenciarFuncionarios = self.IrGerenciarFuncionarios,
            Dashboard= self.IrDashboard,
        )
        self.Gerenciar = GerenciadorInventario(
            Historico=self.IrHistorico,
            Inventario=self.IrInventario,
            Reverter=self.IrReverter,
            GerenciarFuncionarios = self.IrGerenciarFuncionarios,
            Dashboard= self.IrDashboard,
            Usuario=self.GetUser,
        )
        self.Dashboard = DashBoardUi(
            Historico=self.IrHistorico,
            Inventario=self.IrInventario,
            Gerenciar=self.IrGerenciar,
            GerenciarFuncionarios = self.IrGerenciarFuncionarios,
            Reverter=self.IrReverter
        )
        self.GerenciarFuncionarios = GerenciarFuncionariosUI(
            Historico=self.IrHistorico,
            Inventario=self.IrInventario,
            Gerenciar=self.IrGerenciar,
            Dashboard= self.IrDashboard,
            ControleFuncionarios = self.IrControleFuncionarios,
            Reverter=self.IrReverter
        )
        self.ControleFuncionarios=ControleFuncionariosUI(
            tipo = None,
            Historico=self.IrHistorico,
            Inventario=self.IrInventario,
            Gerenciar=self.IrGerenciar,
            Dashboard= self.IrDashboard,
            GerenciarFuncionarios = self.IrGerenciarFuncionarios,
            Reverter=self.IrReverter
        )
        self.ExcluirConta = ExcluirContaUI()  

        for tela in (
            self.Login, self.CriarConta,
            self.Inventario, self.Reverter,
            self.Historico, self.Gerenciar,
            self.ExcluirConta,self.Dashboard,
            self.GerenciarFuncionarios,
            self.ControleFuncionarios
        ):
            self.Stacked.addWidget(tela)

        Layout = QVBoxLayout(self)
        Layout.setContentsMargins(0, 0, 0, 0)
        Layout.addWidget(self.Stacked)

        self.Stacked.setCurrentWidget(self.Login)

    #ajudar no controle

    def SetUser(self, UserId: int) -> None:
        self.UserLogado = UserId

    def GetUser(self) -> int | None:
        return self.UserLogado


    def IrPara(self, widget: QWidget) -> None:
        Atual = self.Stacked.currentWidget()
        if Atual is not widget:
            self.HistoricoNav.append(Atual)
        self.Stacked.setCurrentWidget(widget)
    def IrGerenciar(self, tipo: str) -> None:
        self.Gerenciar.AtualizarTipo(tipo)
        self.IrPara(self.Gerenciar)
    def voltar(self) -> None:
        #Retorna para a tela Anterior (pode ser conectado a um botão global)
        if self.HistoricoNav:
            Anterior = self.HistoricoNav.pop()
            self.Stacked.setCurrentWidget(Anterior)


    def IrLogin(self) -> None:
        self.UserLogado = None          # limpa sessão ao saIr
        self.HistoricoNav.clear()
        self.IrPara(self.Login)

    def IrCriarConta(self) -> None:
        self.IrPara(self.CriarConta)

    def IrDashboard(self) -> None:
        self.Dashboard.atualizar()
        self.IrPara(self.Dashboard)

    def IrGerenciarFuncionarios(self)-> None:
        self.IrPara(self.GerenciarFuncionarios)

    def IrControleFuncionarios(self,tipo:str)->None:
        self.ControleFuncionarios.AtualizarTipo(tipo)
        self.IrPara(self.ControleFuncionarios)

    def IrExcluirConta(self) -> None:
        self.ExcluirConta.ConstruirComboItens(self.ExcluirConta.ListaContas)
        self.IrPara(self.ExcluirConta)


    def IrInventario(self) -> None:
        self.Inventario.AtualizarListaItens()
        if self.UserLogado is not None and not self.AlertaExibido:
            self.AlertaExibido = True
            QTimer.singleShot(300, self.Inventario.AlertasVencimento)
        self.IrPara(self.Inventario)

    def IrReverter(self) -> None:
        self.Reverter.AtualizarReverter()   # garante dados frescos ao abrir
        self.IrPara(self.Reverter)

    def IrHistorico(self) -> None:
        self.Historico.AtualizarHistorico() # garante dados frescos ao abrir
        self.IrPara(self.Historico)

def main() -> None:
    app = QApplication(sys.argv)
    ConfigurarApp(app)
    window = GerenciadorJanelas()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()