from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtGui import QColor, QPalette, QIcon, QSurfaceFormat, QShortcut, QKeySequence, QPixmap
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


#interfaces graficas

#interface principal
class Inventario_ui(QWidget):
    def __init__ (self):
        super().__init__()
        self.setWindowTitle("sistema de inventario")
        self.setWindowIcon(QIcon("app/src/ui/imgs/ideia_de_logo_app_JA.png"))
        #topo ui
        topo_layout = QHBoxLayout()
        add_item =  QPushButton("Adicionar do inventario")
        rem_item =  QPushButton("Remover do inventario")
        edit_item =  QPushButton("Editar o inventario")
        historico = QPushButton("Historico")
        topo_layout.addWidget(add_item)
        topo_layout.addWidget(rem_item)
        topo_layout.addWidget(edit_item)
        topo_layout.addWidget(historico)

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
        COL_IDENT = 200
        COL_DONO  = 120
        COL_COD   = 100
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

        lista_itens_layout = QVBoxLayout()
        scroll_area = QScrollArea()
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFixedHeight(5 * 80)  # ~ 5 linhas
        scroll_content = QWidget()
        lista_itens_layout = QVBoxLayout(scroll_content)
        lista_itens_layout.setSpacing(10)
        lista_itens_layout.setContentsMargins(0, 0, 0, 0)
        db_itens = Inventario().Itens_totais()
        for item in db_itens:
              linha = self.criar_linha_item(item)
              linha.setFixedHeight(78)  # altura fixa por linha
              lista_itens_layout.addWidget(linha)
        lista_itens_layout.addStretch()  # empurra itens pro topo
        scroll_content.setLayout(lista_itens_layout)
        scroll_area.setWidget(scroll_content)


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

    def criar_linha_item(self, item) -> QWidget:
        COL_IMG   = 60
        COL_IDENT = 200
        COL_DONO  = 120
        COL_COD   = 100
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

        layout.addWidget(col(item.dono,          COL_DONO))
        layout.addWidget(col(item.cod_unico,     COL_COD))
        layout.addWidget(col(item.usos,           COL_USOS))
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
#iniciando janela
window = Inventario_ui()
window.show()
sys.exit(app.exec())
