from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtGui import QColor, QPalette, QIcon, QSurfaceFormat, QShortcut, QKeySequence, QPixmap
from PySide6.QtWidgets import *
import os
import sys 
#configurando base da gui
app = QApplication(sys.argv)
paleta = QPalette()
paleta_cores = {
    "ex1": "#060721",
    "ex2": "#080d3f"
}
app.setPalette(paleta)
app.setStyleSheet()
#interfaces graficas
class GerenciadorJanelas():
    def __init__(self):
        pass
    #outras fun para trocar a janela

class Inventario_ui(QWidget):
    def _init__(self):
        super().__init__()
        self.setWindowTitle("aaa")