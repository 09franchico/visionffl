import flet as ft


class Terminal(ft.Container):
    
    def __init__(self):
        super().__init__()
        
         
        self.bgcolor = ft.colors.BLACK12
        self.padding = 20
        self.border_radius = 5
        
        self.content = ft.Column(
                        [
                            ft.TextField(
                                multiline=True,
                                width=500,
                                value="cmdDaley",
                                bgcolor=ft.colors.BLACK,
                                color=ft.colors.YELLOW,
                                disabled=True,
                                adaptive= True
                                
                                ),
                            ft.TextField(
                                multiline=True,
                                width=500,
                                value="cmdDaley",
                                bgcolor=ft.colors.BLACK,
                                color=ft.colors.YELLOW,
                                disabled=True
                                ),
                            ft.TextField(
                                
                                multiline=True,
                                height=400,
                                width=500,
                                value="line1\nline2\nline3\nline4\nline5,line1\nline2\nline3\nline4\nline5,line1\nline2\nline3\nline4\nline5",
                                disabled=True,
                                )
                                
                        ]
                    )
        

        
        
        