import shutil
import sys
from pathlib import Path

import PyInstaller.__main__

curpath = Path(__file__).parent
NAME = "Scheduler"
APP_PATH = curpath / "src/GUI_QT.py"
APP = [str(APP_PATH)]

if sys.platform.startswith("win32"):
    extension = "exe"
    final_dir = "Windows"
elif sys.platform.startswith("darwin"):
    extension = "app"
    final_dir = "OS X"
else:
    #  No building for linux
    exit(0)

ui_data = "src/qtgui.ui;."
PyInstaller.__main__.run(
    ["--onefile", "--noconsole", "--clean", "--name=" + NAME, "--add-data=" + ui_data, str(APP_PATH)])

file_name = f"{NAME}.{extension}"
release_folder = Path(curpath / f"release/{final_dir}")
release_folder.mkdir(parents=True, exist_ok=True)
Path(curpath / f"dist/{file_name}").replace(release_folder / file_name)
shutil.rmtree(curpath / "build")
shutil.rmtree(curpath / "dist")
