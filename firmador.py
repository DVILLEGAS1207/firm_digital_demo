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
    
    def generar_imagen_firma(self, nombre_firmante, motivo, fecha=None):
        """Genera la imagen de firma con el formato exacto de la captura"""
        if fecha is None:
            fecha = datetime.now().strftime("%d.%m.%Y %H:%M:%S -05:00")
        
        # Crear imagen con fondo blanco y borde
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
        draw.text((140, 48), nombre_firmante, fill=(0, 0, 0), font=font_bold)
        draw.text((140, 66), "FAU 20568198272 soft", fill=(80, 80, 80), font=font)
        draw.text((140, 84), f"Motivo: {motivo}", fill=(80, 80, 80), font=font)
        draw.text((140, 102), f"Fecha: {fecha}", fill=(80, 80, 80), font=font)
        
        # "Firma Digital" en la parte inferior
        draw.text((250, 145), "Firma Digital", fill=(0, 0, 139), font=font_bold)
        
        # Convertir a bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        return img_bytes.getvalue()
    
    def firmar_pdf_con_imagen(self, nombre_firmante, motivo, posicion, fecha=None):
        """Firma el PDF colocando la imagen en la posición especificada"""
        if not self.doc:
            return False, "No hay documento abierto"
        
        try:
            pagina = self.doc[0]
            
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