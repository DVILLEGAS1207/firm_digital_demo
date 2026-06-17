import tkinter as tk
from tkinter import ttk, messagebox
import fitz
from PIL import Image, ImageTk, ImageDraw, ImageFont
import os
from datetime import datetime
from modal_certificado import CertificadoModal


class ModalFirmaAvanzada:
    """Modal para firma avanzada con navegación multipágina y múltiples firmas"""

    def __init__(self, parent, ruta_pdf, firmador):
        self.parent = parent
        self.ruta_pdf = ruta_pdf
        self.firmador = firmador
        self.resultado = None  # Lista de tuplas: [(pagina, posicion, fecha), ...]

        # Estado
        self.doc = fitz.open(ruta_pdf)
        self.current_page = 0
        self.total_pages = len(self.doc)
        self.zoom = 1.0

        # Firma
        self.firma_imagen = None
        self.firma_photo = None
        self.firma_item = None
        self.firma_position = None
        self.firma_page_position = None
        self.placement_mode = False

        # Shadow
        self.shadow_photo = None
        self.shadow_item = None

        # Drag
        self.dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0

        # Offset de centrado
        self._page_offset_x = 0
        self._page_offset_y = 0

        # Firmas colocadas (lista de diccionarios)
        self.firmas_colocadas = []

        # Cargar imagen de firma
        self._cargar_imagen_firma()

        # Crear modal
        self._create_modal()

    def _cargar_imagen_firma(self):
        """Carga la imagen del sello"""
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

    def _create_modal(self):
        """Crear la ventana modal"""
        self.modal = tk.Toplevel(self.parent)
        self.modal.title("FIRMA PERSONALIZADA - Seleccione posición")
        self.modal.geometry("520x850")
        self.modal.resizable(True, True)
        self.modal.configure(bg='#2b2b2b')
        self.modal.transient(self.parent)
        self.modal.grab_set()

        # Centrar相对于父窗口
        self.modal.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() - 520) // 2
        y = self.parent.winfo_y() + (self.parent.winfo_height() - 850) // 2
        self.modal.geometry(f"520x850+{x}+{y}")

        # ═══ BARRA DE HERRAMIENTAS ═══
        toolbar = tk.Frame(self.modal, bg='#ffffff', height=50)
        toolbar.pack(fill=tk.X)
        toolbar.pack_propagate(False)

        # Contenedor centrado
        nav_frame = tk.Frame(toolbar, bg='#ffffff')
        nav_frame.pack(expand=True)

        # Navegación
        btn_prev = tk.Button(nav_frame, text="◀", command=self._prev_page,
                             bg="#dbdbdb", fg='black', font=('Segoe UI', 10),
                             relief=tk.FLAT, padx=8, pady=4)
        btn_prev.pack(side=tk.LEFT, padx=2)

        btn_next = tk.Button(nav_frame, text="▶", command=self._next_page,
                             bg="#dbdbdb", fg='black', font=('Segoe UI', 10),
                             relief=tk.FLAT, padx=8, pady=4)
        btn_next.pack(side=tk.LEFT, padx=2)

        # Ir a página
        tk.Label(nav_frame, text="Ir a:", bg='#ffffff', fg='black',
                 font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=(10, 3))
        self.page_entry = tk.Entry(nav_frame, width=4, font=('Segoe UI', 9))
        self.page_entry.pack(side=tk.LEFT)
        self.page_entry.bind("<Return>", self._goto_page)

        btn_go = tk.Button(nav_frame, text="Ir", command=self._goto_page,
                           bg='#ffffff', fg='black', font=('Segoe UI', 9),
                           relief=tk.FLAT, padx=6, pady=4)
        btn_go.pack(side=tk.LEFT, padx=2)

        # Indicador de página
        self.page_indicator = tk.Label(nav_frame, text=f"Pág. 1/{self.total_pages}",
                                       bg='#ffffff', fg='black', font=('Segoe UI', 9))
        self.page_indicator.pack(side=tk.LEFT, padx=(10, 0))

        # ═══ ÁREA DEL CANVAS ═══
        canvas_frame = tk.Frame(self.modal, bg='#c9d3e2')
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(canvas_frame, bg='#c9d3e2', cursor='arrow',
                                highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar vertical
        v_scroll = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=v_scroll.set)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Eventos del canvas
        self.canvas.bind("<Configure>", self._on_resize)
        self.canvas.bind("<Motion>", self._on_canvas_motion)
        self.canvas.bind("<ButtonPress-1>", self._on_canvas_click)

        # ═══ BARRA INFERIOR ═══
        bottom_bar = tk.Frame(self.modal, bg='#2b2b2b', height=50)
        bottom_bar.pack(fill=tk.X)
        bottom_bar.pack_propagate(False)

        # Info
        self.info_label = tk.Label(bottom_bar, text="Seleccione posición y haga clic para colocar la firma",
                                   bg='#2b2b2b', fg='#aaaaaa', font=('Segoe UI', 9))
        self.info_label.pack(side=tk.LEFT, padx=10)

        # Renderizar primera página en modo ajustado
        self.modal.after(100, self._init_fit_and_placement)

    def _init_fit_and_placement(self):
        """Inicializar en modo ajustado y placement automático"""
        # Calcular zoom para ajustar la página
        if self.doc:
            page = self.doc[self.current_page]
            cw = self.canvas.winfo_width()
            ch = self.canvas.winfo_height()
            if cw < 10 or ch < 10:
                cw, ch = 480, 700
            scale_x = cw / page.rect.width
            scale_y = ch / page.rect.height
            self.zoom = min(scale_x, scale_y) * 0.95
            self._render_page()
        
        # Iniciar placement automáticamente
        self._iniciar_placement()

    # ══════════════════════════════════════════════════════════════════
    #  NAVEGACIÓN
    # ══════════════════════════════════════════════════════════════════

    def _prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self._render_page()

    def _next_page(self):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self._render_page()

    def _goto_page(self, event=None):
        try:
            page_num = int(self.page_entry.get()) - 1
            if 0 <= page_num < self.total_pages:
                self.current_page = page_num
                self._render_page()
        except:
            pass

    # ══════════════════════════════════════════════════════════════════
    #  RENDERIZADO
    # ══════════════════════════════════════════════════════════════════

    def _render_page(self):
        if not self.doc:
            return

        page = self.doc[self.current_page]
        mat = fitz.Matrix(self.zoom, self.zoom)
        pix = page.get_pixmap(matrix=mat)

        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        self.photo = ImageTk.PhotoImage(img)

        self.canvas.delete("all")
        self.canvas.config(bg='#c9d3e2')

        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        xo = max(0, (cw - pix.width) // 2)
        yo = max(0, (ch - pix.height) // 2)
        self._page_offset_x = xo
        self._page_offset_y = yo

        # Sombra de página
        self.canvas.create_rectangle(xo + 4, yo + 4, xo + pix.width + 4, yo + pix.height + 4,
                                     fill='#ffffff', outline='')
        # Página
        self.canvas.create_image(xo, yo, anchor=tk.NW, image=self.photo)

        # Scrollregion (solo vertical)
        total_h = yo + pix.height + 10
        self.canvas.config(scrollregion=(0, 0, cw, total_h))

        # Actualizar indicadores
        self.page_indicator.config(text=f"Página {self.current_page + 1}/{self.total_pages}")
        self.page_entry.delete(0, tk.END)
        self.page_entry.insert(0, str(self.current_page + 1))

        # Restaurar firma si existe en esta página
        self._restaurar_firmas_pagina()

    def _restaurar_firmas_pagina(self):
        """Restaura las firmas colocadas en la página actual"""
        for firma in self.firmas_colocadas:
            if firma["pagina"] == self.current_page:
                self._stamps_firma(firma["posicion"][0], firma["posicion"][1])

    # ══════════════════════════════════════════════════════════════════
    #  COORDENADAS
    # ══════════════════════════════════════════════════════════════════

    def _pdf_to_canvas(self, pdf_x, pdf_y):
        return self._page_offset_x + pdf_x * self.zoom, self._page_offset_y + pdf_y * self.zoom

    def _canvas_to_pdf(self, cx, cy):
        return (cx - self._page_offset_x) / self.zoom, (cy - self._page_offset_y) / self.zoom

    def _mouse_in_page(self, event):
        if not self.doc:
            return False
        # Convertir a coordenadas del canvas (para scroll)
        cx = self.canvas.canvasx(event.x)
        cy = self.canvas.canvasy(event.y)
        page = self.doc[self.current_page]
        rw = page.rect.width * self.zoom
        rh = page.rect.height * self.zoom
        return (self._page_offset_x <= cx <= self._page_offset_x + rw and
                self._page_offset_y <= cy <= self._page_offset_y + rh)

    # ══════════════════════════════════════════════════════════════════
    #  MODO PLACEMENT
    # ══════════════════════════════════════════════════════════════════

    def _iniciar_placement(self):
        """Entrar en modo placement: sombra sigue al cursor"""
        if not self.doc:
            return

        self.placement_mode = True
        self.canvas.config(cursor='crosshair')
        self.info_label.config(text="Mueva el cursor sobre la página y haga clic para colocar la firma")

    def _show_shadow(self, canvas_x, canvas_y):
        """Muestra la sombra semi-transparente"""
        if not self.firma_imagen:
            return

        w, h = self._firma_scaled_size()

        # Crear versión semi-transparente
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
    #  COLOCAR FIRMA
    # ══════════════════════════════════════════════════════════════════

    def _stamps_firma(self, pdf_x, pdf_y):
        """Coloca la firma definitivamente en coordenadas de página PDF"""
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
            if self._mouse_in_page(event):
                # Usar coordenadas del canvas para la sombra
                cx = self.canvas.canvasx(event.x)
                cy = self.canvas.canvasy(event.y)
                self._show_shadow(cx, cy)
            else:
                self._hide_shadow()

    def _on_canvas_click(self, event):
        if self.placement_mode:
            if self._mouse_in_page(event):
                # Convertir coordenadas del mouse a PDF (usar canvasx/y para scroll)
                cx = self.canvas.canvasx(event.x)
                cy = self.canvas.canvasy(event.y)
                pdf_x, pdf_y = self._canvas_to_pdf(cx, cy)

                # Quitar sombra y salir del modo placement
                self._hide_shadow()
                self.placement_mode = False
                self.canvas.config(cursor='arrow')

                # Colocar firma definitivamente
                self._stamps_firma(pdf_x, pdf_y)

                # Agregar a la lista de firmas
                fecha = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
                self.firmas_colocadas.append({
                    "pagina": self.current_page,
                    "posicion": (pdf_x, pdf_y),
                    "fecha": fecha
                })

                # Actualizar treeview
                self.info_label.config(text=f"Firma colocada en página {self.current_page + 1}")

                # Mostrar modal de confirmación automáticamente
                self.modal.after(100, self._mostrar_confirmacion)

    def _mostrar_confirmacion(self):
        """Mostrar modal de certificado para confirmar la firma"""
        modal = CertificadoModal(self.modal)
        resultado = modal.show()
        
        if resultado == "aceptar":
            # Generar documento firmado inmediatamente
            self._generar_documento()
        else:
            # Si cancela, quitar la última firma
            if self.firmas_colocadas:
                self.firmas_colocadas.pop()
                # Quitar firma del canvas
                if self.firma_item:
                    self.canvas.delete(self.firma_item)
                    self.firma_item = None
                    self.firma_position = None
                    self.firma_page_position = None
            self.info_label.config(text="Firma cancelada. Puede colocar otra firma")

    def _generar_documento(self):
        """Generar el documento firmado y cerrar el modal"""
        if not self.firmas_colocadas:
            return
        
        # Preparar datos para el firmador
        self.resultado = []
        for firma in self.firmas_colocadas:
            self.resultado.append({
                "pagina": firma["pagina"],
                "posicion": firma["posicion"],
                "fecha": firma["fecha"]
            })
        
        # Cerrar modal
        self.modal.event_generate("<<FirmaAvanzadaComplete>>")
        self.modal.destroy()

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
        self.firma_position = (nw_x, nw_y)

        # Convertir NW canvas -> centro canvas -> PDF
        w, h = self._firma_scaled_size()
        center_cx = nw_x + w / 2
        center_cy = nw_y + h / 2
        pdf_x, pdf_y = self._canvas_to_pdf(center_cx, center_cy)
        self.firma_page_position = (pdf_x, pdf_y)

    # ══════════════════════════════════════════════════════════════════
    #  ACCIONES
    # ══════════════════════════════════════════════════════════════════

    def _on_resize(self, event):
        self._render_page()

    def show(self):
        """Mostrar el modal y esperar resultado"""
        self.modal.wait_window()
        return self.resultado
