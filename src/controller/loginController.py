
from src.orm.repository.usuarioRepository import UsuarioRepository

class LoginController:
    
    def __init__(self):
        self.usuario_repository = UsuarioRepository()
        
        
    def login_usuario(self,email:str):
        usuario = self.usuario_repository.select_email_usuario(email=email)
        return usuario
    
    def cadastrar_usuario_login(self,nome,sobrenome,idade,email,senha):
        usuario_inserido = self.usuario_repository.insert(nome,sobrenome,idade,email,senha)
        return usuario_inserido
        
        
        