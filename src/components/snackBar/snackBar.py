import flet as ft
from typing import Literal


class SnackBar(ft.SnackBar):
    
    def __init__(self, texto: str, bgcolor: Literal['error', 'success']):
        # Mapear valores de bgcolors para as cores reais
        if bgcolor == 'error':
            bg_color_value = ft.colors.RED_700
        elif bgcolor == 'success':
            bg_color_value = ft.colors.GREEN_700
        
        content = ft.Text(texto)
        super().__init__(content=content, bgcolor=bg_color_value,behavior="FLOATING",width=500,show_close_icon=True,dismiss_direction="HORIZONTAL")

        
        
        
        