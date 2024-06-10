import flet as ft
from src.view.login import Login
from src.view.home import Home
from src.view.cadastro import Cadastro
from src.controller.loginController import LoginController



class Main (ft.UserControl):
    
    def __init__(self, page:ft.Page):
        self.page = page
        self.page.window_center()
        self.page.theme_mode = 'Light'
    
        self.page.window_resizable = False
        self.page.window_minimizable = False
        self.page.window_maximizable = False
        self.page.padding = 0
        
        
        self.page.on_route_change = self.route_change
        # self.page.on_view_pop = self.view_pop
        self.page.go(self.page.route)
        
        
        self.login_controller = LoginController()
        


    def route_change(self, route):
        self.page.views.clear()
        self.page.views.append(
            Login(self.page,"/",self.login_controller)
        )
        if self.page.route == "/home":
            self.page.views.append(
                Home(self.page,"/home")
            )
        if self.page.route == "/cadastro":
            self.page.views.append(
            Cadastro(self.page,"/cadastro",self.login_controller)
            )
            
        self.page.update()
    

    def view_pop(self, view):
        self.page.views.pop()
        top_view = self.page.views[-1]
        self.page.go(top_view.route)
        
        
    
        

if __name__ == "__main__":
    ft.app(target=Main)