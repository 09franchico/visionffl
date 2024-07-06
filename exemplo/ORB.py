import tkinter as tk
from tkinter import filedialog
from skimage import color, io
from skimage.feature import ORB, match_descriptors
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# Variáveis globais para armazenar as imagens
image_ref = None
image_query = None

def load_image_ref():
    global image_ref
    file_path = filedialog.askopenfilename()
    if file_path:
        image_ref = io.imread(file_path)
        process_images()

def load_image_query():
    global image_query
    file_path = filedialog.askopenfilename()
    if file_path:
        image_query = io.imread(file_path)
        process_images()

def process_images():
    if image_ref is not None and image_query is not None:
        image_ref_gray = color.rgb2gray(image_ref)
        image_query_gray = color.rgb2gray(image_query)

        # Criar o detector ORB
        detector = ORB(n_keypoints=500)

        # Detectar características na imagem de referência
        detector.detect_and_extract(image_ref_gray)
        keypoints_ref = detector.keypoints
        descriptors_ref = detector.descriptors

        # Detectar características na imagem de consulta
        detector.detect_and_extract(image_query_gray)
        keypoints_query = detector.keypoints
        descriptors_query = detector.descriptors

        # Encontrar correspondências entre as características
        matches = match_descriptors(descriptors_ref, descriptors_query, cross_check=True)

        fig, ax = plt.subplots(1, 1, figsize=(10, 5))
        
        plt.gray()
        plot_matches(ax, image_ref_gray, image_query_gray, keypoints_ref, keypoints_query, matches)
        ax.axis('off')
        ax.set_title('Correspondências de Características')

        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

def plot_matches(ax, image1, image2, keypoints1, keypoints2, matches):
    """Função auxiliar para plotar correspondências"""
    combined_image = np.concatenate((image1, image2), axis=1)

    ax.imshow(combined_image, cmap='gray')
    ax.scatter(keypoints1[:, 1], keypoints1[:, 0], facecolors='none', edgecolors='r')
    ax.scatter(keypoints2[:, 1] + image1.shape[1], keypoints2[:, 0], facecolors='none', edgecolors='b')

    for i, (idx1, idx2) in enumerate(matches):
        x1, y1 = keypoints1[idx1, 1], keypoints1[idx1, 0]
        x2, y2 = keypoints2[idx2, 1] + image1.shape[1], keypoints2[idx2, 0]
        ax.plot([x1, x2], [y1, y2], 'y-', linewidth=0.5)

# Configuração da janela principal do tkinter
window = tk.Tk()
window.title("Reconhecimento de Padrões com ORB")

# Botões para carregar imagens
btn_load_ref = tk.Button(window, text="Carregar Imagem de Referência", command=load_image_ref)
btn_load_ref.pack(side=tk.TOP, pady=10)

btn_load_query = tk.Button(window, text="Carregar Imagem de Consulta", command=load_image_query)
btn_load_query.pack(side=tk.TOP, pady=10)

window.mainloop()
