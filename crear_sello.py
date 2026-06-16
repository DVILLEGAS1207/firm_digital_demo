from PIL import Image, ImageDraw, ImageFont
import os

def crear_sello_base():
    """Crea la imagen base del sello para la firma"""
    # Crear imagen con fondo blanco y borde
    img = Image.new('RGBA', (350, 180), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 12)
        font_bold = ImageFont.truetype("arial.ttf", 14)
        font_small = ImageFont.truetype("arial.ttf", 10)
    except:
        font = ImageFont.load_default()
        font_bold = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Marco del sello
    draw.rectangle([5, 5, 345, 175], outline=(0, 0, 139), width=2)
    draw.rectangle([10, 10, 340, 170], outline=(0, 0, 139), width=1)
    
    # Círculo con "SELLO"
    draw.ellipse([20, 20, 120, 120], outline=(0, 0, 139), width=2)
    draw.text((45, 55), "SELLO", fill=(0, 0, 139), font=font_bold)
    draw.text((48, 75), "DIGITAL", fill=(0, 0, 139), font=font_bold)
    
    # Línea de firma
    draw.line([140, 50, 330, 50], fill=(0, 0, 0), width=1)
    draw.text((145, 58), "Firmado digitalmente por", fill=(0, 0, 0), font=font)
    
    # Nombre del firmante (placeholder)
    draw.text((145, 75), "VILLEGAS AGUIRRE Delmi Oscar", fill=(0, 0, 0), font=font_bold)
    draw.text((145, 92), "FAU 20568198272 soft", fill=(80, 80, 80), font=font_small)
    
    # Motivo
    draw.text((145, 108), "Motivo: Soy el autor del documento", fill=(80, 80, 80), font=font_small)
    
    # Fecha
    draw.text((145, 124), "Fecha: 16.06.2026 13:03:21 -05:00", fill=(80, 80, 80), font=font_small)
    
    # "Firma Digital" en la parte inferior derecha
    draw.text((260, 150), "Firma Digital", fill=(0, 0, 139), font=font_bold)
    
    # Crear directorio
    os.makedirs("assets/images", exist_ok=True)
    
    # Guardar
    img.save("assets/images/sello_base.png")
    print("✅ Sello base creado en assets/images/sello_base.png")
    
    # También crear una versión más pequeña para el arrastre
    img_small = img.resize((175, 90), Image.Resampling.LANCZOS)
    img_small.save("assets/images/sello_small.png")
    print("✅ Sello pequeño creado en assets/images/sello_small.png")

if __name__ == "__main__":
    crear_sello_base()