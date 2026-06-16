"""
Script para crear ejecutable .exe con PyInstaller
Uso: python setup.py
"""
import PyInstaller.__main__
import os
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PYINSTALLER_ARGS = [
    os.path.join(BASE_DIR, "app.py"),
    "--name=FirmaDigitalONPECAP",
    "--onefile",
    "--windowed",
    f"--icon={os.path.join(BASE_DIR, 'assets', 'images', 'Icon11.ico')}",
    "--noconfirm",
    f"--add-data={os.path.join(BASE_DIR, 'assets', 'images', 'Icon11.ico')};assets/images",
    f"--add-data={os.path.join(BASE_DIR, 'assets', 'images', '1.png')};assets/images",
    f"--add-data={os.path.join(BASE_DIR, 'assets', 'images', 'sello_small.png')};assets/images",
    f"--add-data={os.path.join(BASE_DIR, 'assets', 'images', 'sello_base.png')};assets/images",
    f"--add-data={os.path.join(BASE_DIR, 'assets', 'fonts', 'fa-solid-900.ttf')};assets/fonts",
    f"--add-data={os.path.join(BASE_DIR, 'assets', 'icons')};assets/icons",
    "--hidden-import=PIL",
    "--hidden-import=PIL.Image",
    "--hidden-import=PIL.ImageTk",
    "--hidden-import=fitz",
]


def main():
    print("=" * 60)
    print("  GENERANDO EJECUTABLE .exe")
    print("  FirmaDigitalONPECAP")
    print("=" * 60)
    print()
    
    # Verificar archivos
    required_files = [
        "app.py", "pdf_viewer.py", "firmador.py", "modal_certificado.py",
        "assets/images/Icon11.ico", "assets/images/1.png",
        "assets/images/sello_small.png", "assets/fonts/fa-solid-900.ttf",
    ]
    
    print("Verificando archivos...")
    for f in required_files:
        path = os.path.join(BASE_DIR, f)
        if not os.path.exists(path):
            print(f"  [ERROR] Falta: {f}")
            return
        print(f"  [OK] {f}")
    
    print()
    print("Ejecutando PyInstaller...")
    print()
    
    PyInstaller.__main__.run(PYINSTALLER_ARGS)
    
    exe_path = os.path.join(BASE_DIR, "dist", "FirmaDigitalONPECAP.exe")
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print()
        print("=" * 60)
        print(f"  EJECUTABLE GENERADO:")
        print(f"  {exe_path}")
        print(f"  Tamano: {size_mb:.1f} MB")
        print("=" * 60)
        print()
        print("  OPCIONES DE DISTRIBUCION:")
        print()
        print("  1. Ejecutable simple (ya listo):")
        print("     Copia dist\\FirmaDigitalONPECAP.exe a cualquier PC Windows")
        print()
        print("  2. Instalador profesional (requiere Inno Setup):")
        print("     - Descargar: https://jrsoftware.org/isinfo.php")
        print("     - Abrir installer.iss en Inno Setup")
        print("     - Click Build > Compile")
        print("     - Resultado: installer\\FirmaDigitalONPECAP_Installer.exe")
        print()
    else:
        print()
        print("[ERROR] No se genero el ejecutable")
    
    # Limpiar
    print("Limpiando archivos temporales...")
    build_dir = os.path.join(BASE_DIR, "build")
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
        print("  [OK] build/ eliminada")
    
    spec_file = os.path.join(BASE_DIR, "FirmaDigitalONPECAP.spec")
    if os.path.exists(spec_file):
        os.remove(spec_file)
        print("  [OK] .spec eliminado")
    
    print()
    print("Listo!")


if __name__ == "__main__":
    main()
