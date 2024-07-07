import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from skimage import io, color
from skimage.transform import hough_circle, hough_circle_peaks
from skimage.feature import canny
from skimage.draw import circle_perimeter
from skimage.util import img_as_ubyte

class CircleDetectionApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Circle Detection App")
        self.geometry("800x600")
        
        self.create_widgets()
        
    def create_widgets(self):
        self.load_button = ttk.Button(self, text="Load Image", command=self.load_image)
        self.load_button.pack(pady=10)
        
        self.detect_button = ttk.Button(self, text="Detect Circles", command=self.detect_circles)
        self.detect_button.pack(pady=10)
        
        self.figure, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def load_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.image = io.imread(file_path, as_gray=True)
            self.image = img_as_ubyte(self.image)
            self.show_image(self.image)
        
    def show_image(self, image):
        self.ax.clear()
        self.ax.imshow(image, cmap='gray')
        self.canvas.draw()
        
    def detect_circles(self):
        if hasattr(self, 'image'):
            # Ajustar parâmetros do detector Canny
            edges = canny(self.image, sigma=2, low_threshold=50, high_threshold=100)
            
            # Ajustar faixa de raios para o Hough Transform
            hough_radii = np.arange(20, 100, 2)
            hough_res = hough_circle(edges, hough_radii)
            
            # Selecionar os círculos mais proeminentes
            accums, cx, cy, radii = hough_circle_peaks(hough_res, hough_radii, total_num_peaks=1)
            
            if len(cx) > 0:
                center_y, center_x, radius = cy[0], cx[0], radii[0]
                
                # Cortar a imagem ao redor do círculo detectado
                minr, maxr = int(center_y - radius), int(center_y + radius)
                minc, maxc = int(center_x - radius), int(center_x + radius)
                
                cropped_image = self.image[minr:maxr, minc:maxc]
                
                # image_rgb = color.gray2rgb(self.image)
                # circy, circx = circle_perimeter(center_y, center_x, radius, shape=image_rgb.shape)
                # image_rgb[circy, circx] = (220, 20, 20)
                
                # self.show_image(image_rgb)
                
                # Exibir a imagem cortada em uma nova janela
                self.show_cropped_image(cropped_image)
                
            else:
                messagebox.showinfo("Info", "No circles detected!")
        else:
            messagebox.showerror("Error", "No image loaded!")
            
    def show_cropped_image(self, cropped_image):
        fig, ax = plt.subplots()
        ax.imshow(cropped_image, cmap='gray')
        plt.show()

if __name__ == "__main__":
    app = CircleDetectionApp()
    app.mainloop()








# import tkinter as tk
# from tkinter import filedialog, messagebox
# from tkinter import ttk
# import numpy as np
# import matplotlib.pyplot as plt
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# from skimage import io, color
# from skimage.transform import hough_circle, hough_circle_peaks
# from skimage.feature import canny
# from skimage.draw import circle_perimeter
# from skimage.util import img_as_ubyte

# class CircleDetectionApp(tk.Tk):
#     def __init__(self):
#         super().__init__()
#         self.title("Circle Detection App")
#         self.geometry("800x600")
        
#         self.create_widgets()
        
#     def create_widgets(self):
#         self.load_button = ttk.Button(self, text="Load Image", command=self.load_image)
#         self.load_button.pack(pady=10)
        
#         self.detect_button = ttk.Button(self, text="Detect Circles", command=self.detect_circles)
#         self.detect_button.pack(pady=10)
        
#         self.figure, self.ax = plt.subplots(figsize=(8, 6))
#         self.canvas = FigureCanvasTkAgg(self.figure, master=self)
#         self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
#     def load_image(self):
#         file_path = filedialog.askopenfilename()
#         if file_path:
#             self.image = io.imread(file_path, as_gray=True)
#             self.image = img_as_ubyte(self.image)
#             self.show_image(self.image)
        
#     def show_image(self, image):
#         self.ax.clear()
#         self.ax.imshow(image, cmap='gray')
#         self.canvas.draw()
        
#     def detect_circles(self):
#         if hasattr(self, 'image'):
#             # Ajustar parâmetros do detector Canny
#             edges = canny(self.image, sigma=2, low_threshold=50, high_threshold=100)
            
#             # Ajustar faixa de raios para o Hough Transform
#             hough_radii = np.arange(20, 100, 2)
#             hough_res = hough_circle(edges, hough_radii)
            
#             # Selecionar os círculos mais proeminentes
#             accums, cx, cy, radii = hough_circle_peaks(hough_res, hough_radii, total_num_peaks=1)
            
#             image_rgb = color.gray2rgb(self.image)
#             for center_y, center_x, radius in zip(cy, cx, radii):
#                 circy, circx = circle_perimeter(center_y, center_x, radius, shape=image_rgb.shape)
#                 image_rgb[circy, circx] = (220, 20, 20)
                
#             self.show_image(image_rgb)
#         else:
#             messagebox.showerror("Error", "No image loaded!")

# if __name__ == "__main__":
#     app = CircleDetectionApp()
#     app.mainloop()
