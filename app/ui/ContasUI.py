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


class Login(QWidget):
    SEQUENCIASECRETA = ["img", "img", "img"]  # 3 cliques no logo → CriarConta

    def __init__(self, Inventario, CriarConta, Usuario=None):
        """
        Inventario  — callable: ir para tela de inventário após login
        CriarConta  — callable: ir para tela de criar conta
        SetUser    — callable(int): informa ao GerenciadorJanelas qual user logou
        """
        super().__init__()
        self.IrInventario = Inventario
        self.IrCriarConta = CriarConta
        self.SetUser = Usuario           # substitui global UserLogado
        self.HistoricoClick: list[str] = []

        Layout = QVBoxLayout()
        Layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont("Arial", 20)

        # Logo
        logoRow = QHBoxLayout()
        self.BtnLogo = QPushButton("IMG")
        self.BtnLogo.setFont(font)
        self.BtnLogo.setFlat(True)
        self.BtnLogo.setStyleSheet("border: none; background: transparent;")
        self.BtnLogo.clicked.connect(lambda: self.RegistrarClick("img"))
        self.LblLogo = QLabel("Sistema PLACEHOARDER")
        self.LblLogo.setFont(font)
        logoRow.addWidget(self.BtnLogo)
        logoRow.addWidget(self.LblLogo)
        Layout.addLayout(logoRow)

        self.InputUsuario = QLineEdit()
        self.InputUsuario.setPlaceholderText("Usuário")
        Layout.addWidget(self.InputUsuario)

        self.InputSenha = QLineEdit()
        self.InputSenha.setPlaceholderText("Senha")
        self.InputSenha.setEchoMode(QLineEdit.EchoMode.Password)
        Layout.addWidget(self.InputSenha)

        self.LblErro = QLabel("")
        self.LblErro.setStyleSheet("color: #ff4444;")
        Layout.addWidget(self.LblErro)

        BtnLogar = QPushButton("Logar")
        BtnLogar.clicked.connect(self.Logar)
        Layout.addWidget(BtnLogar)

        self.setLayout(Layout)

    #

    def Logar(self) -> None:
        usuario = self.InputUsuario.text().strip()
        senha   = self.InputSenha.text().strip()

        if not usuario or not senha:
            self.LblErro.setText("Preencha todos os campos.")
            return

        conta = Contas.login(usuario, senha)
        if conta:
            self.LblErro.setText("")
            if self.SetUser:
                self.SetUser(Contas.IdLogado(usuario))
            self.IrInventario()
        else:
            self.LblErro.setText("Usuário ou senha incorretos.")

    def RegistrarClick(self, nome: str) -> None:
        self.HistoricoClick.append(nome)
        self.HistoricoClick = self.HistoricoClick[-len(self.SEQUENCIASECRETA):]
        if self.HistoricoClick == self.SEQUENCIASECRETA:
            self.HistoricoClick = []
            self.IrCriarConta()


class CriarConta(QWidget):
    #Acessível apenas pela sequência secreta na tela de Login

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
        BtnCriar.clicked.connect(self.Cadastrar)
        Layout.addWidget(BtnCriar)

        self.setLayout(Layout)

    def Cadastrar(self) -> None:
        usuario = self.InputUsuario.text().strip()
        senha   = self.InputSenha.text().strip()
        cargo   = self.InputCargo.currentText()

        if not usuario or not senha:
            self.LblErro.setText("Preencha todos os campos.")
            return

        Contas.Cadastrar(usuario, senha, cargo)
        self.IrLogin()


class ExcluirContaUI(QWidget):
    def __init__(self):
        super().__init__()
        pass