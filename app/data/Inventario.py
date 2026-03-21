from sqlalchemy import create_engine, Column, Integer, String, JSON, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import date

# config BD
engine = create_engine('sqlite:///GuindastesRibasDB.db', echo=True)
Base = declarative_base()

#region DB_config
class Inventario(Base):
    __tablename__ = 'inventario'

    id = Column(Integer, primary_key=True)
    itens = relationship("Itens", back_populates="inventario")


class Itens(Base):
    __tablename__ = 'itens'

    id = Column(Integer, primary_key=True)
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


# criar sessão ANTES de usar
Session = sessionmaker(bind=engine)
session = Session()


#region fake_data
def fake_data():
    try:
        inv = Inventario()
        session.add(inv)

        for i in range(3):
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
    Base.metadata.create_all(engine)
    fake_data()