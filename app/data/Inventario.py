from requests import session
from sqlalchemy import create_engine, Column, Integer, String, JSON, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import date
import os

# config BD
engine = create_engine('sqlite:///GuindastesRibasDB.db', echo=True)
Base = declarative_base()

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
        itens = session.query(Itens).filter_by(Visivel=True).all()
        for item in itens:
            if isinstance(item.usos, list):
                item.usos_formatado = ", ".join(item.usos)#uso 1 , uso 2
            else:
                item.usos_formatado = str(item.usos)
        return itens

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


if __name__ == '__main__':
    #auto atualizar o db
    if os.path.exists('GuindastesRibasDB.db'):
        os.remove('GuindastesRibasDB.db')
    Base.metadata.create_all(engine)
    fake_data()