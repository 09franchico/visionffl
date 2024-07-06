import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
from skimage import io, color, transform, feature

class CircleDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Circle Detection with scikit-image")
        
        self.load_button = tk.Button(self.root, text="Load Image", command=self.load_image)
        self.load_button.pack(pady=10)
        
        self.detect_button = tk.Button(self.root, text="Detect Circle", command=self.detect_circle)
        self.detect_button.pack(pady=5)
        
        self.canvas = tk.Canvas(self.root, width=400, height=400)
        self.canvas.pack()

        self.image = None
        self.image_display = None
        self.circle_image = None

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])
        if file_path:
            self.image = io.imread(file_path)
            self.display_image(self.image)

    def display_image(self, image):
        # Convert image to tkinter format
        image = Image.fromarray(image)
        image = ImageTk.PhotoImage(image)

        # Keep a reference to avoid garbage collection
        self.image_display = image

        # Display image on canvas
        self.canvas.create_image(0, 0, anchor=tk.NW, image=image)

    def detect_circle(self):
        if self.image is None:
            messagebox.showwarning("No Image", "Please load an image first.")
            return
        
        # Convert image to grayscale
        gray_image = color.rgb2gray(self.image)

        # Apply Canny edge detection
        edges = feature.canny(gray_image, sigma=1.0, low_threshold=0.05, high_threshold=0.2)

        # Define radius range for Hough circle detection
        hough_radii = np.arange(20, 80, 2)

        # Perform Hough circle transform and find peaks
        hough_res = transform.hough_circle(edges, hough_radii)
        accums, cx, cy, radii = transform.hough_circle_peaks(hough_res, hough_radii, total_num_peaks=1)

        # Check if a circle was detected
        if len(cx) > 0:
            center_x = cx[0]
            center_y = cy[0]
            radius = radii[0]
            
            # Increase radius by 20%
            radius *= 1.2

            # Ensure the circle stays within image bounds
            radius = int(radius)
            center_x = int(max(radius, center_x))
            center_y = int(max(radius, center_y))
            if center_x + radius >= self.image.shape[1]:
                center_x = self.image.shape[1] - radius - 1
            if center_y + radius >= self.image.shape[0]:
                center_y = self.image.shape[0] - radius - 1

            # Crop the region of the image that contains the circle
            circle_image = self.image[int(center_y - radius):int(center_y + radius),
                                      int(center_x - radius):int(center_x + radius)]

            # Display the cropped image with the circle
            self.display_image(circle_image)

        else:
            messagebox.showinfo("No Circle Detected", "No circle was detected in the image.")

# Initialize tkinter app
root = tk.Tk()
app = CircleDetectionApp(root)
root.mainloop()
