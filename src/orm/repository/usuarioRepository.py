from src.orm.config.postgreSQLConnectionHandler import PostgreSQLConnectionHandler
from src.orm.entities.usuario import Usuario
from sqlalchemy.orm.exc import NoResultFound

class UsuarioRepository:
    def select(self):
        with  PostgreSQLConnectionHandler() as db:
            try:
                data = db.session.query(Usuario).all()
                return data
            except Exception as exception:
                db.session.rollback()
                raise exception
    
    def select_email_usuario(self,email:str):
        with PostgreSQLConnectionHandler() as db:
            try:
                data = db.session.query(Usuario).filter(Usuario.email == email).one()
                return data    
            except Exception as exception:
                db.session.rollback()
                

    def insert(self,nome,sobrenome,idade,email,senha):
        with PostgreSQLConnectionHandler() as db:
            try:
                data_isert = Usuario(nome=nome,sobrenome=sobrenome,idade=idade,email=email,senha=senha)
                db.session.add(data_isert)
                db.session.commit()
                return True
            
            except Exception as exception:
                db.session.rollback()
                return False

    # def delete(self, titulo):
    #     with DBConnectionHandler() as db:
    #         try:
    #             db.session.query(Filmes).filter(Filmes.titulo == titulo).delete()
    #             db.session.commit()
    #         except Exception as exception:
    #             db.session.rollback()
    #             raise exception

    # def update(self, titulo, ano):
    #     with DBConnectionHandler() as db:
    #         try:
    #             db.session.query(Filmes).filter(Filmes.titulo == titulo).update({ "ano": ano })
    #             db.session.commit()
    #         except Exception as exception:
    #             db.session.rollback()
    #             raise exception