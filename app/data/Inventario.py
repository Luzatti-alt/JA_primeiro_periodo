from sqlalchemy import or_, create_engine, Column, Integer, String, JSON, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import date
import logging
import os
import sys

# config BD
Base = declarative_base()
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)  # pasta do .exe
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "GuindastesRibasDB.db")
engine = create_engine(f'sqlite:///{db_path}', echo=True)
logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
#region DB_config

class Itens(Base):
    __tablename__ = 'itens'

    id = Column(Integer, primary_key=True)
    Visivel = Column(Boolean,default=True)#qnd "excluir" so ira fazer com que nao apareca
    #isso por 6 meses 1²anos algo assim dps disso não precisaria do dado de qualquer forma
    ca = Column(String)
    cod_unico = Column(String)
    tipo_epi = Column(String)
    dono = Column(String)
    usos = Column(JSON)
    data_descarte = Column(String)
    data_devolucao = Column(String)
    descartado = Column(Boolean)
    inventario_id = Column(Integer, ForeignKey("inventario.id"))
    inventario = relationship("Inventario", back_populates="itens")
    #decorator para funcionar melhor
    @property
    def usos_formatado(self):
        if isinstance(self.usos, list):
            return ", ".join(self.usos)
        return str(self.usos) if self.usos else ""
#endregion
class Inventario(Base):
    __tablename__ = 'inventario'
    id = Column(Integer, primary_key=True)
    itens = relationship("Itens", back_populates="inventario")
    historico = relationship("Historico", back_populates="inventario")
class InventarioFuncionalidade():
    def add_item(self, ca, tipo_epi, dono, usos, data_descarte, data_devolucao): #add class de itens_como tipo
        inv = session.query(Inventario).first()
        NovoItemInventario = Itens(
            ca=ca,
            tipo_epi=tipo_epi,
            dono=dono,
            usos=usos,
            data_descarte=data_descarte,
            data_devolucao=data_devolucao,
            Visivel=True,
            descartado=False,
            inventario=inv
            )
        session.add(NovoItemInventario)
        session.commit()
    def rem_item(self,id):
        itens = session.query(Itens).filter_by(id=id).all()
        if itens:
            item = itens[0]
            item.Visivel = False
            session.commit()
        pass
    def RemListaFuncionarios(self):
        itens = session.query(Itens).filter_by(Visivel=True).all()
        #criar listas separadas e juntar com zip desorderna isso
        return [(item.id, item.dono) for item in itens]#nova lista mantendo ordem
    def SelFuncionario(self,ID):
        return session.query(Itens).filter_by(id=ID).first()
    def EditItem(self, id, ca, tipo_epi, dono, usos, data_dev, data_desc):
        item = session.query(Itens).filter_by(id=id).first()
        if item:
            item.ca = ca
            item.tipo_epi = tipo_epi
            item.dono = dono
            item.usos = usos
            item.data_devolucao = data_dev
            item.data_descarte = data_desc
            session.commit()    
    def EditListaFuncionarios(self):
        itens = session.query(Itens).filter_by(Visivel=True).all()
        #criar listas separadas e juntar com zip desorderna isso
        return [(item.id, item.dono) for item in itens]#nova lista mantendo ordem
    def ItensTotais(self):
        #somente os visiveis
        return session.query(Itens).filter_by(Visivel=True).all()
    def pesquisar(self,pesquisar):
        print(f"pesquisou {pesquisar}")
        #ilike(case sensitive) like(insensitive)
        '''
        %texto% encontra qualquer valor que contenha o termo buscado.
        '''
        ItemPesquisado = session.query(Itens).filter(
            #pesquisa em todos as colunas do sqlalchemy
            or_(
                Itens.ca.like(f"%{pesquisar}%"),
                Itens.cod_unico.like(f"%{pesquisar}%"),
                Itens.tipo_epi.like(f"%{pesquisar}%"),
                Itens.dono.like(f"%{pesquisar}%"),
                Itens.usos.like(f"%{pesquisar}%"),
                Itens.data_descarte.like(f"%{pesquisar}%"),
                Itens.data_devolucao.like(f"%{pesquisar}%"),
                Itens.descartado.like(f"%{pesquisar}%")
                )).all()
        return ItemPesquisado
    def descartearItem(self,id,state):
        item = session.query(Itens).filter_by(id=id).first()
        item.descartado = state
        session.commit()
        return f"item foi descartado"
    def ReverterItem(self,id,state):
        item = session.query(Historico).filter_by(id=id).first()
        item.revertido = state
        session.commit()
        #falta reverter na tabela de itens
        return f"item foi alterado"
    def ItensHistorico(self):
        return session.query(Historico).all()
class Historico(Base):
    #aplicar a todos os itens que forem alterados ou "removidos"
    __tablename__ = 'Historico'
    id = Column(Integer, primary_key=True)
    inventario_id = Column(Integer, ForeignKey("inventario.id"))
    inventario = relationship("Inventario", back_populates="historico")
    id_item_alterado = Column(Integer)
    tipo_alteração = Column(String(50))
    versao_anterior = Column(String(200))
    versao_atual = Column(String(50))
    revertido = Column(Boolean,default=False)
# criar sessão ANTES de usar
Session = sessionmaker(bind=engine)
session = Session()


#region fake_data
def fake_data():
    try:
        inv = Inventario()
        session.add(inv)

        for i in range(100):
            novo_item = Itens(
                ca=f"ca {i}",
                cod_unico=f"cod {i}",
                tipo_epi = f"capacete tipo {i}",
                dono=f"fulano {i*20}",
                usos=[f"uso {i+1}", f"uso {i+3}"],
                data_descarte="10/10/2026",
                data_devolucao = "09/10/2026",
                descartado=False,
                inventario=inv
            )
            session.add(novo_item)
        session.flush()#envia ao db sem commit no db 
        tipos = ["adicao", "edicao", "remocao"]
        for i, item in enumerate(inv.itens):
            registro = Historico(
                inventario_id=inv.id,
                id_item_alterado=item.id,
                tipo_alteração=tipos[i % 3],
                versao_anterior=f"capacete tipo {i} / fulano {i*20}",
                versao_atual=f"capacete tipo {i} atualizado / fulano {i*20}"
            )
            session.add(registro)

        session.commit()


    except Exception as e:
        session.rollback()
        print(f'Erro ao criar dados de debug: {e}')
#endregion
Base.metadata.create_all(engine)  
Session = sessionmaker(bind=engine)
session = Session()
log_path = os.path.join(BASE_DIR, 'db.log')
log = logging.FileHandler(filename=log_path, encoding='utf-8', mode='w')
logging.getLogger("sqlalchemy.engine").addHandler(log)
if __name__ == '__main__':
    #auto atualizar o db
    if os.path.exists('GuindastesRibasDB.db'):
        os.remove('GuindastesRibasDB.db')
    fake_data()
    Base.metadata.create_all(engine)