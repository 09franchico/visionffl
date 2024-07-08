import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog, ttk
import matplotlib.pyplot as plt
import cv2
import numpy as np
from PIL import Image, ImageTk
import json
import threading
import time
import base64
from skimage.color import rgb2gray
from skimage.feature import match_descriptors, plot_matches, SIFT
from skimage import data, transform
from skimage.util import img_as_ubyte
from skimage.morphology import disk
from skimage.filters import rank
from skimage import io, color, feature, transform

class TemplateMatchingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Aplicação de Template Matching em Imagem")

        # Variáveis de controle
        self.template_images = []
        self.current_frame = None
        self.captured_image = None
        self.captured_image_with_rois = None  # Para manter a imagem com ROIs desenhadas
        self.roi_list = []
        self.roi_names = []
        self.is_drawing = False
        self.ix, self.iy = -1, -1
        self.display_image_resized = None
        self.after_id = None  # Inicializa o ID do agendamento como None

        # Frame para exibição da imagem carregada
        self.image_frame = tk.Frame(self.root)
        self.image_frame.grid(row=0, column=0, padx=10, pady=10)

        # Label para a imagem carregada
        self.image_label = tk.Label(self.image_frame)
        self.image_label.pack()
        self.image_label.bind("<Button-1>", self.start_draw)
        self.image_label.bind("<B1-Motion>", self.draw_rectangle)
        self.image_label.bind("<ButtonRelease-1>", self.save_roi)

        # Frame para os botões de controle
        self.control_frame = tk.Frame(self.root)
        self.control_frame.grid(row=1, column=0, padx=5, pady=5)
        

        # Botões
        self.load_image_button = tk.Button(self.control_frame, text="Carregar Imagem", command=self.load_image)
        self.load_image_button.grid(row=0, column=0, padx=5, pady=5)

        self.capture_button = tk.Button(self.control_frame, text="Limpar", command=self.capture_image)
        self.capture_button.grid(row=0, column=1, padx=5, pady=5)

        self.match_button = tk.Button(self.control_frame, text="Realizar Template Matching", command=self.start_matching_thread)
        self.match_button.grid(row=0, column=2, padx=5, pady=5)

        self.save_button = tk.Button(self.control_frame, text="Salvar ROIs", command=self.save_to_json)
        self.save_button.grid(row=1, column=0, padx=5, pady=5)

        self.load_button = tk.Button(self.control_frame, text="Carregar ROIs", command=self.load_from_json)
        self.load_button.grid(row=1, column=1, padx=5, pady=5)

        # Label de aprovação/reprovação
        self.status_label = tk.Label(self.control_frame, text="", font=('Helvetica', 16),width=20)
        self.status_label.grid(row=2, column=0, padx=5, pady=5, columnspan=4)
        
         # Barra de progresso
        self.progress = ttk.Progressbar(self.control_frame, orient="horizontal", length=400, mode="determinate")
        self.progress.grid(row=3, column=0, padx=5, pady=5, columnspan=4)

        # Label para mostrar o tempo
        self.time_label = tk.Label(self.control_frame, text="Tempo: 0s", font=('Helvetica', 10))
        self.time_label.grid(row=4, column=0, padx=5, pady=5, columnspan=4)
        
        
        self.frame_image_detect = tk.Frame(self.root)
        self.frame_image_detect.grid(row=0, column=1, padx=10, pady=10)
 
        
        self.zoom_label = tk.Label(self.frame_image_detect)
        self.zoom_label.grid(row=0, column=0, padx=10, pady=10)
        
        self.zoom_label_circulo = tk.Label(self.frame_image_detect)
        self.zoom_label_circulo.grid(row=1, column=0, padx=10, pady=10)


        # Configurar estilo para as tags
        self.style = ttk.Style()
        self.style.configure("Treeview.Heading", font=('Helvetica', 10, 'bold'))
        self.style.configure("OK.T", background="green")
        self.style.configure("NotFound.T", background="red")

    

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Variáveis para controle da câmera
        self.is_camera_running = False


    
    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.bmp")])
        if file_path:
            self.captured_image = cv2.imread(file_path)
            
            self.display_image_resized = self.resize_image(self.captured_image, 800, 600)
            
            self.captured_image_with_rois = self.display_image_resized.copy()
            
            self.display_image(self.captured_image_with_rois)
            
            
    def resize_image(self, image, width, height):
        pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        resized_image = pil_image.resize((width, height), Image.LANCZOS)
        return cv2.cvtColor(np.array(resized_image), cv2.COLOR_RGB2BGR)
    

    def capture_image(self):
        if self.captured_image is None:
            messagebox.showerror("Erro", "Nenhuma imagem carregada.")
            return
        
          # Parar a thread de correspondência se estiver em execução
        if getattr(self, "matching_thread_running", False):
            self.matching_thread_running = False

        # Limpa as listas de ROIs e templates
        self.roi_list = []
        self.roi_names = []
        self.template_images = []
        self.status_label.config(text="", bg="#f0f0f0")

        self.captured_image_with_rois = self.display_image_resized.copy()  # Copia inicial da imagem capturada
        self.display_image(self.captured_image_with_rois)

    def display_image(self, image):
        self.captured_image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        self.captured_image_tk = ImageTk.PhotoImage(self.captured_image_pil)
        self.image_label.configure(image=self.captured_image_tk)
        self.image_label.image = self.captured_image_tk

    def start_draw(self, event):
        if self.captured_image is None:
            return
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
                
                
    def save_roi(self, event):
        if self.is_drawing and self.captured_image is not None:
            self.is_drawing = False
            ex, ey = event.x, event.y
            if self.ix != ex and self.iy != ey:
                x1, y1 = int(self.ix * self.captured_image.shape[1] / self.display_image_resized.shape[1]), int(self.iy * self.captured_image.shape[0] / self.display_image_resized.shape[0])
                x2, y2 = int(event.x * self.captured_image.shape[1] / self.display_image_resized.shape[1]), int(event.y * self.captured_image.shape[0] / self.display_image_resized.shape[0])

                roi_zoom = self.captured_image[min(y1, y2):max(y1, y2), min(x1, x2):max(x1, x2)]
                roi = (min(self.ix, ex), min(self.iy, ey), abs(self.ix - ex), abs(self.iy - ey))
                


                roi_dialog = ROIDialog(self.root)
                roi_name = roi_dialog.roi_name
                roi_type = roi_dialog.roi_type
                

                if roi_name and roi_type:
                    
                    
                    if roi_type != "p" and roi_type != "b":
                        messagebox.showerror("Erro", "Vericar o tipo de componente")
                        return 
                    
                    image_circ_detect = self.detect_circles_type(roi_zoom,roi_type)
                    if image_circ_detect is not None:
                        roi_zoom_rgb = cv2.cvtColor(image_circ_detect, cv2.COLOR_BGR2RGB)
                        roi_zoom_pil = Image.fromarray(roi_zoom_rgb)
                        roi_zoom_tk = ImageTk.PhotoImage(roi_zoom_pil)
                        self.zoom_label_circulo.configure(image=roi_zoom_tk)
                        self.zoom_label_circulo.image = roi_zoom_tk
                    else:
                        messagebox.showerror("Erro", "Nenhum circulo encontrado!")
                        return 
                    
                    confirm = messagebox.askyesno("Confirmação", "Você deseja salvar esta ROI como template?")
                    if confirm:
                        self.roi_list.append(roi)
                        self.roi_names.append((roi_name, roi_type))  # Store both name and type
                        roi_image = image_circ_detect
                        self.template_images.append(roi_image)
                        self.captured_image_with_rois = self.display_image_resized.copy()  # Atualiza a imagem com ROIs desenhadas
                        for idx, r in enumerate(self.roi_list):
                            cv2.rectangle(self.captured_image_with_rois, (r[0], r[1]), (r[0]+r[2], r[1]+r[3]), (0, 255, 0), 1)
                            name, type_ = self.roi_names[idx]
                            cv2.putText(self.captured_image_with_rois, f"{name}", (r[0], r[1] + r[3] + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (197,29,239), 1, cv2.LINE_AA)

                        self.display_image(self.captured_image_with_rois)
                        
            
                    
                    
                    

    def start_matching_thread(self):
        if not self.template_images or self.captured_image is None:
            messagebox.showerror("Erro", "Selecione pelo menos uma ROI e carregue uma imagem.")
            return

        # Verifica se a thread já está em execução
        if getattr(self, "matching_thread_running", False):
            return

        # Define a função alvo da thread
        def match_thread_func():
                self.status_label.config(text="", bg="#f0f0f0")
                self.progress['value'] = 0
                self.time_label.config(text="Tempo: 0s")
                self.match_template()
                

        # Inicia a thread
        self.matching_thread = threading.Thread(target=match_thread_func)
        self.matching_thread.daemon = True
        self.matching_thread.start()

    def on_closing(self):
        self.matching_thread_running = False
        self.root.destroy()
    
            
    def detect_polarity(self, img, show_pol=False):
        ori = 'I'
        if img.ndim > 2:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img

        gray_blurred = cv2.medianBlur(gray, 5)
        shape = gray.shape
        min_radius = int(shape[0] / 6)
        max_radius = int(shape[0] / 2)

        detected_circles = cv2.HoughCircles(gray_blurred, cv2.HOUGH_GRADIENT, 1, 20, param1=200, param2=40, minRadius=min_radius, maxRadius=max_radius)

        if detected_circles is not None:
            detected_circles = np.uint16(np.around(detected_circles))
            a, b, r = -1, -1, -1
            center_a, center_b = int(shape[0] / 2), int(shape[1] / 2)
            for pt in detected_circles[0, :]:
                if a == -1 or b == -1:
                    a, b, r = pt[0], pt[1], pt[2]
                if (abs(a - center_a) + abs(b - center_b)) > (abs(pt[0] - center_a) + abs(pt[1] - center_b)):
                    a, b, r = pt[0], pt[1], pt[2]

            color = (0, 255, 0)
            mask = cv2.circle(img, (a, b), r, color, 2)
            xa1, ya1, xa2, ya2 = a - r + int(r / 2), (b - r), (a + r - int(r / 2)), (b - r + int(r / 2))
            xb1, yb1, xb2, yb2 = a - r + int(r / 2), b + r, a + r - int(r / 2), b + r - int(r / 2)
            xc1, yc1, xc2, yc2 = a - r, b - r + int(r / 2), a - r + int(r / 2), b + r - int(r / 2)
            xd1, yd1, xd2, yd2 = a + r, b - r + int(r / 2), a + r - int(r / 2), b + r - int(r / 2)
            rect1 = cv2.rectangle(img, (a - r + int(r / 2), b - r), (a + r - int(r / 2), b - r + int(r / 2)), color, 1)
            rect2 = cv2.rectangle(img, (a - r + int(r / 2), b + r), (a + r - int(r / 2), b + r - int(r / 2)), color, 1)
            rect3 = cv2.rectangle(img, (a - r + int(r / 2), b - r + int(r / 2)), (a - r + int(r / 2), b + r - int(r / 2)), color, 1)
            rect4 = cv2.rectangle(img, (a + r - int(r / 2), b - r + int(r / 2)), (a + r - int(r / 2), b + r - int(r / 2)), color, 1)

            irect1 = gray[ya1:ya2, xa1:xa2]
            irect2 = gray[yb2:yb1, xb1:xb2]
            irect3 = gray[yc1:yc2, xc1:xc2]
            irect4 = gray[yd1:yd2, xd2:xd1]

            top = cv2.mean(irect1)
            bottom = cv2.mean(irect2)
            left = cv2.mean(irect3)
            right = cv2.mean(irect4)

            if show_pol:
                cv2.circle(img, (a, b), 1, (0, 0, 255), 3)
                cv2.imshow("Detected Circle", img)
                cv2.waitKey(0)

            if (top < bottom) and (top < left) and (top < right):
                ori = 'N'
            elif (bottom < top) and (bottom < left) and (bottom < right):
                ori = 'S'
            elif (right < top) and (right < left) and (right < bottom):
                ori = 'L'
            elif (left < top) and (left < bottom) and (left < right):
                ori = 'O'

        return ori
    
    
    def windowed_histogram_similarity(self, image, footprint, reference_hist, n_bins):
        px_histograms = rank.windowed_histogram(image, footprint, n_bins=n_bins)
        reference_hist = reference_hist.reshape((1, 1) + reference_hist.shape)
        X = px_histograms
        Y = reference_hist
        num = (X - Y) ** 2
        denom = X + Y
        denom[denom == 0] = np.inf
        frac = num / denom
        chi_sqr = 0.5 * np.sum(frac, axis=2)
        similarity = 1 / (chi_sqr + 1.0e-4)
        return similarity

            
    
    def match_template(self):
        if not self.template_images or self.captured_image is None or not self.roi_list:
            messagebox.showerror("Erro", "Selecione pelo menos uma ROI e carregue uma imagem.")
            return

        frame_array = np.array(self.display_image_resized)
    
        start_time = time.time()
        all_matches_found = True

        for idx, roi in enumerate(self.roi_list):
            x, y, w, h = roi
            x_original = int(x * self.captured_image.shape[1] / self.display_image_resized.shape[1])
            y_original = int(y * self.captured_image.shape[0] / self.display_image_resized.shape[0])
            w_original = int(w * self.captured_image.shape[1] / self.display_image_resized.shape[1])
            h_original = int(h * self.captured_image.shape[0] / self.display_image_resized.shape[0])

            roi_image = self.captured_image[y_original:y_original+h_original, x_original:x_original+w_original].copy()

            # Pegar a imagem template correspondente
            template_image = self.template_images[idx]
            template_name, types = self.roi_names[idx]

            try:
                
                result = cv2.matchTemplate(roi_image, template_image, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                print("Valor: ",max_val)
                if max_val >= 0.90:  # Limite de confiança
                    color = (0, 255, 0)  # Verde
                    
                else:
                    color = (0, 0, 255)
                    all_matches_found = False
                
                    
                self.progress['value'] = (idx + 1) * 100 / len(self.template_images)
                self.root.update_idletasks()
    
               # Desenhar retângulo na imagem original correspondente à ROI
                cv2.rectangle(frame_array, (x, y), (x+w, y+h), color, 1)
                text_position = (x, y + h + 10)
                cv2.putText(frame_array, template_name, text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 165, 255), 1, cv2.LINE_AA)

            except cv2.error as e:
                print(f"Erro ao realizar template matching: {e}")
                all_matches_found = False
                
                
                
        elapsed_time = time.time() - start_time
        self.time_label.config(text=f"Tempo: {elapsed_time:.2f}s")

        if all_matches_found:
            self.status_label.config(text="Aprovado", bg="green")
        else:
            self.status_label.config(text="Reprovado", bg="red")

        self.display_image(frame_array)
        
    def detect_circles_type(self, imagem,type):
        # Convertendo para escala de cinza
        gray_image = color.rgb2gray(imagem)
        
        # Aplicando transformada de Hough para detectar círculos
        edges = feature.canny(gray_image, sigma=2.0, low_threshold=0.1, high_threshold=0.3)
        hough_radii = np.arange(20, 100, 2)
        hough_res = transform.hough_circle(edges, hough_radii)
        
        # Encontrando picos na transformada de Hough
        accums, cx, cy, radii = transform.hough_circle_peaks(hough_res, hough_radii, total_num_peaks=1)
        
        # Verifica se foi encontrado algum círculo
        if len(cx) > 0:
            center_x = cx[0]
            center_y = cy[0]
            radius = radii[0]
            
            
            if type == "p":
                scale_factor = 2
                radius = int(radius * scale_factor)
                
                # Garantindo que os índices de recorte não saiam dos limites da imagem
                minr = max(0, int(center_y - radius))
                maxr = min(imagem.shape[0], int(center_y + radius))
                minc = max(0, int(center_x - radius))
                maxc = min(imagem.shape[1], int(center_x + radius))
                
                # Recorta a região da imagem que contém o círculo
                imagem_recortada = imagem[minr:maxr, minc:maxc]
                
            if type == "b":
                # # Recorta a região da imagem que contém o círculo
                imagem_recortada = imagem[int(center_y - radius):int(center_y + radius), 
                                          int(center_x - radius):int(center_x + radius)]
                

            
            return imagem_recortada
        
        else:
            return None
        
        
    def detect_circles(self, imagem):
        # Convertendo para escala de cinza
        gray_image = color.rgb2gray(imagem)
        
        # Aplicando transformada de Hough para detectar círculos
        edges = feature.canny(gray_image, sigma=2.0, low_threshold=0.1, high_threshold=0.3)
        hough_radii = np.arange(20, 100, 2)
        hough_res = transform.hough_circle(edges, hough_radii)
        
        # Encontrando picos na transformada de Hough
        accums, cx, cy, radii = transform.hough_circle_peaks(hough_res, hough_radii, total_num_peaks=1)
        
        # Verifica se foi encontrado algum círculo
        if len(cx) > 0:
            center_x = cx[0]
            center_y = cy[0]
            radius = radii[0]
        
            imagem_recortada = imagem[int(center_y - radius):int(center_y + radius), 
                                      int(center_x - radius):int(center_x + radius)]
            

            
            return imagem_recortada
        
        else:
            return None
        
        
    # Função para identificar componentes conectados (objetos) e verificar a presença de cinza e branco
    def find_gray_and_white_components(self,image_data):
        gray_image = cv2.cvtColor(image_data, cv2.COLOR_BGR2GRAY)
        # Binarização da imagem (thresholding)
        _, binary_image = cv2.threshold(gray_image, 127, 255, cv2.THRESH_BINARY)

        # Encontra componentes conectados
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary_image, connectivity=8)

        # Filtrar componentes conectados por área entre 800 e 10000 pixels quadrados
        min_area = 500
        max_area = 10000

        # Converte imagem para formato colorido, se necessário
        if len(gray_image.shape) == 2:  # Se for imagem em escala de cinza
            image_data = cv2.cvtColor(gray_image, cv2.COLOR_GRAY2BGR)

        # Analisa componentes conectados
        for i in range(1, num_labels):  # começa do 1 para ignorar o fundo (label 0)
            x, y, w, h, area = stats[i]
            if min_area <= area <= max_area:
                # Extrai o componente conectado como uma máscara binária
                component_mask = (labels == i).astype(np.uint8) * 255
                component_pixels = image_data[labels == i]

                # Verifica a presença de cinza e branco
                contains_gray = np.any((component_pixels >= 100) & (component_pixels <= 200))
                contains_white = np.any(component_pixels == 255)

                if contains_gray and contains_white:
                    cv2.rectangle(image_data, (x, y), (x + w, y + h), (255, 0, 0), 2)

        return image_data


   
    def is_image_equal(self, img1, img2, max_ratio=0.6, min_matches=10):
        try:
            # Verifica se as imagens têm 3 canais e converte para escala de cinza, se necessário
            if img1.ndim == 3 and img1.shape[2] == 3:
                img1_gray = rgb2gray(img1)
            else:
                img1_gray = img1
            
            if img2.ndim == 3 and img2.shape[2] == 3:
                img2_gray = rgb2gray(img2)
            else:
                img2_gray = img2

            descriptor_extractor = SIFT()

            # Detectar e extrair descritores na imagem de referência
            descriptor_extractor.detect_and_extract(img1_gray)
            keypoints1 = descriptor_extractor.keypoints
            descriptors1 = descriptor_extractor.descriptors

            # Detectar e extrair descritores na imagem a ser comparada
            descriptor_extractor.detect_and_extract(img2_gray)
            keypoints2 = descriptor_extractor.keypoints
            descriptors2 = descriptor_extractor.descriptors

            # Encontrar correspondências
            matches = match_descriptors(descriptors1, descriptors2, max_ratio=max_ratio, cross_check=True)
            
            # fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(8, 6))
            # plot_matches(ax, img1_gray, img2_gray, keypoints1, keypoints2, matches)
            # ax.axis('off')
            # ax.set_title("Correspondências entre as imagens")
            # plt.show()
            
            print(f"Número de correspondências detectadas: {len(matches)}")
            
            # Verificar se a quantidade de correspondências é suficiente
            if len(matches) >= min_matches:
                print("As imagens são iguais.")
                return True
            else:
                print("As imagens são diferentes.")
                return False

        except Exception as e:
            print(f"Ocorreu um erro: {e}")
            return False

    def save_to_json(self):
        if not self.roi_list:
            messagebox.showerror("Erro", "Nenhuma ROI capturada para salvar.")
            return

        save_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if save_path:
            data = {
                "rois": self.roi_list,
                "roi_names": self.roi_names,
                "templates": [self.image_to_base64(template) for template in self.template_images]
            }
            with open(save_path, 'w') as f:
                json.dump(data, f)
            messagebox.showinfo("Info", "ROIs salvas com sucesso.")

    def load_from_json(self):
        load_path = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if load_path:
            with open(load_path, 'r') as f:
                data = json.load(f)
            self.roi_list = data["rois"]
            self.roi_names = data["roi_names"]
            self.template_images = [self.base64_to_image(template) for template in data["templates"]]

            self.captured_image_with_rois = self.display_image_resized.copy()  # Copia inicial da imagem capturada
            for idx, roi in enumerate(self.roi_list):
                
                name, tipy = self.roi_names[idx]
                cv2.rectangle(self.captured_image_with_rois, (roi[0], roi[1]), 
                              (roi[0]+roi[2], roi[1]+roi[3]), 
                              (0, 255, 0), 1)
                cv2.putText(self.captured_image_with_rois, name, 
                            (roi[0], roi[1] + roi[3] + 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.3, (197,29,239), 1, cv2.LINE_AA)


            self.display_image(self.captured_image_with_rois)

            messagebox.showinfo("Info", "ROIs carregadas com sucesso.")

    def image_to_base64(self, image):
        _, buffer = cv2.imencode('.png', image)
        return base64.b64encode(buffer).decode()

    def base64_to_image(self, base64_string):
        img_data = base64.b64decode(base64_string)
        np_arr = np.frombuffer(img_data, np.uint8)
        return cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    
    
    
  
class ROIDialog(simpledialog.Dialog):
    def body(self, master):
        tk.Label(master, text="Nome da ROI:").grid(row=0)
        tk.Label(master, text="Tipo da ROI:").grid(row=1)

        self.name_entry = tk.Entry(master)
        self.type_entry = tk.Entry(master)

        self.name_entry.grid(row=0, column=1)
        self.type_entry.grid(row=1, column=1)
        
        return self.name_entry  # initial focus

    def apply(self):
        self.roi_name = self.name_entry.get()
        self.roi_type = self.type_entry.get()
        
    def destroy(self) -> None:
        self.roi_name = self.name_entry.get()
        self.roi_type = self.type_entry.get()
        return super().destroy()




if __name__ == "__main__":
    root = tk.Tk()
    app = TemplateMatchingApp(root)
    root.mainloop()