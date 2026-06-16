import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
from datetime import datetime
from pdf_viewer import PDFViewer
from firmador import FirmadorPDF

class AplicacionFirma:
    def __init__(self, root):
        self.root = root
        self.root.title("Firma Digital - Demo Profesional")
        self.root.geometry("1200x750")
        self.root.resizable(True, True)
        
        # Variables
        self.firmador = FirmadorPDF()
        self.ruta_pdf = tk.StringVar()
        self.nombre_firmante = tk.StringVar(value="VILLEGAS AGUIRRE Delmi Oscar")
        self.motivo = tk.StringVar(value="Soy el autor del documento")
        self.firma_activa = False
        
        # Crear interfaz
        self.crear_menu()
        self.crear_widgets()
        
        # Configurar atajos de teclado
        self.configurar_atajos()
        
    def crear_menu(self):
        """Crear barra de menú"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menú Archivo
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="Abrir PDF", command=self.abrir_pdf, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.root.quit)
        
        # Menú Firma
        firmar_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Firma", menu=firmar_menu)
        firmar_menu.add_command(label="Colocar Firma", command=self.colocar_firma, accelerator="Ctrl+F")
        firmar_menu.add_command(label="Quitar Firma", command=self.quitar_firma)
        firmar_menu.add_separator()
        firmar_menu.add_command(label="Aplicar Firma Digital", command=self.aplicar_firma, accelerator="Ctrl+S")
        
        # Menú Ver
        ver_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ver", menu=ver_menu)
        ver_menu.add_command(label="Zoom +", command=self.zoom_in, accelerator="Ctrl++")
        ver_menu.add_command(label="Zoom -", command=self.zoom_out, accelerator="Ctrl+-")
        ver_menu.add_command(label="Zoom 100%", command=self.zoom_normal, accelerator="Ctrl+0")
    
    def crear_widgets(self):
        # Panel principal
        main_pane = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Panel izquierdo - Visor PDF
        left_frame = ttk.Frame(main_pane)
        main_pane.add(left_frame, weight=3)
        
        # Panel derecho - Controles
        right_frame = ttk.Frame(main_pane, width=380)
        main_pane.add(right_frame, weight=1)
        
        # ===== VISOR PDF =====
        # Barra de herramientas
        toolbar = ttk.Frame(left_frame)
        toolbar.pack(fill=tk.X, pady=5)
        
        ttk.Button(toolbar, text="◀", command=self.pagina_anterior, width=3).pack(side=tk.LEFT, padx=2)
        self.page_label = ttk.Label(toolbar, text="Página: 0/0")
        self.page_label.pack(side=tk.LEFT, padx=10)
        ttk.Button(toolbar, text="▶", command=self.pagina_siguiente, width=3).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        ttk.Button(toolbar, text="🔍+", command=self.zoom_in, width=3).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🔍-", command=self.zoom_out, width=3).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="100%", command=self.zoom_normal, width=4).pack(side=tk.LEFT, padx=2)
        
        # Área del visor
        self.viewer = PDFViewer(left_frame, width=750, height=550)
        self.viewer.pack(fill=tk.BOTH, expand=True)
        
        # Eventos del visor
        self.viewer.bind("<<PageChanged>>", self.actualizar_info_pagina)
        self.viewer.bind("<<FirmaMoved>>", self.actualizar_info_firma)
        self.viewer.bind("<<FirmaAdded>>", self.firma_colocada)
        self.viewer.bind("<<FirmaRemoved>>", self.firma_eliminada)
        
        # ===== PANEL DE CONTROLES =====
        # Título
        titulo_frame = ttk.Frame(right_frame)
        titulo_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(titulo_frame, text="📄 CONTROLES DE FIRMA", 
                 font=('Arial', 12, 'bold')).pack(anchor=tk.W, padx=10)
        
        # Sección de archivo
        archivo_frame = ttk.LabelFrame(right_frame, text="Documento")
        archivo_frame.pack(fill=tk.X, padx=10, pady=5)
        
        file_frame = ttk.Frame(archivo_frame)
        file_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.entry_archivo = ttk.Entry(file_frame, textvariable=self.ruta_pdf)
        self.entry_archivo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(file_frame, text="📂", command=self.abrir_pdf, width=3).pack(side=tk.LEFT, padx=2)
        
        # Sección de datos de firma
        datos_frame = ttk.LabelFrame(right_frame, text="Datos de la Firma")
        datos_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Firmante
        ttk.Label(datos_frame, text="Firmante:").pack(anchor=tk.W, padx=10, pady=(5,0))
        entry_firmante = ttk.Entry(datos_frame, textvariable=self.nombre_firmante)
        entry_firmante.pack(fill=tk.X, padx=10, pady=2)
        
        # Motivo
        ttk.Label(datos_frame, text="Motivo:").pack(anchor=tk.W, padx=10, pady=(5,0))
        entry_motivo = ttk.Entry(datos_frame, textvariable=self.motivo)
        entry_motivo.pack(fill=tk.X, padx=10, pady=2)
        
        # Fecha (automática)
        ttk.Label(datos_frame, text="Fecha:").pack(anchor=tk.W, padx=10, pady=(5,0))
        self.fecha_label = ttk.Label(datos_frame, text=datetime.now().strftime("%d.%m.%Y %H:%M:%S -05:00"))
        self.fecha_label.pack(anchor=tk.W, padx=10, pady=2)
        
        # Sección de acciones
        acciones_frame = ttk.LabelFrame(right_frame, text="Acciones")
        acciones_frame.pack(fill=tk.X, padx=10, pady=5)
        
        btn_colocar = ttk.Button(acciones_frame, text="🖊️ Colocar Firma", 
                                 command=self.colocar_firma)
        btn_colocar.pack(fill=tk.X, padx=10, pady=2)
        
        btn_quitar = ttk.Button(acciones_frame, text="🗑️ Quitar Firma", 
                                command=self.quitar_firma)
        btn_quitar.pack(fill=tk.X, padx=10, pady=2)
        
        ttk.Separator(acciones_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=5)
        
        btn_aplicar = ttk.Button(acciones_frame, text="✍️ APLICAR FIRMA DIGITAL", 
                                 command=self.aplicar_firma, style="Accent.TButton")
        btn_aplicar.pack(fill=tk.X, padx=10, pady=5)
        
        # Estado
        estado_frame = ttk.LabelFrame(right_frame, text="Estado")
        estado_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.status_label = ttk.Label(estado_frame, text="🔴 Sin documento", wraplength=340)
        self.status_label.pack(anchor=tk.W, padx=10, pady=2)
        
        self.pos_label = ttk.Label(estado_frame, text="📍 Posición: No establecida", wraplength=340)
        self.pos_label.pack(anchor=tk.W, padx=10, pady=2)
        
        # Información de ayuda
        help_frame = ttk.LabelFrame(right_frame, text="Ayuda")
        help_frame.pack(fill=tk.X, padx=10, pady=5)
        
        help_text = """💡 Instrucciones:
1. Abre un documento PDF
2. Haz clic en "Colocar Firma"
3. Arrastra la firma a la posición deseada
4. Haz clic en "Aplicar Firma Digital" """
        
        ttk.Label(help_frame, text=help_text, wraplength=340, 
                 font=('Arial', 8)).pack(anchor=tk.W, padx=10, pady=5)
        
        # Estilos
        style = ttk.Style()
        style.configure("Accent.TButton", font=('Arial', 10, 'bold'), foreground='blue')
    
    def configurar_atajos(self):
        """Configurar atajos de teclado"""
        self.root.bind('<Control-o>', lambda e: self.abrir_pdf())
        self.root.bind('<Control-f>', lambda e: self.colocar_firma())
        self.root.bind('<Control-s>', lambda e: self.aplicar_firma())
        self.root.bind('<Control-plus>', lambda e: self.zoom_in())
        self.root.bind('<Control-minus>', lambda e: self.zoom_out())
        self.root.bind('<Control-0>', lambda e: self.zoom_normal())
    
    def abrir_pdf(self):
        """Abrir un archivo PDF"""
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo PDF",
            filetypes=[("Archivos PDF", "*.pdf"), ("Todos los archivos", "*.*")]
        )
        if archivo:
            self.ruta_pdf.set(archivo)
            self.status_label.config(text=f"📄 {os.path.basename(archivo)}")
            
            # Cargar en el visor
            exito, mensaje = self.viewer.load_pdf(archivo)
            if exito:
                self.status_label.config(text=f"✅ {mensaje}")
                self.firmador.abrir_pdf(archivo)
                self.actualizar_info_pagina()
            else:
                self.status_label.config(text=f"❌ {mensaje}")
                messagebox.showerror("Error", mensaje)
    
    def colocar_firma(self):
        """Entrar en modo placement: sombra sigue al cursor"""
        if not self.ruta_pdf.get():
            messagebox.showwarning("Advertencia", "Primero abre un documento PDF")
            return
        
        if self.viewer.add_firma():
            self.firma_activa = False  # Aun no esta colocada
            self.status_label.config(text="Mueve el mouse y haz click para colocar la firma")
    
    def quitar_firma(self):
        """Quitar la firma del visor"""
        self.viewer.remove_firma()
        self.firma_activa = False
        self.status_label.config(text="Firma eliminada")
        self.pos_label.config(text="Posicion: No establecida")
    
    def aplicar_firma(self):
        """Aplicar la firma digital al PDF"""
        if not self.ruta_pdf.get():
            messagebox.showwarning("Advertencia", "Primero abre un documento PDF")
            return
        
        if not self.firma_activa:
            messagebox.showwarning("Advertencia", "Primero coloca la firma en el documento")
            return
        
        pos = self.viewer.get_firma_position_for_pdf()
        if not pos:
            messagebox.showerror("Error", "No se pudo obtener la posición de la firma")
            return
        
        nombre = self.nombre_firmante.get().strip() or "Usuario"
        motivo = self.motivo.get().strip() or "Documento firmado digitalmente"
        fecha = self.fecha_label.cget("text")
        
        # Aplicar firma
        exito, mensaje = self.firmador.firmar_pdf_con_imagen(
            nombre, motivo, pos, fecha
        )
        
        if exito:
            self.status_label.config(text=f"✅ {mensaje}")
            messagebox.showinfo("Éxito", f"✅ Documento firmado correctamente:\n{mensaje}")
        else:
            self.status_label.config(text=f"❌ {mensaje}")
            messagebox.showerror("Error", mensaje)
    
    def pagina_anterior(self):
        self.viewer.prev_page()
    
    def pagina_siguiente(self):
        self.viewer.next_page()
    
    def zoom_in(self):
        self.viewer.zoom *= 1.2
        self.viewer.render_page()
    
    def zoom_out(self):
        self.viewer.zoom *= 0.8
        self.viewer.render_page()
    
    def zoom_normal(self):
        self.viewer.zoom = 1.0
        self.viewer.render_page()
    
    def actualizar_info_pagina(self, event=None):
        if self.viewer.doc:
            self.page_label.config(text=f"Página: {self.viewer.current_page + 1}/{self.viewer.total_pages}")
    
    def actualizar_info_firma(self, event=None):
        if hasattr(self.viewer, 'firma_page_position') and self.viewer.firma_page_position:
            x, y = self.viewer.firma_page_position
            self.pos_label.config(text=f"Pag {self.viewer.current_page + 1} - Pos: X={int(x)}, Y={int(y)}")
    
    def firma_colocada(self, event=None):
        self.firma_activa = True
        self.status_label.config(text="Firma colocada - Puedes arrastrarla o firmar")
        self.actualizar_info_firma()
    
    def firma_eliminada(self, event=None):
        self.firma_activa = False
        self.status_label.config(text="Firma eliminada")

if __name__ == "__main__":
    root = tk.Tk()
    app = AplicacionFirma(root)
    root.mainloop()