"""
Generador de sellos de firma digital
Regenera las imagenes sello_base.png y sello_small.png
"""
from PIL import Image, ImageDraw, ImageFont
import os


def crear_sello_base():
    """Crea la imagen base del sello para la firma usando el logo real"""
    img_width = 720
    img_height = 140
    img = Image.new('RGBA', (img_width, img_height), (255, 255, 255, 255))
    
    # Cargar el logo real
    logo_path = os.path.join(os.path.dirname(__file__), "assets", "images", "1.png")
    try:
        logo = Image.open(logo_path)
        logo_height = 110
        logo_ratio = logo.width / logo.height
        logo_width = int(logo_height * logo_ratio)
        logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
        logo_y = (img_height - logo_height) // 2
        img.paste(logo, (10, logo_y), logo if logo.mode == 'RGBA' else None)
    except Exception as e:
        print(f"Error cargando logo: {e}")
        draw = ImageDraw.Draw(img)
        draw.rectangle([10, 10, 130, 130], outline=(150, 50, 50), width=2)
        draw.text((30, 60), "LOGO", fill=(150, 50, 50))
    
    draw = ImageDraw.Draw(img)
    try:
        font_normal = ImageFont.truetype("arial.ttf", 11)
        font_name = ImageFont.truetype("arial.ttf", 13)
    except:
        font_normal = ImageFont.load_default()
        font_name = ImageFont.load_default()
    
    text_x = 280
    y_offset = 20
    draw.line([text_x - 15, 15, text_x - 15, 125], fill=(180, 180, 180), width=1)
    
    nombre_firmante = "VILLEGAS AGUIRRE Delmi Oscar"
    fecha = "16.06.2026 13:03:21 -05:00"
    
    draw.text((text_x, y_offset), "Firmado digitalmente por", fill=(100, 100, 100), font=font_normal)
    draw.text((text_x, y_offset + 18), nombre_firmante, fill=(50, 50, 50), font=font_name)
    draw.text((text_x, y_offset + 38), "FAU 20568198272 soft", fill=(100, 100, 100), font=font_normal)
    draw.text((text_x, y_offset + 56), "Motivo: Soy el autor del documento", fill=(100, 100, 100), font=font_normal)
    draw.text((text_x, y_offset + 74), f"Fecha: {fecha}", fill=(100, 100, 100), font=font_normal)
    
    os.makedirs("assets/images", exist_ok=True)
    
    img.save("assets/images/sello_base.png")
    print("[OK] Sello base creado en assets/images/sello_base.png")
    
    preview_width = 400
    preview_height = int(img_height * (preview_width / img_width))
    img_small = img.resize((preview_width, preview_height), Image.Resampling.LANCZOS)
    img_small.save("assets/images/sello_small.png")
    print("[OK] Sello pequeno creado en assets/images/sello_small.png")


if __name__ == "__main__":
    print("Generando sellos de firma...")
    crear_sello_base()
    print("Listo!")
