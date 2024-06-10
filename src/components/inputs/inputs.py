import flet as ft


class Inputs(ft.Container):
    
    def __init__(self):
        super().__init__()
        
        
        self.bgcolor = ft.colors.BLACK12
        self.padding = 20
        self.border_radius = 5
        
        self.operador = ft.TextField(label="Operador",height=45,border_color=ft.colors.BLUE_600)
        self.mac = ft.TextField(label="MAC",height=45,border_color=ft.colors.BLUE_600)
        self.er = ft.TextField(label="ER",height=45,border_color=ft.colors.BLUE_600)
        self.uuid = ft.TextField(label="UUID",height=45,border_color=ft.colors.BLUE_600)
        self.etq8s = ft.TextField(label="8S",height=45,border_color=ft.colors.BLUE_600)
        
        
        self.botao_resete =  ft.IconButton(
                                            icon=ft.icons.RESTORE_ROUNDED,
                                            icon_size=70,
                                        )
        
        self.botao_apagar = ft.IconButton(
                                            icon=ft.icons.DELETE_ROUNDED,
                                            icon_size=70,
                                            on_click=self.limpar)
        
        self.botao_play = ft.IconButton(
                                          icon=ft.icons.PLAY_CIRCLE,
                                          icon_size=70,
                                          on_click=self.play
                                        )
        
    
        
        
        self.content = ft.Column(
                        [
                            self.operador,
                            self.mac,
                            self.er,
                            self.uuid,
                            self.etq8s,
                            ft.Row(
                                    [
                                       ft.Checkbox(label="Retestar", value=False),
                                       ft.Checkbox(label="Editar", value=False)
                                        
                                    ]
                                ),
                            ft.Row(
                                    [
                                        self.botao_resete,
                                        self.botao_apagar,
                                        self.botao_play
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    width=300
                                    
                                    
                                )
                            
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    
                    )
        
    def play(self,e):
        
        if self.botao_play.icon == 'stop_circle':
            print("OK")
            self.botao_play.icon = ft.icons.PLAY_CIRCLE
            self.botao_play.icon_size = 70
        else:
            self.botao_play.icon = ft.icons.STOP_CIRCLE
            self.botao_play.icon_size = 70
    
        self.update()
        
    def limpar(self,e):
        self.operador.value = ""
        self.mac.value = ""
        self.er.value = ""
        self.uuid.value = ""
        self.etq8s.value = ""
    
        self.update()
        
    # def thema(self,e):
        
    #     if self.modo_thema.icon == 'light_mode':
    #         self.modo_thema.icon = ft.icons.DARK_MODE
    #         self.page.theme_mode = 'Dark'
    #         self.operador.border_color = ft.colors.WHITE30
    #         self.mac.border_color = ft.colors.WHITE30
    #         self.er.border_color = ft.colors.WHITE30
    #         self.uuid.border_color = ft.colors.WHITE30
    #         self.etq8s.border_color = ft.colors.WHITE30
            
    #     else:
    #         self.modo_thema.icon = ft.icons.LIGHT_MODE
    #         self.page.theme_mode = 'Light'
    #         self.operador.border_color = ft.colors.BLACK38
    #         self.mac.border_color = ft.colors.BLACK38
    #         self.er.border_color = ft.colors.BLACK38
    #         self.uuid.border_color = ft.colors.BLACK38
    #         self.etq8s.border_color = ft.colors.BLACK38

    #     self.page.update()
    #     self.update()
            
        
        
        
    
    

    