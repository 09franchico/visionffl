import flet as ft

class Main (ft.UserControl):
    
    def __init__(self, page:ft.Page):
        self.page = page
        self.page.window_center()
        self.page.theme_mode = 'Light'
    
        self.page.window_resizable = False
        self.page.window_minimizable = False
        self.page.window_maximizable = False
        self.page.padding = 0
        
        self.email = ft.TextField(label="Email",border_color=ft.colors.BLACK12)
        self.senha = ft.TextField(label="Senha",border_color=ft.colors.BLACK12,password=True, can_reveal_password=True)
        
        
        self.login = ft.Container(
                    content=ft.Row(
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
                                                ft.ElevatedButton(text="Acessar",width=300,height=40,on_click=self.login)
                                                
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
                    alignment=ft.alignment.center
                    
        )
        
        
        self.page.on_route_change = self.route_change
        self.page.on_view_pop = self.view_pop

        self.page.go(self.page.route)
        
        
        
    def login(self, evento):
        if self.email.value == 'francisco@gmail.com' and self.senha.value == '1234':
            print(self.email.value)
            print(self.senha.value)
            self.page.go("/home")
            
        

    def route_change(self, route):
        self.page.views.clear()
        self.page.views.append(
            ft.View(
                "/",[self.login],
            )
        )
        if self.page.route == "/home":
            self.page.views.append(
                ft.View(
                    "/home",
                    [
                        ft.Text("Pagina home")
                    ],
                )
            )
        self.page.update()

    def view_pop(self, view):
        print(view)
        self.page.views.pop()
        top_view = self.page.views[-1]
        self.page.go(top_view.route)
        
        
    
        

if __name__ == "__main__":
    ft.app(target=Main)
