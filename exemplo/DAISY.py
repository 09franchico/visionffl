import tkinter as tk
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
from skimage import io, feature, color
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Função para carregar uma imagem
def load_image(image_num):
    path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.bmp;*.gif")])
    if path:
        image = io.imread(path)
        if image.ndim == 3:
            image = color.rgb2gray(image)
        if image_num == 1:
            global image1, desc1
            image1 = image
            desc1 = compute_daisy(image1)
            label_image1.config(text="Imagem 1 Carregada")
        elif image_num == 2:
            global image2, desc2
            image2 = image
            desc2 = compute_daisy(image2)
            label_image2.config(text="Imagem 2 Carregada")
    
    # Atualizar a visualização
    update_visualization()

# Função para calcular os descritores DAISY e retornar a imagem visualizada
def compute_daisy(image):
    img_desc, desc = feature.daisy(image, step=8, radius=15, rings=2, histograms=6, orientations=8, visualize=True)
    return desc.ravel()

# Função para comparar as imagens usando os descritores DAISY
def compare_images():
    global image1, image2, desc1, desc2
    if image1 is not None and image2 is not None:
        similarity = np.dot(desc1, desc2) / (np.linalg.norm(desc1) * np.linalg.norm(desc2))
        similarity_percentage = similarity * 100

        messagebox.showinfo("Similaridade", f"A similaridade entre as imagens é de aproximadamente {similarity_percentage:.2f}%.")
    else:
        messagebox.showwarning("Aviso", "Carregue ambas as imagens primeiro.")

# Função para atualizar a visualização das imagens e descritores
def update_visualization():
    if image1 is not None and image2 is not None:
        fig, axes = plt.subplots(1, 2, figsize=(10, 5))

        axes[0].imshow(image1, cmap='gray')
        axes[0].set_title('Imagem 1')

        axes[1].imshow(image2, cmap='gray')
        axes[1].set_title('Imagem 2')

        for ax in axes:
            ax.axis('off')

        # Atualizar o plot na interface gráfica do tkinter
        canvas = FigureCanvasTkAgg(fig, master=root)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

# Configuração da interface gráfica com tkinter
root = tk.Tk()
root.title("Comparação de Imagens com Descritores DAISY")
root.geometry("800x600")

image1 = None
image2 = None
desc1 = None
desc2 = None

# Labels para mostrar o status das imagens carregadas
label_image1 = tk.Label(root, text="Carregue a Imagem 1")
label_image1.pack(pady=5)

label_image2 = tk.Label(root, text="Carregue a Imagem 2")
label_image2.pack(pady=5)

# Botões para carregar as imagens e comparar
button_load_image1 = tk.Button(root, text="Carregar Imagem 1", command=lambda: load_image(1))
button_load_image1.pack(pady=10)

button_load_image2 = tk.Button(root, text="Carregar Imagem 2", command=lambda: load_image(2))
button_load_image2.pack(pady=10)

button_compare = tk.Button(root, text="Comparar Imagens", command=compare_images)
button_compare.pack(pady=10)

root.mainloop()
