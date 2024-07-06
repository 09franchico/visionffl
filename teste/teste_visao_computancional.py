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

        self.capture_button = tk.Button(self.control_frame, text="Capturar Imagem", command=self.capture_image)
        self.capture_button.grid(row=0, column=1, padx=5, pady=5)

        self.match_button = tk.Button(self.control_frame, text="Realizar Template Matching", command=self.start_matching_thread)
        self.match_button.grid(row=0, column=2, padx=5, pady=5)

        self.save_button = tk.Button(self.control_frame, text="Salvar ROIs", command=self.save_to_json)
        self.save_button.grid(row=1, column=0, padx=5, pady=5)

        self.load_button = tk.Button(self.control_frame, text="Carregar ROIs", command=self.load_from_json)
        self.load_button.grid(row=1, column=1, padx=5, pady=5)

        # Label de aprovação/reprovação
        self.status_label = tk.Label(self.control_frame, text="", font=('Helvetica', 16))
        self.status_label.grid(row=2, column=0, padx=5, pady=5, columnspan=2)

        # Tabela para mostrar os ROIs e seus status
        self.table_frame = tk.Frame(self.root)
        self.table_frame.grid(row=2, column=0, padx=5, pady=5)


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

            # Redimensionar a imagem para uma largura máxima de 800 pixels mantendo a proporção
            max_width = 800
            height, width = self.captured_image.shape[:2]
            if width > max_width:
                scale = max_width / width
                new_width = int(width * scale)
                new_height = int(height * scale)
                self.captured_image = cv2.resize(self.captured_image, (new_width, new_height), interpolation=cv2.INTER_AREA)

            self.captured_image_with_rois = self.captured_image.copy()  # Copia inicial da imagem capturada
            self.display_image(self.captured_image_with_rois)

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

        self.captured_image_with_rois = self.captured_image.copy()  # Copia inicial da imagem capturada
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
            # Cópia temporária para mostrar a seleção atual
            temp_image = self.captured_image_with_rois.copy()
            cv2.rectangle(temp_image, (self.ix, self.iy), (event.x, event.y), (0, 255, 0), 1)
            self.display_image(temp_image)

    def save_roi(self, event):
        if self.is_drawing and self.captured_image is not None:
            self.is_drawing = False
            ex, ey = event.x, event.y
            if self.ix != ex and self.iy != ey:
                roi = (min(self.ix, ex), min(self.iy, ey), abs(self.ix - ex), abs(self.iy - ey))
                roi_name = simpledialog.askstring("Input", "Nome da ROI:")
                if roi_name:
                    self.roi_list.append(roi)
                    self.roi_names.append(roi_name)
                    roi_array = np.array(self.captured_image)
                    roi_image = roi_array[roi[1]:roi[1]+roi[3], roi[0]:roi[0]+roi[2]]
                    self.template_images.append(roi_image)
                    self.captured_image_with_rois = self.captured_image.copy()  # Atualiza a imagem com ROIs desenhadas
                    for idx, r in enumerate(self.roi_list):
                        cv2.rectangle(self.captured_image_with_rois, (r[0], r[1]), (r[0]+r[2], r[1]+r[3]), (0, 255, 0), 1)
                        cv2.putText(self.captured_image_with_rois, self.roi_names[idx], (r[0], r[1] + r[3] + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (197,29,239), 1, cv2.LINE_AA)

                    self.display_image(self.captured_image_with_rois)
                    messagebox.showinfo("Info", "ROI selecionada e salva como template.")

    def start_matching_thread(self):
        if not self.template_images or self.captured_image is None:
            messagebox.showerror("Erro", "Selecione pelo menos uma ROI e carregue uma imagem.")
            return

        # Verifica se a thread já está em execução
        if getattr(self, "matching_thread_running", False):
            return

        # Define a função alvo da thread
        def match_thread_func():
            self.matching_thread_running = True
            while self.matching_thread_running:
                self.match_template()
                time.sleep(1)

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


    def match_template(self):
        if not self.template_images or self.captured_image is None:
            messagebox.showerror("Erro", "Selecione pelo menos uma ROI e carregue uma imagem.")
            return

        frame_array = np.array(self.captured_image)
        gray_frame = cv2.cvtColor(frame_array, cv2.COLOR_BGR2GRAY)

        self.captured_image_with_rois = self.captured_image.copy() # Copia inicial da imagem capturada
        
        all_matches_found = True

        for idx, template in enumerate(self.template_images):
            template_name = self.roi_names[idx]
            gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            
             # Aumenta a escala da imagem para visualização
            scale_factor = 1  # Ajuste o fator de escala conforme necessário
            scaled_template = cv2.resize(gray_template, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_LINEAR)
            
            teste = self.detect_polarity(scaled_template,show_pol=True)
            print(teste)
        
            result = cv2.matchTemplate(gray_frame, gray_template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            

            top_left = max_loc
            bottom_right = (top_left[0] + gray_template.shape[1], top_left[1] + gray_template.shape[0])

            if max_val >= 0.90:  # Limite de confiança
                color = (0, 255, 0)  # Verde
                # cv2.rectangle(self.captured_image_with_rois, top_left, bottom_right, (0, 255, 0), 2)
                
            else:
                all_matches_found = False
                color = (0, 0, 255)
                
            
            cv2.rectangle(self.captured_image_with_rois, top_left, bottom_right, color, 1)
            
            text_position = (top_left[0], bottom_right[1] + 9)
            cv2.putText(self.captured_image_with_rois, template_name, text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 165, 255), 1, cv2.LINE_AA)

        self.display_image(self.captured_image_with_rois)

        if all_matches_found:
            self.status_label.config(text="Aprovado", bg="green")
        else:
            self.status_label.config(text="Reprovado", bg="red")

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

            self.captured_image_with_rois = self.captured_image.copy()  # Copia inicial da imagem capturada
            for idx, roi in enumerate(self.roi_list):
                cv2.rectangle(self.captured_image_with_rois, (roi[0], roi[1]), 
                              (roi[0]+roi[2], roi[1]+roi[3]), 
                              (0, 255, 0), 1)
                cv2.putText(self.captured_image_with_rois, self.roi_names[idx], 
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

if __name__ == "__main__":
    root = tk.Tk()
    app = TemplateMatchingApp(root)
    root.mainloop()