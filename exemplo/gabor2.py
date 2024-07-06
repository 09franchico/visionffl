import tkinter as tk
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
from skimage import io, color, filters
from skimage.filters import gabor_kernel
import numpy as np
from PIL import Image, ImageTk

# Função para carregar uma imagem
def load_image():
    path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.bmp;*.gif")])
    if path:
        image = io.imread(path)
        if image.ndim == 3:
            image = color.rgb2gray(image)
        update_image(image)

# Função para aplicar filtros de Gabor na imagem e atualizar a visualização
def update_image(image):
    frequencies = [0.1, 0.5]
    thetas = [0, np.pi/2]
    sigmas = [1, 3]

    kernels = []
    for frequency in frequencies:
        for theta in thetas:
            for sigma in sigmas:
                kernel = gabor_kernel(frequency, theta=theta, sigma_x=sigma, sigma_y=sigma)
                kernels.append(kernel)

    filtered_images = []
    for kernel in kernels:
        filtered = filters.convolve(image, np.real(kernel), mode='reflect')
        filtered_images.append(filtered)

    # Mostrar os resultados em uma janela do tkinter
    show_filtered_images(filtered_images)

# Função para exibir imagens filtradas usando tkinter
def show_filtered_images(images):
    new_window = tk.Toplevel(root)
    new_window.title("Resultados dos Filtros de Gabor")
    new_window.geometry("800x600")

    num_images = len(images)
    rows = int(np.sqrt(num_images))
    cols = num_images // rows + (1 if num_images % rows != 0 else 0)

    for i, image in enumerate(images):
        image = (image - image.min()) / (image.max() - image.min())  # Normalização para exibição
        image = (image * 255).astype(np.uint8)  # Escala para 0-255
        image = Image.fromarray(image)

        tk_image = ImageTk.PhotoImage(image)
        label = tk.Label(new_window, image=tk_image)
        label.grid(row=i // cols, column=i % cols, padx=10, pady=10)

        # Salvar uma referência para evitar garbage collection do tk_image
        label.image = tk_image

    new_window.mainloop()

# Configuração da interface gráfica com tkinter
root = tk.Tk()
root.title("Exemplo de Filtros de Gabor com Tkinter")
root.geometry("400x200")

# Botão para carregar a imagem
load_button = tk.Button(root, text="Carregar Imagem", command=load_image)
load_button.pack(pady=20)

root.mainloop()
