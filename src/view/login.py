import flet as ft
from src.components.snackBar.snackBar import SnackBar
import math
from src.orm.repository.usuarioRepository import UsuarioRepository
from src.controller.loginController import LoginController


class Login(ft.View):
    
    def __init__(self,
                 page:ft.Page,
                 router,
                 login_controller:LoginController):
        
        super().__init__()
        self.page = page
        self.route = router
        self.login_controller = login_controller
        
        self.padding = 0
    
        
        self.email = ft.TextField(label="Email",border_color=ft.colors.BLACK12,on_blur=self.validacao_email)
        self.senha = ft.TextField(label="Senha",border_color=ft.colors.BLACK12,password=True, can_reveal_password=True,on_blur=self.validacao_senha)
        
        
        
        self.controls = [
            ft.Container (
               content = ft.Row(
                        [
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
                                        self.email,
                                        self.senha,
                                        ft.Row(
                                            [
                                                ft.ElevatedButton(
                                                    text="Acessar",
                                                    width=300,
                                                    height=40,
                                                    on_click=self.login,
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
                                                ft.Text("Criar usuario no sistema",size=15),
                                                ft.Text("",size=12,spans=[
                                                    ft.TextSpan(
                                                                "Criar",
                                                                ft.TextStyle(
                                                                    decoration=ft.TextDecoration.UNDERLINE,
                                                                    size=15
                                                                ),
                                                                on_click=self.criar_usuario
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
                            
                            ),
                            
                            
                            ft.Container(
                                # content= ft.Rive(
                                #     "https://cdn.rive.app/animations/vehicles.riv",
                                #         placeholder=ft.ProgressBar(),
                                #         expand=True,
                                #     ),
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
                                
                            )
                            
                            
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    expand=True,
                    alignment=ft.alignment.center,
            # gradient=ft.LinearGradient(
            #     begin=ft.alignment.top_left,
            #     end=ft.Alignment(0.8, 1),
            #     colors=[
            #         ft.colors.BLUE_50,
            #         ft.colors.BLUE_300
            #     ],
            #     tile_mode=ft.GradientTileMode.MIRROR,
            #     rotation=math.pi / 3,
            # ),
           )
            
            
        ]
        
    def validacao_email(self,e:ft.ControlEvent):
        if e.control.value  == "":
            self.email.error_text = "Email não pode ser vazio"
        else:
            self.email.error_text = None
        self.update()
        
    def validacao_senha(self,e:ft.ControlEvent):
        if e.control.value  == "":
            self.senha.error_text = "Senha não pode ser vazio"
        else:
            self.senha.error_text = None
        self.update()
        
        
    def login(self, evento:ft.ControlEvent):
        if self.email.error_text is not None and self.email.error_text !="":
            return
        
        if self.senha.error_text is not None and self.senha.error_text !="":
            return
            
        usuario = self.login_controller.login_usuario(self.email.value)
        if usuario != None:
            if usuario.senha == self.senha.value:
               self.page.go("/home")
            else:
                self.page.show_snack_bar(SnackBar("SENHA INVALIDA","error"))     
        else:
            self.page.show_snack_bar(SnackBar("EMAIL NÃO ENCONTRADO","error"))
        
        
    def criar_usuario(self,evento:ft.ControlEvent):
        self.page.go("/cadastro")