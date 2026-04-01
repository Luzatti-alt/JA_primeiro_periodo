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
    def __init__(self):
        self._cache_itens = None

    def ItensTotais(self, force=False):#somente os visiveis(que seriam aqueles não deletados)
        if self._cache_itens is None or force:
            self._cache_itens = session.query(Itens).filter_by(Visivel=True).all()
        return self._cache_itens
    def GerarCodUnico(self, item):
        parte_dono = item.Dono[:3].upper()
        parte_ca = item.Ca[:4]

        desc = item.DataDescarte.replace("-", "")
        devo = item.DataDevolucao.replace("-", "")

        CodUnico = f"{parte_dono}{parte_ca}{desc[6:8]}{devo[6:8]}"

        item.CodUnico = CodUnico
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
        self.GerarCodUnico(NovoItemInventario)
        session.commit()
        self._cache_itens = None
    def RemItem(self,id):
        itens = session.query(Itens).filter_by(id=id).all()
        if itens:
            item = itens[0]
            item.Visivel = False
            #criar data para a verdadeira remoção
            session.commit()
            self._cache_itens = None
    def RemListaFuncionarios(self):
        itens = session.query(Itens).filter_by(Visivel=True).all()
        #criar listas separadas e juntar com zip desorderna isso
        return [(item.id, item.Dono) for item in itens]#nova lista mantendo ordem
    def SelFuncionario(self,ID):
        return session.query(Itens).filter_by(id=ID).first()
    def EditItem(self, Id, Ca, TipoEpi, Dono, Usos, DataDev, DataDesc):
        Item = session.query(Itens).filter_by(id=Id).first()
        if Item:
            try:
                # salva estado anterior antes de alterar
                EstadoAnterior = {
                    "Ca": Item.Ca,
                    "TipoEpi": Item.TipoEpi,
                    "Dono": Item.Dono,
                    "Usos": Item.Usos,
                    "DataDevolucao": Item.DataDevolucao,
                    "DataDescarte": Item.DataDescarte
                }
                EstadoNovo = {
                    "Ca": Ca,
                    "TipoEpi": TipoEpi,
                    "Dono": Dono,
                    "Usos": Usos,
                    "DataDevolucao": DataDev,
                    "DataDescarte": DataDesc
                }
                # aplica alteração
                Item.Ca = Ca
                Item.TipoEpi = TipoEpi
                Item.Dono = Dono
                Item.Usos = Usos
                Item.DataDevolucao = DataDev
                Item.DataDescarte = DataDesc
                # registra no historico
                Inv = session.query(Inventario).first()
                Registro = Historico(
                    Inventario_id=Inv.id,
                    IdItemAlterado=Id,
                    TiposAlteracao="edicao",
                    VersaoAnterior=EstadoAnterior,
                    VersaoAtual=EstadoNovo,
                    revertido=False
                )
                session.add(Registro)
                session.flush()  # garante ID

                self.GerarCodUnico(Item)

                session.commit()
                self._cache_itens = None
            except Exception as E:
                session.rollback()
                print(f"Erro ao editar: {E}")   
    def EditListaFuncionarios(self):
        itens = session.query(Itens).filter_by(Visivel=True).all()
        #criar listas separadas e juntar com zip desorderna isso
        return [(item.id, item.Dono) for item in itens]#nova lista mantendo ordem
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
        self._cache_itens = None
        return f"item foi descartado"
    def ReverterItem(self, Id, State):
        try:
            Registro = session.query(Historico).filter_by(id=Id).first()
            if not Registro:
                return "registro não encontrado"

            Registro.revertido = State
        
            if State:  # se marcou para reverter, restaura o item
                Item = session.query(Itens).filter_by(id=Registro.IdItemAlterado).first()
                if Item and Registro.VersaoAnterior:
                    Anterior = Registro.VersaoAnterior  # é um dict JSON
                    Item.Ca = Anterior.get("Ca", Item.Ca)
                    Item.TipoEpi = Anterior.get("TipoEpi", Item.TipoEpi)
                    Item.Dono = Anterior.get("Dono", Item.Dono)
                    Item.Usos = Anterior.get("Usos", Item.Usos)
                    Item.DataDevolucao = Anterior.get("DataDevolucao", Item.DataDevolucao)
                    Item.DataDescarte = Anterior.get("DataDescarte", Item.DataDescarte)
            else:  # se desmarcou, restaura para o estado novo
                Item = session.query(Itens).filter_by(id=Registro.IdItemAlterado).first()
                if Item and Registro.VersaoAtual:
                    Atual = Registro.VersaoAtual
                    Item.Ca = Atual.get("Ca", Item.Ca)
                    Item.TipoEpi = Atual.get("TipoEpi", Item.TipoEpi)
                    Item.Dono = Atual.get("Dono", Item.Dono)
                    Item.Usos = Atual.get("Usos", Item.Usos)
                    Item.DataDevolucao = Atual.get("DataDevolucao", Item.DataDevolucao)
                    Item.DataDescarte = Atual.get("DataDescarte", Item.DataDescarte)
        
            #apagar do db
            session.delete(Registro)
            session.commit()
            self._cache_itens = None
            return "item revertido"
        except Exception as E:
            session.rollback()
            return "erro ao reverter"
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
    VersaoAnterior = Column(JSON)
    VersaoAtual = Column(JSON)
    revertido = Column(Boolean,default=False)
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