import cx_Freeze
import os

base = "Win32GUI"

os.environ['TCL_LIBRARY'] = r'C:\Users\Joaquín León\AppData\Local\Programs\Python\Python36\tcl\tcl8.6'
os.environ['TK_LIBRARY'] = r'C:\Users\Joaquín León\AppData\Local\Programs\Python\Python36\tcl\tk8.6'

cx_Freeze.setup(
        name = "I Found a Strange Potion",
        version = "0.3.0",
        options = {"build_exe": {"packages": ["pygame", "libtcodpy"], "include_files": ["resources"]}},
        executables = [cx_Freeze.Executable(script = "main.py", base = base, targetName = "IFoundAStrangePotion.exe")]
        )
