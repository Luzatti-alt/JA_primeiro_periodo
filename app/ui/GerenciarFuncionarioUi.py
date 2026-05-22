#region base projeto
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import *
import sys
from pathlib import Path
# Adiciona o diretório raiz do projeto ao path e permite usar partes/modulos dcleare outras pastas do projeto
if getattr(sys, 'frozen', False):
    root = Path(sys._MEIPASS)
else:
    root = Path(__file__).parent.parent

sys.path.insert(0, str(root))


def resource_path(relative_path):
    base = getattr(sys, '_MEIPASS', Path(__file__).parent.parent)
    return str(Path(base) / relative_path)
#endregion base projeto
class ControleFuncionariosUI(QWidget):
    def __init__(self, Historico, Reverter, Gerenciar,Dashboard, Inventario,):
        super().__init__()
        TopoLayout = QHBoxLayout()
        InventarioUi = QPushButton("Inventario")
        InventarioUi.clicked.connect(Inventario)
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
        TopoLayout.addWidget(InventarioUi)
        TopoLayout.addWidget(AddItem)
        TopoLayout.addWidget(RemItem)
        TopoLayout.addWidget(EditItem)
        TopoLayout.addWidget(ReverterBotao)
        TopoLayout.addWidget(BtnHistorico)
        TopoLayout.addWidget(BtnDashboard)
        
        BaseLayout = QVBoxLayout()
        BaseLayout.addLayout(TopoLayout)
        self.setLayout(BaseLayout)