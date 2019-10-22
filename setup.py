import shutil
import sys
from pathlib import Path

import pip
from setuptools import setup

setup_requires = ["icalendar", "bs4", "requests", "py2app", "pyinstaller"]
if hasattr(pip, 'main'):
    pip_main = pip.main
else:
    pip_main = pip._internal.main
pip_main(['install', "--user"] + setup_requires)
setup_requires = []

curpath = Path(__file__).parent
NAME = "Scheduler"
APP = [curpath / "src/GUI.py"]
if sys.platform.startswith("win32"):
    import PyInstaller.__main__
    extension = "exe"
    final_dir = "Windows"
    app_path = Path(APP[0])
    new_app_path = Path(curpath / "src/GUI.pyw")
    app_path.rename(new_app_path)
    PyInstaller.__main__.run(
        ["-n", NAME, "--onefile", "--clean", str(new_app_path)])
    new_app_path.rename(app_path)
    Path(curpath / f"{NAME}.spec").unlink()
elif sys.platform.startswith("darwin"):
    # Supply py2app CLI arg when on OS X
    extension = "app"
    final_dir = "OS X"
    setup(
        name=NAME,
        app=APP,
        data_files=[],
        options={"py2app": {}},
        setup_requires=setup_requires
    )

file_name = f"{NAME}.{extension}"
release_folder = Path(curpath / f"release/{final_dir}")
release_folder.mkdir(parents=True, exist_ok=True)
Path(curpath / f"dist/{file_name}").replace(release_folder / file_name)
shutil.rmtree(curpath / "build")
shutil.rmtree(curpath / "dist")
