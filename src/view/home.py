import flet as ft



class Home(ft.View):
    
    def __init__(self,page:ft.Page,router):
        super().__init__()
        
        self.page = page
        self.route = router
        
        self.padding = 5
        
        
        self.controls = [
            ft.Container(
                   ft.Row(
                        [
                            ft.TextButton("Voltar para login",on_click=self.voltar_login)
                        ]
                    ),
                   bgcolor=ft.colors.GREEN_ACCENT,
                   
            
                )
        ]
        
        
        
    def voltar_login(self,evento):    
        self.page.go("/")