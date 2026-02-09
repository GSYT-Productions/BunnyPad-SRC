#!/usr/bin/env python3
# v11-PyQt5.py - PyQt5 variant
r"""
 ____                          ____           _ 
| __ ) _   _ _ __  _ __  _   _|  _ \ __ _  __| |
|  _ \| | | | '_ \| '_ \| | | | |_) / _` |/ _` |
| |_) | |_| | | | | | | | |_| |  __/ (_| | (_| |
|____/ \__,_|_| |_|_| |_|\__, |_|   \__,_|\__,_|
                         |___/                  
"""

import datetime, importlib, os, platform, subprocess, sys, textwrap, unicodedata, webbrowser, random, json, shutil, binascii

from pathlib import Path

# Optional third-party libraries
try:
    import distro
except Exception:
    distro = None

try:
    import requests
except Exception:
    requests = None

try:
    from fpdf import FPDF
except Exception:
    FPDF = None

# PyQt5 imports
try:
    from PyQt5.QtCore import (
        QCoreApplication,
        QFile,
        QPoint,
        QSize,
        Qt,
        QTextStream,
        QThread,
		QTimer
    )
    from PyQt5.QtCore import pyqtSignal as Signal
    from PyQt5.QtCore import pyqtSlot as Slot
    from PyQt5.QtGui import (
        QColor,
        QFont,
        QFontMetrics,
        QGuiApplication,
        QIcon,
        QPainter,
        QPixmap,
        QTextCursor,
        QTextDocument,
        QFontDatabase,
        QMouseEvent,
        QPaintEvent,
    )
    from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
    from PyQt5.QtWidgets import (
        QAction,
        QApplication,
        QCheckBox,
        QDialog,
        QDockWidget,
        QFileDialog,
        QFontDialog,
        QGridLayout,
        QInputDialog,
        QLabel,
        QLCDNumber,
        QMainWindow,
        QMenu,
        QMenuBar,
        QMessageBox,
        QProgressBar,
        QPushButton,
        QStatusBar,
        QTextEdit,
        QToolBar,
        QToolTip,
        QVBoxLayout,
        QWidget,
        QGroupBox,
        QFormLayout,
        QComboBox,
        QSpinBox,
        QLineEdit,
        QHBoxLayout,
        QSizePolicy,
        QSplitter,
        QBoxLayout
    )

except ImportError as e:
    print(f"Missing required dependency: {e}")
    print("Attempting to install dependencies...")
    
    
    def is_module_available(module_name):
        """Check if a module is available before importing."""
        return importlib.util.find_spec(module_name) is not None

    
    def is_debian_based():
        """Determine if the OS is Debian-based securely."""
        if is_module_available("distro"):
            import distro
            return distro.id().lower() in [
                "debian", "ubuntu", "linuxmint", "pop", "elementary", 
                "kali", "raspbian"
            ]
        return False

    
    def install_with_pip(pip_cmd):
        """
        Install required Python packages using the provided pip command.
        
        This runs the given pip executable (e.g. "pip", "pip3", or a virtualenv pip path) with
        --no-cache-dir to install a fixed set of runtime dependencies required by the application.
        On installation failure the process will print an error and terminate the interpreter.
        
        Parameters:
            pip_cmd (str): The pip executable or command to invoke.
        
        Side effects:
            Exits the process with status code 1 if installation fails.
        """
        try:
            subprocess.run([
                pip_cmd, "install", "--no-cache-dir",
                "PyQt5", "distro", "fpdf", "setuptools", "requests"
            ], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to install dependencies: {e}")
            sys.exit(1)

    
    def create_venv(venv_dir):
        """Create a virtual environment if it does not already exist."""
        if not os.path.exists(venv_dir):
            print(f"Creating virtual environment at {venv_dir}...")
            try:
                subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)
                return True
            except subprocess.CalledProcessError:
                print("Error: Failed to create virtual environment.")
                return False
        return True

    # Virtual environment directory
    venv_dir = os.path.join(os.getcwd(), "venv")
    venv_pip = (
        os.path.join(venv_dir, "bin", "pip")
        if platform.system() != "Windows"
        else os.path.join(venv_dir, "Scripts", "pip.exe")
    )
    
    # Check if we are already in a virtual environment
    if hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    ):
        print("Virtual environment detected. Installing dependencies...")
        install_with_pip(
            os.path.join(sys.prefix, "bin", "pip")
            if platform.system() != "Windows"
            else os.path.join(sys.prefix, "Scripts", "pip.exe")
        )
    # On Debian-based systems, prefer pipx, but fall back to venv if needed
    elif is_debian_based():
        if shutil.which("pipx"):
            print("Using pipx to install dependencies...")
            try:
                subprocess.run([
                    "pipx", "install", "PyQt5", "distro", "fpdf", 
                     "setuptools", "requests"
                ], check=True)
            except subprocess.CalledProcessError:
                print("Warning: pipx installation failed. Attempting venv...")
                if create_venv(venv_dir):
                    install_with_pip(venv_pip)
                else:
                    print("Error: Neither pipx nor venv is available.")
                    sys.exit(1)
        else:
            print("Warning: pipx is not installed. Attempting venv...")
            if create_venv(venv_dir):
                install_with_pip(venv_pip)
            else:
                print("Error: Neither pipx nor venv is available.")
                sys.exit(1)
    # On other Linux distros and Windows, use venv if not already present
    else:
        if create_venv(venv_dir):
            print("Using virtual environment's pip.")
            install_with_pip(venv_pip)
        else:
            print("Error: Failed to create virtual environment.")
            sys.exit(1)


# -----------------------------
# App metadata
# -----------------------------

CURRENT_VERSION = "v11.1.27935.0209"
APP_NAME = "BunnyPad"
ORGANIZATION_NAME = "GSYT Productions"
VERSION_CODENAME = "Bun Valley (FPL 1)"
REPO_OWNER = "GSYT-Productions"
REPO_NAME = "BunnyPad-SRC"

# -----------------------------
# Platform detection
# -----------------------------

IS_ANDROID = sys.platform == "android"

# -----------------------------
# Temp / state files
# -----------------------------

BUNNYPAD_TEMP = Path(os.path.expanduser("~")) / "BunnyPadTemp"
BUNNYPAD_TEMP.mkdir(parents=True, exist_ok=True)
os.makedirs(BUNNYPAD_TEMP, exist_ok=True)

STATE_FILE = os.path.join(BUNNYPAD_TEMP, "state.json")
DIRTY_FILE = os.path.join(BUNNYPAD_TEMP, "dirty")

# -----------------------------
# Detect platform
# -----------------------------
IS_ANDROID = sys.platform.startswith("android")  # simple flag for Android


# -----------------------------
# Base directories
# -----------------------------
def get_writable_base_dir() -> Path:
    """
    Returns a directory suitable for writing app data.
    On Android, uses Qt's AppDataLocation.
    On desktop, uses ~/.bunnypad
    """
    if IS_ANDROID:
        path = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
        return Path(path)
    return Path.home() / ".bunnypad"


APP_BASE_DIR = get_writable_base_dir()
ASSETS_BASE_DIR = APP_BASE_DIR / "assets"


# -----------------------------
# Asset source location
# -----------------------------
def get_asset_source_root() -> Path:
    """
    Returns the root directory of bundled assets.
    Handles Android (Qt resources), PyInstaller, and normal Python execution.
    """
    if IS_ANDROID:
        return Path(":/assets")  # Qt resource prefix

    if getattr(sys, "frozen", False):
        # PyInstaller bundle
        return Path(sys.executable).parent / "assets"

    # Normal Python execution
    return Path(__file__).parent.resolve() / "assets"


# -----------------------------
# Runtime asset extraction
# -----------------------------

def copy_qt_resource_tree(qt_prefix: str, target_dir: Path):
    """
    Recursively copies Qt resource tree to a writable target directory.
    """
    target_dir.mkdir(parents=True, exist_ok=True)
    qdir = QDir(qt_prefix)

    for entry in qdir.entryList(QDir.AllEntries | QDir.NoDotAndDotDot):
        src = f"{qt_prefix}/{entry}"
        dst = target_dir / entry

        if QFile(src).exists():
            if not dst.exists():
                QFile.copy(src, str(dst))
        else:
            copy_qt_resource_tree(src, dst)


def ensure_assets_available():
    """
    Ensure that the assets directory exists and is populated.
    Copies assets from source if necessary.
    """
    if ASSETS_BASE_DIR.exists() and any(ASSETS_BASE_DIR.iterdir()):
        return  # Already exists and not empty

    src = get_asset_source_root()
    ASSETS_BASE_DIR.mkdir(parents=True, exist_ok=True)

    if IS_ANDROID:
        copy_qt_resource_tree(str(src), ASSETS_BASE_DIR)
    else:
        if src.exists() and src.is_dir():
            shutil.copytree(src, ASSETS_BASE_DIR, dirs_exist_ok=True)

from PyQt6.QtGui import QTextCursor
QTextCursorEnd = QTextCursor.MoveOperation.End


# -----------------------------
# Asset paths
# -----------------------------

ASSETS_DIR = ASSETS_BASE_DIR
IMAGES_DIR = ASSETS_DIR / "images" / "icons"
BRANDING_DIR = ASSETS_DIR / "images" / "branding"
QSS_DIR = ASSETS_DIR / "qss"

# Use a small helper to reduce repetition
def asset_path(*parts: str) -> str:
    return str(Path(*parts))

ICON_PATHS = {
    "bunnypad": asset_path(BRANDING_DIR, "bunnypad.png"),
    "gsyt": asset_path(BRANDING_DIR, "gsyt.png"),
    "bpdl": asset_path(BRANDING_DIR, "bpdl.png"),
    "new": asset_path(IMAGES_DIR, "new.png"),
    "open": asset_path(IMAGES_DIR, "open.png"),
    "save": asset_path(IMAGES_DIR, "save.png"),
    "saveas": asset_path(IMAGES_DIR, "saveas.png"),
    "exit": asset_path(IMAGES_DIR, "exit.png"),
    "undo": asset_path(IMAGES_DIR, "undo.png"),
    "redo": asset_path(IMAGES_DIR, "redo.png"),
    "cut": asset_path(IMAGES_DIR, "cut.png"),
    "copy": asset_path(IMAGES_DIR, "copy.png"),
    "paste": asset_path(IMAGES_DIR, "paste.png"),
    "delete": asset_path(IMAGES_DIR, "delete.png"),
    "datetime": asset_path(IMAGES_DIR, "datetime.png"),
    "charmap": asset_path(IMAGES_DIR, "charmap.png"),
    "find": asset_path(IMAGES_DIR, "find.png"),
    "replace": asset_path(IMAGES_DIR, "replace.png"),
    "selectall": asset_path(IMAGES_DIR, "selectall.png"),
    "wordwrap": asset_path(IMAGES_DIR, "wordwrap.png"),
    "font": asset_path(IMAGES_DIR, "font.png"),
    "info": asset_path(IMAGES_DIR, "info.png"),
    "team": asset_path(IMAGES_DIR, "team.png"),
    "cake": asset_path(IMAGES_DIR, "cake.png"),
    "nocake": asset_path(IMAGES_DIR, "nocake.png"),
    "support": asset_path(IMAGES_DIR, "support.png"),
    "share": asset_path(IMAGES_DIR, "share.png"),
    "update": asset_path(IMAGES_DIR, "update.png"),
    "pdf": asset_path(IMAGES_DIR, "pdf.png"),
    "printer": asset_path(IMAGES_DIR, "printer.png"),
    "encryption": asset_path(IMAGES_DIR, "encryption.png"),
    "status": asset_path(IMAGES_DIR, "status.png"),
    "toolbar": asset_path(IMAGES_DIR, "toolbar.png"),
}

# -----------------------------
# Initialize assets at startup
# -----------------------------
ensure_assets_available()

# -----------------------------
# File filters
# -----------------------------

FILE_FILTERS = {
    "open": (
        "Text Files (*.txt);;Log Files (*.log);;Info files (*.nfo);;"
        "Batch files (*.bat);;Windows Command Script files (*.cmd);;"
        "VirtualBasicScript files (*.vbs);;JSON files (*.json);;"
        "Python Source files (*.py);;All Supported File Types "
        "(*.txt *.log *.nfo *.bat *.cmd *.vbs *.json *.py);;All Files (*.*)"
    ),
    "save": (
        "Text Files (*.txt);;Log Files (*.log);;Info files (*.nfo);;"
        "Batch files (*.bat);;Windows Command Script files (*.cmd);;"
        "VirtualBasicScript files (*.vbs);;JSON files (*.json);;All Files (*.*)"
    ),
    "pdf": "PDF File (*.pdf)",
}

CHAR_MAP_DEFAULT_COLUMNS = 16
CHAR_MAP_MIN_FONT_SIZE = 24

# -----------------------------
# Utilities
# -----------------------------

def safe_subprocess_run(cmd, shell=False, capture_output=True, text=True, timeout=10):
    """Run subprocess safely and return CompletedProcess or None."""
    try:
        if capture_output:
            return subprocess.run(
                cmd,
                shell=shell,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=text,
                timeout=timeout,
                check=False,
            )
        return subprocess.run(
            cmd,
            shell=shell,
            universal_newlines=text,
            timeout=timeout,
            check=False,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return None

def get_icon_path(icon_name: str) -> str:
    """Resolve icon path robustly."""
    key = icon_name.replace(".png", "")
    path = ICON_PATHS.get(key)
    if path and Path(path).exists():
        return path

    candidate = IMAGES_DIR / f"{key}.png"
    if candidate.exists():
        return str(candidate)

    candidate_upper = IMAGES_DIR / f"{key}.PNG"
    if candidate_upper.exists():
        return str(candidate_upper)

    return ""

def load_stylesheet() -> str:
    path = QSS_DIR / "stylesheet.qss"
    if not path.exists():
        return ""

    f = QFile(str(path))
    if not f.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
        return ""

    stream = QTextStream(f)
    content = stream.readAll()
    f.close()
    return content

def save_as_pdf(text: str, file_path: str) -> bool:
    """Save text as PDF using fpdf (if available)."""
    if FPDF is None:
        return False
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        for line in textwrap.wrap(text, width=180):
            pdf.multi_cell(0, 6, txt=line)
        pdf.output(file_path)
        return True
    except Exception:
        return False

def get_real_windows_build() -> tuple:
    """Get real Windows build numbers using RtlGetNtVersionNumbers (anti-spoofing)."""
    try:
        if platform.system() != "Windows":
            return None, None, None
            
        import ctypes
        from ctypes import wintypes
        
        # Load ntdll.dll
        ntdll = ctypes.WinDLL('ntdll.dll')
        
        # Define the function prototype
        RtlGetNtVersionNumbers = ntdll.RtlGetNtVersionNumbers
        RtlGetNtVersionNumbers.argtypes = [
            ctypes.POINTER(wintypes.DWORD),  # MajorVersion
            ctypes.POINTER(wintypes.DWORD),  # MinorVersion
            ctypes.POINTER(wintypes.DWORD)   # BuildNumber
        ]
        RtlGetNtVersionNumbers.restype = None
        
        # Create variables to hold the results
        major = wintypes.DWORD()
        minor = wintypes.DWORD()
        build = wintypes.DWORD()
        
        # Call the function
        RtlGetNtVersionNumbers(
            ctypes.byref(major),
            ctypes.byref(minor),
            ctypes.byref(build)
        )
        
        # Extract the real build number (remove the high bits)
        real_build = build.value & ~0xF0000000
        
        return major.value, minor.value, real_build
        
    except Exception as e:
        return None, None, None

def get_windows_edition_real() -> str:
    """Get Windows edition using multiple methods for anti-spoofing."""
    try:
        if platform.system() != "Windows":
            return None
            
        import winreg
        
        # Method 1: Try to get from registry with anti-spoofing checks
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")
            
            # Get multiple registry values for validation
            product_name = winreg.QueryValueEx(key, "ProductName")[0]
            edition_id = winreg.QueryValueEx(key, "EditionID")[0]
            installation_type = winreg.QueryValueEx(key, "InstallationType")[0]
            
            winreg.CloseKey(key)
            
            # Combine information for better identification
            if edition_id and edition_id != "Core":
                return f"{product_name} ({edition_id})"
            else:
                return product_name
                
        except Exception:
            pass
        
        # Method 2: Try platform module as fallback
        try:
            if hasattr(platform, "win32_edition"):
                return platform.win32_edition()
        except Exception:
            pass
            
        return None
        
    except Exception as e:
        return None

def identify_os() -> str:
    """Return readable OS description with fallbacks."""
    try:
        os_name = platform.system()
        
        if os_name == "Linux":
            try:
                if distro:
                    linux_name = distro.name(pretty=True)
                    linux_ver = distro.version(pretty=True)
                else:
                    linux_name = platform.platform()
                    linux_ver = ""
                return f"Linux {linux_name} {linux_ver} - Kernel: {platform.release()}"
            except Exception:
                return f"Linux - Kernel: {platform.release()}"
                
        elif os_name == "Darwin":
            try:
                mac_version = platform.mac_ver()[0] or "Unknown"
                platform_chip = "Apple Silicon" if platform.machine().startswith("arm") else "Intel"
                return f"macOS {mac_version} - Chip: {platform_chip}"
            except Exception:
                return f"macOS - Chip: {platform.machine()}"

        elif os_name == "Windows":
            win_release = platform.release()
            win_build = platform.version()
            edition = None
            try:
                if hasattr(platform, "win32_edition"):
                    edition = platform.win32_edition()
            except Exception:
                edition = None
            # Try to get edition from registry if platform method fails
            if not edition:
                try:
                    import winreg
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")
                    edition = winreg.QueryValueEx(key, "ProductName")[0]
                    winreg.CloseKey(key)
                except Exception:
                    edition = None
            if edition:
                return f"Windows {win_release} ({edition}) [Build {win_build}]"
            return f"Windows {win_release} [Build {win_build}]"
                
        return f"Unknown Operating System ({os_name})"
        
    except Exception:
        return "Unknown Operating System"

def get_cpu_model() -> str:
    """Get CPU model name with several fallbacks."""
    try:
        # Try platform module first (fastest)
        cpu = platform.processor()
        if cpu and cpu.strip():
            return cpu.strip()
        
        uname_proc = platform.uname().processor
        if uname_proc and uname_proc.strip():
            return uname_proc.strip()
        
        # Only try subprocess commands if platform methods fail
        if platform.system() == "Windows":
            # Use a faster alternative to wmic
            try:
                import winreg
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
                cpu_name = winreg.QueryValueEx(key, "ProcessorNameString")[0]
                winreg.CloseKey(key)
                if cpu_name and cpu_name.strip():
                    return cpu_name.strip()
            except Exception:
                pass
            
            # Fallback to wmic with shorter timeout
            res = safe_subprocess_run(["wmic", "cpu", "get", "name"], shell=True, timeout=5)
            if res and res.stdout:
                lines = [l.strip() for l in res.stdout.splitlines() if l.strip()]
                if len(lines) > 1:
                    return lines[1]
        else:
            # Linux/Unix - try lscpu with shorter timeout
            res = safe_subprocess_run(["lscpu"], shell=True, timeout=5)
            if res and res.stdout:
                for ln in res.stdout.splitlines():
                    if ln.lower().startswith("model name:"):
                        return ln.split(":", 1)[1].strip()
        
        return "Unknown CPU"
    except Exception:
        return "Unknown CPU"

def get_gpu_info() -> str:
    """Get GPU info with fallbacks (best-effort)."""
    try:
        if platform.system() == "Windows":
            # Try registry first (faster than wmic)
            try:
                import winreg
                gpu_names = []
                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}")
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            subkey = winreg.OpenKey(key, subkey_name)
                            try:
                                gpu_name = winreg.QueryValueEx(subkey, "Device Description")[0]
                                if gpu_name and gpu_name.strip():
                                    gpu_names.append(gpu_name.strip())
                            except Exception:
                                pass
                            winreg.CloseKey(subkey)
                        except Exception:
                            continue
                    winreg.CloseKey(key)
                    if gpu_names:
                        return ", ".join(gpu_names)
                except Exception:
                    pass
            except Exception:
                pass
            
            # Fallback to wmic with shorter timeout
            res = safe_subprocess_run(["wmic", "path", "Win32_VideoController", "get", "Name"], shell=True, timeout=5)
            if res and res.stdout:
                names = [l.strip() for l in res.stdout.splitlines() if l.strip() and "Name" not in l]
                if names:
                    return ", ".join(names)
            return "Not available"
        else:
            # Linux/Unix - try faster alternatives first
            try:
                # Try reading from /proc/cpuinfo first (fastest)
                with open("/proc/cpuinfo", "r") as f:
                    for line in f:
                        if line.startswith("model name"):
                            return line.split(":", 1)[1].strip()
            except Exception:
                pass
            
            # Fallback to subprocess commands with shorter timeout
            res = safe_subprocess_run(["lshw", "-C", "display"], shell=True, timeout=5)
            if res and res.stdout:
                for ln in res.stdout.splitlines():
                    if "product:" in ln.lower():
                        return ln.split(":", 1)[1].strip()
            
            res = safe_subprocess_run(["lspci"], shell=True, timeout=5)
            if res and res.stdout:
                for ln in res.stdout.splitlines():
                    if "vga" in ln.lower() or "3d controller" in ln.lower():
                        return ln.split(":")[-1].strip()
            return "Not available"
    except Exception:
        return "Not available"


def get_total_ram() -> str:
    """Return total RAM in GB as a string, or 'Unknown' if unavailable."""
    try:
        system = platform.system()
        if system == "Linux":
            # Try reading /proc/meminfo
            with open("/proc/meminfo", "r") as f:
                for line in f:
                    if line.startswith("MemTotal:"):
                        # Value is in kB
                        kb = int(line.split()[1])
                        gb = kb / (1024**2)
                        return f"{gb:.2f} GB"
        elif system == "Windows":
            # Use ctypes to query memory
            import ctypes

            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [
                    ("dwLength", ctypes.c_ulong),
                    ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
                ]

            mem_status = MEMORYSTATUSEX()
            mem_status.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(mem_status))
            gb = mem_status.ullTotalPhys / (1024**3)
            return f"{gb:.2f} GB"
        else:
            return "Unknown"
    except Exception:
        return "Unknown"

def get_system_info() -> str:
    """Return assembled system info string, cross-platform and without psutil."""
    try:
        parts = []
        parts.append(f"OS: {platform.system()} {platform.release()}")
        parts.append(f"CPU: {platform.processor() or 'Unknown'}")
        parts.append(f"RAM: {get_total_ram()}")
        parts.append(f"GPU: {get_gpu_info() if 'get_gpu_info' in globals() else 'Unknown'}")
        try:
            total, used, free = shutil.disk_usage(os.path.abspath(os.sep))
            parts.append(f"Disk: {total // (2**30)} GB total, {free // (2**30)} GB free")
        except Exception:
            parts.append("Disk: Unknown")
        try:
            screen = QGuiApplication.primaryScreen()
            if screen:
                rect = screen.geometry()
                parts.append(f"Screen Resolution: {rect.width()}x{rect.height()}")
        except Exception:
            parts.append("Screen Resolution: Unknown")
        return "\n".join(parts)
    except Exception:
        return "System information not available"

class CharacterWidget(QWidget):
    characterSelected = Signal(str)
    closed = Signal()

    def __init__(self, parent=None, as_window=False):
        flags = Qt.WindowType.Window if as_window else Qt.WindowType.Widget
        super().__init__(parent, flags)

        self._as_window = as_window
        self._disabled = True  # The key flag

        if self._as_window:
            self.setObjectName("FloatingWindow")
            QMessageBox.information(
                self,
                "Feature Disabled",
                "The character map feature is disabled due to an upcoming migration."
            )

        # Ensure the widget has a reasonable default size
        self.display_font = QFont()
        self.square_size = 32
        self.columns = 8
        self.total_characters = 256

        # Hide physical interaction
        self.setEnabled(False)

    #
    # === EVENT OVERRIDES (all interaction suppressed) ===
    #

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._disabled:
            return

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if self._disabled:
            return

    def closeEvent(self, event):
        self.closed.emit()
        super().closeEvent(event)

    #
    # === DISABLED PAINT EVENT ===
    #
    def paintEvent(self, event: QPaintEvent) -> None:
        """
        Draw a centered 'feature disabled' message.
        No grid, no characters, no expensive rendering.
        """
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(50, 50, 50))

        painter.setPen(QColor("white"))
        font = QFont(self.display_font)
        font.setPointSize(14)
        font.setBold(True)
        painter.setFont(font)

        msg = """Character Map Feature Disabled

BunnyPad is undergoing some major changes.
As part of these changes, certain functions will be disabled
as part of an upcoming migration."""

        fm = QFontMetrics(font)

        tw = fm.horizontalAdvance(msg)
        th = fm.height()

        x = (self.width() - tw) // 2
        y = (self.height() - th) // 2 + fm.ascent()
        from PyQt6.QtGui import QTextOption
        painter.drawText(
            self.rect(),
            Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap,
            msg
        )


    #
    # === BASIC SIZING (matches original layout expectations) ===
    #
    def sizeHint(self) -> QSize:
        return QSize(self.columns * self.square_size,
                     (self.total_characters // self.columns) * self.square_size)

    #
    # === API-COMPAT SHIMS ===GetModuleHandle(L"ntdlx.dll") != NULL
    #

    def setColumns(self, columns: int):
        """Keep signature intact for compatibility."""
        pass

    def set_unicode_range(self, name: str) -> bool:
        return False

    def get_codepoint_from_position(self, x: int, y: int) -> int:
        return -1

    def isValidCharacter(self, ch: str) -> bool:
        return False

    @staticmethod
    def _chr(cp: int) -> str:
        return ""

# --------------------
# Dialog classes (preserve original behavior/easter eggs)
# --------------------
class ClickableLabel(QLabel):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.click_handler = None

    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.click_handler:
            try:
                self.click_handler(event)
            except Exception:
                super().mousePressEvent(event)

    
    def set_click_handler(self, handler):
        self.click_handler = handler

class AboutDialog(QDialog):
    
    def __init__(self, display_os_str: str, current_directory_str: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.display_os = display_os_str
        self.current_dir = current_directory_str
        self.setWindowTitle(self.tr("About " + APP_NAME))
        icon_path = get_icon_path("bunnypad")
        self.setFont(QApplication.font())
        if icon_path:
            self.setWindowIcon(QIcon(icon_path))
        self.setup_ui()

    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        title = QLabel(APP_NAME + "\u2122")
        font = title.font()
        base_font = QApplication.font()
        font = QFont(base_font)
        font.setPointSizeF(base_font.pointSizeF() * 1.6)
        title.setFont(font)

        title.setFont(font)
        layout.addWidget(title)

        logo = ClickableLabel()
        pix = QPixmap(get_icon_path("bunnypad"))
        pix.setDevicePixelRatio(self.devicePixelRatioF())
        if not pix.isNull():
            logo.setPixmap(pix)
        logo.set_click_handler(self.activate_skillsusa_easter_egg)
        layout.addWidget(logo)

        layout.addWidget(
            QLabel(
                self.tr(
                    "A Notepad Clone named in part after Innersloth's "
                    "Off-Topic Regular, PBbunnypower [aka Bunny]"
                )
            )
        )

        layout.addWidget(
            QLabel(
                self.tr(
                    "Copyright \u00a9 2023-2026 GSYT Productions, LLC\n"
                    "Copyright \u00a9 2024-2026 The BunnyPad Contributors"
                )
            )
        )

        layout.addWidget(QLabel(APP_NAME + self.tr(" is licensed under the Apache 2.0 License")))

        original_phrase = "pet the bunny"
        anagrams = [
            "tnentbpu y he",
            "the pet bunny",
            "tnebyt uhn pe",
            "eupntbeyh  tn",
            "ehtueyn pbn t",
            "the bunny pet",
            "bunny pet the",
            "phube yent tn",
            "tp ne tuenyhb",
            "tnentbpu y he",
            original_phrase,
        ]
        selected_anagram = random.choice(anagrams)
        phrases = [
            self.tr('"It was a pleasure to [learn]"'),
            self.tr(
                '"So it was the hand that started it all ... \n'
                'His hands had been infected, and soon it would be his arms ... \n'
                'His hands were ravenous."'
            ),
            self.tr("Hopping past opinions"),
            self.tr(
                '"Is it true that a long time ago, firemen used to put out fires '
                'and not burn books?"'
            ),
            self.tr(
                '"Fahrenheit 451, the temperature at which paper '
                'spontaneously combusts"'
            ),
            self.tr(
                "\"Do you want to know what's inside all these books? Insanity. \"\n"
                "\"The Eels want to measure their place in the universe,\\n\"\n"
                "\"so they turn to these novels about non-existent people. \"\n"
                "\"Or worse, philosophers. \\n\"\n"
                "\"Look, here's Spinoza. One expert screaming down another expert's throat. \"\n"
                "\"\\\"We have free will. No, all of our actions are predetermined.\\\" \"\n"
                "\"Each one says the opposite, and a man comes away lost, \"\n"
                "\"feeling more bestial and lonely than before. \\n\"\n"
                "\"Now, if you don't want a person unhappy, you don't give them \"\n"
                "\"two sides of a question to worry about. Just give 'em one.. \"\n"
                "\"Better yet, none.\\\"\""
            ),
            selected_anagram,
            "Cito - ad posteriorem illius lucernae formae confugite.",
            "celeriter, post illam lucernam commode formatam",
            "Make haste-bethink thyself abaft that fortuitously contoured lantern.",
            "(Noticing how CrDroid has overlays for even the most obscure apps, resulting in endless XMLs and customization... It fills you with determination)",
            "This copy of BunnyPad is ae compatible",
            "see: brains cannot be decompiled ^",
            "Please donate chocolate =)",
            "I make BunnyPad run on everything because I think I can. And because I 'can', I 'have to'.",
            "You really like clicking buttons, don't you?",
            "Save often… or don't. I'll judge either way.",
            "Yes, that was totally the correct shortcut… maybe.",
            "I hope you enjoy your new file name… whatever it is.",
            "I'm not judging… okay, maybe a little.",
            "Ah, you're still here. I was worried for a second."
        ]
        random_phrase = random.choice(phrases)
        layout.addWidget(QLabel(random_phrase))

        layout.addWidget(
            QLabel(
                self.tr("Developer Information: \n")
                + self.tr("Build: ")
                + CURRENT_VERSION
                + "\n"
                + self.tr("Internal Name: ")
                + "Codename PBbunnypower Notepad Variant "
                + VERSION_CODENAME
                + "\n"
                + self.tr("Engine: PrettyFonts")
            )
        )

        layout.addWidget(QLabel(self.tr("You are running ") + APP_NAME + self.tr(" on ") + self.display_os))
        layout.addWidget(QLabel(APP_NAME + self.tr(" is installed at ") + self.current_dir))

        # center align children
        for i in range(layout.count()):
            try:
                item = layout.itemAt(i)
                if item and item.widget():
                    item.widget().setAlignment(Qt.AlignmentFlag.AlignHCenter)
            except Exception:
                pass
        self.adjustSize()
        self.setMinimumSize(self.sizeHint())

    
    def activate_skillsusa_easter_egg(self, event):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(self.tr("SkillsUSA 2025"))
        msg_box.setWindowIcon(QIcon(get_icon_path("bunnypad")))
        msg_box.setText(
            self.tr(
                "No matter what comes our way\n"
                "No matter what they say\n"
                "Our victory is essential\n"
                "We will IGNITE OUR POTENTIAL!"
            )
        )
        msg_box.exec()

# nice job for paying attention :D

class SystemInfoDialog(QDialog):
    
    def __init__(self, system_info_text: str, display_os_str: str, current_directory_str: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.system_info_text = system_info_text
        self.display_os = display_os_str
        self.current_dir = current_directory_str
        self.setWindowTitle(self.tr("System Information"))
        self.setWindowIcon(QIcon(get_icon_path("bunnypad")))
        self.setFont(QApplication.font())
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        title = QLabel(self.tr("System Information"))
        font = title.font()
        base_font = QApplication.font()
        font = QFont(base_font)
        font.setPointSizeF(base_font.pointSizeF() * 1.6)
        title.setFont(font)

        title.setFont(font)
        layout.addWidget(title)

        logo = QLabel()
        pix = QPixmap(get_icon_path("bunnypad"))
        pix.setDevicePixelRatio(self.devicePixelRatioF())
        if not pix.isNull():
            logo.setPixmap(pix)
        layout.addWidget(logo)

        # Add system information as individual labels like CreditsDialog
        if self.system_info_text:
            info_lines = self.system_info_text.split('\n')
            for line in info_lines:
                if line.strip():
                    info_label = QLabel(line.strip())
                    layout.addWidget(info_label)

        # Add OS and directory info like CreditsDialog
        layout.addWidget(QLabel(self.tr("Installation Directory: ") + self.current_dir))
        
        # Add some fun phrases like CreditsDialog
        phrases = [
            self.tr("System information gathered with care"),
            self.tr("Your computer's secrets revealed"),
            self.tr("Hardware and software in harmony"),
            self.tr("Digital fingerprints exposed"),
            self.tr("The machine speaks the truth"),
            self.tr("Bits and bytes tell the story"),
            self.tr("System specs unveiled"),
            self.tr("Hardware detective at work"),
            self.tr("Digital forensics complete"),
            self.tr("Machine introspection successful")
        ]
        random_phrase = random.choice(phrases)
        layout.addWidget(QLabel(random_phrase))
        
        # Center align all widgets like CreditsDialog
        for i in range(layout.count()):
            try:
                item = layout.itemAt(i)
                if item and item.widget():
                    item.widget().setAlignment(Qt.AlignmentFlag.AlignHCenter)
            except Exception:
                pass
        self.adjustSize()
        self.setMinimumSize(self.sizeHint())

class CreditsDialog(QDialog):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle(self.tr("About ") + APP_NAME + self.tr("'s Team"))
        self.setWindowIcon(QIcon(get_icon_path("bunnypad")))
        self.setFont(QApplication.font())
        self.setup_ui()

    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        title = QLabel(self.tr("The Team Behind ") + APP_NAME + "\u2122")
        font = title.font()
        base_font = QApplication.font()
        font = QFont(base_font)
        font.setPointSizeF(base_font.pointSizeF() * 1.6)
        title.setFont(font)

        title.setFont(font)
        layout.addWidget(title)

        logo = ClickableLabel()
        pix = QPixmap(get_icon_path("gsyt"))
        pix.setDevicePixelRatio(self.devicePixelRatioF())
        if not pix.isNull():
            logo.setPixmap(pix)
        logo.set_click_handler(self.alan_egg)
        layout.addWidget(logo)

        layout.addWidget(
            QLabel(
                self.tr(
                    "GarryStraitYT: Lead Developer; PBbunnypower (Bunny): Main icon design, project dedicated to her\n\n"
                )
                + "I-San: "
                + self.tr("Beta Tester\n")
                + "DinoDude: "
                + self.tr("Github contributor\n")
                + "BunnyFndr: "
                + self.tr("Icon Finder and Bug Tester")
            )
        )
        for i in range(layout.count()):
            try:
                item = layout.itemAt(i)
                if item and item.widget():
                    item.widget().setAlignment(Qt.AlignmentFlag.AlignHCenter)
            except Exception:
                pass
        self.adjustSize()
        self.setMinimumSize(self.sizeHint())

    
    def alan_egg(self, event):
        try:
            dlg = alan_walker_wia_egg(self)
            dlg.exec()
        except Exception:
            return None # I need to fix this later
class FeatureNotReady(QDialog):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Feature Not Ready: Work In Progress"))
        self.setWindowIcon(QIcon(get_icon_path("bunnypad")))
        self.setFont(QApplication.font())
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        title = QLabel(APP_NAME + "\u2122")
        font = title.font()
        base_font = QApplication.font()
        font = QFont(base_font)
        font.setPointSizeF(base_font.pointSizeF() * 1.6)
        title.setFont(font)

        title.setFont(font)
        layout.addWidget(title)

        logo = ClickableLabel()
        pix = QPixmap(get_icon_path("bunnypad"))
        pix.setDevicePixelRatio(self.devicePixelRatioF())
        if not pix.isNull():
            logo.setPixmap(pix)
        logo.set_click_handler(self.activate_null_easter_egg)
        layout.addWidget(logo)

        message = QLabel(
            self.tr(
                "The requested feature is either incomplete or caused "
                "instabilities during testing and has been disabled until "
                "further notice. We apologize for the inconvenience."
            )
        )
        message.setWordWrap(True)
        layout.addWidget(message)
        for i in range(layout.count()):
            try:
                item = layout.itemAt(i)
                if item and item.widget():
                    item.widget().setAlignment(Qt.AlignmentFlag.AlignHCenter)
            except Exception:
                pass
        ok_button = QPushButton(self.tr("OK"))
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.adjustSize()
        self.setMinimumSize(self.sizeHint())

    
    def activate_null_easter_egg(self, event):
        gastertext = "❄︎☟︎☜︎ ☹︎✌︎👌︎📬︎📬︎📬︎ ✋︎❄︎ 🕈︎☟︎✋︎💧︎🏱︎☜︎☼︎💧︎📬︎📬︎📬︎ ☟︎⚐︎🕈︎ ✋︎☠︎❄︎☜︎☼︎☜︎💧︎❄︎✋︎☠︎☝︎📬︎📬︎📬︎" # THE LAB... IT WHISPERS... HOW INTERESTING...
        msg_box = QMessageBox(self)
        msg_box.setWindowIcon(QIcon(get_icon_path("bunnypad")))
        msg_box.setWindowTitle("🕈︎📬︎👎︎📬︎ ☝︎✌︎💧︎❄︎☜︎☼︎") # W.D. GASTER
        msg_box.setText(gastertext)
        msg_box.exec()

class CryptoGUI(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("RCCMITOWOATAS CryptoTool"))
        self.setWindowIcon(QIcon(get_icon_path("bunnypad")))
        self.setFont(QApplication.font())
        self.setup_ui()
    def setup_ui(self):
        layout = QVBoxLayout(self)
        title = QLabel(APP_NAME + "\u2122")
        font = title.font()
        base_font = QApplication.font()
        font = QFont(base_font)
        font.setPointSizeF(base_font.pointSizeF() * 1.6)
        title.setFont(font)

        title.setFont(font)
        layout.addWidget(title)

        logo = ClickableLabel()
        pix = QPixmap(get_icon_path("bunnypad"))
        pix.setDevicePixelRatio(self.devicePixelRatioF())
        if not pix.isNull():
            logo.setPixmap(pix)
        layout.addWidget(logo)

        message = QLabel(
        text = self.tr(
    "The Cryptography Tool has been removed as a built-in component of BunnyPad.\n"
    "We removed it because we are migrating several larger functions\n"
    "to a new API, which will allow for more customization than ever before.\n"
    "We understand that this change might cause some inconvenience,\n"
    "and we apologize for that. However, these changes will be beneficial\n"
    "to the stability and security of BunnyPad."
        )

        )
        message.setWordWrap(True)
        layout.addWidget(message)
        for i in range(layout.count()):
            try:
                item = layout.itemAt(i)
                if item and item.widget():
                    item.widget().setAlignment(Qt.AlignmentFlag.AlignHCenter)
            except Exception:
                pass
        ok_button = QPushButton(self.tr("OK"))
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.adjustSize()
        self.setMinimumSize(self.sizeHint())

class TheCakeIsALie(QDialog):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Error: Cake_Is_Lie"))
        self.setWindowIcon(QIcon(get_icon_path("nocake")))
        self.setFont(QApplication.font())
        self.setup_ui()

    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        title = QLabel(self.tr("A Critical Error Has Occurred"))
        font = title.font()
        base_font = QApplication.font()
        font = QFont(base_font)
        font.setPointSizeF(base_font.pointSizeF() * 1.6)
        title.setFont(font)

        title.setFont(font)
        layout.addWidget(title)

        logo = ClickableLabel()
        pix = QPixmap(get_icon_path("nocake"))
        pix.setDevicePixelRatio(self.devicePixelRatioF())
        if not pix.isNull():
            logo.setPixmap(pix)
        logo.set_click_handler(self.momentum_easteregg)
        layout.addWidget(logo)

        message = QLabel(
            self.tr(
                "Unfortunately, there is no cake. You have fallen for a trap. "
                "Where we promised a tasty dessert, there is instead deception. "
                "In other words, THE CAKE IS A LIE!"
            )
        )
        message.setWordWrap(True)
        layout.addWidget(message)

        ok_button = QPushButton(self.tr("OK"))
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.adjustSize()
        self.setMinimumSize(self.sizeHint())

    
    def momentum_easteregg(self, event):
        quote = self.tr(
            "Momentum, a function of mass and velocity, is conserved between "
            "portals. In layman's terms, speedy thing goes in, speedy thing "
            "comes out."
        )
        msg_box = QMessageBox(self)
        msg_box.setWindowIcon(QIcon(get_icon_path("bunnypad")))
        msg_box.setWindowTitle(self.tr("Momentum and Portals"))
        msg_box.setText(quote)
        msg_box.exec()

class ContactUs(QDialog):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Contact BunnyPad Support"))
        self.setWindowIcon(QIcon(get_icon_path("bunnypad")))
        self.setFont(QApplication.font())
        self.setup_ui()

    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        title = QLabel(APP_NAME + "\u2122")
        font = title.font()
        base_font = QApplication.font()
        font = QFont(base_font)
        font.setPointSizeF(base_font.pointSizeF() * 1.6)
        title.setFont(font)

        title.setFont(font)
        layout.addWidget(title)

        logo = ClickableLabel()
        pix = QPixmap(get_icon_path("bunnypad"))
        pix.setDevicePixelRatio(self.devicePixelRatioF())
        if not pix.isNull():
            logo.setPixmap(pix)
        logo.set_click_handler(self.activate_galaxynote7_easter_egg)
        layout.addWidget(logo)

        info_label = QLabel(
            "Website: <a href='http://bunnypad.eclipse.cx' style=\"color: #0078D7;\">http://bunnypad.eclipse.cx/</a> <br> "
            "GSYT Productions Server: <a href='https://guilded.gg/gsyt-productions' style=\"color: #0078D7;\">https://guilded.gg/gsyt-productions</a> <br> "
            "BunnyPad CarrotPatch Server: <a href='https://guilded.gg/bunnypad' style=\"color: #0078D7;\">https://guilded.gg/bunnypad</a><br>"
            "BunnyPad Donation Link: <a href='https://throne.com/bunnypad' style=\"color: #0078D7;\">https://throne.com/bunnypad</a> <br> "
            "Text Us: +1 (814) 204-2333"
        )
        info_label.setTextFormat(Qt.TextFormat.RichText)
        info_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        info_label.setOpenExternalLinks(True)
        layout.addWidget(info_label)

        ok_button = QPushButton(self.tr("OK"))
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.adjustSize()
        self.setMinimumSize(self.sizeHint())


    
    def activate_galaxynote7_easter_egg(self, event):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Galaxy Note 7")
        msg_box.setWindowIcon(QIcon(get_icon_path("bunnypad")))
        msg_box.setText(self.tr("So I heard that the") + " Samsung Galaxy Note 7 " + self.tr("was the bomb, rather literally"))
        msg_box.exec()

class DownloadOptions(QDialog):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Download Options"))
        self.setWindowIcon(QIcon(get_icon_path("bunnypad")))
        self.resize(900, 700)
        self.setup_ui()

    
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        text_label = QLabel(self.tr("Where do you want to go today?\n\nChoose one of the available download options:"))
        main_layout.addWidget(text_label)

        buttons_layout = QGridLayout()
        main_layout.addLayout(buttons_layout)

        button_names = {
            "Latest Stable Release": "Latest Stable Release",
            "Latest Stable Source": "Latest Stable Source",
            "BunnyPad Donation": "BunnyPad Donation",
            "Customizer": "Customizer",
            "Tech Stuff Website": "Tech Stuff Website",
            "r3dfox Download": "r3dfox Download",
            "Donate to Tech Stuff": "Donate to Tech Stuff",
            "Join the Legacy Enthusiasm Discord": "Join the Legacy Enthusiasm Discord",
        }

        row, col = 0, 0
        for full_name, object_name in button_names.items():
            button = QPushButton(full_name)
            method_name = "on_" + object_name.lower().replace(" ", "_").replace("-", "_") + "_clicked"
            if hasattr(self, method_name):
                button.clicked.connect(getattr(self, method_name))
            else:
                button.clicked.connect(lambda checked, url="https://github.com/GSYT-Productions/BunnyPad-SRC/": webbrowser.open(url))
            buttons_layout.addWidget(button, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1

        self.lcd_number = QLCDNumber()
        self.lcd_number.setSegmentStyle(QLCDNumber.SegmentStyle.Flat)
        self.lcd_number.setDigitCount(4)
        self.lcd_number.display(2026)
        main_layout.addWidget(self.lcd_number)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.reject)
        main_layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)
        self.adjustSize()
        self.setMinimumSize(self.sizeHint())
    
    def on_latest_stable_release_clicked(self):
        webbrowser.open("https://garrystraityt.itch.io/bunnypad")

    
    def on_latest_stable_source_clicked(self):
        webbrowser.open("https://github.com/GSYT-Productions/BunnyPad-SRC/")

    
    def on_bunnypad_donation_clicked(self):
        webbrowser.open("https://throne.com/bunnypad")

    
    def on_customizer_clicked(self):
        webbrowser.open("https://gsyt-productions.github.io/BunnyPadCustomizer/")

    
    def on_tech_stuff_website_clicked(self):
        webbrowser.open("https://teknixstuff.com")

    
    def on_r3dfox_download_clicked(self):
        webbrowser.open("https://github.com/Eclipse-Community/r3dfox/releases/")

    def on_donate_to_tech_stuff_clicked(self):
        webbrowser.open("https://teknixstuff.com/Network/Donate/")

    def on_join_the_legacy_enthusiasm_discord_clicked(self):
        webbrowser.open("https://discord.gg/QKnmynMYjy")

class alan_walker_wia_egg(QDialog):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(APP_NAME)
        self.setWindowIcon(QIcon(get_icon_path("bunnypad")))
        self.setFont(QApplication.font())
        self.setup_ui()

    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        title = QLabel(APP_NAME + "\u2122")
        font = title.font()
        base_font = QApplication.font()
        font = QFont(base_font)
        font.setPointSizeF(base_font.pointSizeF() * 1.6)
        title.setFont(font)

        title.setFont(font)
        layout.addWidget(title)

        logo = ClickableLabel()
        pix = QPixmap(get_icon_path("bunnypad"))
        pix.setDevicePixelRatio(self.devicePixelRatioF())
        if not pix.isNull():
            logo.setPixmap(pix)
        logo.set_click_handler(self.activate_escargot_easter_egg)
        layout.addWidget(logo)

        layout.addWidget(QLabel(self.tr("'I'm not playing by the rules if they were made by you'")))
        for i in range(layout.count()):
            try:
                item = layout.itemAt(i)
                if item and item.widget():
                    item.widget().setAlignment(Qt.AlignmentFlag.AlignHCenter)
            except Exception:
                pass
        self.adjustSize()
        self.setMinimumSize(self.sizeHint())
    
    def activate_escargot_easter_egg(self, event):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(self.tr("Snails"))
        msg_box.setWindowIcon(QIcon(get_icon_path("bunnypad")))
        msg_box.setText("@" * 500)
        msg_box.exec()

# --------------------
# Update checker / downloader (threaded)
# --------------------
class update_checker(QThread):
    update_check_completed = Signal(dict)

    
    def __init__(self, repo_owner=REPO_OWNER, repo_name=REPO_NAME, use_pre_release=False):
        super().__init__()
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.use_pre_release = use_pre_release

    
    def run(self):
        info = {}
        if requests is None:
            self.update_check_completed.emit({})
            return
        try:
            url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/releases"
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            releases = resp.json()
            latest_stable = None
            latest_prerelease = None
            for r in releases:
                if r.get("prerelease", False):
                    if latest_prerelease is None or (r.get("published_at") or "") > (latest_prerelease.get("published_at") or ""):
                        latest_prerelease = r
                else:
                    if latest_stable is None or (r.get("published_at") or "") > (latest_stable.get("published_at") or ""):
                        latest_stable = r
            if latest_stable:
                info["stable"] = {"version": latest_stable.get("tag_name"), "url": latest_stable.get("html_url"), "date": latest_stable.get("published_at")}
            if latest_prerelease:
                info["prerelease"] = {"version": latest_prerelease.get("tag_name"), "url": latest_prerelease.get("html_url"), "date": latest_prerelease.get("published_at")}
            self.update_check_completed.emit(info)
        except Exception:
            self.update_check_completed.emit({})

# --------------------
# Main Notepad (kept compatible)
# --------------------
class Notepad(QMainWindow):
    def __init__(self):
        super().__init__()

        # --- Window setup (from Notepad) ---
        self.setWindowTitle(self.tr("Untitled - ") + APP_NAME)
        icon = get_icon_path("bunnypad")
        if icon:
            self.setWindowIcon(QIcon(icon))
        self.resize(900, 700)

        # --- File state and flags ---
        self.file_path = None
        self.unsaved_changes_flag = False
        self.update_thread = None

        # --- Mark session dirty on startup ---
        open(DIRTY_FILE, "w").close()


        # --- Auto-save timer ---
        self.autoSaveTimer = QTimer(self)
        self.autoSaveTimer.timeout.connect(self.autoSave)
        self.autoSaveTimer.start(10000)

        # central text edit
        self.textedit = QTextEdit()
        self.textedit.setAcceptRichText(False)
        self.setCentralWidget(self.textedit)
        self.textedit.document().setModified(False)
        # --- Connect modification signal ---
        self.textedit.document().modificationChanged.connect(self.onModificationChanged)

        # --- Restore session if dirty ---
        if os.path.exists(DIRTY_FILE):
            self.restoreSession()
        
        # menus / toolbar / status
        self.create_actions_and_menus()
        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Ready")

        # character map dock
        self.character_map = CharacterWidget()
        self.character_map.characterSelected.connect(self.insert_character)
        self.character_map.closed.connect(lambda: self._toggle_character_map_action.setChecked(False))
        self.character_dock = QDockWidget(QCoreApplication.translate("MainWindow", "Character Map"), self)
        self.character_dock.setWidget(self.character_map)
        self.character_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        # Theme toggling for dock when floating / docked
        def _char_dock_theme(floating):
            if floating:
                self.character_dock.setObjectName("FloatingWindow")
            else:
                self.character_dock.setObjectName("")
            # Force QSS re‑evaluation
            self.character_dock.style().unpolish(self.character_dock)
            self.character_dock.style().polish(self.character_dock)
            self.character_dock.update()
        self.character_dock.topLevelChanged.connect(_char_dock_theme)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.character_dock)
        self.character_dock.hide()

        # track changes
        self.textedit.textChanged.connect(self.handle_text_changed)
        self.show()

    
    def create_actions_and_menus(self):
        menubar = QMenuBar(self)
        self.setMenuBar(menubar)
        self.menuBar().setNativeMenuBar(False)
        menubar.setStyleSheet("""
        QMenuBar {
            padding: 6px;
        }
        QMenuBar::item {
            padding: 3px 8px;
        }
        """)
        # ----------------
        # File menu
        # ----------------
        file_menu = QMenu(self.tr("File"), self)
        menubar.addMenu(file_menu)

        new_action = QAction(QIcon(get_icon_path("new")), self.tr("New"), self)
        new_action.setShortcut("Ctrl+N")
        new_action.setStatusTip(self.tr("Create a new document"))
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)

        open_action = QAction(QIcon(get_icon_path("open")), self.tr("Open..."), self)
        open_action.setShortcut("Ctrl+O")
        open_action.setStatusTip(self.tr("Open an existing document"))
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction(QIcon(get_icon_path("save")), self.tr("Save"), self)
        save_action.setShortcut("Ctrl+S")
        save_action.setStatusTip(self.tr("Saves the existing document"))
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        save_as_action = QAction(QIcon(get_icon_path("saveas")), self.tr("Save As..."), self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.setStatusTip(self.tr("Saves the existing document under a new name/path"))
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        print_pdf_action = QAction(QIcon(get_icon_path("pdf")), self.tr("Print to PDF..."), self)
        print_pdf_action.setShortcut("Ctrl+Shift+P")
        print_pdf_action.setStatusTip(self.tr("Converts the document to a Portable Document Format (PDF) file"))
        print_pdf_action.triggered.connect(self.print_to_pdf)
        file_menu.addAction(print_pdf_action)

        print_action = QAction(QIcon(get_icon_path("printer")), self.tr("Print..."), self)
        print_action.setShortcut("Ctrl+P")
        print_action.setStatusTip(self.tr("Allows you to make a physical copy of the document"))
        print_action.triggered.connect(self.file_print)
        file_menu.addAction(print_action)

        file_menu.addSeparator()

        exit_action = QAction(QIcon(get_icon_path("exit")), self.tr("Exit"), self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip(self.tr("Closes BunnyPad"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = QMenu(self.tr("Edit"), self)
        menubar.addMenu(edit_menu)

        undo_action = QAction(QIcon(get_icon_path("undo")), self.tr("Undo"), self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.setStatusTip(self.tr("Undo the previous action"))
        undo_action.triggered.connect(self.textedit.undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction(QIcon(get_icon_path("redo")), self.tr("Redo"), self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.setStatusTip(self.tr("Redoes an undone action"))
        redo_action.triggered.connect(self.textedit.redo)
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        cut_action = QAction(QIcon(get_icon_path("cut")), self.tr("Cut"), self)
        cut_action.setShortcut("Ctrl+X")
        cut_action.setStatusTip(self.tr("Moves the highlighted text to the clipboard"))
        cut_action.triggered.connect(self.textedit.cut)
        edit_menu.addAction(cut_action)

        copy_action = QAction(QIcon(get_icon_path("copy")), self.tr("Copy"), self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.setStatusTip(self.tr("Copies the highlighted text to the clipboard"))
        copy_action.triggered.connect(self.textedit.copy)
        edit_menu.addAction(copy_action)

        paste_action = QAction(QIcon(get_icon_path("paste")), self.tr("Paste"), self)
        paste_action.setShortcut("Ctrl+V")
        paste_action.setStatusTip(self.tr("Copies text from the clipboard into the document"))
        paste_action.triggered.connect(self.textedit.paste)
        edit_menu.addAction(paste_action)

        delete_action = QAction(QIcon(get_icon_path("delete")), self.tr("Delete"), self)
        delete_action.setShortcut("Del")
        delete_action.setStatusTip(self.tr("Deletes/removes the highlighted text"))
        delete_action.triggered.connect(lambda: self.textedit.textCursor().deleteChar())
        edit_menu.addAction(delete_action)

        edit_menu.addSeparator()

        datetime_action = QAction(QIcon(get_icon_path("datetime")), self.tr("Date and Time"), self)
        datetime_action.setShortcut("F5")
        datetime_action.setStatusTip(self.tr("Inserts the current date and time into the document at the cursor's placement. Reimplementation of a function from Windows Notepad"))
        datetime_action.triggered.connect(self.date_and_time)
        edit_menu.addAction(datetime_action)

        edit_menu.addSeparator()

        find_action = QAction(QIcon(get_icon_path("find")), self.tr("Find..."), self)
        find_action.setShortcut("Ctrl+F")
        find_action.setStatusTip(self.tr("Finds text in the document"))
        find_action.triggered.connect(self.find_function)
        edit_menu.addAction(find_action)

        go_to_line_action = QAction(QIcon(get_icon_path("find")), self.tr("Go To Line"), self)
        go_to_line_action.setShortcut("Ctrl+G")
        go_to_line_action.setStatusTip(self.tr("Goes to a specified line in the document. Typically used in software development."))
        go_to_line_action.triggered.connect(self.go_to_line)
        edit_menu.addAction(go_to_line_action)

        replace_action = QAction(QIcon(get_icon_path("replace")), self.tr("Replace..."), self)
        replace_action.setShortcut("Ctrl+H")
        replace_action.setStatusTip(self.tr("Replaces text in the document. [Feature not complete.]"))
        replace_action.triggered.connect(self.feature_not_ready)
        edit_menu.addAction(replace_action)

        edit_menu.addSeparator()

        select_all_action = QAction(QIcon(get_icon_path("selectall")), self.tr("Select All"), self)
        select_all_action.setShortcut("Ctrl+A")
        select_all_action.setStatusTip(self.tr("Selects all the text in the document"))
        select_all_action.triggered.connect(self.textedit.selectAll)
        edit_menu.addAction(select_all_action)

        # Format menu
        format_menu = QMenu(self.tr("Format"), self)
        menubar.addMenu(format_menu)

        word_wrap_action = QAction(QIcon(get_icon_path("wordwrap")), self.tr("Word Wrap"), self)
        word_wrap_action.setCheckable(True)
        word_wrap_action.setChecked(True)
        word_wrap_action.setShortcut("Ctrl+W")
        word_wrap_action.setStatusTip(self.tr("Allows the text to \"wrap\" around the window size."))
        word_wrap_action.triggered.connect(self.toggle_word_wrap)
        format_menu.addAction(word_wrap_action)

        font_action = QAction(QIcon(get_icon_path("font")), self.tr("Font..."), self)
        font_action.setShortcut("Alt+F")
        font_action.setStatusTip(self.tr("Allows you to change the font. Current implementation buggy, please file an Issue on Github with any advice/feedback."))
        font_action.triggered.connect(self.choose_font)
        format_menu.addAction(font_action)

        # View menu
        view_menu = QMenu(self.tr("View"), self)
        menubar.addMenu(view_menu)

        statusbar_action = QAction(QIcon(get_icon_path("status")), self.tr("Show statusbar"), self, checkable=True)
        statusbar_action.setChecked(True)
        statusbar_action.setShortcut("Alt+Shift+S")
        statusbar_action.setStatusTip(self.tr("Allows you to toggle the statusbar."))
        statusbar_action.triggered.connect(self.toggle_statusbar)
        view_menu.addAction(statusbar_action)

        toolbar_action = QAction(QIcon(get_icon_path("toolbar")), "Toolbar", self, checkable=True)
        toolbar_action.setChecked(True)
        toolbar_action.setShortcut("Alt+T")
        toolbar_action.setStatusTip(self.tr("Allows you to toggle the toolbar."))
        toolbar_action.triggered.connect(self.toggle_toolbar)
        view_menu.addAction(toolbar_action)

        #Add Tools Menu
        tools_menu = QMenu(self.tr("Tools"), self)
        menubar.addMenu(tools_menu)

        #Add starting point for RCCMITOWOATAS addition
        rcc_action = QAction(QIcon(get_icon_path("encryption")), self.tr("Text Encryption Tool"), self)
        rcc_action.triggered.connect(self.crypto_tool)
        rcc_action.setStatusTip(self.tr("[Deprecated function. Will be migrated to an addon]"))
        tools_menu.addAction(rcc_action)

        # Move Charmap to Tools menu
        toggle_character_map_action = QAction(QIcon(get_icon_path("charmap")), self.tr("Character Map"), self)
        toggle_character_map_action.setCheckable(True)
        toggle_character_map_action.setShortcut("Ctrl+M")
        toggle_character_map_action.toggled.connect(self.toggle_character_map)
        toggle_character_map_action.setStatusTip(self.tr("[Deprecated function. Will be migrated to an addon]"))
        tools_menu.addAction(toggle_character_map_action)
        self._toggle_character_map_action = toggle_character_map_action

        # Help menu
        help_menu = QMenu(self.tr("Help"), self)
        menubar.addMenu(help_menu)

        about_action = QAction(QIcon(get_icon_path("info")), self.tr("About BunnyPad"), self)
        about_action.setShortcut("Alt+H")
        about_action.setStatusTip(self.tr("View information about BunnyPad"))
        about_action.triggered.connect(self.about)
        help_menu.addAction(about_action)

        system_action = QAction(QIcon(get_icon_path("info")), self.tr("About Your System"), self)
        system_action.setShortcut("Shift+F1")
        system_action.setStatusTip(self.tr("View information about your system. Useful for debugging."))
        system_action.triggered.connect(self.sysinfo)
        help_menu.addAction(system_action)

        credits_action = QAction(QIcon(get_icon_path("team")), self.tr("Credits for BunnyPad"), self)
        credits_action.setShortcut("Alt+C")
        credits_action.setStatusTip(self.tr("View the team behind BunnyPad"))
        credits_action.triggered.connect(self.credits)
        help_menu.addAction(credits_action)

        cake_action = QAction(QIcon(get_icon_path("cake")), self.tr("Cake :D"), self)
        cake_action.setShortcut("Alt+A")
        cake_action.setStatusTip(self.tr("Cake... nothing else to say about this one."))
        cake_action.triggered.connect(self.cake)
        help_menu.addAction(cake_action)

        contact_support_action = QAction(QIcon(get_icon_path("support")), self.tr("Contact Us"), self)
        contact_support_action.setShortcut("Alt+S")
        contact_support_action.setStatusTip(self.tr("Contact us if you need help"))
        contact_support_action.triggered.connect(self.support)
        help_menu.addAction(contact_support_action)

        download_action = QAction(QIcon(get_icon_path("share")), self.tr("Download BunnyPad Tools"), self)
        download_action.setShortcut("Ctrl+J")
        download_action.setStatusTip(self.tr("Download various addons for BunnyPad, or visit one of our partners/sponsors"))
        download_action.triggered.connect(self.download)
        help_menu.addAction(download_action)

        update_action = QAction(QIcon(get_icon_path("update")), self.tr("Check For Updates"), self)
        update_action.setShortcut("Alt+U")
        update_action.setStatusTip(self.tr("Check for BunnyPad updates. Current implementation buggy, file an Issue or open a Pull Request on GitHub if you want to help fix it."))
        update_action.triggered.connect(self.check_for_updates)
        help_menu.addAction(update_action)

        # toolbar
        self.toolbar = QToolBar(self)
        self.toolbar.setMovable(True)
        def _toolbar_theme(floating: bool):
            # Set the objectName so QSS can style it dynamically
            self.toolbar.setObjectName("FloatingWindow" if floating else "")
            # Force QSS to re-apply immediately
            self.toolbar.style().unpolish(self.toolbar)
            self.toolbar.style().polish(self.toolbar)
            self.toolbar.update()
        # Connect the signal so this runs whenever the toolbar is floated/docked
        self.toolbar.topLevelChanged.connect(_toolbar_theme)
        self.addToolBar(self.toolbar)
        self.toolbar.addAction(new_action)
        self.toolbar.addAction(open_action)
        self.toolbar.addAction(save_action)
        self.toolbar.addAction(print_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(cut_action)
        self.toolbar.addAction(copy_action)
        self.toolbar.addAction(paste_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(undo_action)
        self.toolbar.addAction(redo_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(find_action)
        self.toolbar.addAction(replace_action)
        # self.toolbar.addSeparator()
        self.toolbar.addSeparator()
        self.toolbar.addAction(font_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(toggle_character_map_action)
        self.toolbar.addAction(rcc_action)
        self.toolbar.addAction(cake_action)
        # File operations
    
    def new_file(self):
        if not self.unsaved_changes_flag or self.warn_unsaved_changes():
            self.textedit.clear()
            self.file_path = None
            self.unsaved_changes_flag = False
            self.setWindowTitle(self.tr("Untitled - ") + APP_NAME)

    
    def open_file(self):
        """Memory-safe file opener for low-RAM devices (patch CVE-2025-59418)."""
        if self.unsaved_changes_flag:
            if not self.warn_unsaved_changes():
                return

        path, _ = QFileDialog.getOpenFileName(self, self.tr("Open File"), "", FILE_FILTERS["open"])
        if not path:
            return
        self.statusBar().showMessage("Loading...")
        QApplication.processEvents()
        
        CHUNK_SIZE = 64 * 1024  # 64 KB chunks
        MAX_QTEXTEDIT_CHARS = 2_000_000  # ~2M chars to stay safe on 512MB RAM

        try:
            self.textedit.clear()
            total_chars = 0

            with open(path, "rb") as f:
                while True:
                    chunk = f.read(CHUNK_SIZE)
                    if not chunk:
                        break

                    try:
                        text_chunk = chunk.decode("utf-8")
                    except UnicodeDecodeError:
                        text_chunk = chunk.decode("latin-1")

                    # truncate chunk if necessary
                    remaining = MAX_QTEXTEDIT_CHARS - total_chars
                    if remaining <= 0:
                        QMessageBox.warning(
                            self,
                            self.tr("File truncated"),
                            self.tr(
                                "This document is too large to be safely loaded and has been truncated "
                                "to prevent memory exhaustion (CVE-2025-59418)."
                            ),
                        )
                        break

                    if len(text_chunk) > remaining:
                        text_chunk = text_chunk[:remaining]

                    # insert immediately
                    self.textedit.moveCursor(QTextCursorEnd)
                    self.textedit.insertPlainText(text_chunk)
                    total_chars += len(text_chunk)

            self.file_path = path
            self.unsaved_changes_flag = False
            self.textedit.document().setModified(False)
            self.setWindowTitle(f"{os.path.basename(path)} - BunnyPad")
            self.statusBar().showMessage("")  # clear status bar after loading

        except Exception as e:
            QMessageBox.critical(
                self,
                self.tr("Error"),
                self.tr(f"Cannot open file: {e}")
            )
            self.statusBar().showMessage("")  # clear even on error

    def warn_unsaved_changes(self) -> bool:
        ret = QMessageBox.warning(
            self,
            "BunnyPad",
            self.tr("The document has been modified. Would you like to save your changes?"),
            QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
        )
        if ret == QMessageBox.StandardButton.Save:
            return self.save_file()
        if ret == QMessageBox.StandardButton.Cancel:
            return False
        return True

    
    def save_file(self) -> bool:
        if not self.file_path:
            return self.save_file_as()
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                f.write(self.textedit.toPlainText())
                self.statusBar().showMessage("Saving file…", 2000)
            self.unsaved_changes_flag = False
            self.setWindowTitle(f"{os.path.basename(self.file_path)} - " + APP_NAME)
            self.statusBar().showMessage("Saved file!", 2000)
            return True
        except Exception as e:
            QMessageBox.critical(self, self.tr("Error"), self.tr(f"Failed to save file: {e}"))
            self.statusBar().showMessage("Could not save file.", 2000)
            return False

    
    def save_file_as(self) -> bool:
        path, sel = QFileDialog.getSaveFileName(self, self.tr("Save As"), "", FILE_FILTERS["save"])
        if not path:
            return False
        # Append extension if needed
        self.file_path = path
        return self.save_file()

    
    def closeEvent(self, event):
        today = datetime.date.today()
        leroy_anniv = datetime.date(today.year, 4, 11)
        undertale_anniv = datetime.date(today.year, 9, 15)  # Set correct Undertale anniversary

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Confirm Exit")

        if today == leroy_anniv:
            msg_box.setText(
                "All right, time's up, let's do this!\n\n"
                "LEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEROY\n"
                "JEEEEEEEEEEEEEEEEEEEEEEEEEEEEEENKINS!"
            )
            ok_button_text = "Charge ahead! No regrets!"
            cancel_button_text = "ABORT! ABORT!"
        elif today == undertale_anniv:
            msg_box.setText(
            """☜︎☠︎❄︎☼︎✡︎ ☠︎🕆︎💣︎👌︎☜︎☼︎ 💧︎☜︎✞︎☜︎☠︎❄︎☜︎☜︎☠︎
👎︎✌︎☼︎😐︎ 👎︎✌︎☼︎😐︎☜︎☼︎ ✡︎☜︎❄︎ 👎︎✌︎☼︎😐︎☜︎☼︎
❄︎☟︎☜︎ 👎︎✌︎☼︎😐︎☠︎☜︎💧︎💧︎ 😐︎☜︎☜︎🏱︎💧︎ ☝︎☼︎⚐︎🕈︎✋︎☠︎☝︎
❄︎☟︎☜︎ 💧︎☟︎✌︎👎︎⚐︎🕈︎💧 👍︎🕆︎❄︎❄︎✋︎☠︎☝︎ 👎︎☜︎☜︎🏱︎☜︎☼︎
🏱︎☟︎⚐︎❄︎⚐︎☠︎ ☼︎☜︎✌︎👎︎✋︎☠︎☝︎💧︎ ☠︎☜︎☝︎✌︎❄︎✋︎✞︎☜︎
❄︎☟︎✋︎💧︎ ☠︎☜︎✠︎❄︎ ☜︎✠︎🏱︎☜︎☼︎✋︎💣︎☜︎☠︎❄︎
💧︎☜︎☜︎💣︎💧︎
✞︎☜︎☼︎✡︎
✞︎☜︎☼︎✡︎
✋︎☠︎❄︎☜︎☼︎☜︎💧︎❄︎✋︎☠︎☝︎
📬︎📬︎📬︎
🕈︎☟︎✌︎❄︎ 👎︎⚐︎ ✡︎⚐︎🕆︎ ❄︎🕈︎⚐︎ ❄︎☟︎✋︎☠︎😐︎"""
        )
            ok_button_text = "OK"
            cancel_button_text = "Cancel"
        else:
            msg_box.setText("Are you sure you want to exit?")
            ok_button_text = "Yes, exit"
            cancel_button_text = "Cancel"

        ok_button = msg_box.addButton(ok_button_text, QMessageBox.ButtonRole.AcceptRole)
        cancel_button = msg_box.addButton(cancel_button_text, QMessageBox.ButtonRole.RejectRole)

        msg_box.exec()

        if msg_box.clickedButton() == cancel_button:
            event.ignore()
            return

        # Now check unsaved changes if user agreed to exit
        if self.unsaved_changes_flag:
            # warn_unsaved_changes() returns True if the app should close (Save/Discard)
            # and False if it should not (Cancel).
            if self.warn_unsaved_changes():
                self.cleanupTemp()
                event.accept()
            else:
                # User cancelled the "save changes" dialog
                event.ignore()
        else:
            # No unsaved changes, so we can close safely
            self.cleanupTemp()
            event.accept()

    def handle_text_changed(self):
        self.unsaved_changes_flag = True
        if self.file_path:
            self.setWindowTitle(f"*{os.path.basename(self.file_path)} - "+ APP_NAME)
        else:
            self.setWindowTitle("*Untitled - "+ APP_NAME)

    
    def file_print(self):
        try:
            dlg = QPrintDialog()
            if dlg.exec():
                self.textedit.print(dlg.printer())
        except Exception:
            return None # I need to fix this later

    
    def update_statusbar(self):
        try:
            cursor = self.textedit.textCursor()
            line = cursor.blockNumber() + 1
            col = cursor.columnNumber() + 1
            self.statusbar.showMessage(f"Ln {line}, Col {col}", 5000)
        except Exception:
            pass

    
    def toggle_word_wrap(self):
        mode = self.textedit.lineWrapMode()
        # toggle (PyQt6: use enum values)
        if mode == QTextEdit.LineWrapMode.WidgetWidth:
            self.textedit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        else:
            self.textedit.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)

    
    def choose_font(self):
        font, ok = QFontDialog.getFont(self)
        if ok and font:
            self.textedit.setFont(font)

    
    def toggle_toolbar(self):
        self.toolbar.setVisible(not self.toolbar.isVisible())

    
    def toggle_statusbar(self):
        self.statusbar.setVisible(not self.statusbar.isVisible())

    
    def about(self):
        display_os_str = identify_os()
        current_directory_str = os.getcwd()
        dlg = AboutDialog(display_os_str, current_directory_str)
        dlg.exec()

    
    def credits(self):
        dlg = CreditsDialog()
        dlg.exec()

    
    def sysinfo(self):
        # Show a loading message first
        QApplication.processEvents()  # Process any pending events
        
        try:
            system_info_text = get_system_info()
            display_os_str = identify_os()
            current_directory_str = os.getcwd()
            dlg = SystemInfoDialog(system_info_text, display_os_str, current_directory_str)
            dlg.exec()
        except Exception as e:
            QMessageBox.critical(self, self.tr("Error"), self.tr(f"Failed to get system information: {str(e)}"))

    
    def feature_not_ready(self):
        dlg = FeatureNotReady()
        dlg.exec()

    
    def cake(self):
        dlg = TheCakeIsALie()
        dlg.exec()

    
    def support(self):
        dlg = ContactUs()
        dlg.exec()

    
    def download(self):
        dlg = DownloadOptions()
        dlg.exec()

    def crypto_tool(self):
        self.open_encryption_tool()
    
    def toggle_character_map(self, checked):
        self.character_dock.setVisible(checked)

    
    def insert_character(self, ch: str):
        self.textedit.insertPlainText(ch)

    
    def print_to_pdf(self):
        path, _ = QFileDialog.getSaveFileName(self, self.tr("Print to PDF [Save as]"), "", FILE_FILTERS["pdf"])
        if path:
            save_as_pdf(self.textedit.toPlainText(), path)

    
    def date_and_time(self):
        cdate = str(datetime.datetime.now())
        self.textedit.append(cdate)

    
    def go_to_line(self):
        line_number, ok = QInputDialog.getInt(self, self.tr("Go to Line"), self.tr("Enter line number:"), value=1)
        if ok:
            cursor = self.textedit.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            cursor.movePosition(QTextCursor.MoveOperation.Down, QTextCursor.MoveMode.MoveAnchor, line_number - 1)
            self.textedit.setTextCursor(cursor)
            self.textedit.ensureCursorVisible()

    
    def find_function(self):
        word_to_find, ok = QInputDialog.getText(self, self.tr("Find"), self.tr("Enter the text you want to find:"))
        if ok and word_to_find:
            cursor = self.textedit.document().find(word_to_find)
            if not cursor.isNull():
                self.textedit.setTextCursor(cursor)
                self.textedit.ensureCursorVisible()
            else:
                QMessageBox.critical(self, self.tr("Text could not be found!"), self.tr("The specified text is not currently present in this document."))

    
    def replace_function(self):
        QMessageBox.warning(self, self.tr("Replace Function - Warning"), self.tr("The Replace feature is functional but may not work perfectly in some cases."))

        old_word, ok1 = QInputDialog.getText(self, self.tr("Replace Word"), self.tr("Enter the word you want to replace:"))
        if ok1 and old_word.strip():
            new_word, ok2 = QInputDialog.getText(self, self.tr("Replace With"), self.tr("Enter the new word:"))
            if ok2:
                doc = self.textedit.document()
                cursor = doc.find(old_word)
                replaced = 0
                while cursor and not cursor.isNull():
                    cursor.insertText(new_word)
                    replaced += 1
                    cursor = doc.find(old_word)
                QMessageBox.information(self, self.tr("Replace Completed"), self.tr(f"Replaced {replaced} occurrence(s) of '{old_word}' with '{new_word}'."))

    
    def check_for_updates(self):
        # Keep a reference to the thread object to prevent it from being garbage collected
        self.update_thread = update_checker(REPO_OWNER, REPO_NAME, False)
        self.update_thread.update_check_completed.connect(self.on_update_check_completed)
        self.update_thread.start()

    
    def on_update_check_completed(self, release_info: dict):
        if release_info:
            # show info using first available tag
            tag = release_info.get("stable", {}).get("version") or release_info.get("prerelease", {}).get("version")
            QMessageBox.information(self, self.tr("Update"), self.tr("New version available: %s") % tag)
        else:
            QMessageBox.information(self, self.tr("Update"), self.tr("No updates available."))
    
    def open_encryption_tool(self):
        dlg = CryptoGUI(self)
        dlg.exec()

    def onModificationChanged(self, changed: bool):
        self.unsaved_changes_flag = True

    def autoSave(self):
        if not self.unsaved_changes_flag:
            return

        if self.file_path:
            fname = os.path.basename(self.file_path) + ".bptmp"
            temp_path = os.path.join(BUNNYPAD_TEMP, fname)
            with open(temp_path, "w", encoding="utf-8") as f:
                f.write("[TYPE:WITHPATH]\n")
                f.write(self.file_path + "\n")
                f.write("[DATA]\n")
                f.write(self.textedit.toPlainText())
            self.saveState(temp_path)
        else:
            temp_path = os.path.join(BUNNYPAD_TEMP, "unsaved_note.bptmp")
            text = self.textedit.toPlainText()
            encoded = binascii.hexlify(text.encode("utf-8")).decode("utf-8")
            with open(temp_path, "w", encoding="utf-8") as f:
                f.write("[TYPE:UNSAVED]\n")
                f.write(encoded)
            self.saveState(temp_path)
        self.statusBar().showMessage("Autosaved", 2000)

    def saveState(self, path: str):
        state = {"last_file": path}
        with open(STATE_FILE, "w") as f:
            json.dump(state, f)

    def loadState(self):
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r") as f:
                return json.load(f).get("last_file")
        return None

    def restoreSession(self):
        last_file = self.loadState()
        if last_file and os.path.exists(last_file):
            with open(last_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            if lines[0].startswith("[TYPE:UNSAVED]"):
                encoded = "".join(lines[1:]).strip()
                try:
                    decoded = binascii.unhexlify(encoded).decode("utf-8")
                except Exception:
                    decoded = ""
                self.textedit.setPlainText(decoded)
                self.file_path = None

            elif lines[0].startswith("[TYPE:WITHPATH]"):
                # Safely get path
                path = lines[1].strip() if len(lines) > 1 else None

                # Find "[DATA]" line safely
                data_index = None
                for i, line in enumerate(lines):
                    if line.strip() == "[DATA]":
                        data_index = i
                        break

                if data_index is not None:
                    content = "".join(lines[data_index + 1:])
                else:
                    content = ""

                # Apply content to textedit
                self.textedit.setPlainText(content)
                self.file_path = path
                self.unsaved_changes_flag = True
                self.textedit.document().setModified(True)

                
    def cleanupTemp(self):
        if BUNNYPAD_TEMP.exists():
            for fname in BUNNYPAD_TEMP.iterdir():
                if fname.suffix == ".bptmp":
                    try:
                        fname.unlink()
                    except Exception:
                        pass


# --------------------
# App entrypoint
# --------------------

def main():
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName(ORGANIZATION_NAME)
    stylesheet = load_stylesheet()
    if stylesheet:
        app.setStyleSheet(stylesheet)
    else:
        app.setStyle("Fusion")
    window = Notepad()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
