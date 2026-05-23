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
    SEQUENCIA_CRIAR   = ["img", "img", "img"]
    SEQUENCIA_EXCLUIR = ["img", "nome", "img"]
    _TAMANHO_MAX = max(len(SEQUENCIA_CRIAR), len(SEQUENCIA_EXCLUIR))

    def __init__(self, Inventario, CriarConta, ExcluirConta, Usuario=None):
        super().__init__()
        self.IrInventario   = Inventario
        self.IrCriarConta   = CriarConta
        self.IrExcluirConta = ExcluirConta
        self.SetUser        = Usuario
        self.HistoricoClick: list[str] = []

        Layout = QVBoxLayout()
        Layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont("Arial", 20)

        # Logo
        logoRow = QHBoxLayout()
        self.BtnLogo = QPushButton("IMG")#criar logo para isso e trocar para img real
        self.BtnLogo.setFont(font)
        self.BtnLogo.setFlat(True)
        self.BtnLogo.setStyleSheet("border: none; background: transparent;")
        self.BtnLogo.clicked.connect(lambda: self.RegistrarClick("img"))
        self.BtnNome = QPushButton("Sistema Controle Epi Inteligente")
        self.BtnNome.setFont(font)
        self.BtnNome.setFlat(True)
        self.BtnNome.setStyleSheet("border: none; background: transparent;")
        self.BtnNome.clicked.connect(lambda: self.RegistrarClick("nome"))
        self.BtnNome.setFont(font)
        logoRow.addWidget(self.BtnLogo)
        logoRow.addWidget(self.BtnNome)
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

    def Logar(self) -> None:
        usuario = self.InputUsuario.text().strip()
        senha   = self.InputSenha.text().strip()

        if not usuario or not senha:
            self.LblErro.setText("Preencha todos os campos.")
            return

        resultado = Contas.login(usuario, senha)
        if resultado == "bloqueado":
            self.LblErro.setText("Conta bloqueada. Tente em 15 minutos.")
        elif resultado:
            self.LblErro.setText("")
            if self.SetUser:
                self.SetUser(Contas.IdLogado(usuario))
            self.IrInventario()
        else:
            self.LblErro.setText("Usuário ou senha incorretos.")

    def RegistrarClick(self, nome: str) -> None:
        self.HistoricoClick.append(nome)
        self.HistoricoClick = self.HistoricoClick[-self._TAMANHO_MAX:]
        sufixo_criar   = self.HistoricoClick[-len(self.SEQUENCIA_CRIAR):]
        sufixo_excluir = self.HistoricoClick[-len(self.SEQUENCIA_EXCLUIR):]
        if sufixo_criar == self.SEQUENCIA_CRIAR:
            self.HistoricoClick = []
            self.IrCriarConta()
        elif sufixo_excluir == self.SEQUENCIA_EXCLUIR:
            self.HistoricoClick = []
            self.IrExcluirConta()
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

        ok = Contas.Cadastrar(usuario, senha, cargo)
        if ok:
            self.IrLogin()
        else:
            self.LblErro.setText("Usuário já existe ou cargo inválido.")
            self.IrLogin()


class ExcluirContaUI(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
 
        self.ListaContas = QComboBox()
        self.ConstruirComboItens(self.ListaContas)
 
        self.LblErro = QLabel("")
        self.LblErro.setStyleSheet("color: #ff4444;")
 
        self.RemoverFuncionario = QPushButton("Remover conta")
        self.RemoverFuncionario.clicked.connect(self.Remover)
 
        layout.addWidget(self.ListaContas)
        layout.addWidget(self.LblErro)
        layout.addWidget(self.RemoverFuncionario)
        self.setLayout(layout)
 
    def Remover(self) -> None:
        usuario = self.ListaContas.currentData()
        if not usuario:
            return
        ok = Contas.RemoverConta(usuario)
        if ok:
            self.ConstruirComboItens(self.ListaContas)
            self.LblErro.setText("")
        else:
            self.LblErro.setText("Erro ao remover conta.")
 
    @staticmethod
    def ConstruirComboItens(combo: QComboBox) -> None:
        combo.clear()
        for ItemId, nome in Contas.ListarContas():
            combo.addItem(f"{nome} (ID: {ItemId})", userData=nome)