import tkinter as tk
from tkinter import filedialog
from skimage import io, color, measure, morphology
from skimage.filters import threshold_otsu
from skimage.segmentation import clear_border
from skimage.restoration import inpaint
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Variáveis globais para armazenar as imagens
image = None
image_result = None

def load_image():
    global image, image_result
    file_path = filedialog.askopenfilename()
    if file_path:
        image = io.imread(file_path)
        image_result = remove_objects(image)
        display_images()

def remove_objects(image):
    image_gray = color.rgb2gray(image)
    
    # Aplicar um limiar Otsu para segmentação
    thresh = threshold_otsu(image_gray)
    binary = image_gray > thresh
    
    # Remover objetos conectados às bordas da imagem
    cleared = clear_border(binary)
    
    # Rotular as regiões conectadas
    label_image = measure.label(cleared)
    
    # Criar uma máscara para os objetos que desejamos remover
    mask = np.zeros(image_gray.shape, dtype=bool)
    for region in measure.regionprops(label_image):
        # Mantemos apenas objetos de tamanho maior que um limite mínimo
        if region.area >= 100:
            for coordinates in region.coords:
                mask[coordinates[0], coordinates[1]] = True

    # Usar a máscara para preencher os objetos removidos
    image_result = inpaint.inpaint_biharmonic(image_gray, ~mask)
    return image_result

def display_images():
    if image is not None and image_result is not None:
        fig, axes = plt.subplots(1, 2, figsize=(10, 5))
        ax = axes.ravel()

        ax[0].imshow(image, cmap='gray')
        ax[0].set_title('Imagem Original')
        ax[0].axis('off')

        ax[1].imshow(image_result, cmap='gray')
        ax[1].set_title('Imagem com Objetos Removidos')
        ax[1].axis('off')

        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

# Configuração da janela principal do tkinter
window = tk.Tk()
window.title("Remoção de Objetos com scikit-image")

# Botão para carregar a imagem
btn_load = tk.Button(window, text="Carregar Imagem", command=load_image)
btn_load.pack(side=tk.TOP, pady=20)

window.mainloop()
