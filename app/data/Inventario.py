from sqlalchemy import create_engine, Column, Integer, String, JSON, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import date
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
    def __init__(self):
        pass
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
    def edit_item(self, id, ca, tipo_epi, dono, usos, data_dev, data_desc):
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
    def Itens_totais(self):
        #somente os visiveis
        return session.query(Itens).filter_by(Visivel=True).all()

# criar sessão ANTES de usar
Session = sessionmaker(bind=engine)
session = Session()


#region fake_data
def fake_data():
    try:
        inv = Inventario()
        session.add(inv)

        for i in range(10):
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

        session.commit()

    except Exception as e:
        session.rollback()
        print(f'Erro ao criar dados de debug: {e}')
#endregion
fake_data()
Base.metadata.create_all(engine)
fake_data()
if __name__ == '__main__':
    #auto atualizar o db
    if os.path.exists('GuindastesRibasDB.db'):
        os.remove('GuindastesRibasDB.db')
    fake_data()
    Base.metadata.create_all(engine)