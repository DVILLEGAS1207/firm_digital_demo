import tkinter as tk
from tkinter import ttk
import fitz
from PIL import Image, ImageTk, ImageDraw, ImageFont
import os

class PDFViewer(ttk.Frame):
    def __init__(self, parent, width=700, height=550):
        super().__init__(parent)
        self.width = width
        self.height = height
        self.doc = None
        self.current_page = 0
        self.total_pages = 0
        self.zoom = 1.0
        
        # ── Firma ──
        self.firma_imagen = None      # PIL image de la firma
        self.firma_photo = None       # PhotoImage para canvas
        self.firma_item = None        # id del item en canvas (None = no colocada)
        self.firma_position = None    # NW corner en canvas coords
        self.firma_page_position = None  # centro en coords de pagina PDF
        
        # ── Shadow (seguimiento del cursor) ──
        self.shadow_photo = None      # PhotoImage de la sombra
        self.shadow_item = None       # id del item sombra en canvas
        
        # ── Modo placement ──
        self.placement_mode = False   # True = esperando click para colocar
        
        # ── Drag ──
        self.dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        # ── Offset de centrado de pagina ──
        self._page_offset_x = 0
        self._page_offset_y = 0
        
        # ── Canvas ──
        self.canvas = tk.Canvas(self, width=width, height=height, bg='#808080', cursor='arrow')
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        v_scroll = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.canvas.xview)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        # Eventos del canvas (no de la firma)
        self.canvas.bind("<Configure>", self.on_resize)
        self.canvas.bind("<Motion>", self._on_canvas_motion)
        self.canvas.bind("<ButtonPress-1>", self._on_canvas_click)
        
        # Cargar imagen de firma
        self.cargar_imagen_firma()
        
    # ══════════════════════════════════════════════════════════════════
    #  IMAGEN DE FIRMA
    # ══════════════════════════════════════════════════════════════════
    
    def cargar_imagen_firma(self):
        try:
            sello_path = os.path.join(os.path.dirname(__file__), "assets", "images", "sello_small.png")
            if os.path.exists(sello_path):
                self.firma_imagen = Image.open(sello_path)
                ratio = self.firma_imagen.width / self.firma_imagen.height
                new_h = int(400 / ratio)
                self.firma_imagen = self.firma_imagen.resize((400, new_h), Image.Resampling.LANCZOS)
            else:
                self._crear_firma_default()
        except Exception as e:
            print(f"Error cargando imagen: {e}")
            self._crear_firma_default()
    
    def _crear_firma_default(self):
        w, h = 720, 140
        img = Image.new('RGBA', (w, h), (255, 255, 255, 255))
        logo_path = os.path.join(os.path.dirname(__file__), "assets", "images", "1.png")
        try:
            logo = Image.open(logo_path)
            lh = 110
            lw = int(lh * logo.width / logo.height)
            logo = logo.resize((lw, lh), Image.Resampling.LANCZOS)
            img.paste(logo, (10, (h - lh) // 2), logo if logo.mode == 'RGBA' else None)
        except:
            pass
        draw = ImageDraw.Draw(img)
        try:
            fn = ImageFont.truetype("arial.ttf", 11)
            fb = ImageFont.truetype("arial.ttf", 13)
        except:
            fn = fb = ImageFont.load_default()
        tx = 280
        draw.line([tx - 15, 15, tx - 15, 125], fill=(180, 180, 180), width=1)
        draw.text((tx, 20), "Firmado digitalmente por", fill=(100, 100, 100), font=fn)
        draw.text((tx, 38), "VILLEGAS AGUIRRE Delmi Oscar", fill=(50, 50, 50), font=fb)
        draw.text((tx, 58), "FAU 20568198272 soft", fill=(100, 100, 100), font=fn)
        draw.text((tx, 76), "Motivo: Soy el autor del documento", fill=(100, 100, 100), font=fn)
        draw.text((tx, 94), "Fecha: 16.06.2026 13:03:21 -05:00", fill=(100, 100, 100), font=fn)
        self.firma_imagen = img.resize((400, int(h * 400 / w)), Image.Resampling.LANCZOS)
    
    def _firma_scaled_size(self):
        """Retorna (width, height) de la firma escalada con el zoom actual"""
        w = int(self.firma_imagen.width * self.zoom)
        h = int(self.firma_imagen.height * self.zoom)
        return w, h
    
    # ══════════════════════════════════════════════════════════════════
    #  COORDENADAS
    # ══════════════════════════════════════════════════════════════════
    
    def _recalc_page_offset(self):
        if not self.doc:
            return
        page = self.doc[self.current_page]
        rw = page.rect.width * self.zoom
        rh = page.rect.height * self.zoom
        cw = max(self.canvas.winfo_width(), self.width)
        ch = max(self.canvas.winfo_height(), self.height)
        self._page_offset_x = max(0, (cw - rw) / 2)
        self._page_offset_y = max(0, (ch - rh) / 2)
    
    def _pdf_to_canvas(self, pdf_x, pdf_y):
        self._recalc_page_offset()
        return self._page_offset_x + pdf_x * self.zoom, self._page_offset_y + pdf_y * self.zoom
    
    def _canvas_to_pdf(self, cx, cy):
        self._recalc_page_offset()
        return (cx - self._page_offset_x) / self.zoom, (cy - self._page_offset_y) / self.zoom
    
    def _mouse_in_page(self, event):
        """True si el mouse esta dentro del area de la pagina renderizada"""
        if not self.doc:
            return False
        page = self.doc[self.current_page]
        rw = page.rect.width * self.zoom
        rh = page.rect.height * self.zoom
        return (self._page_offset_x <= event.x <= self._page_offset_x + rw and
                self._page_offset_y <= event.y <= self._page_offset_y + rh)
    
    # ══════════════════════════════════════════════════════════════════
    #  RENDERIZADO
    # ══════════════════════════════════════════════════════════════════
    
    def render_page(self):
        if not self.doc:
            return
        
        page = self.doc[self.current_page]
        mat = fitz.Matrix(self.zoom, self.zoom)
        pix = page.get_pixmap(matrix=mat)
        
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        self.photo = ImageTk.PhotoImage(img)
        
        self.canvas.delete("all")
        self.canvas.config(bg='#808080')
        
        cw = max(self.canvas.winfo_width(), self.width)
        ch = max(self.canvas.winfo_height(), self.height)
        xo = max(0, (cw - pix.width) // 2)
        yo = max(0, (ch - pix.height) // 2)
        self._page_offset_x = xo
        self._page_offset_y = yo
        
        # Sombra de pagina
        self.canvas.create_rectangle(xo + 4, yo + 4, xo + pix.width + 4, yo + pix.height + 4,
                                     fill='#404040', outline='')
        # Pagina
        self.canvas.create_image(xo, yo, anchor=tk.NW, image=self.photo)
        
        self.canvas.config(scrollregion=(0, 0, pix.width, pix.height))
        self.event_generate("<<PageChanged>>")
        
        # Restaurar firma si existia
        if self.firma_page_position and self.firma_imagen:
            self._stamps_firma(self.firma_page_position[0], self.firma_page_position[1])
    
    # ══════════════════════════════════════════════════════════════════
    #  MODO PLACEMENT: sombra sigue al cursor
    # ══════════════════════════════════════════════════════════════════
    
    def add_firma(self):
        """Entra en modo placement: sombra sigue al cursor, click para colocar"""
        if not self.doc:
            return False
        
        # Si ya hay firma colocada, quitarla primero
        if self.firma_item:
            self.remove_firma()
        
        self.placement_mode = True
        self.canvas.config(cursor='crosshair')
        self.event_generate("<<FirmaPlacementStarted>>")
        return True
    
    def _show_shadow(self, canvas_x, canvas_y):
        """Muestra la sombra semi-transparente centrada en (canvas_x, canvas_y)"""
        if not self.firma_imagen:
            return
        
        w, h = self._firma_scaled_size()
        
        # Crear version semi-transparente
        img_copy = self.firma_imagen.copy()
        if img_copy.mode == 'RGBA':
            alpha = img_copy.split()[3]
            alpha = alpha.point(lambda p: int(p * 0.45))
            img_copy.putalpha(alpha)
        
        img_resized = img_copy.resize((w, h), Image.Resampling.LANCZOS)
        self.shadow_photo = ImageTk.PhotoImage(img_resized)
        
        # Eliminar sombra anterior
        if self.shadow_item:
            self.canvas.delete(self.shadow_item)
        
        nw_x = canvas_x - w / 2
        nw_y = canvas_y - h / 2
        
        self.shadow_item = self.canvas.create_image(
            nw_x, nw_y, anchor=tk.NW, image=self.shadow_photo, tags=("shadow",))
    
    def _hide_shadow(self):
        if self.shadow_item:
            self.canvas.delete(self.shadow_item)
            self.shadow_item = None
            self.shadow_photo = None
    
    # ══════════════════════════════════════════════════════════════════
    #  COLOCAR FIRMA (stamps definitivo)
    # ══════════════════════════════════════════════════════════════════
    
    def _stamps_firma(self, pdf_x, pdf_y):
        """Coloca la firma definitivamente en coordenadas de pagina PDF"""
        if not self.firma_imagen:
            return
        
        w, h = self._firma_scaled_size()
        img_resized = self.firma_imagen.resize((w, h), Image.Resampling.LANCZOS)
        self.firma_photo = ImageTk.PhotoImage(img_resized)
        
        # Eliminar firma anterior si existe
        if self.firma_item:
            self.canvas.delete(self.firma_item)
        
        # Centro en canvas
        cx, cy = self._pdf_to_canvas(pdf_x, pdf_y)
        nw_x = cx - w / 2
        nw_y = cy - h / 2
        
        # Crear item definitivo
        self.firma_item = self.canvas.create_image(
            nw_x, nw_y, anchor=tk.NW, image=self.firma_photo, tags=("firma",))
        
        # Guardar posiciones
        self.firma_position = (nw_x, nw_y)
        self.firma_page_position = (pdf_x, pdf_y)
        
        # Eventos de arrastre solo en la firma colocada
        self.canvas.tag_bind("firma", "<ButtonPress-1>", self._drag_start)
        self.canvas.tag_bind("firma", "<B1-Motion>", self._drag_move)
        self.canvas.tag_bind("firma", "<ButtonRelease-1>", self._drag_end)
        self.canvas.tag_bind("firma", "<Enter>", lambda e: self.canvas.config(cursor='hand2'))
        self.canvas.tag_bind("firma", "<Leave>",
                             lambda e: self.canvas.config(cursor='arrow' if not self.placement_mode else 'crosshair'))
    
    # ══════════════════════════════════════════════════════════════════
    #  EVENTOS DEL CANVAS
    # ══════════════════════════════════════════════════════════════════
    
    def _on_canvas_motion(self, event):
        """Movimiento del mouse en el canvas"""
        if self.placement_mode:
            # En modo placement: sombra sigue al cursor
            if self._mouse_in_page(event):
                self._show_shadow(event.x, event.y)
            else:
                self._hide_shadow()
    
    def _on_canvas_click(self, event):
        """Click en el canvas"""
        if self.placement_mode:
            # Solo colocar si el click es dentro de la pagina
            if self._mouse_in_page(event):
                # Convertir coordenadas del mouse a PDF
                pdf_x, pdf_y = self._canvas_to_pdf(event.x, event.y)
                
                # Quitar sombra y salir del modo placement
                self._hide_shadow()
                self.placement_mode = False
                self.canvas.config(cursor='arrow')
                
                # Colocar firma definitivamente
                self._stamps_firma(pdf_x, pdf_y)
                
                self.event_generate("<<FirmaAdded>>")
    
    # ══════════════════════════════════════════════════════════════════
    #  ARRASTRE de firma ya colocada
    # ══════════════════════════════════════════════════════════════════
    
    def _drag_start(self, event):
        self.dragging = True
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        self.canvas.config(cursor='fleur')
    
    def _drag_move(self, event):
        if not self.dragging or not self.firma_item:
            return
        dx = event.x - self.drag_start_x
        dy = event.y - self.drag_start_y
        self.canvas.move(self.firma_item, dx, dy)
        self.drag_start_x = event.x
        self.drag_start_y = event.y
    
    def _drag_end(self, event):
        self.dragging = False
        self.canvas.config(cursor='arrow')
        
        if not self.firma_item:
            return
        
        coords = self.canvas.coords(self.firma_item)
        if not coords:
            return
        
        nw_x, nw_y = coords[0], coords[1]
        self.firma_position = (nw_x, nw_y)
        
        # Convertir NW canvas -> centro canvas -> PDF
        w, h = self._firma_scaled_size()
        center_cx = nw_x + w / 2
        center_cy = nw_y + h / 2
        pdf_x, pdf_y = self._canvas_to_pdf(center_cx, center_cy)
        self.firma_page_position = (pdf_x, pdf_y)
        
        self.event_generate("<<FirmaMoved>>")
    
    # ══════════════════════════════════════════════════════════════════
    #  ACCIONES PUBLICAS
    # ══════════════════════════════════════════════════════════════════
    
    def remove_firma(self):
        """Elimina la firma y cancela placement mode"""
        self.placement_mode = False
        self._hide_shadow()
        self.canvas.config(cursor='arrow')
        if self.firma_item:
            self.canvas.delete(self.firma_item)
            self.firma_item = None
            self.firma_position = None
            self.firma_page_position = None
            self.event_generate("<<FirmaRemoved>>")
    
    def get_firma_position_for_pdf(self):
        """Retorna (x, y, w, h) en coordenadas de pagina PDF para insertar en el PDF final"""
        if not self.doc or not self.firma_page_position or not self.firma_imagen:
            return None
        
        page = self.doc[self.current_page]
        rect = page.rect
        
        sig_w = rect.width * 0.45
        sig_h = sig_w * (self.firma_imagen.height / self.firma_imagen.width)
        
        pdf_x, pdf_y = self.firma_page_position
        x = pdf_x - sig_w / 2
        y = pdf_y - sig_h / 2
        
        x = max(0, min(x, rect.width - sig_w))
        y = max(0, min(y, rect.height - sig_h))
        
        return (x, y, sig_w, sig_h)
    
    # ══════════════════════════════════════════════════════════════════
    #  NAVEGACION
    # ══════════════════════════════════════════════════════════════════
    
    def load_pdf(self, pdf_path):
        try:
            self.doc = fitz.open(pdf_path)
            self.total_pages = len(self.doc)
            self.current_page = 0
            self.firma_item = None
            self.firma_position = None
            self.firma_page_position = None
            self.placement_mode = False
            self._hide_shadow()
            self.render_page()
            return True, f"PDF cargado: {self.total_pages} paginas"
        except Exception as e:
            return False, f"Error al cargar PDF: {str(e)}"
    
    def next_page(self):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.render_page()
    
    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.render_page()
    
    def on_resize(self, event):
        self.width = event.width
        self.height = event.height
        self.render_page()
