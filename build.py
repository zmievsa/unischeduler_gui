import sys
from pathlib import Path
from unischeduler_qt import DATA_FOLDER

import PyInstaller.__main__

curpath = Path(__file__).parent
NAME = "Scheduler"
APP_PATH = curpath / "unischeduler_qt.py"

if sys.platform.startswith("win32"):
    final_dir = "Windows"
    delimeter = ";"
elif sys.platform.startswith("darwin"):
    final_dir = "OS X"
    delimeter = ":"
elif sys.platform.starstwith("linux"):
    final_dir = "Linux"
    delimeter = ":"
else:
    raise NotImplementedError("Compilation to your platform has not been implemented")

PyInstaller.__main__.run(
    [
        str(APP_PATH), "--onefile", "--noconsole", "--clean",
        f"--name={NAME}", f"--distpath={curpath}/release/{final_dir}",
        f"--add-data={DATA_FOLDER}{delimeter}data",
    ]
)
