import shutil
import sys
from pathlib import Path
from unittest.mock import patch

setup_requires = []

curpath = Path(__file__).parent
NAME = "Scheduler"
APP_PATH = curpath / "src/GUI_QT.py"
APP = [str(APP_PATH)]
if sys.platform.startswith("win32"):
    import PyInstaller.__main__
    extension = "exe"
    final_dir = "Windows"
    new_app_path = Path(curpath / "src/GUI.pyw")
    APP_PATH.rename(new_app_path)
    PyInstaller.__main__.run(
        ["-n", NAME, "--onefile", "--clean", str(new_app_path)])
    new_app_path.rename(APP_PATH)
    Path(curpath / f"{NAME}.spec").unlink()
elif sys.platform.startswith("darwin"):
    from setuptools import setup
    extension = "app"
    final_dir = "OS X"
    with patch('sys.argv', ["setup.py", "py2app"]):
        setup(
            name=NAME,
            app=APP,
            data_files=[],
            options={"py2app": {}},
            setup_requires=setup_requires
        )
else:
    #  No building for linux
    exit(0)

file_name = f"{NAME}.{extension}"
release_folder = Path(curpath / f"release/{final_dir}")
release_folder.mkdir(parents=True, exist_ok=True)
Path(curpath / f"dist/{file_name}").replace(release_folder / file_name)
shutil.rmtree(curpath / "build")
shutil.rmtree(curpath / "dist")
