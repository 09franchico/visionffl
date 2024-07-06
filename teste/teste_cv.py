import flet as ft
import cv2
import numpy as np
from PIL import Image
import base64
import json
from io import BytesIO
import asyncio

class TemplateMatchingApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Aplicação de Template Matching em Vídeo da Câmera"
        
        # Variáveis de controle
        self.template_images = []
        self.video_capture = None
        self.current_frame = None
        self.captured_image = None
        self.captured_image_with_rois = None
        self.roi_list = []
        self.roi_names = []
        self.is_drawing = False
        self.ix, self.iy = -1, -1
        self.after_id = None
        
        # Frame para exibição do vídeo
        self.video_container = ft.Container()
        self.page.add(self.video_container)
        
        # Frame para exibição da imagem capturada
        self.image_container = ft.Container()
        self.page.add(self.image_container)
        
        # Botões
        self.start_video_button = ft.ElevatedButton("Iniciar Câmera", on_click=self.start_camera)
        self.capture_button = ft.ElevatedButton("Capturar Imagem", on_click=self.capture_image)
        self.stop_video_button = ft.ElevatedButton("Parar Câmera", on_click=self.stop_camera)
        self.match_button = ft.ElevatedButton("Realizar Template Matching", on_click=self.match_template)
        self.save_button = ft.ElevatedButton("Salvar Imagem e ROIs", on_click=self.save_to_json)
        self.load_button = ft.ElevatedButton("Carregar Imagem e ROIs", on_click=self.load_from_json)
        
        self.page.add(self.start_video_button, self.capture_button, self.stop_video_button, self.match_button, self.save_button, self.load_button)
        
        # Label de aprovação/reprovação
        self.status_label = ft.Text("", size=20)
        self.page.add(self.status_label)
    
        # Variáveis para controle da câmera
        self.is_camera_running = False
    
    def start_camera(self, e):
        if not self.is_camera_running:
            self.video_capture = cv2.VideoCapture(0)
            if self.video_capture.isOpened():
                self.is_camera_running = True
                asyncio.run(self.show_camera())
            else:
                self.show_error("Erro", "Não foi possível iniciar a câmera.")
    
    def stop_camera(self, e):
        self.is_camera_running = False
        if self.video_capture:
            self.video_capture.release()
            self.video_capture = None
            self.video_container.content = None
            self.page.update()
    
    async def show_camera(self):
        while self.is_camera_running:
            ret, frame = self.video_capture.read()
            if ret:
                self.current_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.current_frame_pil = Image.fromarray(self.current_frame)
                self.current_frame_tk = self.image_to_data_url(frame)
                self.video_container.content = ft.Image(src_base64=self.current_frame_tk)
                self.page.update()
                await asyncio.sleep(0.1)
            else:
                self.stop_camera(None)
                self.show_warning("Aviso", "Câmera desconectada ou finalizada.")
                break
    
    def capture_image(self, e):
        if self.current_frame is None:
            self.show_error("Erro", "Inicie a câmera primeiro.")
            return
        
        self.roi_list = []
        self.roi_names = []
        self.template_images = []
        self.status_label.value = ""
        self.captured_image = self.current_frame.copy()
        self.captured_image_with_rois = self.captured_image.copy()
        self.captured_image_pil = Image.fromarray(self.captured_image_with_rois)
        self.captured_image_tk = self.image_to_data_url(self.captured_image)
        self.image_container.content = ft.Image(src_base64=self.captured_image_tk)
        self.page.update()
    
    def match_template(self, e):
        if not self.template_images or self.current_frame is None:
            self.show_error("Erro", "Selecione pelo menos uma ROI")
            return
        
        frame_array = np.array(self.current_frame)
        frame_gray = cv2.cvtColor(frame_array, cv2.COLOR_RGB2GRAY)
        
        all_green = True
        
        for idx, template in enumerate(self.template_images):
            template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            result = cv2.matchTemplate(frame_gray, template_gray, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            h, w = template.shape[:2]
            top_left = max_loc
            bottom_right = (top_left[0] + w, top_left[1] + h)
            
            if max_val >= 0.90:
                color = (0, 255, 0)
            else:
                color = (255, 0, 0)
                all_green = False
            
            roi = self.roi_list[idx]
            cv2.rectangle(self.captured_image_with_rois, (roi[0], roi[1]), (roi[0]+roi[2], roi[1]+roi[3]), color, 2)
        
        self.captured_image_pil = Image.fromarray(self.captured_image_with_rois)
        self.captured_image_tk = self.image_to_data_url(self.current_frame)
        self.image_container.content = ft.Image(src_base64=self.captured_image_tk)
        self.page.update()
        
        if all_green:
            self.status_label.value = "Aprovado"
            self.status_label.color = ft.colors.GREEN
        else:
            self.status_label.value = "Reprovado"
            self.status_label.color = ft.colors.RED
        self.page.update()
    
    def save_to_json(self, e):
        if self.captured_image is None or not self.roi_list:
            self.show_error("Erro", "Nenhuma imagem capturada ou ROIs para salvar.")
            return
        
        file_path = ft.FilePicker.save_file()
        if not file_path:
            return
        
        _, buffer = cv2.imencode('.png', self.captured_image)
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        
        data = {
            'image': image_base64,
            'rois': self.roi_list,
            'names': self.roi_names
        }
        
        with open(file_path, 'w') as json_file:
            json.dump(data, json_file)
        
        self.show_info("Info", "Imagem e ROIs salvos com sucesso.")

    def load_from_json(self, e):
        file_path = ft.FilePicker.open_file()
        if not file_path:
            return
        
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
        
        image_base64 = data['image']
        image_data = base64.b64decode(image_base64)
        image_array = np.frombuffer(image_data, np.uint8)
        self.captured_image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        
        self.roi_list = data['rois']
        self.roi_names = data['names']
        self.template_images = []
        
        for roi in self.roi_list:
            roi_image = self.captured_image[roi[1]:roi[1]+roi[3], roi[0]:roi[0]+roi[2]]
            self.template_images.append(roi_image)
        
        self.captured_image_with_rois = self.captured_image.copy()
        for idx, roi in enumerate(self.roi_list):
            cv2.rectangle(self.captured_image_with_rois, (roi[0], roi[1]), (roi[0]+roi[2], roi[1]+roi[3]), (0, 255, 0), 2)
            cv2.putText(self.captured_image_with_rois, self.roi_names[idx], (roi[0], roi[1] + roi[3] + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (197,29,239), 1, cv2.LINE_AA)
        
        self.captured_image_pil = Image.fromarray(self.captured_image_with_rois)
        self.captured_image_tk = self.image_to_data_url(self.captured_image_pil)
        self.image_container.content = ft.Image(src_base64=self.captured_image_tk)
        self.page.update()
        
        self.show_info("Info", "Imagem e ROIs carregados com sucesso.")

    def show_error(self, title, message):
        self.page.show_snack_bar(ft.SnackBar(ft.Text(f"{message}")))

    def show_warning(self, title, message):
        self.page.show_snack_bar(ft.SnackBar(ft.Text(f"{message}")))

    def show_info(self, title, message):
        self.page.show_snack_bar(ft.SnackBar(ft.Text(f"{message}")))

    def image_to_data_url(self, img):
        
        _, im_arr = cv2.imencode('.png', img)
        
        im_b64 = base64.b64encode(im_arr)
        
        dec = im_b64.decode("utf-8")
        
        return dec
        # buffered = BytesIO()
        # img.save(buffered, format="PNG")
        # return "data:image/png;base64," + base64.b64encode(buffered.getvalue()).decode()



def main(page: ft.Page):
    app = TemplateMatchingApp(page)

ft.app(target=main)
