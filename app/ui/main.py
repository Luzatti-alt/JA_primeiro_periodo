from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor, QPalette, QIcon, QPixmap
from PySide6.QtWidgets import *
import os
import sys
import json
from pathlib import Path
# Adiciona o diretório raiz do projeto ao path e permite usar partes/modulos dcleare outras pastas do projeto
root = Path(__file__).parent.parent  # root da pasta app
sys.path.insert(0, str(root))
from data.Inventario import Inventario,Itens #criar init.py para reconhecer modulo
#configurando base da gui
app = QApplication(sys.argv)
paleta = QPalette()
paleta_cores = {
    "fundo": "#002F48",
    "topo_inventario": "#080d3f",
    "botao": "#080d3f",
    "houver":"#0a1370",
    "ativo": "#2636e4",
    "texto": "#ffffff"
}
paleta.setColor(QPalette.ColorRole.Window, QColor(paleta_cores["fundo"]))
app.setPalette(paleta)
#stylesheet do app
app.setStyleSheet(f"""
                  QPushButton {{
                  background-color: {paleta_cores['botao']};color: {paleta_cores['texto']
                  }}}
                  QCheckBox::indicator {{
                    width: 18px;
                    height: 18px;
                    border: 2px solid {paleta_cores['botao']};
                    border-radius: 3px;
                    background-color: {paleta_cores['botao']};
                    image: url(app/ui/imgs/check-nao.png);
                    }}
                  QCheckBox::indicator:checked {{
                    background-color: {paleta_cores['texto']};
                    border: 2px solid {paleta_cores['texto']};
                    image: url(app/ui/imgs/check-ok.png);
    }}
""")#trocar icon
imagens = {
    "capacete": "imagens/capacete.png"
}

#region gerenciador de janelas
#gerenciador interfaces graficas
class Gerenciador_janelas(QWidget):
    def __init__(self):
        super().__init__()
        self.historico_navegacao = []
        self.stacked = QStackedWidget()
        self.Inventario = Inventario_ui(voltar=self.voltar, historico=self.IrHistorico, gerenciar=self.IrGerenciarInventario)
        self.Historico = Historico_ui(Inventario=self.IrInventario, gerenciar=self.IrGerenciarInventario)
        self.Gerenciar_inventario = GerenciadorInventario(historico=self.IrHistorico,Inventario=self.IrInventario)
        self.stacked.addWidget(self.Inventario)
        self.stacked.addWidget(self.Historico)
        self.stacked.addWidget(self.Gerenciar_inventario)

        # definir layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.stacked)

        # tela inicial
        self.stacked.setCurrentWidget(self.Inventario)
    def ir_para(self, widget):
        tela_atual = self.stacked.currentWidget()
        if tela_atual != widget:  # Só adiciona se for uma tela diferente
            self.historico_navegacao.append(tela_atual)
        self.stacked.setCurrentWidget(widget)
    def IrHistorico(self):
        self.ir_para(self.Historico)
    def IrInventario(self):
        self.Inventario.atualizar_lista()#recarregar o db sempre
        self.ir_para(self.Inventario)
    def IrGerenciarInventario(self, tipo):
        self.Gerenciar_inventario.atualizar_tipo(tipo)
        self.ir_para(self.Gerenciar_inventario)
    def voltar(self):
        # Volta para a última tela no histórico
        tela_anterior = self.historico_navegacao.pop()
        self.stacked.setCurrentWidget(tela_anterior)
#endregion gerenciador de janelas
#interface principal
#region main ui
class Inventario_ui(QWidget):
    def __init__ (self,voltar,historico, gerenciar):
        super().__init__()
        self.setWindowTitle("sistema de inventario")
        self.setWindowIcon(QIcon("app/ui/imgs/ideia_de_logo_app_JA.png"))
        #topo ui
        topo_layout = QHBoxLayout()
        add_item =  QPushButton("Adicionar do inventario")
        add_item.clicked.connect(lambda: gerenciar("add"))
        rem_item =  QPushButton("Remover do inventario")
        rem_item.clicked.connect(lambda: gerenciar("rem"))
        edit_item =  QPushButton("Editar o inventario")
        edit_item.clicked.connect(lambda: gerenciar("edit"))
        HistoricoBotao = QPushButton("Historico")
        HistoricoBotao.clicked.connect(historico)
        topo_layout.addWidget(add_item)
        topo_layout.addWidget(rem_item)
        topo_layout.addWidget(edit_item)
        topo_layout.addWidget(HistoricoBotao)

        #inventario na ui

        inv_topo_lay = QVBoxLayout()
        # Inventario no topo
        fundo_topo = QWidget()
        fundo_topo.setStyleSheet("background-color: #005B8C; color: #ffffff;")
        fundo_topo.setAutoFillBackground(True)
        inventario_topo_layout = QHBoxLayout(fundo_topo)
        inventario_topo_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        inventario_topo_layout.setContentsMargins(8, 4, 8, 4)
        inventario_topo_layout.addSpacing(10)

        #tentativa de alinhar texto e img com o texto do topo
        COL_IMG   = 60
        COL_IDENT = 80
        COL_ID = 30
        COL_DONO  = 120
        COL_COD   = 80
        COL_USOS  = 140
        COL_DEVO  = 100
        COL_DESC  = 80
        COL_CB    = 60
        def header_label(text, width):
            lbl = QLabel(text)
            lbl.setFixedWidth(width)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            return lbl
        inventario_topo_layout.addWidget(header_label("", COL_IMG))           # espaço da imagem
        inventario_topo_layout.addWidget(header_label("Identificação", COL_IDENT))
        inventario_topo_layout.addWidget(header_label("ID",          COL_ID))#conversao necessaria int -> str
        inventario_topo_layout.addWidget(header_label("Dono",          COL_DONO))
        inventario_topo_layout.addWidget(header_label("Código único",  COL_COD))
        inventario_topo_layout.addWidget(header_label("Usos",          COL_USOS))
        inventario_topo_layout.addWidget(header_label("Devolução",     COL_DEVO))
        inventario_topo_layout.addWidget(header_label("Validade",      COL_DESC))
        inventario_topo_layout.addWidget(header_label("Descartado",    COL_CB))
        inv_topo_lay.addWidget(fundo_topo)
        
        inventario_base_layout = QVBoxLayout()
        #iterando esse layout para cada item no db
        item_container = QWidget()
        item_linha_layout = QHBoxLayout(item_container)
        invetario_centro_layout = QHBoxLayout()
        indentificacao_layout = QVBoxLayout()

        self.scroll_content = QWidget()
        scroll_area = QScrollArea()
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFixedHeight(5 * 80)  # ~ 5 linhas
        self.lista_itens_layout = QVBoxLayout(self.scroll_content)
        self.lista_itens_layout.setSpacing(10)
        self.lista_itens_layout.setContentsMargins(0, 0, 0, 0)
        db_itens = Inventario().Itens_totais()
        for item in db_itens:
              linha = self.criar_linha_item(item)
              linha.setFixedHeight(78)  # altura fixa por linha
              self.lista_itens_layout.addWidget(linha)
        self.lista_itens_layout.addStretch()  # empurra itens pro topo
        self.scroll_content.setLayout(self.lista_itens_layout)
        scroll_area.setWidget(self.scroll_content)


        #stylesheet nos layout
        #add layout na tela
        inventario_base_layout.addLayout(inv_topo_lay)
        inventario_base_layout.addWidget(scroll_area)  
        inventario_base_layout.addWidget(item_container)
        invetario_centro_layout.addLayout(indentificacao_layout)
        base_layout = QVBoxLayout()
        base_layout.addLayout(topo_layout)
        base_layout.addLayout(inventario_base_layout)
        self.setLayout(base_layout)
        #garantir atualizar a lista
        self.atualizar_lista()
    def atualizar_lista(self):
        while self.lista_itens_layout.count():
            item = self.lista_itens_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        db_itens = Inventario().Itens_totais()

        for item in db_itens:
            linha = self.criar_linha_item(item)
            linha.setFixedHeight(78)
            self.lista_itens_layout.addWidget(linha)

        self.lista_itens_layout.addStretch()

    def criar_linha_item(self, item) -> QWidget:
        COL_IMG   = 60
        COL_IDENT = 80
        COL_ID = 30
        COL_DONO  = 120
        COL_COD   = 80
        COL_USOS  = 140
        COL_DEVO  = 100
        COL_DESC  = 80
        COL_CB    = 60
        item_container = QWidget()
        item_container.setStyleSheet("background-color: #D9D9D9; color: #000000;")
        layout = QHBoxLayout(item_container)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(0)

        # imagem
        img_label = QLabel()
        img_label.setPixmap(QPixmap('app/ui/imgs/capacete-icon.png'))
        img_label.setScaledContents(True)
        img_label.setFixedSize(48, 60)
        img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        col_img = QWidget()
        col_img.setFixedWidth(COL_IMG)
        col_img_lay = QHBoxLayout(col_img)
        col_img_lay.setContentsMargins(0,0,0,0)
        col_img_lay.addWidget(img_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(col_img)

        # identificação
        ident = QWidget()
        ident.setFixedWidth(COL_IDENT)
        ident_lay = QVBoxLayout(ident)
        ident_lay.setContentsMargins(0,0,0,0)
        ident_lay.setSpacing(2)
        ident_lay.addWidget(QLabel(item.tipo_epi))
        ident_lay.addWidget(QLabel(f"CA: {item.ca}"))
        ident_lay.addWidget(QLabel(f"Cód: {item.cod_unico}"))
        layout.addWidget(ident)

        # colunas simples
        def col(text, width, align=Qt.AlignmentFlag.AlignCenter):
            lbl = QLabel(text)
            lbl.setFixedWidth(width)
            lbl.setAlignment(align)
            lbl.setWordWrap(True)
            return lbl

        layout.addWidget(col(str(item.id), COL_ID))#conversao necessaria int -> str
        layout.addWidget(col(item.dono, COL_DONO))
        layout.addWidget(col(item.cod_unico, COL_COD))
        layout.addWidget(col(item.usos_formatado, COL_USOS))
        layout.addWidget(col(item.data_devolucao, COL_DEVO))
        layout.addWidget(col(item.data_descarte, COL_DESC))

        # checkbox centralizado
        cb_container = QWidget()
        cb_container.setFixedWidth(COL_CB)
        cb_lay = QHBoxLayout(cb_container)
        cb_lay.setContentsMargins(0,0,0,0)
        cb = QCheckBox()
        cb.setChecked(item.descartado or False)
        cb_lay.addWidget(cb, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(cb_container)

        return item_container
#endregion main ui
#region historico
class Historico_ui(QWidget):
    def __init__(self,Inventario, gerenciar):
        super().__init__()
        self.setWindowTitle("historico do inventario")
        VoltarBotao = QPushButton("Inventario")
        VoltarBotao.clicked.connect(Inventario)
        topo_layout = QHBoxLayout()
        add_item =  QPushButton("Adicionar do inventario")
        add_item.clicked.connect(lambda: gerenciar("add"))
        rem_item =  QPushButton("Remover do inventario")
        rem_item.clicked.connect(lambda: gerenciar("rem"))
        edit_item =  QPushButton("Editar o inventario")
        edit_item.clicked.connect(lambda: gerenciar("edit"))
        topo_layout.addWidget(VoltarBotao)
        topo_layout.addWidget(add_item)
        topo_layout.addWidget(rem_item)
        topo_layout.addWidget(edit_item)


        #add layout na tela
        base_layout = QVBoxLayout()
        base_layout.addLayout(topo_layout)
        self.setLayout(base_layout)
#endregion historico
#region gerenciador de inventario
class GerenciadorInventario(QWidget):
    def __init__(self, Inventario, historico):
        super().__init__()
        self.IrInventario = Inventario
        self.Irhistorico = historico

        # botões fixos do topo
        self.InventarioBotao = QPushButton("Inventário")
        self.btn_add = QPushButton("Adicionar")
        self.btn_rem = QPushButton("Remover")
        self.btn_edit = QPushButton("Editar")
        self.btn_historico = QPushButton("Historico")
        
        self.InventarioBotao.clicked.connect(self.IrInventario)
        self.btn_historico.clicked.connect(self.Irhistorico)
        self.btn_add.clicked.connect(lambda: self.atualizar_tipo("add"))
        self.btn_rem.clicked.connect(lambda: self.atualizar_tipo("rem"))
        self.btn_edit.clicked.connect(lambda: self.atualizar_tipo("edit"))

        topo_layout = QHBoxLayout()
        topo_layout.addWidget(self.InventarioBotao)
        topo_layout.addWidget(self.btn_add)
        topo_layout.addWidget(self.btn_rem)
        topo_layout.addWidget(self.btn_edit)
        topo_layout.addWidget(self.btn_historico)

        # área de conteúdo dinâmico
        self.conteudo = QWidget()
        self.conteudo_layout = QHBoxLayout(self.conteudo)

        base_layout = QVBoxLayout()
        base_layout.addLayout(topo_layout)
        base_layout.addWidget(self.conteudo)
        self.setLayout(base_layout)
    #permitir a troca sem criar outras classes
    def _limpar_conteudo(self):
        while self.conteudo_layout.count():
            item = self.conteudo_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def add(self):
        self._limpar_conteudo()
    
        form = QWidget()
        form_layout = QFormLayout(form)
        form_layout.setSpacing(10)
    
        self.input_ca = QLineEdit()
        self.input_tipo = QLineEdit()
        self.input_dono = QLineEdit()
        self.input_usos = QLineEdit()
        self.input_devolucao = QDateEdit()
        self.input_devolucao.setCalendarPopup(True)
        self.input_devolucao.setDate(QDate.currentDate())
        self.input_descarte = QDateEdit()
        self.input_descarte.setCalendarPopup(True)
        self.input_descarte.setDate(QDate.currentDate())

        form_layout.addRow("CA:",self.input_ca)
        form_layout.addRow("Tipo de EPI:",self.input_tipo)
        form_layout.addRow("Responsável:",self.input_dono)
        form_layout.addRow("Usos:",self.input_usos)
        form_layout.addRow("Data devolução:",self.input_devolucao)
        form_layout.addRow("Data descarte:",self.input_descarte)

        btn_confirmar = QPushButton("Adicionar item")
        btn_confirmar.clicked.connect(self.confirmar_add)
        form_layout.addRow(btn_confirmar)

        self.conteudo_layout.addWidget(form)

        #data para descarte e devolução
    def confirmar_add(self):
        data_dev = self.input_devolucao.date().toPython()
        data_desc = self.input_descarte.date().toPython()

        Inventario().add_item(
            ca=self.input_ca.text(),
            tipo_epi=self.input_tipo.text(),
            dono=self.input_dono.text(),
            usos=self.input_usos.text(),
            data_descarte=str(data_desc),
            data_devolucao=str(data_dev)
        )
        self.IrInventario()
    def rem(self):
        self._limpar_conteudo()
        #"select de funcionario"
        self.ListaFuncionario = QComboBox() #itera de 
        DBListaFuncionarios=Inventario().RemListaFuncionarios()
        self.ListaFuncionario.addItems([f"ID: {id} nome: {nome} "for id,nome in DBListaFuncionarios])
        self.conteudo_layout.addWidget(self.ListaFuncionario)
        RemBotao = QPushButton("remover item")
        RemBotao.clicked.connect(self.confirmar_rem)
        self.conteudo_layout.addWidget(RemBotao)
    def confirmar_rem(self):
        texto = self.ListaFuncionario.currentText()
        item_id = int(texto.split("ID: ")[1].split(" ")[0])  # extrai o id do texto
        Inventario().rem_item(item_id)
        VoltarInventario = self.IrInventario
        VoltarInventario()

    def edit(self):
        self._limpar_conteudo()
        self.EditUi = QVBoxLayout()
        selecionar = QWidget()
        selecionar_layout = QFormLayout(selecionar)
        #"select de funcionario"
        self.ListaFuncionario = QComboBox()
        DBListaFuncionarios = Inventario().RemListaFuncionarios()
        self.ListaFuncionario.addItems(
            [f"ID: {id} nome: {nome}" for id, nome in DBListaFuncionarios]
        )
        SelecionarBotao = QPushButton("Selecionar")
        SelecionarBotao.clicked.connect(self.selecionar_edicao)
        EditBotao = QPushButton("Editar")
        EditBotao.clicked.connect(self.confirmar_edicao)
        selecionar_layout.addRow("Funcionário:", self.ListaFuncionario)
        selecionar_layout.addRow(SelecionarBotao)
        self.EditUi.addWidget(selecionar)
        #parte escondida até selecionar
        self.form = QWidget()
        self.form.hide()
        self.EditUi.addWidget(self.form)
        self.form_layout = QFormLayout(self.form)
        self.form_layout.setSpacing(10)
    
        self.input_ca = QLineEdit()
        self.input_tipo = QLineEdit()
        self.input_dono = QLineEdit()
        self.input_usos = QLineEdit()
        self.input_devolucao = QDateEdit()
        self.input_devolucao.setCalendarPopup(True)
        self.input_devolucao.setDate(QDate.currentDate())
        self.input_descarte = QDateEdit()
        self.input_descarte.setCalendarPopup(True)
        self.input_descarte.setDate(QDate.currentDate())

        self.form_layout.addRow("CA:",self.input_ca)
        self.form_layout.addRow("Tipo de EPI:",self.input_tipo)
        self.form_layout.addRow("Responsável:",self.input_dono)
        self.form_layout.addRow("Usos:",self.input_usos)
        self.form_layout.addRow("Data devolução:",self.input_devolucao)
        self.form_layout.addRow("Data descarte:",self.input_descarte)
        #
        self.EditUi.addWidget(EditBotao)
        self.conteudo_layout.addLayout(self.EditUi)
    def selecionar_edicao(self):
        texto = self.ListaFuncionario.currentText()
        item_id = int(texto.split("ID: ")[1].split(" ")[0])
        item = Inventario().SelFuncionario(item_id)
        if item:
            self.input_ca.setText(item.ca)
            self.input_tipo.setText(item.tipo_epi)
            self.input_dono.setText(item.dono)
            self.input_usos.setText(item.usos_formatado)
        self.form.show()
    def confirmar_edicao(self):
        texto = self.ListaFuncionario.currentText()
        self.item_id_edicao = int(texto.split("ID: ")[1].split(" ")[0])
        Inventario().edit_item(
            self.item_id_edicao,
            self.input_ca.text(),
            self.input_tipo.text(),
            self.input_dono.text(),
            self.input_usos.text().split(","),
            str(self.input_devolucao.date().toPython()),
            str(self.input_descarte.date().toPython())
        )
        self.IrInventario() 

    def atualizar_tipo(self, tipo):
        # reseta visibilidade
        for btn in [self.btn_add, self.btn_rem, self.btn_edit]:
            btn.setVisible(True)
        acoes = {"add": self.add, "rem": self.rem, "edit": self.edit}
        esconder = {"add": self.btn_add, "rem": self.btn_rem, "edit": self.btn_edit}
        if tipo in acoes:
            esconder[tipo].setVisible(False)
            acoes[tipo]()  #chama tela especifica
        self.setWindowTitle({"add": "Adicionar", "rem": "Remover", "edit": "Editar"}.get(tipo, ""))
#endregion gerenciador de inventario
#iniciando janela
window = Gerenciador_janelas()
window.show()
sys.exit(app.exec())
