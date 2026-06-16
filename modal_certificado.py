import tkinter as tk
from tkinter import ttk
from datetime import datetime
import os

# Cargar iconos Font Awesome
ICON_DIR = os.path.join(os.path.dirname(__file__), "assets", "icons")


class CertificadoModal(tk.Toplevel):
    """Modal de seleccion de certificado estilo ONPE"""
    
    def __init__(self, parent, nombre_firmante="VILLEGAS AGUIRRE Delmi Oscar",
                 dni="FAU 20568198272 soft"):
        super().__init__(parent)
        self.resultado = None
        
        self.title("SELECCIONAR CERTIFICADO")
        self.geometry("520x340")
        self.resizable(False, False)
        self.configure(bg='white')
        
        self.transient(parent)
        self.grab_set()
        px = parent.winfo_x() + (parent.winfo_width() - 520) // 2
        py = parent.winfo_y() + (parent.winfo_height() - 340) // 2
        self.geometry(f"+{px}+{py}")
        
        self._load_icons()
        self._build_ui(nombre_firmante, dni)
    
    def _load_icons(self):
        """Carga iconos PNG desde assets/icons"""
        self._icon_aceptar = None
        self._icon_cancelar = None
        
        try:
            from PIL import Image, ImageTk
            
            # Icono de carpeta para el certificado
            icon_cert_path = os.path.join(ICON_DIR, "archivo.png")
            if os.path.exists(icon_cert_path):
                img = Image.open(icon_cert_path).resize((24, 24), Image.Resampling.LANCZOS)
                self._icon_cert = ImageTk.PhotoImage(img)
            else:
                self._icon_cert = None
            
            # Icono de aceptar (vb.png = check)
            icon_aceptar_path = os.path.join(ICON_DIR, "vb.png")
            if os.path.exists(icon_aceptar_path):
                img = Image.open(icon_aceptar_path).resize((40, 40), Image.Resampling.LANCZOS)
                self._icon_aceptar = ImageTk.PhotoImage(img)
            
            # Icono de cancelar (usar zoom_out como X)
            icon_cancelar_path = os.path.join(ICON_DIR, "zoom_out.png")
            if os.path.exists(icon_cancelar_path):
                img = Image.open(icon_cancelar_path).resize((40, 40), Image.Resampling.LANCZOS)
                self._icon_cancelar = ImageTk.PhotoImage(img)
                
        except Exception as e:
            print(f"Error cargando iconos modal: {e}")
            self._icon_cert = None
    
    def _build_ui(self, nombre_firmante, dni):
        # ── Header teal ──
        header = tk.Frame(self, bg='#808080', height=40)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text="SELECCIONAR CERTIFICADO", bg='#808080', fg='white',
                 font=('Segoe UI', 11, 'bold')).pack(side=tk.LEFT, padx=15, pady=8)
        
        # ── Tabs ──
        tabs_frame = tk.Frame(self, bg='white')
        tabs_frame.pack(fill=tk.X)
        
        tk.Label(tabs_frame, text="Certificados Instalados", bg='#41b1e1',
                 fg='white', font=('Segoe UI', 10, 'bold'), padx=15, pady=8).pack(side=tk.LEFT)
        tk.Label(tabs_frame, text="Importar Certificado", bg='#e0e0e0',
                 fg='#666666', font=('Segoe UI', 10), padx=15, pady=8).pack(side=tk.LEFT)
        
        # ── Certificado seleccionado ──
        list_frame = tk.Frame(self, bg='white', bd=1, relief='solid')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(10, 5))
        
        cert_item = tk.Frame(list_frame, bg='#41b1e1', cursor='hand2')
        cert_item.pack(fill=tk.X, padx=2, pady=2)
        
        # Icono del certificado
        if self._icon_cert:
            icon_label = tk.Label(cert_item, image=self._icon_cert, bg='#41b1e1')
            icon_label.pack(side=tk.LEFT, padx=(8, 5), pady=8)
        else:
            icon_frame = tk.Frame(cert_item, bg='#41b1e1', width=40)
            icon_frame.pack(side=tk.LEFT, padx=(8, 5), pady=8)
            c = tk.Canvas(icon_frame, width=28, height=28, bg='#41b1e1', highlightthickness=0)
            c.pack()
            c.create_oval(2, 2, 26, 26, outline='white', width=1.5)
            c.create_text(14, 14, text="\u2605", fill='white', font=('Segoe UI', 12))
        
        # Info
        info_frame = tk.Frame(cert_item, bg='#41b1e1')
        info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=8)
        
        tk.Label(info_frame, text=f"{nombre_firmante}  {dni}",
                 bg='#41b1e1', fg='white',
                 font=('Segoe UI', 10, 'bold'), anchor='w').pack(fill=tk.X)
        tk.Label(info_frame, text="ECEP-RENIEC CA Class 3",
                 bg='#41b1e1', fg="#ffffff",
                 font=('Segoe UI', 8), anchor='w').pack(fill=tk.X)
        tk.Label(info_frame,
                 text="Valido del 11/05/2026 15:37:19 -05'00' al 11/05/2027 15:37:18 -05'00'",
                 bg='#41b1e1', fg="#ffffff",
                 font=('Segoe UI', 8), anchor='w').pack(fill=tk.X)
        
        # ── Botones Aceptar / Cancelar con iconos ──
        btn_frame = tk.Frame(self, bg='white')
        btn_frame.pack(fill=tk.X, padx=15, pady=10)
        
        
        # Cancelar
        cancelar_frame = tk.Frame(btn_frame, bg='white', cursor='hand2')
        cancelar_frame.pack(side=tk.RIGHT, padx=5)
        
        if self._icon_cancelar:
            lbl = tk.Label(cancelar_frame, image=self._icon_cancelar, bg='white', cursor='hand2')
            lbl.pack()
            lbl.bind("<Button-1>", lambda e: self._cancelar())
        else:
            c = tk.Canvas(cancelar_frame, width=44, height=44, bg='white', highlightthickness=0, cursor='hand2')
            c.pack()
            c.create_oval(2, 2, 42, 42, outline='#888', width=1)
            c.create_text(22, 22, text="\u2716", fill='#333', font=('Segoe UI', 14, 'bold'))
            c.bind("<Button-1>", lambda e: self._cancelar())
        
        tk.Label(cancelar_frame, text="Cancelar", bg='white', fg='#333',
                 font=('Segoe UI', 8)).pack()
        
             # Aceptar
        aceptar_frame = tk.Frame(btn_frame, bg='white', cursor='hand2')
        aceptar_frame.pack(side=tk.RIGHT, padx=(5, 0))
        
        if self._icon_aceptar:
            lbl = tk.Label(aceptar_frame, image=self._icon_aceptar, bg='white', cursor='hand2')
            lbl.pack()
            lbl.bind("<Button-1>", lambda e: self._aceptar())
        else:
            c = tk.Canvas(aceptar_frame, width=44, height=44, bg='white', highlightthickness=0, cursor='hand2')
            c.pack()
            c.create_oval(2, 2, 42, 42, outline='#888', width=1)
            c.create_text(22, 22, text="\u2714", fill='#333', font=('Segoe UI', 16, 'bold'))
            c.bind("<Button-1>", lambda e: self._aceptar())
        
        tk.Label(aceptar_frame, text="Aceptar", bg='white', fg='#333',
                 font=('Segoe UI', 8)).pack()
        
        aceptar_frame.bind("<Button-1>", lambda e: self._aceptar())
        cancelar_frame.bind("<Button-1>", lambda e: self._cancelar())
    
    def _aceptar(self):
        self.resultado = "aceptar"
        self.destroy()
    
    def _cancelar(self):
        self.resultado = None
        self.destroy()
    
    def show(self):
        self.wait_window()
        return self.resultado
