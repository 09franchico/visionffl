import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2
import numpy as np

class TemplateMatchingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Aplicação de Template Matching em Imagem")

        self.image_frame = tk.Frame(self.root)
        self.image_frame.grid(row=0, column=0, padx=10, pady=10)

        self.image_label = tk.Label(self.image_frame)
        self.image_label.pack()

        self.load_button = tk.Button(self.root, text="Carregar Imagem", command=self.load_image)
        self.load_button.grid(row=1, column=0, pady=10)

        self.zoom_label = tk.Label(self.root)
        self.zoom_label.grid(row=0, column=1, padx=10, pady=10)

        self.captured_image = None
        self.display_image_resized = None
        self.is_drawing = False
        self.ix = 0
        self.iy = 0

        self.image_label.bind("<ButtonPress-1>", self.start_drawing)
        self.image_label.bind("<B1-Motion>", self.draw_rectangle)
        self.image_label.bind("<ButtonRelease-1>", self.stop_drawing)

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.bmp")])
        if file_path:
            self.captured_image = cv2.imread(file_path)
            self.display_image_resized = self.resize_image(self.captured_image, 800, 600)
            self.display_image(self.display_image_resized)

    def start_drawing(self, event):
        self.is_drawing = True
        self.ix, self.iy = event.x, event.y

    def draw_rectangle(self, event):
        if self.is_drawing and self.captured_image is not None:
            temp_image = self.display_image_resized.copy()
            cv2.rectangle(temp_image, (self.ix, self.iy), (event.x, event.y), (0, 255, 0), 1)
            self.display_image(temp_image)

            x1, y1 = int(self.ix * self.captured_image.shape[1] / self.display_image_resized.shape[1]), int(self.iy * self.captured_image.shape[0] / self.display_image_resized.shape[0])
            x2, y2 = int(event.x * self.captured_image.shape[1] / self.display_image_resized.shape[1]), int(event.y * self.captured_image.shape[0] / self.display_image_resized.shape[0])

            roi_zoom = self.captured_image[min(y1, y2):max(y1, y2), min(x1, x2):max(x1, x2)]
            if roi_zoom.size > 0:
                roi_zoom = cv2.resize(roi_zoom, (200, 200), interpolation=cv2.INTER_CUBIC)
                roi_zoom_rgb = cv2.cvtColor(roi_zoom, cv2.COLOR_BGR2RGB)
                roi_zoom_pil = Image.fromarray(roi_zoom_rgb)
                roi_zoom_tk = ImageTk.PhotoImage(roi_zoom_pil)

                self.zoom_label.configure(image=roi_zoom_tk)
                self.zoom_label.image = roi_zoom_tk

    def stop_drawing(self, event):
        self.is_drawing = False

    def resize_image(self, image, width, height):
        pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        resized_image = pil_image.resize((width, height), Image.LANCZOS)
        return cv2.cvtColor(np.array(resized_image), cv2.COLOR_RGB2BGR)

    def display_image(self, image):
        bgr_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(bgr_image)
        tk_image = ImageTk.PhotoImage(image=pil_image)
        self.image_label.config(image=tk_image)
        self.image_label.image = tk_image

if __name__ == "__main__":
    root = tk.Tk()
    app = TemplateMatchingApp(root)
    root.mainloop()
