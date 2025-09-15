#!/usr/bin/env python3
# v11-PyQt6.py - PyQt6 variant
r"""
 ____                          ____           _ 
| __ ) _   _ _ __  _ __  _   _|  _ \ __ _  __| |
|  _ \| | | | '_ \| '_ \| | | | |_) / _` |/ _` |
| |_) | |_| | | | | | | | |_| |  __/ (_| | (_| |
|____/ \__,_|_| |_|_| |_|\__, |_|   \__,_|\__,_|
                         |___/                  
"""

import datetime
import importlib
import logging
import os
import platform
import shutil
import subprocess
import sys
import textwrap
import unicodedata
import webbrowser
import random
import json
import base64
import binascii
from pathlib import Path

# Optional third-party libraries
try:
    import distro
except Exception:
    distro = None

try:
    import psutil
except Exception:
    psutil = None

try:
    import requests
except Exception:
    requests = None

try:
    from fpdf import FPDF
except Exception:
    FPDF = None

# PyQt6 imports
try:
    from PyQt6.QtCore import (
        QCoreApplication,
        QFile,
        QPoint,
        QSize,
        Qt,
        QTextStream,
        QThread,
        QTimer
    )
    from PyQt6.QtCore import pyqtSignal as Signal
    from PyQt6.QtCore import pyqtSlot as Slot
    from PyQt6.QtGui import (
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
        QAction,  # moved here from QtWidgets
    )
    from PyQt6.QtPrintSupport import QPrintDialog, QPrinter
    from PyQt6.QtWidgets import (
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
        """Install dependencies using the specified pip command."""
        try:
            subprocess.run([
                pip_cmd, "install", "--no-cache-dir",
                "PyQt6", "distro", "fpdf", "psutil", "setuptools", "requests", "elevate", "pyperclip", "cryptography"
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
                    "pipx", "install", "PyQt6", "distro", "fpdf", 
                    "psutil", "setuptools", "requests", "elevate", "pyperclip", "cryptography"
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
try:
    import pyperclip
    CLIPBOARD_ENABLED = True
except ImportError:
    CLIPBOARD_ENABLED = False
try:
    from cryptography.hazmat.primitives import padding
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend
except ImportError:
    print("Cryptography package not found. Install with: pip install cryptography")
    sys.exit(1)

# --------------------
# Constants and paths
# --------------------
CURRENT_VERSION = "v11.0.27000.0915"
APP_NAME = "BunnyPad"
ORGANIZATION_NAME = "GSYT Productions"
REPO_OWNER = "GSYT-Productions"
REPO_NAME = "BunnyPad-SRC"
BUNNYPAD_TEMP = os.path.join(os.path.expanduser("~"), "BunnyPadTemp")
os.makedirs(BUNNYPAD_TEMP, exist_ok=True)
STATE_FILE = os.path.join(BUNNYPAD_TEMP, "state.json")
DIRTY_FILE = os.path.join(BUNNYPAD_TEMP, "dirty")

# ---------------- Crypto Engine ----------------
GERMAN_MARKER = "§"
GERMAN_WORDS = [
    "dost", "orden", "meer", "baum", "vogel", "fluss", "himmel", "freude",
    "licht", "schloss", "apfel", "garten", "wasser", "freund", "blume", "straße",
    "morgen", "nacht", "sonne", "mond", "stern", "eule", "hausaufgabe", "katze",
    "wolke", "freundlich", "schnell", "langsam", "laut", "ruhig", "schön",
    "schlecht", "freundschaft", "abenteuer", "trinken", "laufen", "springen",
    "tanzen", "schreiben", "musizieren", "singen", "fühlen", "träumen", "denken"
]

if getattr(sys, 'frozen', False):
    # Running as a PyInstaller bundled executable
    SCRIPT_DIR = Path(sys.executable).parent
else:
    # Running as a normal Python script
    SCRIPT_DIR = Path(__file__).parent.resolve()

IMAGES_DIR = SCRIPT_DIR / "images"

ICON_PATHS = {
    "bunnypad": str(SCRIPT_DIR / "bunnypad.png"),
    "gsyt": str(SCRIPT_DIR / "gsyt.png"),
    "bpdl": str(SCRIPT_DIR / "bpdl.png"),
    "new": str(IMAGES_DIR / "new.png"),
    "open": str(IMAGES_DIR / "open.png"),
    "save": str(IMAGES_DIR / "save.png"),
    "saveas": str(IMAGES_DIR / "saveas.png"),
    "exit": str(IMAGES_DIR / "exit.png"),
    "undo": str(IMAGES_DIR / "undo.png"),
    "redo": str(IMAGES_DIR / "redo.png"),
    "cut": str(IMAGES_DIR / "cut.png"),
    "copy": str(IMAGES_DIR / "copy.png"),
    "paste": str(IMAGES_DIR / "paste.png"),
    "delete": str(IMAGES_DIR / "delete.png"),
    "datetime": str(IMAGES_DIR / "datetime.png"),
    "charmap": str(IMAGES_DIR / "charmap.png"),
    "find": str(IMAGES_DIR / "find.png"),
    "replace": str(IMAGES_DIR / "replace.png"),
    "selectall": str(IMAGES_DIR / "selectall.png"),
    "wordwrap": str(IMAGES_DIR / "wordwrap.png"),
    "font": str(IMAGES_DIR / "font.png"),
    "info": str(IMAGES_DIR / "info.png"),
    "team": str(IMAGES_DIR / "team.png"),
    "cake": str(IMAGES_DIR / "cake.png"),
    "nocake": str(IMAGES_DIR / "nocake.png"),
    "support": str(IMAGES_DIR / "support.png"),
    "share": str(IMAGES_DIR / "share.png"),
    "update": str(IMAGES_DIR / "update.png"),
    "pdf": str(IMAGES_DIR / "pdf.png"),
    "printer": str(IMAGES_DIR / "printer.png"),
    "encryption": str(IMAGES_DIR / "encryption.png"),
    "status": str(IMAGES_DIR / "status.png"),
    "toolbar": str(IMAGES_DIR / "toolbar.png")
}

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

# Logging
log_filename = Path.home() / f"BunnyPad_update_log.{datetime.datetime.now().strftime('%Y-%m-%d_%H')}.log"
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(log_filename), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


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
                timeout=timeout,  # Reduced from 30 to 10 seconds
                check=False,
            )
        else:
            return subprocess.run(cmd, shell=shell, universal_newlines=text, timeout=timeout, check=False)
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
        logger.warning("Subprocess command failed: %s  Error: %s", cmd, e)
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
    # fallback to empty
    return ""

def load_stylesheet() -> str:
    """Load stylesheet.qss if present."""
    path = SCRIPT_DIR / "stylesheet.qss"
    if not path.exists():
        return ""
    try:
        f = QFile(str(path))
        if f.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
            stream = QTextStream(f)
            content = stream.readAll()
            f.close()
            return content
    except Exception:
        logger.exception("Failed loading stylesheet")
    return ""

def parse_rccm_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            hexdata = f.read().strip()
        decoded_json = bytes.fromhex(hexdata).decode("utf-8")
        return json.loads(decoded_json)
    except Exception:
        return None

def save_as_pdf(text: str, file_path: str) -> bool:
    """Save text as PDF using fpdf (if available)."""
    if FPDF is None:
        logger.error("FPDF not available.")
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
        logger.exception("Failed to save PDF")
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
        logger.warning(f"Failed to get real Windows build: {e}")
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
        logger.warning(f"Failed to get Windows edition: {e}")
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
        logger.exception("identify_os failed")
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
        logger.exception("get_cpu_model failed")
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
        logger.exception("get_gpu_info failed")
        return "Not available"

def get_system_info() -> str:
    """Return assembled system info string."""
    try:
        parts = []
        parts.append(f"OS: {identify_os()}")
        parts.append(f"CPU: {get_cpu_model()}")
        try:
            if psutil:
                ram = psutil.virtual_memory().total / (1024 ** 3)
                parts.append(f"RAM: {ram:.2f} GB")
            else:
                parts.append("RAM: Unknown")
        except Exception:
            parts.append("RAM: Unknown")
        parts.append(f"GPU: {get_gpu_info()}")
        try:
            total, used, free = shutil.disk_usage(os.path.abspath(os.sep))
            parts.append(f"Disk: {total // (2 ** 30)} GB total, {free // (2 ** 30)} GB free")
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
        logger.exception("get_system_info failed")
        return "System information not available"

class CharacterWidget(QWidget):
    characterSelected = Signal(str)
    closed = Signal()

    def __init__(self, parent=None, as_window=False):
        flags = Qt.WindowType.Window if as_window else Qt.WindowType.Widget
        super().__init__(parent, flags)
        self.display_font = QFont()
        self.square_size = CHAR_MAP_MIN_FONT_SIZE
        self.columns = CHAR_MAP_DEFAULT_COLUMNS
        self.last_key = -1
        self.setMouseTracking(True)
        self._as_window = as_window
        if self._as_window:
            self.setObjectName("FloatingWindow")

        self.unicode_ranges = {
            "Basic Latin": (0x0020, 0x007F),
            "Latin-1 Supplement": (0x00A0, 0x00FF),
            "Arrows": (0x2190, 0x21FF),
            "Mathematical Operators": (0x2200, 0x22FF),
            "Geometric Shapes": (0x25A0, 0x25FF),
            "Dingbats": (0x2700, 0x27BF),
        }

        self.current_range_name = "Basic Latin"
        self.start_codepoint, self.end_codepoint = self.unicode_ranges[self.current_range_name]
        self.total_characters = self.end_codepoint - self.start_codepoint + 1
        self._last_tooltip_cp = None

        if self._as_window:
            self.setFixedSize(self.sizeHint())

    @staticmethod
    def _chr(cp: int) -> str:
        try:
            return chr(int(cp))
        except Exception:
            return ""

    def sizeHint(self) -> QSize:
        rows = (self.total_characters + self.columns - 1) // self.columns
        width = self.columns * self.square_size
        height = rows * self.square_size
        return QSize(width, height)

    def setColumns(self, columns: int):
        self.columns = max(1, int(columns))
        self.updateGeometry()
        self.update()
        if self._as_window:
            self.setFixedSize(self.sizeHint())

    def set_unicode_range(self, name: str) -> bool:
        if name in self.unicode_ranges:
            self.current_range_name = name
            self.start_codepoint, self.end_codepoint = self.unicode_ranges[name]
            self.total_characters = self.end_codepoint - self.start_codepoint + 1
            self.last_key = -1
            self._last_tooltip_cp = None
            self.updateGeometry()
            self.update()
            if self._as_window:
                self.setFixedSize(self.sizeHint())
            return True
        return False

    def get_codepoint_from_position(self, x: int, y: int) -> int:
        col = x // self.square_size
        row = y // self.square_size
        index = row * self.columns + col
        if 0 <= index < self.total_characters:
            return self.start_codepoint + index
        return -1

    def isValidCharacter(self, ch: str) -> bool:
        if not ch:
            return False
        try:
            return unicodedata.category(ch) != "Cn"
        except Exception:
            return False

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        pos = event.position().toPoint()  # PyQt6 uses position() returning QPointF
        codepoint = self.get_codepoint_from_position(pos.x(), pos.y())
        if codepoint == -1:
            if self._last_tooltip_cp is not None:
                QToolTip.hideText()
                self._last_tooltip_cp = None
            return
        if codepoint == self._last_tooltip_cp:
            return
        self._last_tooltip_cp = codepoint
        ch = self._chr(codepoint)
        if self.isValidCharacter(ch):
            tooltip_pos = self.mapToGlobal(pos)
            text = (
                f'<p>Character: <span style="font-size: 18pt; font-family:{self.display_font.family()}">'
                f"{ch}</span></p><p>Value: 0x{codepoint:x} ({codepoint})</p>"
                f"<p>Range: {self.current_range_name}</p>"
            )
            QToolTip.showText(tooltip_pos, text, self)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position().toPoint()
            codepoint = self.get_codepoint_from_position(pos.x(), pos.y())
            if codepoint != -1:
                self.last_key = codepoint
                ch = self._chr(codepoint)
                if self.isValidCharacter(ch):
                    self.characterSelected.emit(ch)
                self.update()
        else:
            super().mousePressEvent(event)

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.fillRect(event.rect(), QColor(50, 50, 50, 50))
        painter.setFont(self.display_font)
        fm = QFontMetrics(self.display_font)

        begin_row = max(0, event.rect().top() // self.square_size)
        end_row = min((self.total_characters + self.columns - 1) // self.columns - 1, event.rect().bottom() // self.square_size)
        begin_col = max(0, event.rect().left() // self.square_size)
        end_col = min(self.columns - 1, event.rect().right() // self.square_size)

        painter.setPen(QColor("lightgray"))
        for row in range(begin_row, end_row + 2):
            y = row * self.square_size
            painter.drawLine(0, y, self.columns * self.square_size, y)
        for col in range(begin_col, end_col + 2):
            x = col * self.square_size
            painter.drawLine(x, 0, x, ((self.total_characters + self.columns - 1) // self.columns) * self.square_size)

        painter.setPen(QColor("white"))
        font = QFont(self.display_font)
        font.setBold(True)
        painter.setFont(font)
        for row in range(begin_row, end_row + 1):
            for col in range(begin_col, end_col + 1):
                idx = row * self.columns + col
                if idx >= self.total_characters:
                    continue
                cp = self.start_codepoint + idx
                ch = self._chr(cp)
                if not ch:
                    continue
                x = col * self.square_size
                y = row * self.square_size
                if cp == self.last_key:
                    painter.fillRect(x + 1, y + 1, self.square_size - 2, self.square_size - 2, QColor("#ffdddd"))
                tw = fm.horizontalAdvance(ch)
                th = fm.ascent()
                tx = x + (self.square_size - tw) // 2
                ty = y + (self.square_size + th) // 2 - 2
                painter.drawText(tx, ty, ch)

    def closeEvent(self, event):
        self.closed.emit()
        super().closeEvent(event)

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
                logger.exception("ClickableLabel handler error")
        super().mousePressEvent(event)

    
    def set_click_handler(self, handler):
        self.click_handler = handler

class AboutDialog(QDialog):
    
    def __init__(self, display_os_str: str, current_directory_str: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.display_os = display_os_str
        self.current_dir = current_directory_str
        self.setWindowTitle(self.tr("About BunnyPad"))
        icon_path = get_icon_path("bunnypad")
        if icon_path:
            self.setWindowIcon(QIcon(icon_path))
        self.setup_ui()

    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        title = QLabel(self.tr("BunnyPad\u2122"))
        font = title.font()
        font.setPointSize(20)
        title.setFont(font)
        layout.addWidget(title)

        logo = ClickableLabel()
        pix = QPixmap(get_icon_path("bunnypad"))
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
                    "Copyright \u00a9 2023-2025 GSYT Productions, LLC\n"
                    "Copyright \u00a9 2024-2025 The BunnyPad Contributors"
                )
            )
        )

        layout.addWidget(QLabel(self.tr("BunnyPad is licensed under the Apache 2.0 License")))

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
            "バニーパッド",
            selected_anagram,
            "Cito — ad posteriorem illius lucernae formae confugite.",
            "celeriter, post illam lucernam commode formatam",
            "Make haste—bethink thyself abaft that fortuitously contoured lantern.",
            "(Noticing how CrDroid has overlays for even the most obscure apps, resulting in endless XMLs and customization... It fills you with determination)",
            "This copy of BunnyPad is ae compatible",
            "see: brains cannot be decompiled ^",
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
                + "Codename PBbunnypower Notepad Variant Bun Valley\n"
                + self.tr("Engine: PrettyFonts")
            )
        )

        layout.addWidget(QLabel(self.tr("You are running BunnyPad on ") + self.display_os))
        layout.addWidget(QLabel(self.tr("BunnyPad is installed at ") + self.current_dir))

        # center align children
        for i in range(layout.count()):
            try:
                item = layout.itemAt(i)
                if item and item.widget():
                    item.widget().setAlignment(Qt.AlignmentFlag.AlignHCenter)
            except Exception:
                pass

    
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
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        title = QLabel(self.tr("System Information"))
        font = title.font()
        font.setPointSize(20)
        title.setFont(font)
        layout.addWidget(title)

        logo = QLabel()
        pix = QPixmap(get_icon_path("bunnypad"))
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

class CreditsDialog(QDialog):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle(self.tr("About BunnyPad's Team"))
        self.setWindowIcon(QIcon(get_icon_path("bunnypad")))
        self.setup_ui()

    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        title = QLabel(self.tr("The Team Behind BunnyPad\u2122"))
        font = title.font()
        font.setPointSize(20)
        title.setFont(font)
        layout.addWidget(title)

        logo = ClickableLabel()
        pix = QPixmap(get_icon_path("gsyt"))
        if not pix.isNull():
            logo.setPixmap(pix)
        logo.set_click_handler(self.alan_egg)
        layout.addWidget(logo)

        layout.addWidget(
            QLabel(
                self.tr(
                    "GarryStraitYT: Lead Developer; PBbunnypower (Bunny): Main icon design, tester, project dedicated to her\n\n"
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

    
    def alan_egg(self, event):
        try:
            dlg = alan_walker_wia_egg(self)
            dlg.exec()
        except Exception:
            logger.exception("alan_egg failed")

class FeatureNotReady(QDialog):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Feature Not Ready: Work In Progress"))
        self.setWindowIcon(QIcon(get_icon_path("bunnypad")))
        self.setup_ui()

    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        title = QLabel(self.tr("BunnyPad\u2122"))
        font = title.font()
        font.setPointSize(20)
        title.setFont(font)
        layout.addWidget(title)

        logo = ClickableLabel()
        pix = QPixmap(get_icon_path("bunnypad"))
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

    
    def activate_null_easter_egg(self, event):
        gastertext = "❄︎☟︎☜︎ ☹︎✌︎👌︎📬︎📬︎📬︎ ✋︎❄︎ 🕈︎☟︎✋︎💧︎🏱︎☜︎☼︎💧︎📬︎📬︎📬︎ ☟︎⚐︎🕈︎ ✋︎☠︎❄︎☜︎☼︎☜︎💧︎❄︎✋︎☠︎☝︎📬︎📬︎📬︎" # THE LAB... IT WHISPERS... HOW INTERESTING...
        msg_box = QMessageBox(self)
        msg_box.setWindowIcon(QIcon(get_icon_path("bunnypad")))
        msg_box.setWindowTitle("🕈︎📬︎👎︎📬︎ ☝︎✌︎💧︎❄︎☜︎☼︎") # W.D. GASTER
        msg_box.setText(gastertext)
        msg_box.exec()

class TheCakeIsALie(QDialog):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Error: Cake_Is_Lie"))
        self.setWindowIcon(QIcon(get_icon_path("nocake")))
        self.setup_ui()

    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        title = QLabel(self.tr("A Critical Error Has Occurred"))
        font = title.font()
        font.setPointSize(20)
        title.setFont(font)
        layout.addWidget(title)

        logo = ClickableLabel()
        pix = QPixmap(get_icon_path("nocake"))
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
        self.setup_ui()

    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        title = QLabel(self.tr("BunnyPad\u2122"))
        font = title.font()
        font.setPointSize(20)
        title.setFont(font)
        layout.addWidget(title)

        logo = ClickableLabel()
        pix = QPixmap(get_icon_path("bunnypad"))
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
            "Join our Discord": "Join our Discord",
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
        self.lcd_number.setDigitCount(5)
        self.lcd_number.display(27000)
        main_layout.addWidget(self.lcd_number)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.reject)
        main_layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)

    
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

    def on_join_our_discord_clicked(self):
        webbrowser.open("https://discord.gg/w7ls")

class alan_walker_wia_egg(QDialog):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("BunnyPad"))
        self.setWindowIcon(QIcon(get_icon_path("bunnypad")))
        self.setup_ui()

    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        title = QLabel(self.tr("BunnyPad\u2122"))
        font = title.font()
        font.setPointSize(20)
        title.setFont(font)
        layout.addWidget(title)

        logo = ClickableLabel()
        pix = QPixmap(get_icon_path("bunnypad"))
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
            logger.exception("Update check failed")
            self.update_check_completed.emit({})

# --------------------
# Cryptography Engine
# --------------------
class CryptoEngine:
    def __init__(self):
        self.german_marker = GERMAN_MARKER
        self.german_words = GERMAN_WORDS.copy()

    # ---- Caesar ----
    @staticmethod
    def caesar_cipher(text, shift):
        result = ""
        for char in text:
            if char.isalpha():
                offset = 65 if char.isupper() else 97
                result += chr((ord(char) - offset + shift) % 26 + offset)
            else:
                result += char
        return result

    @staticmethod
    def caesar_decipher(text, shift):
        return CryptoEngine.caesar_cipher(text, -shift)

    # ---- Hex/Base64 ----
    @staticmethod
    def hex_encode(text):
        return text.encode("utf-8").hex()

    @staticmethod
    def hex_decode(text):
        return bytes.fromhex(text).decode("utf-8")

    @staticmethod
    def base64_encode(text):
        return base64.b64encode(text.encode("utf-8")).decode("utf-8")

    @staticmethod
    def base64_decode(text):
        return base64.b64decode(text).decode("utf-8")

    # ---- AES ----
    @staticmethod
    def valid_aes_key(key):
        return len(key) in (16, 24, 32)

    @staticmethod
    def aes_encrypt(plaintext, key):
        if not CryptoEngine.valid_aes_key(key):
            raise ValueError("AES key must be 16, 24, or 32 characters long")
        key_bytes = key.encode()
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(key_bytes), modes.CBC(iv), backend=default_backend())
        padder = padding.PKCS7(128).padder()
        padded = padder.update(plaintext.encode()) + padder.finalize()
        encryptor = cipher.encryptor()
        enc = encryptor.update(padded) + encryptor.finalize()
        return base64.b64encode(iv + enc).decode("utf-8")

    @staticmethod
    def aes_decrypt(ciphertext, key):
        if not CryptoEngine.valid_aes_key(key):
            raise ValueError("AES key must be 16, 24, or 32 characters long")
        raw = base64.b64decode(ciphertext)
        iv, ct = raw[:16], raw[16:]
        cipher = Cipher(algorithms.AES(key.encode()), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded = decryptor.update(ct) + decryptor.finalize()
        unpadder = padding.PKCS7(128).unpadder()
        return (unpadder.update(padded) + unpadder.finalize()).decode()

    # ---- German words insertion ----
    def insert_german_words(self, text, interval):
        if not interval or interval < 1:
            return text
        words = text.split()
        result = []
        for i, word in enumerate(words):
            result.append(word)
            if (i + 1) % interval == 0:
                result.append(self.german_marker + self.german_words[(i // interval) % len(self.german_words)])
        return ' '.join(result)

    def remove_german_words(self, text):
        return ' '.join(word for word in text.split() if not word.startswith(self.german_marker))

    # ---- Pipelines ----
    def encrypt_pipeline(self, text, shift, key, interval):
        step1 = self.insert_german_words(text, interval)
        step2 = self.caesar_cipher(step1, shift)
        step3 = self.hex_encode(step2)
        step4 = self.base64_encode(step3)
        encrypted = self.aes_encrypt(step4, key)
        debug_steps = {
            'Inserted German Words': step1,
            'Caesar Cipher': step2,
            'Hex Encoded': step3,
            'Base64 Encoded': step4,
            'AES Encrypted': encrypted
        }
        return encrypted, debug_steps

    def decrypt_pipeline(self, text, shift, key, interval):
        try:
            step1 = self.aes_decrypt(text, key)
            step2 = self.base64_decode(step1)
            step3 = self.hex_decode(step2)
            step4 = self.caesar_decipher(step3, shift)
            clean = self.remove_german_words(step4)
            debug_steps = {
                'AES Decrypted': step1,
                'Base64 Decoded': step2,
                'Hex Decoded': step3,
                'Caesar Deciphered': step4,
                'Cleaned Text': clean
            }
            return clean, debug_steps
        except Exception as e:
            return f"[!] Decryption error: {e}", {}

# --------------------
# Cryptography GUI
# --------------------

class CryptoGUI(QWidget):
    def __init__(self, parent=None, as_window=False):
        flags = Qt.WindowType.Window if as_window else Qt.WindowType.Widget
        super().__init__(parent, flags)
        self.setObjectName("CryptoGUI")
        self.engine = CryptoEngine()
        self.setWindowTitle("RCCMITOWOATAS Encryption Tool")
        icon = get_icon_path("bunnypad")
        if icon:
            self.setWindowIcon(QIcon(icon))
        #self.setGeometry(300, 300, 700, 600)
        self.init_ui()

    def init_ui(self):
        # Cross-version enum aliases for QSizePolicy
        try:
            SP_Expanding = QSizePolicy.Policy.Expanding
            SP_Fixed = QSizePolicy.Policy.Fixed
        except AttributeError:
            SP_Expanding = QSizePolicy.Expanding
            SP_Fixed = QSizePolicy.Fixed

        dpi = QGuiApplication.primaryScreen().logicalDotsPerInch() / 96.0

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(int(10*dpi), int(10*dpi), int(10*dpi), int(10*dpi))
        main_layout.setSpacing(int(8*dpi))

        # ===== SETTINGS & OPTIONS =====
        settings_group = QGroupBox("Settings")
        settings_outer_layout = QVBoxLayout()
        settings_outer_layout.setSpacing(int(6*dpi))

        # --- Grid Layout for settings ---
        settings_grid = QGridLayout()
        settings_grid.setSpacing(int(6*dpi))

        # Controls
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Encrypt", "Decrypt"])

        self.shift_spin = QSpinBox()
        self.shift_spin.setRange(-25, 25)
        self.shift_spin.setValue(3)

        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 10)
        self.interval_spin.setValue(2)

        self.key_box = QLineEdit()
        self.key_box.setPlaceholderText("AES key (16, 24, or 32 chars)")

        for w in (self.mode_combo, self.shift_spin, self.interval_spin, self.key_box):
            w.setSizePolicy(SP_Expanding, SP_Fixed)
            w.setMinimumHeight(int(26*dpi))

        # Row 0: Mode + Shift + Word Interval
        settings_grid.addWidget(QLabel("Mode:"), 0, 0)
        settings_grid.addWidget(self.mode_combo, 0, 1)
        settings_grid.addWidget(QLabel("Caesar Shift:"), 0, 2)
        settings_grid.addWidget(self.shift_spin, 0, 3)
        settings_grid.addWidget(QLabel("Word Interval:"), 0, 4)
        settings_grid.addWidget(self.interval_spin, 0, 5)

        # Row 1: AES Key + Options
        settings_grid.addWidget(QLabel("AES Key:"), 1, 0)
        settings_grid.addWidget(self.key_box, 1, 1, 1, 3)

        # Options group — checkboxes in a single line
        options_group = QGroupBox("Options")
        options_layout = QHBoxLayout()
        options_layout.setSpacing(int(10*dpi))

        self.critical_check = QCheckBox("Copy output to clipboard")
        self.verbose_check = QCheckBox("Show debug")

        options_layout.addWidget(self.critical_check)
        options_layout.addWidget(self.verbose_check)
        options_layout.addStretch(1)

        options_group.setLayout(options_layout)
        settings_grid.addWidget(options_group, 1, 4, 1, 2)

        settings_outer_layout.addLayout(settings_grid)
        settings_group.setLayout(settings_outer_layout)
        main_layout.addWidget(settings_group)

        # ===== FILE OPERATIONS =====
        file_group = QGroupBox("File Operations")
        file_layout = QHBoxLayout()
        file_layout.setSpacing(int(6*dpi))

        self.import_btn = QPushButton("Import .rccm File")
        self.export_btn = QPushButton("Export .rccm File")
        file_layout.addWidget(self.import_btn)
        file_layout.addWidget(self.export_btn)
        file_group.setLayout(file_layout)
        main_layout.addWidget(file_group)

        # ===== SPLITTER FOR MAIN AREAS =====
        splitter = QSplitter(Qt.Orientation.Vertical)

        # --- Input section ---
        input_widget = QWidget()
        input_layout = QVBoxLayout(input_widget)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.addWidget(QLabel("Input / Cipher Text:"))
        self.input_box = QTextEdit()
        input_layout.addWidget(self.input_box)
        btn_row = QHBoxLayout()
        self.go_btn = QPushButton("Run")
        self.copy_btn = QPushButton("Copy Output")
        btn_row.addWidget(self.go_btn)
        btn_row.addWidget(self.copy_btn)
        input_layout.addLayout(btn_row)

        # --- Output section ---
        output_widget = QWidget()
        output_layout = QVBoxLayout(output_widget)
        output_layout.setContentsMargins(0, 0, 0, 0)
        output_layout.addWidget(QLabel("Output:"))
        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)
        output_layout.addWidget(self.output_box)

        # --- Debug section ---
        debug_widget = QWidget()
        debug_layout = QVBoxLayout(debug_widget)
        debug_layout.setContentsMargins(0, 0, 0, 0)
        debug_layout.addWidget(QLabel("Debug Information:"))
        self.debug_box = QTextEdit()
        self.debug_box.setReadOnly(True)
        debug_layout.addWidget(self.debug_box)

        splitter.addWidget(input_widget)
        splitter.addWidget(output_widget)
        splitter.addWidget(debug_widget)
        splitter.setSizes([200, 150, 0])  # Debug starts hidden

        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

        # ===== DEBUG VISIBILITY TOGGLE =====
        def toggle_debug(checked: bool):
            if checked:
                # QMessageBox.information(self, "Debugging the Debugger", "[Show] toggle request acknowledged")
                self.debug_box.show()
                splitter.setSizes([200, 150, 100])
            else:
                # QMessageBox.information(self, "Debugging the Debugger", "[Hide] toggle request acknowledged")
                self.debug_box.hide()
                splitter.setSizes([200, 150, 0])

        self.debug_box.hide()
        self.verbose_check.toggled.connect(toggle_debug)

    # ---- UI Handlers ----
    def on_mode_changed(self):
        self.input_box.clear()
        self.output_box.clear()
        self.debug_box.clear()
        self.key_box.clear()
        self.copy_btn.setEnabled(False)
        self.critical_check.setChecked(False)
        self.verbose_check.setChecked(False)
        self.shift_spin.setValue(3)
        self.interval_spin.setValue(2)
        self.update_import_export_visibility()

    def update_import_export_visibility(self):
        mode = self.mode_combo.currentText().lower()
        self.import_btn.setVisible(mode == "decrypt")
        self.export_btn.setVisible(mode == "encrypt")

    def import_rccm_file(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Open RCCM File", "", "RCCM Files (*.rccm)")
        if not filepath:
            return
        config = parse_rccm_file(filepath)
        if not config:
            QMessageBox.warning(self, "Error", "Failed to parse the selected .rccm file.")
            return
        self.mode_combo.setCurrentText("Decrypt")
        self.shift_spin.setValue(config.get("caesar_shift", 0))
        self.interval_spin.setValue(config.get("german_interval", 2))
        self.output_box.setText(config.get("encrypted", ""))
        self.copy_btn.setEnabled(True)
        QMessageBox.information(self, "Import Successful", f"Imported {os.path.basename(filepath)}\nEnter your AES key and press Run to decrypt.")

    def export_rccm_file(self):
        encrypted_message = self.output_box.toPlainText().strip()
        if not encrypted_message:
            self.show_error("No encrypted output to export.")
            return
        key = self.key_box.text().strip()
        if not CryptoEngine.valid_aes_key(key):
            self.show_error("AES key must be exactly 16, 24, or 32 characters long to export config.")
            return
        config_data = {
            "encrypted": encrypted_message,
            "caesar_shift": self.shift_spin.value(),
            "aes_key_length": len(key),
            "german_interval": self.interval_spin.value(),
            "timestamp": datetime.datetime.now().isoformat()
        }
        hex_data = json.dumps(config_data, indent=2).encode("utf-8").hex()
        filepath, _ = QFileDialog.getSaveFileName(self, "Save RCCM Configuration File", "", "RCCM Files (*.rccm)")
        if filepath:
            if not filepath.lower().endswith(".rccm"):
                filepath += ".rccm"
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(hex_data)
                QMessageBox.information(self, "Export Successful", f"Configuration exported to:\n{filepath}")
            except Exception as e:
                self.show_error(f"Failed to write file:\n{e}")

    def run_crypto(self):
        text = self.input_box.toPlainText().strip()
        key = self.key_box.text().strip()
        shift = self.shift_spin.value()
        interval = self.interval_spin.value()
        mode = self.mode_combo.currentText().lower()
        verbose = self.verbose_check.isChecked()
        if mode == "decrypt" and not text and self.output_box.toPlainText().strip():
            text = self.output_box.toPlainText().strip()
        if not text:
            self.show_error("Input text/cipher is required.")
            return
        if not CryptoEngine.valid_aes_key(key):
            self.show_error("AES key must be exactly 16, 24, or 32 characters long.")
            return
        if mode == 'encrypt':
            output_text, debug_info = self.engine.encrypt_pipeline(text, shift, key, interval)
        else:
            output_text, debug_info = self.engine.decrypt_pipeline(text, shift, key, interval)
        self.output_box.setText(output_text)
        self.copy_btn.setEnabled(True)
        self.debug_box.setVisible(verbose)
        if verbose:
            debug_lines = [f"[{k}]: {v}" for k, v in debug_info.items()]
            self.debug_box.setText("\n\n".join(debug_lines))
        else:
            self.debug_box.clear()
        if self.critical_check.isChecked():
            if CLIPBOARD_ENABLED:
                import pyperclip
                pyperclip.copy(output_text)
                QMessageBox.information(self, "Clipboard", "Output copied to clipboard.")
            else:
                QMessageBox.warning(self, "Clipboard", "pyperclip not installed; clipboard functionality disabled.")

    def copy_output(self):
        if CLIPBOARD_ENABLED:
            import pyperclip
            text = self.output_box.toPlainText()
            if text:
                pyperclip.copy(text)
                QMessageBox.information(self, "Clipboard", "Output copied to clipboard.")
            else:
                self.show_error("No output text to copy.")
        else:
            QMessageBox.warning(self, "Clipboard", "pyperclip not installed; clipboard functionality disabled.")

    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)
# --------------------
# Main Notepad (kept compatible)
# --------------------
class Notepad(QMainWindow):
    def __init__(self):
        super().__init__()

        # --- Window setup (from Notepad) ---
        self.setWindowTitle(self.tr("Untitled - BunnyPad"))
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
        # 🔹 Theme toggling for dock when floating / docked
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

        # File menu
        file_menu = QMenu(self.tr("File"), self)
        menubar.addMenu(file_menu)
        new_action = QAction(QIcon(get_icon_path("new")), self.tr("New"), self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)

        open_action = QAction(QIcon(get_icon_path("open")), self.tr("Open..."), self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction(QIcon(get_icon_path("save")), self.tr("Save"), self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        save_as_action = QAction(QIcon(get_icon_path("saveas")), self.tr("Save As..."), self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        print_pdf_action = QAction(QIcon(get_icon_path("pdf")), self.tr("Print to PDF..."), self)
        print_pdf_action.setShortcut("Ctrl+Shift+P")
        print_pdf_action.triggered.connect(self.print_to_pdf)
        file_menu.addAction(print_pdf_action)

        print_action = QAction(QIcon(get_icon_path("printer")), self.tr("Print..."), self)
        print_action.setShortcut("Ctrl+P")
        print_action.triggered.connect(self.file_print)
        file_menu.addAction(print_action)

        file_menu.addSeparator()

        exit_action = QAction(QIcon(get_icon_path("exit")), self.tr("Exit"), self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = QMenu(self.tr("Edit"), self)
        menubar.addMenu(edit_menu)

        undo_action = QAction(QIcon(get_icon_path("undo")), self.tr("Undo"), self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self.textedit.undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction(QIcon(get_icon_path("redo")), self.tr("Redo"), self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(self.textedit.redo)
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        cut_action = QAction(QIcon(get_icon_path("cut")), self.tr("Cut"), self)
        cut_action.setShortcut("Ctrl+X")
        cut_action.triggered.connect(self.textedit.cut)
        edit_menu.addAction(cut_action)

        copy_action = QAction(QIcon(get_icon_path("copy")), self.tr("Copy"), self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(self.textedit.copy)
        edit_menu.addAction(copy_action)

        paste_action = QAction(QIcon(get_icon_path("paste")), self.tr("Paste"), self)
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(self.textedit.paste)
        edit_menu.addAction(paste_action)

        delete_action = QAction(QIcon(get_icon_path("delete")), self.tr("Delete"), self)
        delete_action.setShortcut("Del")
        delete_action.triggered.connect(lambda: self.textedit.textCursor().deleteChar())
        edit_menu.addAction(delete_action)

        edit_menu.addSeparator()

        datetime_action = QAction(QIcon(get_icon_path("datetime")), self.tr("Date and Time"), self)
        datetime_action.setShortcut("F5")
        datetime_action.triggered.connect(self.date_and_time)
        edit_menu.addAction(datetime_action)

        edit_menu.addSeparator()

        find_action = QAction(QIcon(get_icon_path("find")), self.tr("Find..."), self)
        find_action.setShortcut("Ctrl+F")
        find_action.triggered.connect(self.find_function)
        edit_menu.addAction(find_action)

        go_to_line_action = QAction(QIcon(get_icon_path("find")), self.tr("Go To Line"), self)
        go_to_line_action.setShortcut("Ctrl+G")
        go_to_line_action.triggered.connect(self.go_to_line)
        edit_menu.addAction(go_to_line_action)

        replace_action = QAction(QIcon(get_icon_path("replace")), self.tr("Replace..."), self)
        replace_action.setShortcut("Ctrl+H")
        replace_action.triggered.connect(self.feature_not_ready)
        edit_menu.addAction(replace_action)

        edit_menu.addSeparator()

        select_all_action = QAction(QIcon(get_icon_path("selectall")), self.tr("Select All"), self)
        select_all_action.setShortcut("Ctrl+A")
        select_all_action.triggered.connect(self.textedit.selectAll)
        edit_menu.addAction(select_all_action)

        # Format menu
        format_menu = QMenu(self.tr("Format"), self)
        menubar.addMenu(format_menu)

        word_wrap_action = QAction(QIcon(get_icon_path("wordwrap")), self.tr("Word Wrap"), self)
        word_wrap_action.setCheckable(True)
        word_wrap_action.setChecked(True)
        word_wrap_action.setShortcut("Ctrl+W")
        word_wrap_action.triggered.connect(self.toggle_word_wrap)
        format_menu.addAction(word_wrap_action)

        font_action = QAction(QIcon(get_icon_path("font")), self.tr("Font..."), self)
        font_action.setShortcut("Alt+F")
        font_action.triggered.connect(self.choose_font)
        format_menu.addAction(font_action)

        # View menu
        view_menu = QMenu(self.tr("View"), self)
        menubar.addMenu(view_menu)

        statusbar_action = QAction(QIcon(get_icon_path("status")), self.tr("Show statusbar"), self, checkable=True)
        statusbar_action.setChecked(True)
        statusbar_action.setShortcut("Alt+Shift+S")
        statusbar_action.triggered.connect(self.toggle_statusbar)
        view_menu.addAction(statusbar_action)

        toolbar_action = QAction(QIcon(get_icon_path("toolbar")), "Toolbar", self, checkable=True)
        toolbar_action.setChecked(True)
        toolbar_action.setShortcut("Alt+T")
        toolbar_action.triggered.connect(self.toggle_toolbar)
        view_menu.addAction(toolbar_action)

        #Add Tools Menu
        tools_menu = QMenu(self.tr("Tools"), self)
        menubar.addMenu(tools_menu)

        #Add starting point for RCCMITOWOATAS addition
        rcc_action = QAction(QIcon(get_icon_path("encryption")), self.tr("Text Encryption Tool"), self)
        rcc_action.triggered.connect(self.crypto_tool)
        tools_menu.addAction(rcc_action)

        # Move Charmap to Tools menu
        toggle_character_map_action = QAction(QIcon(get_icon_path("charmap")), self.tr("Character Map"), self)
        toggle_character_map_action.setCheckable(True)
        toggle_character_map_action.setShortcut("Ctrl+M")
        toggle_character_map_action.toggled.connect(self.toggle_character_map)
        tools_menu.addAction(toggle_character_map_action)
        self._toggle_character_map_action = toggle_character_map_action

        # Help menu
        help_menu = QMenu(self.tr("Help"), self)
        menubar.addMenu(help_menu)

        about_action = QAction(QIcon(get_icon_path("info")), self.tr("About BunnyPad"), self)
        about_action.setShortcut("Alt+H")
        about_action.triggered.connect(self.about)
        help_menu.addAction(about_action)

        system_action = QAction(QIcon(get_icon_path("info")), self.tr("About Your System"), self)
        system_action.setShortcut("Shift+F1")
        system_action.triggered.connect(self.sysinfo)
        help_menu.addAction(system_action)

        credits_action = QAction(QIcon(get_icon_path("team")), self.tr("Credits for BunnyPad"), self)
        credits_action.setShortcut("Alt+C")
        credits_action.triggered.connect(self.credits)
        help_menu.addAction(credits_action)

        cake_action = QAction(QIcon(get_icon_path("cake")), self.tr("Cake :D"), self)
        cake_action.setShortcut("Alt+A")
        cake_action.triggered.connect(self.cake)
        help_menu.addAction(cake_action)

        contact_support_action = QAction(QIcon(get_icon_path("support")), self.tr("Contact Us"), self)
        contact_support_action.setShortcut("Alt+S")
        contact_support_action.triggered.connect(self.support)
        help_menu.addAction(contact_support_action)

        download_action = QAction(QIcon(get_icon_path("share")), self.tr("Download BunnyPad Tools"), self)
        download_action.setShortcut("Ctrl+J")
        download_action.triggered.connect(self.download)
        help_menu.addAction(download_action)

        update_action = QAction(QIcon(get_icon_path("update")), self.tr("Check For Updates"), self)
        update_action.setShortcut("Alt+U")
        update_action.triggered.connect(self.check_for_updates)
        help_menu.addAction(update_action)

        # toolbar
        self.toolbar = QToolBar(self)
        self.toolbar.setMovable(True)
        def _toolbar_theme(floating: bool):
            # Set the objectName so QSS can style it dynamically
            self.toolbar.setObjectName("FloatingWindow" if floating else "")
            # Force QSS to re‑apply immediately
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
            self.setWindowTitle(self.tr("Untitled - BunnyPad"))

    
    def open_file(self):
        if self.unsaved_changes_flag:
            if not self.warn_unsaved_changes():
                return

        file_types = FILE_FILTERS["open"]
        path, _ = QFileDialog.getOpenFileName(self, self.tr("Open File"), "", file_types)
        if not path:
            return

        # Temporary safeguard: 10 MB hard cap to prevent resource-exhaustion DoS
        MAX_SAFE_SIZE = 10 * 1024 * 1024  # 10 MB
        try:
            file_size = os.path.getsize(path)
        except Exception:
            QMessageBox.critical(self, self.tr("Error"), self.tr("Cannot determine file size."))
            return

        if file_size > MAX_SAFE_SIZE:
            QMessageBox.warning(
                self,
                self.tr("File too large"),
                self.tr(
                    "This file exceeds 10 MB and cannot be opened safely.\n"
                    "This is a temporary safeguard against a reported resource-exhaustion vulnerability."
                )
            )
            return

        # Safe to open
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                self.textedit.setPlainText(f.read())
            self.file_path = path
            self.unsaved_changes_flag = False
            self.setWindowTitle(f"{os.path.basename(path)} - BunnyPad")
        except Exception:
            QMessageBox.critical(self, self.tr("Error"), self.tr("Unicode Error: Cannot open file"))
    
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
            self.unsaved_changes_flag = False
            self.setWindowTitle(f"{os.path.basename(self.file_path)} - BunnyPad")
            return True
        except Exception as e:
            QMessageBox.critical(self, self.tr("Error"), self.tr(f"Failed to save file: {e}"))
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
            self.setWindowTitle(f"*{os.path.basename(self.file_path)} - BunnyPad")
        else:
            self.setWindowTitle("*Untitled - BunnyPad")

    
    def file_print(self):
        try:
            dlg = QPrintDialog()
            if dlg.exec():
                self.textedit.print(dlg.printer())
        except Exception:
            logger.exception("Print failed")

    
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
            logger.exception("sysinfo failed")
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
        self.feature_not_ready()
        """
        Open the Cryptography tool window as a single instance,
        tied to the main window, and raise it if already open.
        """
        """try:
            # If already open & visible: just bring to front
            if hasattr(self, "crypto_window") and self.crypto_window is not None:
                if self.crypto_window.isVisible():
                    self.crypto_window.raise_()
                    self.crypto_window.activateWindow()
                    return
                else:
                    # Window exists but closed => delete reference
                    self.crypto_window.deleteLater()
                    self.crypto_window = None

            # Create a new instance, parented to the main window
            self.crypto_window = CryptoGUI(self, as_window=True)

            # Make sure that when user closes it manually, we clear the reference
            self.crypto_window.destroyed.connect(lambda: setattr(self, "crypto_window", None))

            # Show the new window
            self.crypto_window.show()
            self.crypto_window.raise_()
            self.crypto_window.activateWindow()

        except Exception:
            logger.exception("Failed to open CryptoGUI")"""
    
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
        dlg = TextEncToolDialog(self)
        dlg.exec_()

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

        self.textedit.document().setModified(False)
        self.unsaved_changes_flag = False

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
                path = lines[1].strip()
                try:
                    sep_index = lines.index("[DATA]\n")
                    content = "".join(lines[sep_index + 1:])
                except ValueError:
                    content = ""
                self.textedit.setPlainText(content)
                self.file_path = path
                self.unsaved_changes_flag = True
                
    def cleanupTemp(self):
        for fname in os.listdir(BUNNYPAD_TEMP):
            if fname.endswith(".bptmp"):
                try:
                    os.remove(os.path.join(BUNNYPAD_TEMP, fname))
                except Exception:
                    pass
        if os.path.exists(DIRTY_FILE):
            os.remove(DIRTY_FILE)


# --------------------
# App entrypoint
# --------------------

def main():
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
