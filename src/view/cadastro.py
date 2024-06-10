import flet as ft
from src.components.snackBar.snackBar import SnackBar
from src.controller.loginController import LoginController



class Cadastro(ft.View):
    
    def __init__(self,
                 page:ft.Page,
                 router,
                 login_controller:LoginController):
        
        super().__init__()
        self.page = page
        self.route = router
        
        self.login_controller = login_controller
        
        self.padding = 0
    
        self.nome = ft.TextField(label="Nome",border_color=ft.colors.BLACK12)
        self.sobrenome = ft.TextField(label="Sobrenome",border_color=ft.colors.BLACK12)
        self.email = ft.TextField(label="Email",border_color=ft.colors.BLACK12)
        self.idade = ft.TextField(label="Idade",border_color=ft.colors.BLACK12)
        self.senha = ft.TextField(label="Senha",border_color=ft.colors.BLACK12,password=True, can_reveal_password=True)
        self.confirma_senha = ft.TextField(label="Confirmar senha",border_color=ft.colors.BLACK12,password=True, can_reveal_password=True)
        
        
        self.controls = [
            ft.Container (
               content = ft.Row(
                        [        
                            
                            ft.Container(
                                content=ft.Image(
                                        src=f"https://picsum.photos/1000/1000?aventure",
                                        width=1000,
                                        height=1000,
                                        fit=ft.ImageFit.NONE,
                                        repeat=ft.ImageRepeat.NO_REPEAT,
                                        expand=True
                                ),
                                alignment=ft.alignment.center,
                                expand=True,
                                
                            ),
                            ft.Container(
                                content = ft.Column(
                                    [
                                        ft.Row(
                                            [
                                                ft.Icon(name=ft.icons.LOGO_DEV, color=ft.colors.PINK,size=40),
                                                
                                            ],
                                            alignment=ft.MainAxisAlignment.CENTER,
                                            width=300
                                            
                
                                        ),
                                        self.nome,
                                        self.sobrenome,
                                        self.idade,
                                        self.email,
                                        self.senha,
                                        self.confirma_senha,
                                        ft.Row(
                                            [
                                                ft.ElevatedButton(
                                                    text="Cadastrar",
                                                    width=300,
                                                    height=40,
                                                    on_click=self.cadastro,
                                                    style=ft.ButtonStyle(
                                                          shape=ft.RoundedRectangleBorder(
                                                          radius=5 , # Ajuste o valor conforme necessário,
                    
                                                     ),
                                                    bgcolor=ft.colors.BLUE,color=ft.colors.WHITE
                                            ))
                                                
                                            ]
                                        ),
                                        ft.Row(
                                            [
                                                ft.Text("Login ja criado -",size=15),
                                                ft.Text("",size=12,spans=[
                                                    ft.TextSpan(
                                                                "Login",
                                                                ft.TextStyle(
                                                                    decoration=ft.TextDecoration.UNDERLINE,
                                                                    size=15
                                                                ),
                                                                on_click=self.voltar_login
                                                            )
                                                ])
                                                
                                            ],
                                            alignment=ft.MainAxisAlignment.CENTER,
                                            width=300
                                            
                
                                        ),
                                        
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    horizontal_alignment=ft.MainAxisAlignment.CENTER
                                    
                                ),
                                
                                padding=70,
                            
                            )
                            
                            
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    expand=True,
                    alignment=ft.alignment.center,
           )
            
            
        ]
        
        
    def cadastro(self, evento):
        self.nome.error_text = "Verificar o texto"
        self.nome.update()
        usuario_inserido = self.login_controller.cadastrar_usuario_login(
                self.nome.value,
                self.sobrenome.value,
                self.idade.value,
                self.email.value,
                self.senha.value
            )
        if usuario_inserido :
            self.page.show_snack_bar(SnackBar("Cadastro realizado com sucesso","success"))
            self.page.go("/")
        else:
            self.page.show_snack_bar(SnackBar("Erro ao realizar cadastro de usuario","error"))
            
        
        
    def voltar_login(self,evento:ft.ControlEvent):
        self.page.go("/")