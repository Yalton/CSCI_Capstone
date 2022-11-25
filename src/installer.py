import os 
import platform


if platform.system() == "Windows":
    print("Windows system detected; performing installation") 
    os.system("pyinstaller --onefile --windowed quadp.py")
elif platform.system() == "Linux": 
    print("Linux system detected; performing installation")
    os.system("pyinstaller --onefile quadp.py")