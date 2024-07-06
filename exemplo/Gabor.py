import tkinter as tk
from tkinter import filedialog
from skimage import io, color, filters, feature, transform
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# Variáveis globais para armazenar as imagens e keypoints
image_ref = None
image_query = None
filtered_image_ref = None
filtered_image_query = None
keypoints_ref = None
keypoints_query = None
matches = None

def load_image_ref():
    global image_ref, filtered_image_ref, keypoints_ref
    file_path = filedialog.askopenfilename()
    if file_path:
        image_ref = io.imread(file_path)
        filtered_image_ref = apply_gabor_filter(image_ref)
        keypoints_ref = detect_keypoints(filtered_image_ref)
        process_images()

def load_image_query():
    global image_query, filtered_image_query, keypoints_query
    file_path = filedialog.askopenfilename()
    if file_path:
        image_query = io.imread(file_path)
        filtered_image_query = apply_gabor_filter(image_query)
        keypoints_query = detect_keypoints(filtered_image_query)
        process_images()

def apply_gabor_filter(image):
    image_gray = color.rgb2gray(image)
    theta = np.pi / 4  # orientação do filtro
    frequency = 0.3  # frequência do filtro
    filt_real, filt_imag = filters.gabor(image_gray, frequency=frequency, theta=theta)
    return filt_real

def detect_keypoints(image):
    keypoints = feature.corner_peaks(feature.corner_fast(image), min_distance=5)
    keypoints = feature.corner_subpix(image, keypoints)
    return keypoints

def process_images():
    global matches
    if keypoints_ref is not None and keypoints_query is not None:
        # Descrever keypoints usando descritores simples
        desc_ref = feature.BRIEF(descriptor_size=512)
        desc_query = feature.BRIEF(descriptor_size=512)

        desc_ref.extract(filtered_image_ref, keypoints_ref)
        desc_query.extract(filtered_image_query, keypoints_query)

        # Encontrar correspondências entre os descritores
        matches = feature.match_descriptors(desc_ref.descriptors, desc_query.descriptors, cross_check=True)

        # Exibir resultados
        display_images()

def display_images():
    if image_ref is not None and image_query is not None and matches is not None:
        fig, axes = plt.subplots(1, 2, figsize=(10, 5))
        ax = axes.ravel()

        ax[0].imshow(np.concatenate((image_ref, image_query), axis=1), cmap='gray')
        ax[0].set_title('Imagens Originais')
        ax[0].axis('off')

        plot_matches(ax[1], filtered_image_ref, filtered_image_query, keypoints_ref, keypoints_query, matches)
        ax[1].set_title('Correspondências de Padrões')

        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

def plot_matches(ax, image1, image2, keypoints1, keypoints2, matches):
    """Função para desenhar correspondências entre keypoints em duas imagens"""
    ax.imshow(np.concatenate((image1, image2), axis=1), cmap='gray')
    ax.axis('off')

    for match in matches:
        idx_ref, idx_query = match
        y_ref, x_ref = keypoints1[idx_ref]
        y_query, x_query = keypoints2[idx_query]

        line = plt.Line2D([x_ref, x_query + image1.shape[1]], [y_ref, y_query], linewidth=0.5, color='yellow')
        ax.add_line(line)

# Configuração da janela principal do tkinter
window = tk.Tk()
window.title("Detecção de Padrões com Filtros de Gabor")

# Botões para carregar as imagens de referência e consulta
btn_load_ref = tk.Button(window, text="Carregar Imagem de Referência", command=load_image_ref)
btn_load_ref.pack(side=tk.TOP, pady=10)

btn_load_query = tk.Button(window, text="Carregar Imagem de Consulta", command=load_image_query)
btn_load_query.pack(side=tk.TOP, pady=10)

window.mainloop()
