import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog, ttk
import cv2
import numpy as np
from PIL import Image, ImageTk
import json
import threading
import time
import base64
from skimage.color import rgb2gray
from skimage.feature import match_descriptors, plot_matches, SIFT

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
        self.display_image_resized = None
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

        self.capture_button = tk.Button(self.control_frame, text="Limpar", command=self.capture_image)
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
            self.captured_image_original = cv2.imread(file_path)

            # Redimensionar a imagem para uma largura máxima de 800 pixels mantendo a proporção
            self.display_image_resized = self.resize_image(self.captured_image_original, 800, 600)

            self.captured_image = self.display_image_resized.copy()

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
            temp_image = self.display_image_resized.copy()

            cv2.rectangle(temp_image, (self.ix, self.iy), (event.x, event.y), (0, 255, 0), 1)
            self.display_image(temp_image)

    def save_roi(self, event):
        if self.is_drawing and self.captured_image is not None:
            self.is_drawing = False
            ex, ey = event.x, event.y
            if self.ix != ex and self.iy != ey:
                x1, y1 = int(self.ix * self.captured_image_original.shape[1] / self.display_image_resized.shape[1]), int(self.iy * self.captured_image_original.shape[0] / self.display_image_resized.shape[0])
                x2, y2 = int(event.x * self.captured_image_original.shape[1] / self.display_image_resized.shape[1]), int(event.y * self.captured_image_original.shape[0] / self.display_image_resized.shape[0])

                roi_zoom = self.captured_image_original[min(y1, y2):max(y1, y2), min(x1, x2):max(x1, x2)]
                if roi_zoom.size > 0:
                    roi_zoom = cv2.resize(roi_zoom, (200, 200), interpolation=cv2.INTER_CUBIC)
                    roi_zoom_rgb = cv2.cvtColor(roi_zoom, cv2.COLOR_BGR2RGB)
                    roi_zoom_pil = Image.fromarray(roi_zoom_rgb)
                    roi_zoom_tk = ImageTk.PhotoImage(roi_zoom_pil)

                    self.roi_list.append((min(self.ix, ex), min(self.iy, ey), abs(self.ix - ex), abs(self.iy - ey)))
                    roi_name = simpledialog.askstring("Input", "Nome da ROI:")
                    if roi_name:
                        self.roi_names.append(roi_name)
                        self.template_images.append(roi_zoom)
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
            messagebox.showinfo("Info", "A correspondência de template já está em execução.")
            return

        self.matching_thread_running = True
        threading.Thread(target=self.matching_thread).start()

    def matching_thread(self):
        for idx, template in enumerate(self.template_images):
            if not self.matching_thread_running:
                break

            result_image = self.captured_image.copy()
            template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            w, h = template_gray.shape[::-1]

            # Aplicar correspondência de template
            res = cv2.matchTemplate(cv2.cvtColor(result_image, cv2.COLOR_BGR2GRAY), template_gray, cv2.TM_CCOEFF_NORMED)
            threshold = 0.8
            loc = np.where(res >= threshold)

            for pt in zip(*loc[::-1]):
                cv2.rectangle(result_image, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
                cv2.putText(result_image, self.roi_names[idx], (pt[0], pt[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

            self.display_image(result_image)

        self.matching_thread_running = False

    def save_to_json(self):
        if not self.roi_list or not self.template_images:
            messagebox.showerror("Erro", "Nenhuma ROI ou template salvo para exportar.")
            return

        save_dict = {"rois": [], "templates": []}
        for idx, roi in enumerate(self.roi_list):
            save_dict["rois"].append({
                "name": self.roi_names[idx],
                "x": roi[0],
                "y": roi[1],
                "width": roi[2],
                "height": roi[3]
            })

            _, buffer = cv2.imencode('.jpg', self.template_images[idx])
            template_bytes = base64.b64encode(buffer).decode('utf-8')
            save_dict["templates"].append({
                "name": self.roi_names[idx],
                "image_base64": template_bytes
            })

        save_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if save_path:
            with open(save_path, 'w') as f:
                json.dump(save_dict, f, indent=4)
            messagebox.showinfo("Info", "ROIs e templates salvos com sucesso.")

    def load_from_json(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if file_path:
            with open(file_path, 'r') as f:
                load_dict = json.load(f)

            self.roi_list = []
            self.roi_names = []
            self.template_images = []

            for roi_data, template_data in zip(load_dict["rois"], load_dict["templates"]):
                x, y, width, height = roi_data["x"], roi_data["y"], roi_data["width"], roi_data["height"]
                roi_template_bytes = base64.b64decode(template_data["image_base64"])
                roi_template_nparr = np.frombuffer(roi_template_bytes, np.uint8)
                roi_template = cv2.imdecode(roi_template_nparr, cv2.IMREAD_COLOR)

                self.roi_list.append((x, y, width, height))
                self.roi_names.append(roi_data["name"])
                self.template_images.append(roi_template)

            self.captured_image_with_rois = self.captured_image.copy()  # Atualiza a imagem com ROIs desenhadas
            for idx, r in enumerate(self.roi_list):
                cv2.rectangle(self.captured_image_with_rois, (r[0], r[1]), (r[0]+r[2], r[1]+r[3]), (0, 255, 0), 1)
                cv2.putText(self.captured_image_with_rois, self.roi_names[idx], (r[0], r[1] + r[3] + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (197,29,239), 1, cv2.LINE_AA)

            self.display_image(self.captured_image_with_rois)
            messagebox.showinfo("Info", "ROIs e templates carregados com sucesso.")

    def on_closing(self):
        if getattr(self, "matching_thread_running", False):
            self.matching_thread_running = False
            time.sleep(0.5)  # Aguarda um pouco para que a thread possa encerrar

        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = TemplateMatchingApp(root)
    root.mainloop()
