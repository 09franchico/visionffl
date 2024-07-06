import tkinter as tk
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
from skimage import io, color, filters, transform
import numpy as np
from skimage.feature import shape_index

# Variáveis globais para armazenar as imagens carregadas e seus Shape Index
image_path1 = None
image_path2 = None
shape_index1 = None
shape_index2 = None

def load_image1():
    global image_path1, shape_index1
    image_path1 = filedialog.askopenfilename()
    if image_path1:
        shape_index1 = calculate_shape_index(image_path1)
        if shape_index1 is not None:
            messagebox.showinfo("Imagem 1", "Imagem 1 carregada e Shape Index calculado com sucesso!")
            show_shape_index()

def load_image2():
    global image_path2, shape_index2
    image_path2 = filedialog.askopenfilename()
    if image_path2:
        shape_index2 = calculate_shape_index(image_path2)
        if shape_index2 is not None:
            messagebox.showinfo("Imagem 2", "Imagem 2 carregada e Shape Index calculado com sucesso!")
            show_shape_index()

def calculate_shape_index(image_path):
    try:
        # Carregar a imagem usando scikit-image
        image = io.imread(image_path)

        # Converter para escala de cinza se a imagem for colorida
        if image.ndim == 3:
            image_gray = color.rgb2gray(image)
        else:
            image_gray = image
        
        # Calcular o Shape Index
        index = shape_index(image_gray)
        
        # Redimensionar para um tamanho padrão (opcional)
        index_resized = transform.resize(index, (300, 300), anti_aliasing=True)

        return index_resized
    
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao processar a imagem: {e}")
        return None

def show_shape_index():
    global shape_index1, shape_index2

    if shape_index1 is not None and shape_index2 is not None:
        # Criar uma figura com subplots para exibir os Shape Index das imagens
        fig, axes = plt.subplots(1, 2, figsize=(10, 5))
        
        # Plot do Shape Index da Imagem 1
        axes[0].imshow(shape_index1, cmap='jet')
        axes[0].set_title('Shape Index - Imagem 1')

        # Plot do Shape Index da Imagem 2
        axes[1].imshow(shape_index2, cmap='jet')
        axes[1].set_title('Shape Index - Imagem 2')

        # Ajustar o layout e exibir a figura
        plt.tight_layout()
        plt.show()

def compare_shape_index():
    global shape_index1, shape_index2

    if shape_index1 is not None and shape_index2 is not None:
        try:
            # Calcular alguma medida de similaridade entre os Shape Index
            correlation = np.corrcoef(shape_index1.ravel(), shape_index2.ravel())[0, 1]
            messagebox.showinfo("Similaridade de Shape Index", f"A similaridade entre os Shape Index das imagens é: {correlation:.2f}")
        
        except ValueError as e:
            messagebox.showerror("Erro", f"Erro ao comparar os Shape Index: {e}")

# Criar a interface gráfica com tkinter
root = tk.Tk()
root.title("Verificação de Similaridade de Imagens por Shape Index")

# Botões para carregar as imagens
btn_load_image1 = tk.Button(root, text="Carregar Imagem 1", command=load_image1)
btn_load_image1.pack(pady=10)

btn_load_image2 = tk.Button(root, text="Carregar Imagem 2", command=load_image2)
btn_load_image2.pack(pady=10)

# Botão para mostrar os Shape Index
btn_show_shape_index = tk.Button(root, text="Mostrar Shape Index", command=show_shape_index)
btn_show_shape_index.pack(pady=20)

# Botão para comparar os Shape Index
btn_compare_shape_index = tk.Button(root, text="Comparar Shape Index", command=compare_shape_index)
btn_compare_shape_index.pack(pady=20)

# Iniciar o loop principal do tkinter
root.mainloop()
