from sqlalchemy import Column, Integer, String, DECIMAL, Date, DateTime, Enum, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from db import Base

class Apartamento(Base):
    __tablename__ = "apartamento"
    id        = Column(Integer, primary_key=True)
    numero    = Column(String(10), nullable=False)
    bloco     = Column(String(10))
    andar     = Column(Integer)
    moradores = relationship("Morador", back_populates="apartamento", cascade="all, delete")
    despesas  = relationship("Despesa",  back_populates="apartamento", cascade="all, delete")

class Morador(Base):
    __tablename__  = "morador"
    id             = Column(Integer, primary_key=True)
    nome           = Column(String(100), nullable=False)
    email          = Column(String(120), unique=True)
    telefone       = Column(String(20))
    profissao      = Column(String(50))
    senha_hash     = Column(String(256))
    papel          = Column(Enum("SINDICO","MORADOR"), default="MORADOR")
    apartamento_id = Column(Integer, ForeignKey("apartamento.id"))
    apartamento    = relationship("Apartamento", back_populates="moradores")
    notificacoes   = relationship("Notificacao", back_populates="morador", cascade="all, delete")
    pagamentos     = relationship("Pagamento",   back_populates="morador", cascade="all, delete")

class Despesa(Base):
    __tablename__  = "despesa"
    id             = Column(Integer, primary_key=True)
    descricao      = Column(String(150))
    valor          = Column(DECIMAL(10,2))
    vencimento     = Column(Date)
    pago           = Column(Enum("SIM","NAO"), default="NAO")
    apartamento_id = Column(Integer, ForeignKey("apartamento.id"))
    apartamento    = relationship("Apartamento", back_populates="despesas")
    pagamentos     = relationship("Pagamento", back_populates="despesa", cascade="all, delete")

class Pagamento(Base):
    __tablename__ = "pagamento"
    id          = Column(Integer, primary_key=True)
    despesa_id  = Column(Integer, ForeignKey("despesa.id"))
    morador_id  = Column(Integer, ForeignKey("morador.id"))
    valor_pago  = Column(DECIMAL(10,2))
    pago_em     = Column(DateTime, server_default=func.now())
    despesa     = relationship("Despesa", back_populates="pagamentos")
    morador     = relationship("Morador", back_populates="pagamentos")

class Notificacao(Base):
    __tablename__ = "notificacao"
    id         = Column(Integer, primary_key=True)
    morador_id = Column(Integer, ForeignKey("morador.id"))
    titulo     = Column(String(120))
    mensagem   = Column(Text)
    criada_em  = Column(DateTime, server_default=func.now())
    lida       = Column(Enum("SIM","NAO"), default="NAO")
    morador    = relationship("Morador", back_populates="notificacoes")
