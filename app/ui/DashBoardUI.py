#region base projeto
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QComboBox,
)
import sys
from pathlib import Path

if getattr(sys, 'frozen', False):
    root = Path(sys._MEIPASS)
else:
    root = Path(__file__).parent.parent   # app/ui → app → raiz

sys.path.insert(0, str(root))
from data.Inventario import Contas
#endregion base projeto


class Dashboard(QWidget):
    def __init__(self,Historico, Reverter, Gerenciar,Inventario):
        super().__init__()
        #plotly/matploitlib
        #tem que definir tipos de dashboard/
        pass

class DashBoardUi(QWidget):
    def __init__(self,Historico, Reverter, Gerenciar,Inventario):
        super().__init__()
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
        BtnInventario = QPushButton("Inventario")
        BtnInventario.clicked.connect(Inventario)
        TopoLayout.addWidget(BtnInventario)
        TopoLayout.addWidget(AddItem)
        TopoLayout.addWidget(RemItem)
        TopoLayout.addWidget(EditItem)
        TopoLayout.addWidget(ReverterBotao)
        TopoLayout.addWidget(BtnHistorico)

        #add dashboards

        #resto
        BaseLayout = QVBoxLayout()
        BaseLayout.addLayout(TopoLayout)
        self.setLayout(BaseLayout)