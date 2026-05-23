#region base do sistema
#region imports
from sqlalchemy import or_, create_engine, Column, Integer, String, JSON, Boolean, ForeignKey, func
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import date, datetime, timedelta
import bcrypt as Brycpt
import os
import sys
#endregion imports

#region Db Config
Base = declarative_base()
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)  # pasta do .exe
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DbPath = os.path.join(BASE_DIR, "GuindastesRibasDB.db")
engine = create_engine(f'sqlite:///{DbPath}')

class Contas(Base):
    __tablename__ = 'conta'
    id = Column(Integer, primary_key=True)
    Conta = Column(String(50))
    Senha = Column(String(255))
    cargo = Column(String(50))#para o caso de expandir para api/caso futuramente o funcionario tiver
    #a opção de ver os seus epi via app
    
    InventarioId = Column(Integer, ForeignKey("Inventario.id"))
    Inventario = relationship("Inventario", back_populates="contas")

    def ListarContas():
        contas = session.query(Contas).all()
        return [(c.id, c.Conta) for c in contas]

    def RemoverConta(Usuario):
        conta = session.query(Contas).filter_by(Conta=Usuario).first()
        if conta:
            session.delete(conta)
            session.commit()
            return True
        return False

    def login(Usuario, Senha):
        conta = session.query(Contas).filter_by(Conta=Usuario).first()
        if conta and Brycpt.checkpw(Senha.encode(), conta.Senha.encode()):
            return True
        return False

    def IdLogado(Usuario):
        conta = session.query(Contas).filter_by(Conta=Usuario).first()
        return conta.id if conta else None

    def Cadastrar(Usuario, Senha, Cargo) -> None:
        HashSenha = Brycpt.hashpw(Senha.encode(), Brycpt.gensalt()).decode()
        conta = Contas(Conta=Usuario, Senha=HashSenha, cargo=Cargo)
        session.add(conta)
        session.commit()

class Funcionarios(Base):
    __tablename__ = 'Funcionarios'
    id = Column(Integer, primary_key=True)
    Nome = Column(String(70))
    Email = Column(String(70))
    Cargo = Column(String(70))
    DataAdmissao = Column(String)       # ISO: YYYY-MM-DD
    Status = Column(String(30), default="Ativo")  # Ativo | Inativo | Férias | Licença
    ListaEpiAtual = Column(JSON)
    ListaDevAtrasadas = Column(JSON)
    QuantidadeDevAtrasadas = Column(Integer)
    ListaDevEmDia = Column(JSON)
    QuantidadeDevEmDia = Column(Integer)

class Itens(Base):
    __tablename__ = 'itens'
    id = Column(Integer, primary_key=True)
    Visivel = Column(Boolean, default=True)
    Ca = Column(String)
    CodUnico = Column(String)
    TipoEpi = Column(String)
    Dono = Column(String)
    Usos = Column(JSON)
    CriadoPor = Column(String)
    DataDescarte = Column(String)
    DataDevolucao = Column(String)
    DataDevolvido = Column(String)
    DataRegistro = Column(String)
    Descartado = Column(Boolean, default=False)
    InventarioId = Column(Integer, ForeignKey("Inventario.id"))
    Inventario = relationship("Inventario", back_populates="itens")
    DataDeletar = Column(String())

    @property
    def Usosformatado(self):
        if isinstance(self.Usos, list):
            return ", ".join(self.Usos)
        return str(self.Usos) if self.Usos else ""

class Reverter(Base):
    __tablename__ = 'Reverter'
    id = Column(Integer, primary_key=True)
    InventarioId = Column(Integer, ForeignKey("Inventario.id"))
    Inventario = relationship("Inventario", back_populates="Reverter")
    IdItemAlterado = Column(Integer)
    TiposAlteracao = Column(String(50))
    VersaoAnterior = Column(JSON)
    VersaoAtual = Column(JSON)
    QuemAlterou = Column(String)
    revertido = Column(Boolean, default=False)

class Historico(Base):
    __tablename__ = 'Historico'
    id = Column(Integer, primary_key=True)
    InventarioId = Column(Integer, ForeignKey("Inventario.id"))
    Inventario = relationship("Inventario", back_populates="Historico")
    IdItemAlterado = Column(Integer)
    TiposAlteracao = Column(String(50))
    VersaoAnterior = Column(JSON)
    QuemAlterou = Column(String)
    VersaoAtual = Column(JSON)
    # novo: timestamp automático para facilitar filtros por data no dashboard
    DataAlteracao = Column(String, default=lambda: date.today().isoformat())

class Inventario(Base):
    __tablename__ = 'Inventario'
    id = Column(Integer, primary_key=True)
    itens = relationship("Itens", back_populates="Inventario")
    Reverter = relationship("Reverter", back_populates="Inventario")
    Historico = relationship("Historico", back_populates="Inventario")
    contas = relationship("Contas", back_populates="Inventario")

#endregion Db Config
#endregion base do sistema

#region funcionalidades
class GerenciadorTemporal():
    def __init__(self):
        pass

    def ConferirValDev(self):
        """Retorna lista de (item, status, dias_restantes) para alertas."""
        hoje = date.today()
        itens = session.query(Itens).filter_by(Visivel=True, Descartado=False).all()
        alertas = []
        for item in itens:
            try:
                devolucao = date.fromisoformat(item.DataDevolucao)
                dias = (devolucao - hoje).days
                if dias < 0:
                    alertas.append((item, "atrasado", abs(dias)))
                elif dias <= 7:
                    alertas.append((item, "proximo", dias))
            except (ValueError, TypeError):
                pass
        return alertas

    def ExclusaoVerdadeira(self):
        """Deleta permanentemente itens invisíveis com DataDeletar vencida (1 ano)."""
        hoje = date.today()
        itens = session.query(Itens).filter_by(Visivel=False).all()
        removidos = 0
        for item in itens:
            if item.DataDeletar:
                try:
                    data_del = date.fromisoformat(item.DataDeletar)
                    if hoje >= data_del:
                        session.delete(item)
                        removidos += 1
                except (ValueError, TypeError):
                    pass
        if removidos:
            session.commit()
        return removidos

class ControleFuncionario():
    def __init__(self):
        pass
    def TotalFuncionarios(self) -> int:
        return session.query(Funcionarios).count()
 
    def ListarFuncionarios(self):
        return session.query(Funcionarios).all()
 
    def FuncionariosPaginados(self, offset=0, limit=30):
        return (
            session.query(Funcionarios)
            .offset(offset)
            .limit(limit)
            .all()
        )
 
    def Pesquisar(self, texto: str):
        return session.query(Funcionarios).filter(
            or_(
                Funcionarios.Nome.like(f"%{texto}%"),
                Funcionarios.Cargo.like(f"%{texto}%"),
                Funcionarios.Email.like(f"%{texto}%"),
                Funcionarios.Status.like(f"%{texto}%"),
            )
        ).all()
 
    def Contratar(self, nome: str, email: str, cargo: str, data_admissao: str) -> None:
        func = Funcionarios(
            Nome=nome,
            Email=email,
            Cargo=cargo,
            DataAdmissao=data_admissao,
            Status="Ativo",
            ListaEpiAtual=[],
            ListaDevAtrasadas=[],
            QuantidadeDevAtrasadas=0,
            ListaDevEmDia=[],
            QuantidadeDevEmDia=0,
        )
        session.add(func)
        session.commit()
 
    def Demitir(self, id: int) -> bool:
        func = session.query(Funcionarios).filter_by(id=id).first()
        if not func:
            return False
        session.delete(func)
        session.commit()
        return True
 
    def AlterarStatus(self, id: int, novo_status: str) -> bool:
        """Ativo | Inativo | Ferias | Licenca"""
        func = session.query(Funcionarios).filter_by(id=id).first()
        if not func:
            return False
        func.Status = novo_status
        session.commit()
        return True
 
    def AtualizarEpiAtual(self, id: int, lista_epi: list) -> None:
        func = session.query(Funcionarios).filter_by(id=id).first()
        if func:
            func.ListaEpiAtual = lista_epi
            session.commit()
 
    def EntregaEpiEmDia(self, id: int, lista: list) -> None:
        func = session.query(Funcionarios).filter_by(id=id).first()
        if func:
            func.ListaDevEmDia = lista
            func.QuantidadeDevEmDia = len(lista)
            session.commit()
 
    def AtrasoEntregaEpi(self, id: int, lista: list) -> None:
        func = session.query(Funcionarios).filter_by(id=id).first()
        if func:
            func.ListaDevAtrasadas = lista
            func.QuantidadeDevAtrasadas = len(lista)
            session.commit()

class InventarioFuncionalidade():
    #optimizar query e usabilidade do usuario
    
    def __init__(self):
        self._cache_itens = None
    PAGE_SIZE = 30

    def ItensTotais(self, force=False):
        if self._cache_itens is None or force:
            self._cache_itens = (
                session.query(Itens)
                .filter_by(Visivel=True)
                .limit(self.PAGE_SIZE)
                .all()
            )
        return self._cache_itens

    def ItensPaginados(self, offset=0, limit=None):
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
        return session.query(Itens).filter_by(Visivel=True).count()

    def SelFuncionario(self, ID):
        return session.query(Itens).filter_by(id=ID).first()

    def RemListaFuncionarios(self):
        itens = session.query(Itens).filter_by(Visivel=True).all()
        return [(item.id, item.Dono) for item in itens]

    def EditListaFuncionarios(self):
        itens = session.query(Itens).filter_by(Visivel=True).all()
        return [(item.id, item.Dono) for item in itens]

    def pesquisar(self, pesquisar):
        return session.query(Itens).filter(
            or_(
                Itens.Ca.like(f"%{pesquisar}%"),
                Itens.CodUnico.like(f"%{pesquisar}%"),
                Itens.TipoEpi.like(f"%{pesquisar}%"),
                Itens.Dono.like(f"%{pesquisar}%"),
                Itens.DataDescarte.like(f"%{pesquisar}%"),
                Itens.DataDevolucao.like(f"%{pesquisar}%"),
            )
        ).filter_by(Visivel=True).all()

    def ItensReverter(self):
        return session.query(Reverter).filter_by(revertido=False).all()

    def ItensHistorico(self):
        return session.query(Historico).all()
    
    def GerarCodUnico(self, item) -> None:
        parte_dono = (item.Dono or "XXX")[:3].upper()
        parte_ca   = (item.Ca   or "0000")[:4]
        desc = (item.DataDescarte  or "0000-00-00").replace("-", "")
        devo = (item.DataDevolucao or "0000-00-00").replace("-", "")
        item.CodUnico = f"{parte_dono}{parte_ca}{desc[6:8]}{devo[6:8]}"


    def _nome_conta(self, registro_id: int) -> str:
        conta = session.query(Contas).filter_by(id=registro_id).first()
        return conta.Conta if conta else str(registro_id)

    def _inv(self):
        inv = session.query(Inventario).first()
        if not inv:
            inv = Inventario()
            session.add(inv)
            session.commit()
        return inv

    def AddItem(self, Registrodata, registro, ca, tipo_epi, dono, usos,
                data_descarte, data_devolucao) -> None:
        inv = self._inv()
        nome = self._nome_conta(registro)
        novo = Itens(
            Ca=ca,
            TipoEpi=tipo_epi,
            Dono=dono,
            Usos=usos,
            DataRegistro=Registrodata,
            DataDescarte=data_descarte,
            DataDevolucao=data_devolucao,
            Visivel=True,
            CriadoPor=nome,
            Descartado=False,
            Inventario=inv,
        )
        session.add(novo)
        session.flush()           # garante ID antes de gerar código
        self.GerarCodUnico(novo)

        # registros de auditoria
        estado = {
            "Ca": ca, "TipoEpi": tipo_epi, "Dono": dono,
            "Usos": usos, "DataDescarte": data_descarte,
            "DataDevolucao": data_devolucao,
        }
        inv_id = inv.id
        session.add(Reverter(
            InventarioId=inv_id, IdItemAlterado=novo.id,
            TiposAlteracao="adicao", VersaoAnterior={}, VersaoAtual=estado,
            QuemAlterou=nome, revertido=False,
        ))
        session.add(Historico(
            InventarioId=inv_id, IdItemAlterado=novo.id,
            TiposAlteracao="adicao", VersaoAnterior={}, VersaoAtual=estado,
            QuemAlterou=nome,
            DataAlteracao=date.today().isoformat(),
        ))
        session.commit()
        self._cache_itens = None

    def RemItem(self, id, registro) -> None:
        # BUGFIX: era .filter_by(...) sem .first() — query object não tem .Visivel
        item = session.query(Itens).filter_by(id=id).first()
        if not item:
            return
        nome = self._nome_conta(registro)
        estado_anterior = {"Visivel": True}
        estado_novo     = {"Visivel": False}

        item.Visivel   = False
        # define data real de exclusão: 1 ano a partir de hoje
        item.DataDeletar = (date.today() + timedelta(days=365)).isoformat()

        inv_id = self._inv().id
        session.add(Reverter(
            InventarioId=inv_id, IdItemAlterado=id,
            TiposAlteracao="remocao", VersaoAnterior=estado_anterior,
            VersaoAtual=estado_novo, QuemAlterou=nome, revertido=False,
        ))
        session.add(Historico(
            InventarioId=inv_id, IdItemAlterado=id,
            TiposAlteracao="remocao", VersaoAnterior=estado_anterior,
            VersaoAtual=estado_novo, QuemAlterou=nome,
            DataAlteracao=date.today().isoformat(),
        ))
        session.commit()
        self._cache_itens = None

    def EditItem(self, registro, Id, Ca, TipoEpi, Dono, Usos,
                 DataDev, DataDesc) -> None:
        item = session.query(Itens).filter_by(id=Id).first()
        if not item:
            return
        nome = self._nome_conta(registro)
        anterior = {
            "Ca": item.Ca, "TipoEpi": item.TipoEpi, "Dono": item.Dono,
            "Usos": item.Usos, "DataDevolucao": item.DataDevolucao,
            "DataDescarte": item.DataDescarte,
        }
        novo_estado = {
            "Ca": Ca, "TipoEpi": TipoEpi, "Dono": Dono,
            "Usos": Usos, "DataDevolucao": DataDev,
            "DataDescarte": DataDesc, "QuemAlterou": nome,
        }
        try:
            item.Ca = Ca; item.TipoEpi = TipoEpi; item.Dono = Dono
            item.Usos = Usos; item.DataDevolucao = DataDev; item.DataDescarte = DataDesc
            self.GerarCodUnico(item)

            inv_id = self._inv().id
            session.add(Reverter(
                InventarioId=inv_id, IdItemAlterado=Id,
                TiposAlteracao="edicao", VersaoAnterior=anterior,
                VersaoAtual=novo_estado, QuemAlterou=nome, revertido=False,
            ))
            session.add(Historico(
                InventarioId=inv_id, IdItemAlterado=Id,
                TiposAlteracao="edicao", VersaoAnterior=anterior,
                VersaoAtual=novo_estado, QuemAlterou=nome,
                DataAlteracao=date.today().isoformat(),
            ))
            session.commit()
            self._cache_itens = None
        except Exception as e:
            session.rollback()
            print(f"Erro ao editar: {e}")

    def descartarItem(self, id, state, registro) -> str:
        item = session.query(Itens).filter_by(id=id).first()
        if not item:
            return "item não encontrado"
        nome = self._nome_conta(registro)
        anterior = {"Descartado": item.Descartado}
        novo_estado = {"Descartado": state}

        item.Descartado = state
        if state:
            item.DataDevolvido = date.today().isoformat()

        inv_id = self._inv().id
        session.add(Historico(
            InventarioId=inv_id, IdItemAlterado=id,
            TiposAlteracao="descarte", VersaoAnterior=anterior,
            VersaoAtual=novo_estado, QuemAlterou=nome,
            DataAlteracao=date.today().isoformat(),
        ))
        session.commit()
        self._cache_itens = None
        return "item descartado" if state else "descarte desfeito"

    def ReverterItem(self, Id, State, registro) -> str:
        try:
            reg = session.query(Reverter).filter_by(id=Id).first()
            if not reg:
                return "registro não encontrado"
            nome = self._nome_conta(registro)
            item = session.query(Itens).filter_by(id=reg.IdItemAlterado).first()
            if item:
                fonte = reg.VersaoAnterior if State else reg.VersaoAtual
                item.Ca            = fonte.get("Ca",            item.Ca)
                item.TipoEpi       = fonte.get("TipoEpi",       item.TipoEpi)
                item.Dono          = fonte.get("Dono",          item.Dono)
                item.Usos          = fonte.get("Usos",          item.Usos)
                item.DataDevolucao = fonte.get("DataDevolucao", item.DataDevolucao)
                item.DataDescarte  = fonte.get("DataDescarte",  item.DataDescarte)
                # restaurar visibilidade se for reversão de remoção
                if reg.TiposAlteracao == "remocao" and State:
                    item.Visivel    = True
                    item.DataDeletar = None
            reg.revertido = True
            session.add(Historico(
                InventarioId=self._inv().id, IdItemAlterado=reg.IdItemAlterado,
                TiposAlteracao="reversao",
                VersaoAnterior=reg.VersaoAtual,
                VersaoAtual=reg.VersaoAnterior,
                QuemAlterou=nome,
                DataAlteracao=date.today().isoformat(),
            ))
            session.commit()
            self._cache_itens = None
            return "item revertido"
        except Exception as e:
            session.rollback()
            return f"erro ao reverter: {e}"


    def DadosDashboard(self) -> dict:
        """
        Agrega tudo que o Dashboard precisa em um único dict,
        evitando múltiplas queries avulsas na camada de UI.

        Retorna:
            total_ativos      – itens visíveis e não descartados
            total_descartados – itens descartados (visíveis)
            por_tipo          – {tipo_epi: quantidade} itens ativos
            por_dono          – {dono: quantidade} itens ativos
            atrasos           – [(item, 'atrasado'|'proximo', dias)]
            entregas_mes      – itens descartados no mês corrente
            historico_30dias  – alterações dos últimos 30 dias por tipo
        """
        hoje = date.today()
        inicio_mes  = hoje.replace(day=1)
        inicio_30d  = hoje - timedelta(days=30)

        # contagens base
        q_ativos = (
            session.query(Itens)
            .filter_by(Visivel=True, Descartado=False)
        )
        total_ativos = q_ativos.count()
        total_descartados = (
            session.query(Itens)
            .filter_by(Visivel=True, Descartado=True)
            .count()
        )

        # distribuição por tipo e por dono
        por_tipo = {}
        por_dono = {}
        for item in q_ativos.all():
            por_tipo[item.TipoEpi or "N/A"] = por_tipo.get(item.TipoEpi or "N/A", 0) + 1
            por_dono[item.Dono    or "N/A"] = por_dono.get(item.Dono    or "N/A", 0) + 1

        # alertas de devolução
        atrasos = GerenciadorTemporal().ConferirValDev()

        # entregas/descartes no mês atual
        entregas_mes = (
            session.query(Itens)
            .filter(
                Itens.Visivel == True,
                Itens.Descartado == True,
                Itens.DataDevolvido >= inicio_mes.isoformat(),
            )
            .count()
        )

        # histórico de alterações nos últimos 30 dias (por tipo de ação)
        historico_30dias = {}
        registros = (
            session.query(Historico)
            .filter(Historico.DataAlteracao >= inicio_30d.isoformat())
            .all()
        )
        for r in registros:
            historico_30dias[r.TiposAlteracao] = (
                historico_30dias.get(r.TiposAlteracao, 0) + 1
            )

        return {
            "total_ativos":      total_ativos,
            "total_descartados": total_descartados,
            "por_tipo":          por_tipo,
            "por_dono":          por_dono,
            "atrasos":           atrasos,
            "entregas_mes":      entregas_mes,
            "historico_30dias":  historico_30dias,
        }

    def DadosDashPessoal(self, dono: str) -> dict:
        """Dados filtrados para o dashboard individual de um funcionário."""
        hoje = date.today()
        itens = (
            session.query(Itens)
            .filter_by(Visivel=True, Dono=dono)
            .all()
        )
        ativos     = [i for i in itens if not i.Descartado]
        descartados = [i for i in itens if i.Descartado]
        atrasos    = []
        em_dia     = []
        for item in ativos:
            try:
                dev = date.fromisoformat(item.DataDevolucao)
                dias = (dev - hoje).days
                if dias < 0:
                    atrasos.append((item, abs(dias)))
                else:
                    em_dia.append((item, dias))
            except (ValueError, TypeError):
                pass
        return {
            "dono":       dono,
            "ativos":     ativos,
            "descartados": descartados,
            "atrasos":    atrasos,
            "em_dia":     em_dia,
        }


# criar sessão ANTES de usar
Session = sessionmaker(bind=engine)
session = Session()

#endregion funcionalidades

#region fake_data
def fake_data():
    try:
        inv = Inventario()
        session.add(inv)
        session.flush()

        nomes = ["Carlos Silva", "Ana Souza", "Pedro Lima", "Maria Costa"]
        tipos = ["Capacete", "Luva", "Óculos", "Cinto", "Colete"]
        for i in range(8):
            dono = nomes[i % len(nomes)]
            tipo = tipos[i % len(tipos)]
            desc_date = (date.today() + timedelta(days=180 + i * 15)).isoformat()
            dev_date  = (date.today() + timedelta(days=30  + i * 5 - 20)).isoformat()
            novo = Itens(
                Ca=f"CA-{1000+i}",
                TipoEpi=tipo,
                Dono=dono,
                Usos=[f"uso {j}" for j in range(1, 3)],
                DataRegistro=date.today().isoformat(),
                DataDescarte=desc_date,
                DataDevolucao=dev_date,
                Visivel=True,
                CriadoPor="admin",
                Descartado=(i % 3 == 0),
                DataDevolvido=date.today().isoformat() if i % 3 == 0 else None,
                Inventario=inv,
            )
            session.add(novo)
            session.flush()
            inv_func = InventarioFuncionalidade()
            inv_func.GerarCodUnico(novo)

        conta = Contas(
            Conta="admin",
            Senha=Brycpt.hashpw(b"123456", Brycpt.gensalt()).decode(),
            cargo="adm",
            Inventario=inv,
        )
        session.add(conta)

        for i in range(5):
            session.add(Historico(
                InventarioId=inv.id,
                IdItemAlterado=i + 1,
                TiposAlteracao=["adicao","edicao","descarte","remocao","reversao"][i],
                VersaoAnterior={}, VersaoAtual={},
                QuemAlterou="admin",
                DataAlteracao=(date.today() - timedelta(days=i*4)).isoformat(),
            ))
        cargos  = ["Operador", "Supervisor", "Técnico", "Analista", "Almoxarife"]
        status  = ["Ativo", "Ativo", "Férias", "Ativo", "Inativo"]
        nomes_func = ["João Silva", "Maria Costa", "Rafael Pinto", "Ana Lima", "Carlos Melo"]

        for i, nome in enumerate(nomes_func):
            adm = (date.today() - timedelta(days=365 * (i + 1))).isoformat()
            session.add(Funcionarios(
                Nome=nome,
                Email=f"{nome.split()[0].lower()}@empresa.com",
                Cargo=cargos[i],
                DataAdmissao=adm,
                Status=status[i],
                ListaEpiAtual=[],
                ListaDevAtrasadas=[],
                QuantidadeDevAtrasadas=0,
                ListaDevEmDia=[],
                QuantidadeDevEmDia=0,
            ))

        session.commit()
        print("Dados de teste criados com sucesso.")
    except Exception as e:
        session.rollback()
        print(f"Erro ao criar dados de debug: {e}")
#endregion

#region rodar
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

if __name__ == '__main__':
    if os.path.exists('GuindastesRibasDB.db'):
        os.remove('GuindastesRibasDB.db')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    fake_data()
    gt = GerenciadorTemporal()
    alertas = gt.ConferirValDev()
#endregion rodar