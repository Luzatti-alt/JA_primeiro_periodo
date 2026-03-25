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
                  QPushButton {{background-color: {paleta_cores['botao']};color: {paleta_cores['texto']}}}
                  QLabel{{
                  color: {paleta_cores['texto']};
                  }}
                  QCheckBox::indicator {{
                    width: 18px;
                    height: 18px;
                    border: 2px solid {paleta_cores['texto']};
                    border-radius: 3px;
                    background-color: {paleta_cores['botao']};
                    }}
                  QCheckBox::indicator:checked {{
                    background-color: #1a3dff;
                    border: 2px solid {paleta_cores['ativo']};
    }}
""")
imagens = {
    "capacete": "imagens/capacete.png"
}


#interfaces graficas

#interface principal
class Inventario_ui(QWidget):
    def __init__ (self):
        super().__init__()
        self.setWindowTitle("sistema de inventario")
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

        ident_text = QLabel("Identificação")
        inventario_topo_layout.addWidget(ident_text)
        dono_text = QLabel("Dono")
        inventario_topo_layout.addWidget(dono_text)
        cod_unico_text = QLabel("Código único")
        inventario_topo_layout.addWidget(cod_unico_text)
        usos_text = QLabel("Usos")
        inventario_topo_layout.addWidget(usos_text)
        val_text = QLabel("Validade")
        inventario_topo_layout.addWidget(val_text)
        devo_text = QLabel("Devolução")
        inventario_topo_layout.addWidget(devo_text)
        descartado_text = QLabel("Descartado")
        inventario_topo_layout.addWidget(descartado_text)

        inv_topo_lay.addWidget(fundo_topo)
        
        inventario_base_layout = QVBoxLayout()
        #iterando esse layout para cada item no db
        item_container = QWidget()
        item_linha_layout = QHBoxLayout(item_container)
        invetario_centro_layout = QHBoxLayout()
        indentificacao_layout = QVBoxLayout()

        lista_itens_layout = QVBoxLayout()

        db_itens = Inventario().Itens_totais()
        for item in db_itens:
            lista_itens_layout.addWidget(self.criar_linha_item(item))


        #stylesheet nos layout
        #add layout na tela
        inventario_base_layout.addLayout(inv_topo_lay)
        inventario_base_layout.addLayout(lista_itens_layout)  
        inventario_base_layout.addWidget(item_container)
        invetario_centro_layout.addLayout(indentificacao_layout)
        base_layout = QVBoxLayout()
        base_layout.addLayout(topo_layout)
        base_layout.addLayout(inventario_base_layout)
        self.setLayout(base_layout)

    def criar_linha_item(self, item) -> QWidget:
        item_container = QWidget()
        item_container.setStyleSheet("background-color: #D9D9D9; color: #000000;")
        item_linha_layout = QHBoxLayout(item_container)

        # imagem (futuramente: imagens[item.tipo_epi])
        img_pixmap = QPixmap('app/ui/imgs/capacete-icon.png')
        img_label = QLabel()
        img_label.setPixmap(img_pixmap)
        img_label.setScaledContents(True)
        img_label.setFixedSize(48, 60)
        item_linha_layout.addWidget(img_label)

        # identificação
        ident_layout = QVBoxLayout()
        ident_layout.addWidget(QLabel(item.tipo_epi))
        ident_layout.addWidget(QLabel(f"CA: {item.ca}"))
        ident_layout.addWidget(QLabel(f"Cód: {item.cod_unico}"))
        item_linha_layout.addLayout(ident_layout)

        # outras colunas
        outras_layout = QHBoxLayout()
        outras_layout.addWidget(QLabel(item.dono))
        outras_layout.addWidget(QLabel(item.cod_unico))
        outras_layout.addWidget(QLabel(str(item.usos)))
        outras_layout.addWidget(QLabel(item.data_devolucao))
        outras_layout.addWidget(QLabel(item.data_descarte))
        cb = QCheckBox()
        cb.setChecked(item.descartado or False)
        outras_layout.addWidget(cb)
        item_linha_layout.addLayout(outras_layout)
        return item_container
#iniciando janela
window = Inventario_ui()
window.show()
sys.exit(app.exec())