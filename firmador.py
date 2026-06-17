import fitz
import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import io

class FirmadorPDF:
    def __init__(self):
        self.ruta_archivo = None
        self.doc = None
        
    def abrir_pdf(self, ruta):
        try:
            self.ruta_archivo = ruta
            self.doc = fitz.open(ruta)
            return True, f"PDF abierto: {os.path.basename(ruta)}"
        except Exception as e:
            return False, f"Error al abrir: {str(e)}"
    
    def _detect_y_flip(self):
        """Detecta si el PDF tiene transformación Y-invertida (común en DOCX→PDF)"""
        if not self.doc or len(self.doc) == 0:
            return 0
        
        try:
            page = self.doc[0]
            contents = page.get_contents()
            for cxref in contents:
                stream = self.doc.xref_stream(cxref)
                if stream:
                    text = stream.decode('latin-1', errors='replace')
                    # Buscar patrón "1 0 0 -1 0 H cm" (Y-flip)
                    import re
                    match = re.search(r'([\d.]+)\s+0\s+0\s+(-[\d.]+)\s+\d+\s+([\d.]+)\s+cm', text)
                    if match:
                        a = float(match.group(1))
                        d = float(match.group(2))
                        f = float(match.group(3))
                        if a == 1.0 and d < 0:
                            return f
        except:
            pass
        
        return 0
    
    def generar_imagen_firma(self, nombre_firmante, motivo, fecha=None):
        """Genera la imagen de firma con logo real y datos del firmante"""
        if fecha is None:
            fecha = datetime.now().strftime("%d.%m.%Y %H:%M:%S -05:00")
        
        # Dimensiones de la imagen final
        img_width = 720
        img_height = 140
        
        # Crear imagen con fondo blanco
        img = Image.new('RGBA', (img_width, img_height), (255, 255, 255, 255))
        
        # Cargar el logo real
        logo_path = os.path.join(os.path.dirname(__file__), "assets", "images", "1.png")
        try:
            logo = Image.open(logo_path)
            # Redimensionar logo manteniendo proporción
            logo_height = 110
            logo_ratio = logo.width / logo.height
            logo_width = int(logo_height * logo_ratio)
            logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
            # Pegar logo en la izquierda
            logo_y = (img_height - logo_height) // 2
            img.paste(logo, (10, logo_y), logo if logo.mode == 'RGBA' else None)
        except Exception as e:
            print(f"Error cargando logo: {e}")
            # Fallback: dibujar rectángulo placeholder
            draw = ImageDraw.Draw(img)
            draw.rectangle([10, 10, 130, 130], outline=(150, 50, 50), width=2)
            draw.text((30, 60), "LOGO", fill=(150, 50, 50))
        
        # Configurar fuentes para el texto
        draw = ImageDraw.Draw(img)
        try:
            font_normal = ImageFont.truetype("arial.ttf", 11)
            font_bold = ImageFont.truetype("arial.ttf", 12)
            font_name = ImageFont.truetype("arial.ttf", 13)
        except:
            font_normal = ImageFont.load_default()
            font_bold = ImageFont.load_default()
            font_name = ImageFont.load_default()
        
        # Texto de la firma (lado derecho del logo - después del texto "Firma Digital")
        # La imagen del logo mide ~230px de ancho con el texto
        text_x = 280
        y_offset = 20
        
        # Línea separadora vertical
        draw.line([text_x - 15, 15, text_x - 15, 125], fill=(180, 180, 180), width=1)
        
        # "Firmado digitalmente por"
        draw.text((text_x, y_offset), "Firmado digitalmente por", fill=(100, 100, 100), font=font_normal)
        
        # Nombre del firmante (negrita)
        draw.text((text_x, y_offset + 18), nombre_firmante, fill=(50, 50, 50), font=font_name)
        
        # DNI y.soft
        draw.text((text_x, y_offset + 38), "FAU 20568198272 soft", fill=(100, 100, 100), font=font_normal)
        
        # Motivo
        draw.text((text_x, y_offset + 56), f"Motivo: {motivo}", fill=(100, 100, 100), font=font_normal)
        
        # Fecha
        draw.text((text_x, y_offset + 74), f"Fecha: {fecha}", fill=(100, 100, 100), font=font_normal)
        
        # Convertir a bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        return img_bytes.getvalue()
    
    def firmar_pdf_con_imagen(self, nombre_firmante, motivo, posicion, fecha=None, page_idx=0):
        """Firma el PDF colocando la imagen en la posición especificada"""
        if not self.doc:
            return False, "No hay documento abierto"
        
        try:
            # Usar la página especificada (por defecto la primera)
            if page_idx < 0 or page_idx >= len(self.doc):
                page_idx = 0
            pagina = self.doc[page_idx]
            
            # Generar imagen de firma
            img_data = self.generar_imagen_firma(nombre_firmante, motivo, fecha)
            
            # Usar la posición proporcionada
            x, y, w, h = posicion
            
            # Crear rectángulo para la imagen
            rect = fitz.Rect(x, y, x + w, y + h)
            
            # Insertar imagen en la página
            pagina.insert_image(rect, stream=img_data)
            
            # Guardar con nuevo nombre
            base, ext = os.path.splitext(self.ruta_archivo)
            nueva_ruta = f"{base}[F].pdf"
            
            contador = 1
            while os.path.exists(nueva_ruta):
                nueva_ruta = f"{base}[F]({contador}).pdf"
                contador += 1
            
            self.doc.save(nueva_ruta)
            self.doc.close()
            
            return True, f"PDF firmado guardado como: {os.path.basename(nueva_ruta)}"
            
        except Exception as e:
            return False, f"Error al firmar: {str(e)}"
    
    def firmar_pdf_multiples_firmas(self, nombre_firmante, motivo, firmas, fecha=None):
        """Firma el PDF con múltiples firmas en diferentes páginas
        
        Returns:
            (bool, str, str): (éxito, mensaje, ruta_archivo_creado)
        """
        if not self.doc:
            return False, "No hay documento abierto", ""
        
        try:
            # Generar imagen de firma una sola vez
            if fecha is None:
                fecha = datetime.now().strftime("%d.%m.%Y %H:%M:%S -05:00")
            img_data = self.generar_imagen_firma(nombre_firmante, motivo, fecha)
            
            # Detectar si la página tiene transformación Y-invertida (común en DOCX→PDF)
            y_flip = self._detect_y_flip()
            
            # Insertar firma en cada página especificada
            for firma in firmas:
                pagina_num = firma["pagina"]
                posicion = firma["posicion"]
                fecha_firma = firma.get("fecha", fecha)
                
                if pagina_num < 0 or pagina_num >= len(self.doc):
                    continue
                
                pagina = self.doc[pagina_num]
                x, y, w, h = posicion
                
                # Aplicar Y-flip si el PDF lo requiere
                if y_flip > 0:
                    y = y_flip - y - h
                
                # Crear rectángulo para la imagen
                rect = fitz.Rect(x, y, x + w, y + h)
                
                # Insertar imagen en la página
                pagina.insert_image(rect, stream=img_data)
            
            # Guardar con nuevo nombre usando nomenclatura [F]
            base, ext = os.path.splitext(self.ruta_archivo)
            nueva_ruta = f"{base}[F].pdf"
            
            contador = 1
            while os.path.exists(nueva_ruta):
                nueva_ruta = f"{base}[F]({contador}).pdf"
                contador += 1
            
            self.doc.save(nueva_ruta)
            self.doc.close()
            
            return True, f"PDF firmado guardado como: {os.path.basename(nueva_ruta)}", nueva_ruta
            
        except Exception as e:
            return False, f"Error al firmar: {str(e)}", ""