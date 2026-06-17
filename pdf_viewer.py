import tkinter as tk
from tkinter import ttk
import fitz
from PIL import Image, ImageTk, ImageDraw, ImageFont
import os


class PDFViewer(ttk.Frame):
    """Visor PDF con scroll continuo (todas las páginas apiladas verticalmente)"""

    def __init__(self, parent, width=700, height=550):
        super().__init__(parent)
        self.width = width
        self.height = height
        self.doc = None
        self.total_pages = 0
        self.zoom = 1.0
        
        # ── Firma ──
        self.firma_imagen = None
        self.firma_photo = None
        self.firma_item = None
        self.firma_page_position = None
        self.firma_canvas_page = None  # Página donde está la firma (canvas item)
        
        # ── Shadow ──
        self.shadow_photo = None
        self.shadow_item = None
        
        # ── Modo placement ──
        self.placement_mode = False
        
        # ── Drag ──
        self.dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        # ── Mapa de páginas en canvas ──
        # {page_index: {"y_start": int, "y_end": int, "photo": PhotoImage}}
        self._pages_map = {}
        
        # ── Canvas ──
        self.canvas = tk.Canvas(self, width=width, height=height, bg='#585858',
                                cursor='arrow', highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbars
        self.v_scroll = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        self.h_scroll = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self._on_scroll, xscrollcommand=self._on_scroll_h)
        
        self._v_scroll_visible = False
        self._h_scroll_visible = False
        
        # Eventos
        self.canvas.bind("<Configure>", self.on_resize)
        self.canvas.bind("<Motion>", self._on_canvas_motion)
        self.canvas.bind("<ButtonPress-1>", self._on_canvas_click)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Button-4>", self._on_mousewheel)
        self.canvas.bind("<Button-5>", self._on_mousewheel)
        
        # Cargar imagen de firma
        self.cargar_imagen_firma()
    
    # ══════════════════════════════════════════════════════════════════
    #  SCROLLBAR CALLBACKS
    # ══════════════════════════════════════════════════════════════════
    
    def _on_scroll(self, *args):
        self.v_scroll.set(*args)
    
    def _on_scroll_h(self, *args):
        self.h_scroll.set(*args)
    
    def _on_mousewheel(self, event):
        if not self.doc:
            return
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-3, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(3, "units")
    
    def _update_scrollbars(self):
        if not self.doc:
            return
        sr = self.canvas.cget("scrollregion")
        if not sr:
            return
        parts = sr.split()
        content_w = float(parts[2])
        content_h = float(parts[3])
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        
        if content_h > canvas_h and not self._v_scroll_visible:
            self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
            self._v_scroll_visible = True
        elif content_h <= canvas_h and self._v_scroll_visible:
            self.v_scroll.pack_forget()
            self._v_scroll_visible = False
        
        if content_w > canvas_w and not self._h_scroll_visible:
            self.h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
            self._h_scroll_visible = True
        elif content_w <= canvas_w and self._h_scroll_visible:
            self.h_scroll.pack_forget()
            self._h_scroll_visible = False
    
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
        w = int(self.firma_imagen.width * self.zoom)
        h = int(self.firma_imagen.height * self.zoom)
        return w, h
    
    # ══════════════════════════════════════════════════════════════════
    #  RENDERIZADO (scroll continuo - todas las páginas)
    # ══════════════════════════════════════════════════════════════════
    
    def render_page(self):
        """Renderiza TODAS las páginas apiladas verticalmente"""
        if not self.doc:
            return
        
        self.canvas.delete("all")
        self.canvas.config(bg='#585858')
        self._pages_map.clear()
        
        cw = max(self.canvas.winfo_width(), self.width)
        
        gap = 15  # Espacio entre páginas
        y_cursor = 20  # Margen superior
        x_center = cw // 2
        
        for i in range(self.total_pages):
            page = self.doc[i]
            mat = fitz.Matrix(self.zoom, self.zoom)
            pix = page.get_pixmap(matrix=mat)
            
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            photo = ImageTk.PhotoImage(img)
            
            # Centrar horizontalmente
            x_pos = max(0, (cw - pix.width) // 2)
            
            # Sombra de página
            self.canvas.create_rectangle(
                x_pos + 4, y_cursor + 4,
                x_pos + pix.width + 4, y_cursor + pix.height + 4,
                fill='#3a3a3a', outline='', tags=f"shadow_{i}")
            
            # Página
            self.canvas.create_image(
                x_pos, y_cursor, anchor=tk.NW, image=photo, tags=f"page_{i}")
            
            # Guardar referencia para evitar garbage collection
            self._pages_map[i] = {
                "y_start": y_cursor,
                "y_end": y_cursor + pix.height,
                "x_start": x_pos,
                "x_end": x_pos + pix.width,
                "photo": photo,
                "width": pix.width,
                "height": pix.height
            }
            
            # Etiqueta de página
            label_y = y_cursor + pix.height + 3
            self.canvas.create_text(
                x_center, label_y,
                text=f"Página {i + 1} / {self.total_pages}",
                fill='#aaaaaa', font=('Segoe UI', 9), tags=f"label_{i}")
            
            y_cursor += pix.height + gap + 20
        
        # Scrollregion total
        total_h = y_cursor + 20
        self.canvas.config(scrollregion=(0, 0, cw, total_h))
        
        self._update_scrollbars()
        
        # Restaurar firma si existe
        if self.firma_page_position and self.firma_imagen:
            self._stamps_firma(self.firma_page_position[0], self.firma_page_position[1])
        
        self.event_generate("<<PageChanged>>")
    
    # ══════════════════════════════════════════════════════════════════
    #  COORDENADAS: Canvas <-> PDF (por página)
    # ══════════════════════════════════════════════════════════════════
    
    def _canvas_to_pdf(self, cx, cy):
        """Convierte coordenadas del canvas a (page_index, pdf_x, pdf_y)"""
        for page_idx, info in self._pages_map.items():
            if (info["y_start"] <= cy <= info["y_end"] and
                    info["x_start"] <= cx <= info["x_end"]):
                pdf_x = (cx - info["x_start"]) / self.zoom
                pdf_y = (cy - info["y_start"]) / self.zoom
                return page_idx, pdf_x, pdf_y
        return None, None, None
    
    def _pdf_to_canvas(self, page_idx, pdf_x, pdf_y):
        """Convierte coordenadas PDF a coordenadas del canvas"""
        if page_idx not in self._pages_map:
            return None, None
        info = self._pages_map[page_idx]
        cx = info["x_start"] + pdf_x * self.zoom
        cy = info["y_start"] + pdf_y * self.zoom
        return cx, cy
    
    def _mouse_to_page(self, event):
        """Determina en qué página está el mouse y sus coordenadas PDF"""
        # Convertir coordenadas del evento a coordenadas del canvas
        cx = self.canvas.canvasx(event.x)
        cy = self.canvas.canvasy(event.y)
        return self._canvas_to_pdf(cx, cy)
    
    # ══════════════════════════════════════════════════════════════════
    #  MODO PLACEMENT
    # ══════════════════════════════════════════════════════════════════
    
    def add_firma(self):
        if not self.doc:
            return False
        if self.firma_item:
            self.remove_firma()
        self.placement_mode = True
        self.canvas.config(cursor='crosshair')
        return True
    
    def _show_shadow(self, canvas_x, canvas_y):
        if not self.firma_imagen:
            return
        w, h = self._firma_scaled_size()
        img_copy = self.firma_imagen.copy()
        if img_copy.mode == 'RGBA':
            alpha = img_copy.split()[3]
            alpha = alpha.point(lambda p: int(p * 0.45))
            img_copy.putalpha(alpha)
        img_resized = img_copy.resize((w, h), Image.Resampling.LANCZOS)
        self.shadow_photo = ImageTk.PhotoImage(img_resized)
        if self.shadow_item:
            self.canvas.delete(self.shadow_item)
        nw_x = canvas_x - w / 2
        nw_y = canvas_y - h / 2
        self.shadow_item = self.canvas.create_image(
            nw_x, nw_y, anchor=tk.NW, image=self.shadow_photo, tags="shadow")
    
    def _hide_shadow(self):
        if self.shadow_item:
            self.canvas.delete(self.shadow_item)
            self.shadow_item = None
            self.shadow_photo = None
    
    # ══════════════════════════════════════════════════════════════════
    #  COLOCAR FIRMA
    # ══════════════════════════════════════════════════════════════════
    
    def _stamps_firma(self, pdf_x, pdf_y, page_idx=None):
        """Coloca la firma en la página especificada (o la detectada)"""
        if not self.firma_imagen:
            return
        
        # Si no se especifica página, buscar dónde está la posición
        if page_idx is None:
            # Buscar en todas las páginas
            for idx, info in self._pages_map.items():
                page = self.doc[idx]
                if pdf_x <= page.rect.width and pdf_y <= page.rect.height:
                    page_idx = idx
                    break
            if page_idx is None:
                page_idx = 0
        
        w, h = self._firma_scaled_size()
        img_resized = self.firma_imagen.resize((w, h), Image.Resampling.LANCZOS)
        self.firma_photo = ImageTk.PhotoImage(img_resized)
        
        if self.firma_item:
            self.canvas.delete(self.firma_item)
        
        # Coordenadas en canvas
        cx, cy = self._pdf_to_canvas(page_idx, pdf_x, pdf_y)
        if cx is None:
            return
        
        nw_x = cx - w / 2
        nw_y = cy - h / 2
        
        self.firma_item = self.canvas.create_image(
            nw_x, nw_y, anchor=tk.NW, image=self.firma_photo, tags="firma")
        
        # Guardar estado
        self.firma_page_position = (pdf_x, pdf_y)
        self.firma_canvas_page = page_idx
        
        # Eventos de arrastre
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
        if self.placement_mode:
            page_idx, pdf_x, pdf_y = self._mouse_to_page(event)
            if page_idx is not None:
                # Mostrar sombra en la posición del mouse
                cx = self.canvas.canvasx(event.x)
                cy = self.canvas.canvasy(event.y)
                self._show_shadow(cx, cy)
                self.event_generate("<<FirmaPlacementStarted>>")
            else:
                self._hide_shadow()
    
    def _on_canvas_click(self, event):
        if self.placement_mode:
            page_idx, pdf_x, pdf_y = self._mouse_to_page(event)
            if page_idx is not None:
                self._hide_shadow()
                self.placement_mode = False
                self.canvas.config(cursor='arrow')
                
                # Colocar firma en la página detectada
                self._stamps_firma(pdf_x, pdf_y, page_idx)
                
                self.event_generate("<<FirmaAdded>>")
    
    # ══════════════════════════════════════════════════════════════════
    #  ARRASTRE
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
        w, h = self._firma_scaled_size()
        center_cx = nw_x + w / 2
        center_cy = nw_y + h / 2
        
        page_idx, pdf_x, pdf_y = self._canvas_to_pdf(center_cx, center_cy)
        if page_idx is not None:
            self.firma_page_position = (pdf_x, pdf_y)
            self.firma_canvas_page = page_idx
        
        self.event_generate("<<FirmaMoved>>")
    
    # ══════════════════════════════════════════════════════════════════
    #  ACCIONES PUBLICAS
    # ══════════════════════════════════════════════════════════════════
    
    def remove_firma(self):
        self.placement_mode = False
        self._hide_shadow()
        self.canvas.config(cursor='arrow')
        if self.firma_item:
            self.canvas.delete(self.firma_item)
            self.firma_item = None
            self.firma_page_position = None
            self.firma_canvas_page = None
            self.event_generate("<<FirmaRemoved>>")
    
    def get_firma_position_for_pdf(self):
        """Retorna (x, y, w, h, page_idx) para insertar en el PDF final"""
        if not self.doc or not self.firma_page_position or not self.firma_imagen:
            return None
        
        page_idx = self.firma_canvas_page if self.firma_canvas_page is not None else 0
        page = self.doc[page_idx]
        rect = page.rect
        
        sig_w = rect.width * 0.45
        sig_h = sig_w * (self.firma_imagen.height / self.firma_imagen.width)
        
        pdf_x, pdf_y = self.firma_page_position
        x = pdf_x - sig_w / 2
        y = pdf_y - sig_h / 2
        
        x = max(0, min(x, rect.width - sig_w))
        y = max(0, min(y, rect.height - sig_h))
        
        return (x, y, sig_w, sig_h, page_idx)
    
    # ══════════════════════════════════════════════════════════════════
    #  NAVEGACION
    # ══════════════════════════════════════════════════════════════════
    
    def load_pdf(self, pdf_path):
        try:
            self.doc = fitz.open(pdf_path)
            self.total_pages = len(self.doc)
            self.firma_item = None
            self.firma_page_position = None
            self.firma_canvas_page = None
            self.placement_mode = False
            self._hide_shadow()
            self.render_page()
            return True, f"PDF cargado: {self.total_pages} paginas"
        except Exception as e:
            return False, f"Error al cargar PDF: {str(e)}"
    
    def next_page(self):
        """Scroll a la siguiente página"""
        if not self.doc or self.total_pages == 0:
            return
        # En scroll continuo, hacer scroll hacia abajo
        self.canvas.yview_scroll(1, "pages")
    
    def prev_page(self):
        """Scroll a la página anterior"""
        if not self.doc or self.total_pages == 0:
            return
        self.canvas.yview_scroll(-1, "pages")
    
    def on_resize(self, event):
        self.width = event.width
        self.height = event.height
        if self.doc:
            self.render_page()
