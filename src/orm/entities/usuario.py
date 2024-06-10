from src.orm.config.base import Base
from sqlalchemy import Column, String, Integer, ForeignKey

class Usuario(Base):
    __tablename__ = "tbusuario"

    id_usuario = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    sobrenome = Column(String, nullable=False)
    idade = Column(Integer, nullable=False)
    email = Column(String, nullable=False)
    senha = Column(String, nullable=False)

    def __repr__(self):
        return f"Usuario [id_usuario = {self.id_usuario},nome={self.nome},sobrenome={self.sobrenome},idade={self.idade},email={self.email},senha={self.senha}]"