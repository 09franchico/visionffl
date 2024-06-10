import flet as ft


class Configuracao(ft.Container):
    
    def __init__(self):
        super().__init__()
        
        
        self.bgcolor = ft.colors.BLACK12
        self.padding = 20
        self.border_radius = 5
        
        self.content = ft.Column(
                        [
                            ft.Container(
                                content=ft.Row(
                                    [
                                        ft.Text("Cameras"),
                                   
                                        
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER
                                    ),
                                  bgcolor=ft.colors.BLACK12,
                                  height=100,
                                  border_radius=5
                    
                            ),
                            ft.Container(
                                content=ft.Row(
                                    [
                                        ft.Text("Arduino"),
                                   
                                        
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER
                                    ),
                                  bgcolor=ft.colors.BLACK12,
                                  height=200,
                                  border_radius=5
                    
                            ),
                            ft.Container(
                                content=ft.Row(
                                    [
                                        ft.Text("Botoes"),
                                   
                                        
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER
                                    ),
                                  bgcolor=ft.colors.BLACK12,
                                  height=150,
                                  border_radius=5
                    
                            )
                            
                        ]
                        ,
                        width=300
                    )
        
        
