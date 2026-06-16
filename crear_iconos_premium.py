"""
Generador de iconos premium usando Font Awesome
Descarga automaticamente la fuente y crea iconos de alta calidad
"""
import os
import urllib.request
from PIL import Image, ImageDraw, ImageFont


# Font Awesome - Codepoints para cada icono
ICONOS = {
    "archivo":    ("\uf07b", (200, 200, 200)),   # fa-folder-open
    "firmar":     ("\uf303", (200, 200, 200)),   # fa-pen-fancy
    "vb":         ("\uf058", (200, 200, 200)),   # fa-check-circle
    "imprimir":   ("\uf02f", (200, 200, 200)),   # fa-print
    "verificar":  ("\uf002", (200, 200, 200)),   # fa-search
    "zoom_in":    ("\uf00e", (200, 200, 200)),   # fa-search-plus
    "zoom_out":   ("\uf010", (200, 200, 200)),   # fa-search-minus
    "ajustar":    ("\uf31e", (200, 200, 200)),   # fa-expand-arrows-alt
}


def download_fontawesome():
    """Descarga Font Awesome Free si no existe"""
    font_dir = os.path.join(os.path.dirname(__file__), "assets", "fonts")
    font_path = os.path.join(font_dir, "fa-solid-900.ttf")
    
    if os.path.exists(font_path):
        print(f"  Font ya existe: {font_path}")
        return font_path
    
    os.makedirs(font_dir, exist_ok=True)
    
    urls = [
        "https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@5.15.4/webfonts/fa-solid-900.ttf",
        "https://raw.githubusercontent.com/FortAwesome/Font-Awesome/5.x/webfonts/fa-solid-900.ttf",
    ]
    
    print("  Descargando Font Awesome...")
    for url in urls:
        try:
            print(f"  Intentando: {url[:60]}...")
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=30) as response:
                with open(font_path, 'wb') as f:
                    f.write(response.read())
            print(f"  OK: {font_path}")
            return font_path
        except Exception as e:
            print(f"  Error: {e}")
            continue
    
    print("  No se pudo descargar automaticamente")
    print("  Descarga manual desde: https://fontawesome.com/download")
    print(f"  Copia fa-solid-900.ttf a: {font_path}")
    return None


def crear_iconos_premium(size=48):
    """Crea iconos premium de alta calidad usando Font Awesome"""
    font_path = download_fontawesome()
    
    if not font_path or not os.path.exists(font_path):
        print("  No se encontro la fuente Font Awesome")
        return False
    
    icon_dir = os.path.join(os.path.dirname(__file__), "assets", "icons")
    os.makedirs(icon_dir, exist_ok=True)
    
    font_large = ImageFont.truetype(font_path, int(size * 0.55))
    
    print(f"  Generando iconos {size}x{size}...")
    
    for nombre, (codepoint, color) in ICONOS.items():
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        cx, cy = size // 2, size // 2
        radius = size // 2 - 2
        
        # Circulo de fondo
        for r in range(radius, 0, -1):
            alpha = int(255 * (r / radius) * 0.3)
            draw.ellipse([cx-r, cy-r, cx+r, cy+r],
                        fill=(50, 50, 50, 255 - alpha))
        
        draw.ellipse([cx-radius, cy-radius, cx+radius, cy+radius],
                    outline=(100, 100, 100, 200), width=2)
        
        # Icono Font Awesome
        bbox = draw.textbbox((0, 0), codepoint, font=font_large)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        tx = cx - tw // 2
        ty = cy - th // 2 - bbox[1]
        
        draw.text((tx, ty), codepoint, fill=color + (255,), font=font_large)
        
        img.save(os.path.join(icon_dir, f"{nombre}.png"))
    
    print("  Iconos premium generados!")
    return True


if __name__ == "__main__":
    print("=== Generador de Iconos Premium ===\n")
    crear_iconos_premium(size=48)
    print("\nListo!")
