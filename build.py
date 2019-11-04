import shutil
import sys
from pathlib import Path
from src.util import DATA_FOLDER

import PyInstaller.__main__

curpath = Path(__file__).parent
NAME = "Scheduler"
APP_PATH = curpath / "src/GUI_QT.py"
APP = [str(APP_PATH)]

if sys.platform.startswith("win32"):
    extension = "exe"
    final_dir = "Windows"
    delimeter = ";"
elif sys.platform.startswith("darwin"):
    extension = "app"
    final_dir = "OS X"
    delimeter = ":"
else:
    #  No building for linux
    exit(0)


PyInstaller.__main__.run(
    ["--onefile", "--noconsole", "--clean", "--name=" + NAME, f"--add-data={DATA_FOLDER}{delimeter}data", str(APP_PATH)])

file_name = f"{NAME}.{extension}"
release_folder = Path(curpath / f"release/{final_dir}")
release_folder.mkdir(parents=True, exist_ok=True)
Path(curpath / f"dist/{file_name}").replace(release_folder / file_name)
shutil.rmtree(curpath / "build")
shutil.rmtree(curpath / "dist")
