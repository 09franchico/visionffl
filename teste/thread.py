import asyncio
import flet as ft

class Countdown(ft.Text):
    def __init__(self, seconds):
        super().__init__()
        self.seconds = seconds

    def did_mount(self):
        self.running = True
        print("Executou aqui")
        self.page.run_task(self.update_timer)

    def will_unmount(self):
        print("Finalizou")
        self.running = False

    async def update_timer(self):
        while self.seconds and self.running:
            mins, secs = divmod(self.seconds, 60)
            self.value = "{:02d}:{:02d}".format(mins, secs)
            self.update()
            await asyncio.sleep(1)
            self.seconds -= 1
        print("Finalizou aqui........")

def main(page: ft.Page):
    page.add(
            Countdown(15), 
            Countdown(10)
        )

ft.app(main)