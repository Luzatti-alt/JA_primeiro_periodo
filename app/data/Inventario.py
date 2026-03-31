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
DbPath = os.path.join(BASE_DIR, "GuindastesRibasDB.db")
engine = create_engine(f'sqlite:///{DbPath}', echo=True)
logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
#region DB_config

class Itens(Base):
    __tablename__ = 'itens'

    id = Column(Integer, primary_key=True)
    Visivel = Column(Boolean,default=True)#qnd "excluir" so ira fazer com que nao apareca
    #isso por 6 meses 1²anos algo assim dps disso não precisaria do dado de qualquer forma
    Ca = Column(String)
    CodUnico = Column(String)
    TipoEpi = Column(String)
    Dono = Column(String)
    Usos = Column(JSON)
    DataDescarte = Column(String)
    DataDevolucao = Column(String)
    Descartado = Column(Boolean)
    InventarioId = Column(Integer, ForeignKey("Inventario.id"))
    Inventario = relationship("Inventario", back_populates="itens")
    DataDeletar = Column(String())#livrar espaço de itens que ja estão marcados como removidos faz tempo
    #decorator para funcionar melhor
    @property
    def usos_formatado(self):
        if isinstance(self.Usos, list):
            return ", ".join(self.Usos)
        return str(self.Usos) if self.Usos else ""
#endregion
class Inventario(Base):
    __tablename__ = 'Inventario'
    id = Column(Integer, primary_key=True)
    itens = relationship("Itens", back_populates="Inventario")
    historico = relationship("Historico", back_populates="Inventario")
class InventarioFuncionalidade():
    def AddItem(self, ca, tipo_epi, dono, usos, data_descarte, data_devolucao): #add class de itens_como tipo
        inv = session.query(Inventario).first()
        NovoItemInventario = Itens(
            Ca=ca,
            TipoEpi=tipo_epi,
            Dono=dono,
            Usos=usos,
            DataDescarte=data_descarte,
            DataDevolucao=data_devolucao,
            Visivel=True,
            Descartado=False,
            Inventario=inv
            )
        session.add(NovoItemInventario)
        session.commit()
    def RemItem(self,id):
        itens = session.query(Itens).filter_by(id=id).all()
        if itens:
            item = itens[0]
            item.Visivel = False
            #criar data para a verdadeira remoção
            session.commit()
        pass
    def RemListaFuncionarios(self):
        itens = session.query(Itens).filter_by(Visivel=True).all()
        #criar listas separadas e juntar com zip desorderna isso
        return [(item.id, item.Dono) for item in itens]#nova lista mantendo ordem
    def SelFuncionario(self,ID):
        return session.query(Itens).filter_by(id=ID).first()
    def EditItem(self, id, ca, tipo_epi, dono, usos, data_dev, data_desc):
        item = session.query(Itens).filter_by(id=id).first()
        if item:
            item.Ca = ca
            item.TipoEpi = tipo_epi
            item.Dono = dono
            item.Usos = usos
            item.DataDevolucao = data_dev
            item.DataDescarte = data_desc
            #falta colocar no historico a versão antiga
            session.commit()    
    def EditListaFuncionarios(self):
        itens = session.query(Itens).filter_by(Visivel=True).all()
        #criar listas separadas e juntar com zip desorderna isso
        return [(item.id, item.Dono) for item in itens]#nova lista mantendo ordem
    def ItensTotais(self):#somente os visiveis(que seriam aqueles não deletados)
        return session.query(Itens).filter_by(Visivel=True).all()
    #add funcao que se for invisivel e der x meses ele realmente deletar do db
    def pesquisar(self,pesquisar):
        #ilike(case sensitive) like(insensitive)
        '''
        %texto% encontra qualquer valor que contenha o termo buscado.
        '''
        ItemPesquisado = session.query(Itens).filter(
            #pesquisa em todos as colunas do sqlalchemy
            or_(
                Itens.Ca.like(f"%{pesquisar}%"),
                Itens.CodUnico.like(f"%{pesquisar}%"),
                Itens.TipoEpi.like(f"%{pesquisar}%"),
                Itens.Dono.like(f"%{pesquisar}%"),
                Itens.Usos.like(f"%{pesquisar}%"),
                Itens.DataDescarte.like(f"%{pesquisar}%"),
                Itens.DataDevolucao.like(f"%{pesquisar}%"),
                Itens.Descartado.like(f"%{pesquisar}%")
                )).all()
        return ItemPesquisado
    def descartearItem(self,id,state):
        item = session.query(Itens).filter_by(id=id).first()
        item.Descartado = state
        #add alteração no outro banco de dados
        session.commit()
        return f"item foi descartado"
    def ReverterItem(self,id,state):
        item = session.query(Historico).filter_by(id=id).first()
        item.revertido = state
        #add alteração no outro banco de dados
        session.commit()
        #falta reverter na tabela de itens
        return f"item foi alterado"
    def ItensHistorico(self):
        return session.query(Historico).all()
class Historico(Base):
    #aplicar a todos os itens que forem alterados ou "removidos"
    __tablename__ = 'Historico'
    id = Column(Integer, primary_key=True)
    Inventario_id = Column(Integer, ForeignKey("Inventario.id"))
    Inventario = relationship("Inventario", back_populates="historico")
    IdItemAlterado = Column(Integer)
    TiposAlteracao = Column(String(50))
    VersaoAnterior = Column(String(200))
    VersaoAtual = Column(String(50))
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
                Ca=f"ca {i}",
                CodUnico=f"cod {i}",
                TipoEpi = f"capacete tipo {i} v2",
                Dono=f"fulano {i*20}",
                Usos=[f"uso {i+1}", f"uso {i+3}"],
                DataDescarte="10/10/2026",
                DataDevolucao = "09/10/2026",
                Descartado=False,
                Inventario=inv
            )
            session.add(novo_item)
        session.flush()#envia ao db sem commit no db 
        tipos = ["adicao", "edicao", "remocao"]
        for i, item in enumerate(inv.itens):
            registro = Historico(
                Inventario_id=inv.id,
                IdItemAlterado=item.id,
                TiposAlteracao=tipos[i % 3],
                VersaoAnterior=f"capacete tipo {i} / fulano {i*20}",
                VersaoAtual=f"capacete tipo {i} v2 / fulano {i*20}"
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