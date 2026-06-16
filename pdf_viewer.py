import tkinter as tk
from tkinter import ttk
import fitz
from PIL import Image, ImageTk, ImageDraw, ImageFont
import os
import io

class PDFViewer(ttk.Frame):
    def __init__(self, parent, width=700, height=550):
        super().__init__(parent)
        self.width = width
        self.height = height
        self.doc = None
        self.current_page = 0
        self.total_pages = 0
        self.zoom = 1.0
        
        # Variables para la firma
        self.firma_item = None
        self.firma_position = None
        self.firma_imagen = None
        self.firma_photo = None
        
        # Variables para el arrastre con sombra
        self.dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.shadow_item = None
        self.shadow_photo = None
        self.firma_original_pos = None
        
        # Crear widget de visualización
        self.canvas = tk.Canvas(self, width=width, height=height, bg='white', 
                                cursor='cross')
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        h_scroll = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.canvas.xview)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        self.canvas.bind("<Configure>", self.on_resize)
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<Leave>", self.on_mouse_leave)
        
        # Cargar imagen de firma
        self.cargar_imagen_firma()
        
    def cargar_imagen_firma(self):
        """Carga la imagen del sello desde assets"""
        try:
            # Intentar cargar la imagen del sello
            sello_path = "assets/images/sello_small.png"
            if os.path.exists(sello_path):
                self.firma_imagen = Image.open(sello_path)
                self.firma_imagen = self.firma_imagen.resize((280, 145), Image.Resampling.LANCZOS)
            else:
                # Crear imagen por defecto si no existe
                self.crear_imagen_firma_default()
        except Exception as e:
            print(f"Error cargando imagen: {e}")
            self.crear_imagen_firma_default()
    
    def crear_imagen_firma_default(self):
        """Crea una imagen de firma por defecto con todos los datos"""
        img = Image.new('RGBA', (350, 180), (255, 255, 255, 240))
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 11)
            font_bold = ImageFont.truetype("arial.ttf", 13)
            font_small = ImageFont.truetype("arial.ttf", 9)
        except:
            font = ImageFont.load_default()
            font_bold = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Marco
        draw.rectangle([5, 5, 345, 175], outline=(0, 0, 139), width=2)
        draw.rectangle([10, 10, 340, 170], outline=(0, 0, 139), width=1)
        
        # Círculo del sello (lado izquierdo)
        draw.ellipse([20, 25, 115, 120], outline=(0, 0, 139), width=2)
        draw.text((43, 60), "SELLO", fill=(0, 0, 139), font=font_bold)
        draw.text((46, 78), "DIGITAL", fill=(0, 0, 139), font=font_bold)
        
        # Texto de la firma (lado derecho)
        draw.text((140, 30), "Firmado digitalmente por", fill=(80, 80, 80), font=font)
        draw.text((140, 48), "VILLEGAS AGUIRRE Delmi Oscar", fill=(0, 0, 0), font=font_bold)
        draw.text((140, 66), "FAU 20568198272 soft", fill=(80, 80, 80), font=font)
        draw.text((140, 84), "Motivo: Soy el autor del documento", fill=(80, 80, 80), font=font)
        draw.text((140, 102), "Fecha: 16.06.2026 13:03:21 -05:00", fill=(80, 80, 80), font=font)
        
        # "Firma Digital" en la parte inferior
        draw.text((250, 145), "Firma Digital", fill=(0, 0, 139), font=font_bold)
        
        self.firma_imagen = img.resize((280, 145), Image.Resampling.LANCZOS)
    
    def crear_sombra_firma(self, x, y):
        """Crea una sombra/placeholder de la firma en la posición del mouse"""
        if not self.firma_imagen:
            return
        
        # Eliminar sombra anterior
        if self.shadow_item:
            self.canvas.delete(self.shadow_item)
            self.shadow_item = None
        
        # Escalar imagen para la sombra
        scale = self.zoom
        width = int(280 * scale)
        height = int(145 * scale)
        
        # Crear versión semi-transparente para la sombra
        img_copy = self.firma_imagen.copy()
        # Hacerla semi-transparente
        alpha = img_copy.split()[3] if img_copy.mode == 'RGBA' else None
        if alpha:
            # Reducir opacidad
            alpha = alpha.point(lambda p: p * 0.5)
            img_copy.putalpha(alpha)
        
        img_resized = img_copy.resize((width, height), Image.Resampling.LANCZOS)
        self.shadow_photo = ImageTk.PhotoImage(img_resized)
        
        # Colocar sombra en la posición del mouse
        # Ajustar para centrar la imagen en el cursor
        x_offset = x - width // 2
        y_offset = y - height // 2
        
        self.shadow_item = self.canvas.create_image(x_offset, y_offset, 
                                                     anchor=tk.NW, 
                                                     image=self.shadow_photo,
                                                     tags=("shadow",))
        
        # Actualizar la posición de la sombra
        self.current_shadow_pos = (x_offset, y_offset)
    
    def actualizar_sombra(self, x, y):
        """Actualiza la posición de la sombra"""
        if self.shadow_item and self.firma_imagen:
            scale = self.zoom
            width = int(280 * scale)
            height = int(145 * scale)
            
            x_offset = x - width // 2
            y_offset = y - height // 2
            
            self.canvas.coords(self.shadow_item, x_offset, y_offset)
            self.current_shadow_pos = (x_offset, y_offset)
    
    def ocultar_sombra(self):
        """Oculta la sombra de la firma"""
        if self.shadow_item:
            self.canvas.delete(self.shadow_item)
            self.shadow_item = None
            self.shadow_photo = None
    
    def on_mouse_move(self, event):
        """Maneja el movimiento del mouse"""
        if self.firma_item and not self.dragging:
            # Si hay una firma colocada y no estamos arrastrando, mostrar sombra
            self.crear_sombra_firma(event.x, event.y)
        elif self.dragging:
            # Si estamos arrastrando, actualizar sombra
            self.actualizar_sombra(event.x, event.y)
        elif not self.firma_item:
            # Si no hay firma, ocultar sombra
            self.ocultar_sombra()
    
    def on_mouse_leave(self, event):
        """Cuando el mouse sale del canvas"""
        self.ocultar_sombra()
    
    def colocar_firma_con_preview(self, x=None, y=None):
        """Coloca la firma con preview en tiempo real"""
        if not self.doc:
            return False
        
        if x is None or y is None:
            # Centrar si no se especifica posición
            x = self.width // 2
            y = self.height // 2
        
        # Crear la firma en la posición especificada
        self.firma_position = (x, y)
        self.crear_firma_en_posicion(x, y)
        self.firma_original_pos = (x, y)
        
        # Ocultar sombra
        self.ocultar_sombra()
        
        self.event_generate("<<FirmaAdded>>")
        return True
    
    def crear_firma_en_posicion(self, x, y):
        """Crea la firma en una posición específica"""
        if not self.firma_imagen:
            self.cargar_imagen_firma()
        
        # Escalar según zoom
        scale = self.zoom
        width = int(280 * scale)
        height = int(145 * scale)
        
        img_resized = self.firma_imagen.resize((width, height), Image.Resampling.LANCZOS)
        self.firma_photo = ImageTk.PhotoImage(img_resized)
        
        # Eliminar firma anterior si existe
        if self.firma_item:
            self.canvas.delete(self.firma_item)
        
        # Ajustar posición para centrar
        x_offset = x - width // 2
        y_offset = y - height // 2
        
        # Crear la firma
        self.firma_item = self.canvas.create_image(x_offset, y_offset, 
                                                    anchor=tk.NW, 
                                                    image=self.firma_photo,
                                                    tags=("firma",))
        
        # Hacer que la firma sea arrastrable
        self.canvas.tag_bind("firma", "<Button-1>", self.start_drag)
        self.canvas.tag_bind("firma", "<B1-Motion>", self.on_drag)
        self.canvas.tag_bind("firma", "<ButtonRelease-1>", self.end_drag)
        
        # Guardar posición
        self.firma_position = (x_offset, y_offset)
    
    def start_drag(self, event):
        """Inicia el arrastre de la firma"""
        self.dragging = True
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        
        # Obtener posición actual de la firma
        if self.firma_item:
            coords = self.canvas.coords(self.firma_item)
            if coords:
                self.firma_original_pos = (coords[0], coords[1])
    
    def on_drag(self, event):
        """Mueve la firma durante el arrastre con sombra"""
        if self.dragging and self.firma_item:
            # Mover la firma
            dx = event.x - self.drag_start_x
            dy = event.y - self.drag_start_y
            self.canvas.move(self.firma_item, dx, dy)
            self.drag_start_x = event.x
            self.drag_start_y = event.y
            
            # Mostrar sombra en la posición actual (como guía)
            self.crear_sombra_firma(event.x, event.y)
            
            # Actualizar posición guardada
            coords = self.canvas.coords(self.firma_item)
            if coords:
                self.firma_position = (coords[0], coords[1])
    
    def end_drag(self, event):
        """Finaliza el arrastre de la firma"""
        self.dragging = False
        
        # Ocultar sombra
        self.ocultar_sombra()
        
        if self.firma_item:
            # Guardar nueva posición
            coords = self.canvas.coords(self.firma_item)
            if coords:
                self.firma_position = (coords[0], coords[1])
                self.firma_original_pos = (coords[0], coords[1])
                self.event_generate("<<FirmaMoved>>")
    
    def add_firma(self, x=None, y=None):
        """Añade una firma en la posición especificada"""
        if x is None or y is None:
            # Obtener centro del canvas visible
            bbox = self.canvas.bbox("all")
            if bbox:
                x = (bbox[0] + bbox[2]) // 2
                y = (bbox[1] + bbox[3]) // 2
            else:
                x = self.width // 2
                y = self.height // 2
        
        return self.colocar_firma_con_preview(x, y)
    
    def remove_firma(self):
        """Elimina la firma actual"""
        if self.firma_item:
            self.canvas.delete(self.firma_item)
            self.firma_item = None
            self.firma_position = None
            self.firma_original_pos = None
            self.ocultar_sombra()
            self.event_generate("<<FirmaRemoved>>")
    
    def load_pdf(self, pdf_path):
        """Carga un archivo PDF para visualización"""
        try:
            self.doc = fitz.open(pdf_path)
            self.total_pages = len(self.doc)
            self.current_page = 0
            self.render_page()
            return True, f"PDF cargado: {self.total_pages} páginas"
        except Exception as e:
            return False, f"Error al cargar PDF: {str(e)}"
    
    def render_page(self):
        """Renderiza la página actual"""
        if not self.doc:
            return
        
        # Obtener página
        page = self.doc[self.current_page]
        
        # Crear imagen en tamaño adecuado
        mat = fitz.Matrix(self.zoom, self.zoom)
        pix = page.get_pixmap(matrix=mat)
        
        # Convertir a formato PIL
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        self.photo = ImageTk.PhotoImage(img)
        
        # Limpiar canvas (pero mantener la firma)
        self.canvas.delete("all")
        
        # Mostrar imagen
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        self.canvas.config(scrollregion=(0, 0, pix.width, pix.height))
        
        # Ajustar tamaño del canvas
        canvas_width = min(pix.width, self.width)
        canvas_height = min(pix.height, self.height)
        self.canvas.config(width=canvas_width, height=canvas_height)
        
        # Actualizar información de página
        self.event_generate("<<PageChanged>>")
        
        # Restaurar firma si existe
        if self.firma_position:
            # Recalcular posición con el nuevo zoom
            x, y = self.firma_position
            self.crear_firma_en_posicion(x + 140, y + 72)  # Centrar en la posición guardada
    
    def next_page(self):
        """Avanzar página"""
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.render_page()
    
    def prev_page(self):
        """Retroceder página"""
        if self.current_page > 0:
            self.current_page -= 1
            self.render_page()
    
    def on_resize(self, event):
        """Manejar redimensionamiento"""
        self.width = event.width
        self.height = event.height
        self.render_page()
    
    def get_firma_position_for_pdf(self):
        """Obtiene la posición de la firma para aplicar al PDF"""
        if not self.firma_position or not self.doc:
            return None
        
        # Obtener posición del canvas
        x, y = self.firma_position
        
        # Ajustar para obtener el centro de la firma
        scale = self.zoom
        width = int(280 * scale)
        height = int(145 * scale)
        
        center_x = x + width // 2
        center_y = y + height // 2
        
        # Obtener dimensiones de la página
        page = self.doc[self.current_page]
        rect = page.rect
        page_width = rect.width
        page_height = rect.height
        
        # Obtener dimensiones del canvas visible
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 0:
            canvas_width = self.width
        if canvas_height <= 0:
            canvas_height = self.height
        
        # Calcular escalado
        scale_x = page_width / (canvas_width / self.zoom)
        scale_y = page_height / (canvas_height / self.zoom)
        
        # Convertir a coordenadas PDF
        pdf_x = center_x * scale_x
        pdf_y = center_y * scale_y
        
        # Tamaño de la imagen de firma en PDF
        width_scale = 280 * scale_x / self.zoom
        height_scale = 145 * scale_y / self.zoom
        
        return (pdf_x - width_scale/2, pdf_y - height_scale/2, width_scale, height_scale)