#region base do sistema
#region imports
from sqlalchemy import or_, create_engine, Column, Integer, String, JSON, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import *
import logging
from flask_bcrypt import Bcrypt
import os
import sys
#endregion imports

#region DB_config
Base = declarative_base()
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)  # pasta do .exe
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DbPath = os.path.join(BASE_DIR, "GuindastesRibasDB.db")
engine = create_engine(f'sqlite:///{DbPath}', echo=True)
bcrypt = Bcrypt() #criptografia
logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

#fazer algo para localmente não ser facil de achar conta e afins
class Contas(Base):
    __tablename__ = 'conta'
    id = Column(Integer, primary_key=True)
    Conta = Column(String(50))
    Senha = Column(String(50))
    cargo = Column(String(50))#para o caso de expandir para api/caso futuramente o funcionario tiver
    #a opção de ver os seus epi via app
    InventarioId = Column(Integer, ForeignKey("Inventario.id")) 
    Inventario = relationship("Inventario", back_populates="contas")
    def RemoverConta():
        #adicionar isso dps
        pass
    def login(Usuario,senha):
        #adicionar hash
        logar = session.query(Contas).filter_by(Conta=Usuario,Senha=senha).all()
        if logar:
            return True
        else:
            return False
    def IdLogado(Usuario):
        conta = session.query(Contas).filter_by(Conta=Usuario).first()
        return conta.id if conta else None
    def Cadastrar(Usuario,Senha,Cargo):
        conta = Contas(
            Conta = Usuario,
            Senha = Senha,
            cargo = Cargo
        )
        session.add(conta)
        session.commit()
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
    CriadoPor = Column(String)
    DataDescarte = Column(String)
    DataDevolucao = Column(String)
    DataRegistro = Column(String)
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

class Reverter(Base):
    #aplicar a todos os itens que forem alterados ou "removidos"
    __tablename__ = 'Reverter'
    id = Column(Integer, primary_key=True)
    Inventario_id = Column(Integer, ForeignKey("Inventario.id"))
    Inventario = relationship("Inventario", back_populates="Reverter")
    IdItemAlterado = Column(Integer)
    TiposAlteracao = Column(String(50))
    VersaoAnterior = Column(JSON)
    VersaoAtual = Column(JSON)
    QuemAlterou = Column(String)
    revertido = Column(Boolean,default=False)

class Historico(Base):
    #aplicar a todos os itens que forem alterados ou "removidos"
    __tablename__ = 'Historico'
    id = Column(Integer, primary_key=True)
    Inventario_id = Column(Integer, ForeignKey("Inventario.id"))
    Inventario = relationship("Inventario", back_populates="Historico")
    IdItemAlterado = Column(Integer)
    TiposAlteracao = Column(String(50))
    VersaoAnterior = Column(JSON)
    QuemAlterou = Column(String)
    VersaoAtual = Column(JSON)

class Inventario(Base):
    __tablename__ = 'Inventario'
    id = Column(Integer, primary_key=True)
    itens = relationship("Itens", back_populates="Inventario")
    Reverter = relationship("Reverter", back_populates="Inventario")
    Historico = relationship("Historico", back_populates="Inventario")
    contas = relationship("Contas", back_populates="Inventario")

#endregion DB_config

#endregion base do sistema

#region funcionalidades
class GerenciadorTemporal():
    def __init__(self):
        pass
    def ConferirValDev(self):
        #ve se esta valido ou se já era para ser devolvido
        hoje = date.today()
        itens = session.query(Itens).filter_by(Visivel=True,Descartado=False).all()
        alertas = []
        for item in itens:
            try:
                devolucao = date.fromisoformat(item.DataDevolucao)
                dias = (devolucao - hoje).days
                if dias < 0:
                    alertas.append((item, "atrasado", dias))
                elif dias <= 7:
                    alertas.append((item, "proximo", dias))
            except (ValueError, TypeError):
                pass
        return alertas
    def ExclusaoVerdadeira(self):
        #apos x meses ele ira deletar no db
        pass

class InventarioFuncionalidade():
    def __init__(self):
        self._cache_itens = None

    #optimizar query e usabilidade do usuario
    PAGE_SIZE = 30
 
    def ItensTotais(self, force=False):#somente os visiveis(que seriam aqueles não deletados)
        if self._cache_itens is None or force:
            self._cache_itens = (
                session.query(Itens)
                .filter_by(Visivel=True)
                .limit(self.PAGE_SIZE)
                .all()
            )
        return self._cache_itens
 
    def ItensPaginados(self, offset=0, limit=None):
        """Retorna itens visíveis com paginação. Usado para lazy loading no scroll."""
        if limit is None:
            limit = self.PAGE_SIZE
        return (
            session.query(Itens)
            .filter_by(Visivel=True)
            .offset(offset)
            .limit(limit)
            .all()
        )
 
    def TotalItens(self):
        """Conta total de itens visíveis no banco (sem carregar todos)."""
        return session.query(Itens).filter_by(Visivel=True).count()

    def GerarCodUnico(self, item):
        parte_dono = item.Dono[:3].upper()
        parte_ca = item.Ca[:4]

        desc = item.DataDescarte.replace("-", "")
        devo = item.DataDevolucao.replace("-", "")

        CodUnico = f"{parte_dono}{parte_ca}{desc[6:8]}{devo[6:8]}"

        item.CodUnico = CodUnico
    
    def AddItem(self,Registrodata,registro, ca, tipo_epi, dono, usos, data_descarte, data_devolucao): #add class de itens_como tipo
        inv = session.query(Inventario).first()
        conta = session.query(Contas).filter_by(id=registro).first()
        nome_criador = conta.Conta if conta else str(registro)

        NovoItemInventario = Itens(
            Ca=ca,
            TipoEpi=tipo_epi,
            Dono=dono,
            Usos=usos,
            DataRegistro  = Registrodata,
            DataDescarte=data_descarte,
            DataDevolucao=data_devolucao,
            Visivel=True,
            CriadoPor = nome_criador,
            Descartado=False,
            Inventario=inv
            )
        session.add(NovoItemInventario)
        self.GerarCodUnico(NovoItemInventario)
        session.commit()
        self._cache_itens = None
    
    def RemItem(self,id,registro):
        itens = session.query(Itens).filter_by(id=id)
        if itens:
            conta = session.query(Contas).filter_by(id=registro).first()
            nome_criador = conta.Conta if conta else str(registro)
            estado_anterior = {"Visivel": True}
            estado_novo     = {"Visivel": False}
            
            itens.Visivel = False

            Inv = session.query(Inventario).first()
            session.add(Historico(
                Inventario_id=Inv.id,
                IdItemAlterado=id,
                TiposAlteracao="remocao",
                VersaoAnterior=estado_anterior,
                VersaoAtual=estado_novo,
                QuemAlterou=nome_criador
            ))
            session.commit()
            self._cache_itens = None
    
    def RemListaFuncionarios(self):
        itens = session.query(Itens).filter_by(Visivel=True).all()
        #criar listas separadas e juntar com zip desorderna isso
        return [(item.id, item.Dono) for item in itens]#nova lista mantendo ordem
    
    def SelFuncionario(self,ID):
        return session.query(Itens).filter_by(id=ID).first()
    
    def EditItem(self,registro, Id, Ca, TipoEpi, Dono, Usos, DataDev, DataDesc):
        Item = session.query(Itens).filter_by(id=Id).first()
        conta = session.query(Contas).filter_by(id=registro).first()
        nome_criador = conta.Conta if conta else str(registro)
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
                    "DataDescarte": DataDesc,
                    "QuemALterou": nome_criador
                }
                # aplica alteração
                Item.Ca = Ca
                Item.TipoEpi = TipoEpi
                Item.Dono = Dono
                Item.Usos = Usos
                Item.DataDevolucao = DataDev
                Item.DataDescarte = DataDesc
                # registra no Reverter
                Inv = session.query(Inventario).first()
                Registro = Reverter(
                    Inventario_id=Inv.id,
                    IdItemAlterado=Id,
                    TiposAlteracao="edicao",
                    VersaoAnterior=EstadoAnterior,
                    VersaoAtual=EstadoNovo,
                    QuemAlterou = nome_criador,
                    revertido=False
                )
                RegistroHistorico = Historico(
                    Inventario_id=Inv.id,
                    IdItemAlterado=Id,
                    TiposAlteracao="edicao",
                    VersaoAnterior=EstadoAnterior,
                    QuemAlterou = nome_criador,
                    VersaoAtual=EstadoNovo
                )
                session.add(Registro)
                session.add(RegistroHistorico)
                session.commit()
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
    #melhorar o historico para quem alterou a em qualquer mudança de itens dalvar no historioco
    #isso esta parcialmente integrado
    def descartearItem(self,id,state,registro):
        item = session.query(Itens).filter_by(id=id).first()
        conta = session.query(Contas).filter_by(id=registro).first()
        nome_criador = conta.Conta if conta else str(registro)#add em historico a alteração
        item.Descartado = state
        #add alteração no outro banco de dados
        estado_anterior = {"Descartado": item.Descartado}
        estado_novo     = {"Descartado": state}

        Inv = session.query(Inventario).first()
        session.add(Historico(
            Inventario_id=Inv.id,
            IdItemAlterado=id,
            TiposAlteracao="descarte",
            VersaoAnterior=estado_anterior,
            VersaoAtual=estado_novo,
            QuemAlterou=nome_criador
            ))
        session.commit()
        self._cache_itens = None
        return f"item foi descartado"
    
    def ReverterItem(self, Id, State,registro):
        try:
            Registro = session.query(Reverter).filter_by(id=Id).first()
            if not Registro:
                return "registro não encontrado"
            conta = session.query(Contas).filter_by(id=registro).first()
            nome_criador = conta.Conta if conta else str(registro)

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
            Registro.revertido = True
            session.commit()
            self._cache_itens = None
            return "item revertido"
        except Exception as E:
            session.rollback()
            return "erro ao reverter"
        return f"item foi alterado"
    
    def ItensReverter(self):
        return session.query(Reverter).all()
    
    def ItensHistorico(self):
        return session.query(Historico).all()

# criar sessão ANTES de usar
Session = sessionmaker(bind=engine)
session = Session()

#endregion funcionalidades

#region fake_data

#temporario até a aplicação ser finalizada
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
        conta = Contas(
            Conta = "Lucas G",
            senha = "123467",
            cargo = "adm supremo"
        )
        session.add(conta)
        session.commit()

    except Exception as e:
        session.rollback()
        print(f'Erro ao criar dados de debug: {e}')
#endregion

#region rodar
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
    GerenciadorTemporal()
#endregion rodar