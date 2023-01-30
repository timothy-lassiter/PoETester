import distutils
import sys

from cx_Freeze import Executable, setup

from app import APP_NAME

app_name = APP_NAME


description = "My PySide App!"
author = "John Doe"
icon = "./icons/icon.ico"
# Generate a unique upgrade code by running the below command in Python
# str(uuid.uuid3(uuid.NAMESPACE_DNS, "myapp.example.com")).upper()
# https://learn.microsoft.com/en-us/windows/win32/msi/using-an-upgradecode
upgrade_code = ""
# Start Menu Folder
start_folder = ""


base = "Win32GUI" if sys.platform == "win32" else None
install_dir = (
    "ProgramFiles64Folder"
    if distutils.util.get_platform() == "win-amd64"
    else "ProgramFilesFolder"
)


build_exe_options = {
    "zip_include_packages": ["encoder", "PySide6"],
    "include_msvcr": True,
    "excludes": [
        "tkinter",
        "wheel",
        "setuptools",
        "setuptools_scm",
        "email",
        "unittest",
        "html",
        "http",
        "xml",
    ],
}

# Used to create the start menu folder
# https://learn.microsoft.com/en-us/windows/win32/msi/directory-table
directory_table = [
    ("ProgramMenuFolder", "TARGETDIR", "."),
    ("ProgramMenuSubFolder", "ProgramMenuFolder", start_folder or "."),
]

msi_data = {"Directory": directory_table}

bdist_msi_options = {
    "data": msi_data,
    "upgrade_code": f"{{{upgrade_code}}}" if upgrade_code else None,
    "summary_data": {"author": author},
    "initial_target_dir": f"[{install_dir}]{app_name}",
    "install_icon": icon,
}

executable = Executable(
    script="main.py",
    base=base,
    target_name=app_name,
    icon=icon,
    shortcut_name=app_name,
    shortcut_dir="ProgramMenuSubFolder",
)

setup(
    name=app_name,
    description=description,
    options={
        "build_exe": build_exe_options,
        "bdist_msi": bdist_msi_options,
    },
    executables=[executable],
    use_scm_version={"write_to": "app/_version.py"},
    setup_requires=["setuptools_scm"],
)
