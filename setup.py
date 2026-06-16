import sys
from cx_Freeze import setup, Executable

# Dependencias
build_exe_options = {
    "packages": ["tkinter", "fitz", "PIL", "os", "datetime", "io"],
    "include_files": ["assets/"]
}

# Base para GUI (sin terminal)
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="SimuladorFirmaDigital",
    version="1.0",
    description="Demo de firma digital en PDF",
    options={"build_exe": build_exe_options},
    executables=[Executable("app.py", base=base)]
)