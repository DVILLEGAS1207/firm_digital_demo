import tkinter as tk
from tkinter import filedialog, messagebox
import os
from datetime import datetime
from pdf_viewer import PDFViewer
from firmador import FirmadorPDF
from modal_certificado import CertificadoModal
from modal_firma_avanzada import ModalFirmaAvanzada


# ══════════════════════════════════════════════════════════════════════
#  BOTON DE TOOLBAR CON DROPDOWN
# ══════════════════════════════════════════════════════════════════════

class ToolbarButton(tk.Frame):
    """Boton de toolbar con icono PNG arriba y texto debajo"""
    def __init__(self, parent, icon_file, label, command=None, menu_items=None, **kwargs):
        super().__init__(parent, bg='#2b2b2b', **kwargs)
        self.command = command
        self.menu_items = menu_items
        self.menu_popup = None
        
        # Cargar icono PNG
        icon_path = os.path.join(os.path.dirname(__file__), "assets", "icons", icon_file)
        self._icon_normal = None
        self._icon_hover = None
        
        try:
            from PIL import Image, ImageTk, ImageEnhance
            img = Image.open(icon_path).convert("RGBA")
            self._icon_normal = ImageTk.PhotoImage(img)
            
            # Version hover (mas clara)
            img_hover = ImageEnhance.Brightness(img).enhance(1.3)
            self._icon_hover = ImageTk.PhotoImage(img_hover)
        except Exception as e:
            print(f"Error cargando icono {icon_file}: {e}")
        
        # PRIMERO el icono (arriba)
        self.icon_label = tk.Label(self, bg='#2b2b2b', cursor='hand2')
        if self._icon_normal:
            self.icon_label.config(image=self._icon_normal)
        self.icon_label.pack(pady=(6, 2))
        
        # DESPUES el texto (debajo)
        self.label = tk.Label(self, text=label, bg='#2b2b2b', fg='#cccccc',
                              font=('Segoe UI', 8), cursor='hand2')
        self.label.pack(pady=(0, 6))
        
        # Eventos
        for w in (self.icon_label, self.label):
            w.bind("<Button-1>", self._on_click)
            w.bind("<Button-3>", self._on_right_click)
            w.bind("<Enter>", self._on_enter)
            w.bind("<Leave>", self._on_leave)
    
    def _on_click(self, event):
        if self.menu_items:
            self._show_menu(event)
        elif self.command:
            self.command()
    
    def _on_right_click(self, event):
        if self.menu_items:
            self._show_menu(event)
    
    def _show_menu(self, event):
        if self.menu_popup:
            self.menu_popup.destroy()
        
        self.menu_popup = tk.Menu(self, tearoff=0, bg='#3a3a3a', fg='white',
                                  activebackground='#41b1e1', activeforeground='white',
                                  font=('Segoe UI', 9))
        
        for texto, cmd in self.menu_items:
            if texto == "---":
                self.menu_popup.add_separator()
            else:
                self.menu_popup.add_command(label=texto, command=cmd)
        
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height()
        self.menu_popup.tk_popup(x, y)
    
    def _on_enter(self, event):
        self.icon_label.config(bg='#3d3d3d')
        self.label.config(fg='white')
        if self._icon_hover:
            self.icon_label.config(image=self._icon_hover)
    
    def _on_leave(self, event):
        self.icon_label.config(bg='#2b2b2b')
        self.label.config(fg='#cccccc')
        if self._icon_normal:
            self.icon_label.config(image=self._icon_normal)


class SeparadorToolbar(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg='#2b2b2b', width=20)
        self.pack_propagate(False)
        tk.Canvas(self, width=1, bg='#555555', highlightthickness=0).pack(expand=True, pady=8)


# ══════════════════════════════════════════════════════════════════════
#  APLICACION PRINCIPAL
# ══════════════════════════════════════════════════════════════════════

class AplicacionFirma:
    def __init__(self, root):
        self.root = root
        self.root.title("FIRMA ONPE")
        self.root.geometry("1300x800")
        self.root.resizable(True, True)
        self.root.configure(bg='#2b2b2b')
        
        # Model
        self.firmador = FirmadorPDF()
        self.ruta_pdf = tk.StringVar()
        self.firma_activa = False
        
        self._build_ui()
    
    def _build_ui(self):
        # ═══ ICONO Y TITULO DE VENTANA ═══
        icon_path = os.path.join(os.path.dirname(__file__), "assets", "images", "Icon11.ico")
        
        # Titulo vacio en title bar nativo (todo va en la barra teal)
        self.root.title("")
        
        # Icono en title bar (pequeno, para que Windows lo muestre)
        try:
            from PIL import Image, ImageTk
            icon_img = Image.open(icon_path)
            self._icon_photos = [ImageTk.PhotoImage(icon_img.resize(sz, Image.Resampling.LANCZOS))
                                 for sz in [(16, 16), (32, 32), (48, 48)]]
            self.root.iconphoto(True, *self._icon_photos)
        except Exception as e:
            print(f"Error cargando icono: {e}")
        
        # ═══ BARRA TEAL (icono + titulo + indicadores) ═══
        top_bar = tk.Frame(self.root, bg='#41b1e1', height=32)
        top_bar.pack(fill=tk.X)
        top_bar.pack_propagate(False)
        
        # Icono grande en la barra teal
        try:
            icon_grande = icon_img.resize((22, 22), Image.Resampling.LANCZOS)
            self._icon_teal = ImageTk.PhotoImage(icon_grande)
            tk.Label(top_bar, image=self._icon_teal, bg='#41b1e1').pack(side=tk.LEFT, padx=(10, 6), pady=5)
        except:
            pass
        
        # Titulo FIRMA ONPE
        tk.Label(top_bar, text="FIRMA ONPE", bg='#41b1e1', fg='white',
                 font=('Segoe UI', 11, 'bold')).pack(side=tk.LEFT, pady=5)
        
        # Indicadores derecha
        right_top = tk.Frame(top_bar, bg='#41b1e1')
        right_top.pack(side=tk.RIGHT, padx=10)
        
        for txt in ["\u2714 Estado", "\u2699 Configurar", "\u2302 Acerca de"]:
            tk.Label(right_top, text=f"  {txt}", bg='#41b1e1', fg="#ffffff",
                     font=('Segoe UI', 9), cursor='hand2').pack(side=tk.LEFT, padx=3)
        
        # ═══ TOOLBAR ═══
        toolbar = tk.Frame(self.root, bg='#2b2b2b', height=80)
        toolbar.pack(fill=tk.X)
        toolbar.pack_propagate(False)
        
        # --- Archivo (con submenu) ---
        ToolbarButton(toolbar, "archivo.png", "Archivo", menu_items=[
            ("Abrir PDF", self.abrir_pdf),
            ("---", None),
            ("Salir", self.root.quit),
        ]).pack(side=tk.LEFT, padx=2)
        
        # --- Firmar (con submenu) ---
        ToolbarButton(toolbar, "firmar.png", "Firmar", menu_items=[
            ("Firmar", self.firmar_documento),
            ("Firma Avanzada", self.firma_avanzada),
        ]).pack(side=tk.LEFT, padx=2)
        
        # --- V B (sin accion) ---
        ToolbarButton(toolbar, "vb.png", "V\u00b0 B\u00b0").pack(side=tk.LEFT, padx=2)
        
        SeparadorToolbar(toolbar).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # --- Imprimir (sin accion) ---
        ToolbarButton(toolbar, "imprimir.png", "Imprimir").pack(side=tk.LEFT, padx=2)
        
        # --- Verificar (sin accion) ---
        ToolbarButton(toolbar, "verificar.png", "Verificar").pack(side=tk.LEFT, padx=2)
        
        SeparadorToolbar(toolbar).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # --- Zoom ---
        ToolbarButton(toolbar, "zoom_in.png", "Acercar", command=self.zoom_in).pack(side=tk.LEFT, padx=2)
        ToolbarButton(toolbar, "zoom_out.png", "Alejar", command=self.zoom_out).pack(side=tk.LEFT, padx=2)
        ToolbarButton(toolbar, "ajustar.png", "Ajustar", command=self.zoom_ajustar).pack(side=tk.LEFT, padx=2)
        
        # ═══ VISOR PDF ═══
        main_frame = tk.Frame(self.root, bg='#585858')
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.viewer = PDFViewer(main_frame, width=800, height=600)
        self.viewer.pack(fill=tk.BOTH, expand=True)
        
        self.viewer.bind("<<PageChanged>>", self._on_page_changed)
        self.viewer.bind("<<FirmaAdded>>", self._on_firma_added)
        self.viewer.bind("<<FirmaMoved>>", self._on_firma_moved)
        self.viewer.bind("<<FirmaRemoved>>", self._on_firma_removed)
        
        # ═══ STATUS BAR ═══
        status = tk.Frame(self.root, bg='#2b2b2b', height=26)
        status.pack(fill=tk.X)
        status.pack_propagate(False)
        
        self.status_label = tk.Label(status, text="Listo", bg='#2b2b2b', fg='#aaaaaa',
                                     font=('Segoe UI', 9), anchor='w')
        self.status_label.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        self.page_label = tk.Label(status, text="", bg='#2b2b2b', fg='#aaaaaa',
                                   font=('Segoe UI', 9))
        self.page_label.pack(side=tk.RIGHT, padx=10)
        
        self.pos_label = tk.Label(status, text="", bg='#2b2b2b', fg='#aaaaaa',
                                  font=('Segoe UI', 9))
        self.pos_label.pack(side=tk.RIGHT, padx=10)
        
        # Atajos
        self.root.bind('<Control-o>', lambda e: self.abrir_pdf())
        self.root.bind('<Control-f>', lambda e: self.firma_avanzada())
        self.root.bind('<Control-s>', lambda e: self.firmar_documento())
    
    # ══════════════════════════════════════════════════════════════════
    #  ACCIONES ARCHIVO
    # ══════════════════════════════════════════════════════════════════
    
    def abrir_pdf(self):
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo PDF",
            filetypes=[("Archivos PDF", "*.pdf"), ("Todos los archivos", "*.*")]
        )
        if archivo:
            self.ruta_pdf.set(archivo)
            self.status_label.config(text="Abriendo...")
            
            ok, msg = self.viewer.load_pdf(archivo)
            if ok:
                self.status_label.config(text=f"{msg} - {os.path.basename(archivo)}")
                self.firmador.abrir_pdf(archivo)
                self._update_page_info()
            else:
                self.status_label.config(text=f"Error: {msg}")
                messagebox.showerror("Error", msg)
    
    # ══════════════════════════════════════════════════════════════════
    #  ACCIONES FIRMA
    # ══════════════════════════════════════════════════════════════════
    
    def colocar_firma(self):
        """Entrar en modo placement: sombra sigue al cursor"""
        if not self.ruta_pdf.get():
            messagebox.showwarning("Advertencia", "Primero abra un documento PDF")
            return
        
        if self.viewer.add_firma():
            self.firma_activa = False
            self.status_label.config(text="Ubique el cursor y haga click para colocar la firma")
    
    def firma_avanzada(self):
        """Abrir modal de firma avanzada con navegación multipágina"""
        if not self.ruta_pdf.get():
            messagebox.showwarning("Advertencia", "Primero abra un documento PDF")
            return
        
        # Abrir modal de firma avanzada
        modal = ModalFirmaAvanzada(self.root, self.ruta_pdf.get(), self.firmador)
        resultado = modal.show()
        
        if resultado:
            # Hay firmas para procesar
            self._procesar_firmas_avanzadas(resultado)
    
    def _procesar_firmas_avanzadas(self, firmas):
        """Procesar las firmas del modal avanzado"""
        if not firmas:
            return
        
        # Datos del firmante (demo)
        nombre = "VILLEGAS AGUIRRE Delmi Oscar"
        motivo = "Soy el autor del documento"
        
        self.status_label.config(text="Generando documento firmado...")
        self.root.update()
        
        # Preparar datos para el firmador
        firmas_data = []
        for firma in firmas:
            # Calcular posición exacta para el PDF
            page = self.firmador.doc[firma["pagina"]]
            rect = page.rect
            
            pdf_x, pdf_y = firma["posicion"]
            
            # Usar dimensiones de la imagen del visor principal
            if self.viewer.firma_imagen:
                sig_w = rect.width * 0.45
                sig_h = sig_w * (self.viewer.firma_imagen.height / self.viewer.firma_imagen.width)
            else:
                # Fallback: dimensiones por defecto
                sig_w = rect.width * 0.45
                sig_h = sig_w * (140 / 720)
            
            # La posición (pdf_x, pdf_y) es el CENTRO donde se hizo click
            x = pdf_x - sig_w / 2
            y = pdf_y - sig_h / 2
            
            # Asegurar que esté dentro de la página
            x = max(0, min(x, rect.width - sig_w))
            y = max(0, min(y, rect.height - sig_h))
            
            firmas_data.append({
                "pagina": firma["pagina"],
                "posicion": (x, y, sig_w, sig_h),
                "fecha": firma.get("fecha", datetime.now().strftime("%d.%m.%Y %H:%M:%S -05:00"))
            })
        
        # Firmar PDF
        ok, msg, ruta_firmada = self.firmador.firmar_pdf_multiples_firmas(nombre, motivo, firmas_data)
        
        if ok:
            # Cargar el documento firmado en el visor
            if ruta_firmada and os.path.exists(ruta_firmada):
                self.ruta_pdf.set(ruta_firmada)
                self.viewer.load_pdf(ruta_firmada)
                self.firmador.abrir_pdf(ruta_firmada)
                self._update_page_info()
            
            self.status_label.config(text=msg)
            messagebox.showinfo("Éxito", f"Documento firmado:\n{msg}")
        else:
            self.status_label.config(text=f"Error: {msg}")
            messagebox.showerror("Error", msg)
    
    def firmar_documento(self):
        """Mostrar modal de certificado, y si acepta, generar PDF firmado"""
        if not self.ruta_pdf.get():
            return
        
        if not self.viewer.firma_page_position:
            messagebox.showwarning("Advertencia", "Primero coloque la firma en el documento")
            return
        
        # Mostrar modal de seleccion de certificado
        modal = CertificadoModal(self.root)
        resultado = modal.show()
        
        if resultado != "aceptar":
            self.status_label.config(text="Firma cancelada - Puede reposicionar la firma y volver a Firmar")
            return
        
        # Obtener posicion de la firma (x, y, w, h, page_idx)
        pos = self.viewer.get_firma_position_for_pdf()
        if not pos:
            messagebox.showerror("Error", "No se pudo obtener la posicion de la firma")
            return
        
        x, y, w, h, page_idx = pos
        
        # Datos del firmante (demo)
        nombre = "VILLEGAS AGUIRRE Delmi Oscar"
        motivo = "Soy el autor del documento"
        fecha = datetime.now().strftime("%d.%m.%Y %H:%M:%S -05:00")
        
        self.status_label.config(text="Generando documento firmado...")
        self.root.update()
        
        ok, msg = self.firmador.firmar_pdf_con_imagen(nombre, motivo, (x, y, w, h), fecha, page_idx)
        
        if ok:
            self.status_label.config(text=msg)
            messagebox.showinfo("Exito", f"Documento firmado:\n{msg}")
        else:
            self.status_label.config(text=f"Error: {msg}")
            messagebox.showerror("Error", msg)
    
    # ══════════════════════════════════════════════════════════════════
    #  ZOOM
    # ══════════════════════════════════════════════════════════════════
    
    def zoom_in(self):
        self.viewer.zoom *= 1.25
        self.viewer.render_page()
    
    def zoom_out(self):
        self.viewer.zoom *= 0.8
        self.viewer.render_page()
    
    def zoom_ajustar(self):
        """Ajustar la pagina para que quepa completa en el visor"""
        if not self.viewer.doc:
            return
        # En scroll continuo, usar la primera página para calcular zoom
        page = self.viewer.doc[0]
        cw = max(self.viewer.canvas.winfo_width(), self.viewer.width)
        ch = max(self.viewer.canvas.winfo_height(), self.viewer.height)
        
        scale_x = cw / page.rect.width
        scale_y = ch / page.rect.height
        self.viewer.zoom = min(scale_x, scale_y) * 0.95  # 95% para margen
        self.viewer.render_page()
    
    # ══════════════════════════════════════════════════════════════════
    #  EVENTOS DEL VISOR
    # ══════════════════════════════════════════════════════════════════
    
    def _on_page_changed(self, event=None):
        self._update_page_info()
    
    def _on_firma_added(self, event=None):
        self.firma_activa = True
        self.status_label.config(text="Firma colocada")
        self._update_pos_info()
        # Mostrar modal de certificado automaticamente
        self.root.after(100, self.firmar_documento)
    
    def _on_firma_moved(self, event=None):
        self._update_pos_info()
    
    def _on_firma_removed(self, event=None):
        self.firma_activa = False
        self.status_label.config(text="Firma eliminada")
        self.pos_label.config(text="")
    
    def _update_page_info(self):
        if self.viewer.doc:
            # En scroll continuo, mostrar total de páginas
            self.page_label.config(
                text=f"Pag 1/{self.viewer.total_pages}")
    
    def _update_pos_info(self):
        if self.viewer.firma_page_position:
            x, y = self.viewer.firma_page_position
            self.pos_label.config(text=f"X:{int(x)} Y:{int(y)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = AplicacionFirma(root)
    root.mainloop()
