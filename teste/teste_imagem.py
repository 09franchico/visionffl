import flet as ft

def main(page: ft.Page):
    page.title = "Images Example"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 50
    page.update()

    img = ft.Image(
        src=f"/icons/icon-512.png",
        width=100,
        height=100,
        fit=ft.ImageFit.CONTAIN,
    )
    images = ft.Row(expand=1, wrap=False, scroll="always")

    page.add(img, images)
    
    # images.controls.append(
    #         ft.Image(
    #             src=f"https://picsum.photos/900/1200?{1}",
    #             width=900,
    #             height=1200,
    #             fit=ft.ImageFit.NONE,
    #             repeat=ft.ImageRepeat.NO_REPEAT,
    #             border_radius=ft.border_radius.all(10),
    #         )
    # )

    for i in range(0, 30):
        images.controls.append(
            ft.Image(
                src=f"https://picsum.photos/900/1200?{i}",
                width=900,
                height=1200,
                fit=ft.ImageFit.NONE,
                repeat=ft.ImageRepeat.NO_REPEAT,
                border_radius=ft.border_radius.all(10),
            )
        )
    page.update()

ft.app(target=main)