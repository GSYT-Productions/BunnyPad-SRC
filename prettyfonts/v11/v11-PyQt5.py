r"""
 ____                          ____           _ 
| __ ) _   _ _ __  _ __  _   _|  _ \ __ _  __| |
|  _ \| | | | '_ \| '_ \| | | | |_) / _` |/ _` |
| |_) | |_| | | | | | | | |_| |  __/ (_| | (_| |
|____/ \__,_|_| |_|_| |_|\__, |_|   \__,_|\__,_|
                         |___/                  
"""
import sys, os, platform, shutil, subprocess, logging, ctypes
import importlib.util  # Secure module checking
from pathlib import Path

def is_module_available(module_name):
    """Check if a module is available before importing."""
    return importlib.util.find_spec(module_name) is not None

def is_debian_based():
    """Determine if the OS is Debian-based securely."""
    if is_module_available("distro"):
        import distro
        return distro.id().lower() in ["debian", "ubuntu", "linuxmint", "pop", "elementary", "kali", "raspbian"]
    return False

def install_with_pip(pip_cmd):
    """Install dependencies using the specified pip command."""
    subprocess.run([pip_cmd, "install", "PyQt5", "distro", "fpdf", "psutil", "setuptools", "requests"], check=True)

def create_venv(venv_dir):
    """Create a virtual environment if it does not already exist."""
    if not os.path.exists(venv_dir):
        print(f"Creating a virtual environment at {venv_dir}...")
        try:
            subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)
            return True
        except subprocess.CalledProcessError:
            print("Error: Failed to create a virtual environment.")
            return False
    return True

# Try to import required modules, install them if missing
try:
    import sys, os, platform, distro, unicodedata, textwrap, datetime, re, random, webbrowser, psutil, shutil, subprocess, requests
    from PyQt5.QtCore import *
    from fpdf import FPDF
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QTextEdit, QAction, QFileDialog, QWidget, QDialog, 
        QMenuBar, QMenu, QToolBar, QStatusBar, QVBoxLayout, QDockWidget, QLabel, 
        QToolTip, QPushButton, QFontDialog, QMessageBox, QProgressBar, QCheckBox
    )
    from PyQt5.QtGui import QTextCursor, QIcon, QFont, QPixmap, QPainter, QFontMetrics, QColor
    from PyQt5.QtPrintSupport import QPrintDialog

except ImportError:
    venv_dir = os.path.join(os.getcwd(), "venv")  # Virtual environment directory
    venv_pip = os.path.join(venv_dir, "bin", "pip") if platform.system() != "Windows" else os.path.join(venv_dir, "Scripts", "pip.exe")
    # Check if we are already in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("Virtual environment detected. Installing dependencies...")
        install_with_pip(os.path.join(sys.prefix, "bin", "pip") if platform.system() != "Windows" else os.path.join(sys.prefix, "Scripts", "pip.exe"))
    # On Debian-based systems, prefer pipx, but fall back to venv if needed
    elif is_debian_based():
        if shutil.which("pipx"):
            print("Using pipx to install dependencies...")
            subprocess.run(["pipx", "install", "PyQt5", "distro", "fpdf", "psutil", "requests", "setuptools"], check=True)
        else:
            print("Warning: pipx is not installed. Attempting to create a virtual environment...")
            if create_venv(venv_dir):
                install_with_pip(venv_pip)
            else:
                print("Error: Neither pipx nor venv is available. Please install pipx or create a virtual environment manually.")
    # On other Linux distros and Windows, use venv if not already present
    else:
        if create_venv(venv_dir):
            print("Using virtual environment's pip.")
            install_with_pip(venv_pip)
# Define the current version
current_version = "v11.0.26000.3038"
# Build a logfile path in the user's home directory.
log_filename = Path.home() / f"BunnyPad_update_log.{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler(str(log_filename)),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)
def save_as_pdf(text, file_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    # Split text into lines based on a specified width (e.g., 180)
    lines = textwrap.wrap(text, width=180)
    for line in lines:
        pdf.multi_cell(0, 10, txt=line)
    pdf.output(file_path)
def identify_os():
    os_name = platform.system()
    if os_name == "Linux":
        linux_distro_id = distro.id()
        linux_distro_version = distro.version()
        linux_distro_name = distro.name()
        linux_version = platform.release()
        display_OS = f"Linux {linux_distro_name} {linux_distro_version} - Kernel: {linux_version}"
    elif os_name == "Darwin":
        mac_version = platform.mac_ver()[0]
        mac_platform = "Apple Silicon" if platform.processor() == "arm" else "Intel"
        display_OS = f"macOS {mac_version} - Chip: {mac_platform}"
    elif os_name == "Windows":
        win_version = platform.release()
        win_variant = platform.win32_edition() or "(Wine Environment?)"
        display_OS = f"Windows {win_version} {win_variant}"
    else:
        display_OS = self.tr("Unknown Operating System")
    return display_OS
def get_cpu_model():
    os_name = platform.system()
    if os_name == "Windows":
        try:
            cpu_name = subprocess.check_output("wmic cpu get name", shell=True).decode().strip().split("\n")[1]
            return QCoreApplication.translate("SystemInfo", f"CPU Model Name: {cpu_name}")
        except subprocess.CalledProcessError:
            return QCoreApplication.translate("SystemInfo", "CPU Model Name: Not available")
    else:
        try:
            cpu_details = subprocess.check_output("lscpu", shell=True)
            for line in cpu_details.decode().split('\n'):
                if line.startswith("Model name:"):
                    cpu_model = line.split(":")[1].strip()
                    return QCoreApplication.translate("SystemInfo", f"CPU Model Name: {cpu_model}")
            return QCoreApplication.translate("SystemInfo", "CPU Model Name: Not available")
        except subprocess.CalledProcessError:
            return QCoreApplication.translate("SystemInfo", "CPU Model Name: Not available")
def get_system_info():
    system_info = []
    # RAM capacity
    memory = psutil.virtual_memory()
    ram = QCoreApplication.translate("SystemInfo", f"RAM Capacity: {memory.total / (1024**3):.2f} GB")
    system_info.append(ram)
    # Hard drive capacity (root directory)
    total, _, _ = shutil.disk_usage("/")
    diskspace = QCoreApplication.translate("SystemInfo", f"Hard Drive Capacity: {total / (1024**3):.2f} GB")
    system_info.append(diskspace)
    # CPU details
    system_info.append(get_cpu_model())
    return '\n'.join(system_info)
def show_current_directory():
    return os.getcwd()
class CharacterWidget(QWidget):
    characterSelected = pyqtSignal(str)
    def __init__(self, parent=None):
        super(CharacterWidget, self).__init__(parent)
        self.displayFont = QFont()
        self.squareSize = 24
        self.columns = 16
        self.lastKey = -1
        self.setMouseTracking(True)
    def updateFont(self, fontFamily):
        self.displayFont.setFamily(fontFamily)
        self.squareSize = max(24, QFontMetrics(self.displayFont).xHeight() * 3)
        self.adjustSize()
        self.update()
    def updateSize(self, fontSize):
        fontSize, _ = fontSize.toInt()
        self.displayFont.setPointSize(fontSize)
        self.squareSize = max(24, QFontMetrics(self.displayFont).xHeight() * 3)
        self.adjustSize()
        self.update() 
    def updateStyle(self, fontStyle):
        fontDatabase = QFontDatabase()
        oldStrategy = self.displayFont.styleStrategy()
        self.displayFont = fontDatabase.font(self.displayFont.family(),
                fontStyle, self.displayFont.pointSize())
        self.displayFont.setStyleStrategy(oldStrategy)
        self.squareSize = max(24, QFontMetrics(self.displayFont).xHeight() * 3)
        self.adjustSize()
        self.update()
    def updateFontMerging(self, enable):
        if enable:
            self.displayFont.setStyleStrategy(QFont.PreferDefault)
        else:
            self.displayFont.setStyleStrategy(QFont.NoFontMerging)
        self.adjustSize()
        self.update()
    # Add the following method to the class
    def setColumns(self, columns):
        self.columns = columns
        self.adjustSize()
        self.update()
    def sizeHint(self):
        return QSize(self.columns * self.squareSize, int((65536 / self.columns) * self.squareSize))
    def mouseMoveEvent(self, event):
        widgetPosition = self.mapFromGlobal(event.globalPos())
        key = (widgetPosition.y() // self.squareSize) * self.columns + widgetPosition.x() // self.squareSize
        text = '<p>Character: <span style="font-size: 24pt; font-family: %s">%s</span><p>Value: 0x%x' % (self.displayFont.family(), self._chr(key), key)
        QToolTip.showText(event.globalPos(), text, self)
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.lastKey = (event.y() // self.squareSize) * self.columns + event.x() // self.squareSize
            key_ch = self._chr(self.lastKey)
            if unicodedata.category(key_ch) != 'Cn':
                self.characterSelected.emit(key_ch)
            self.update()
        else:
            super(CharacterWidget, self).mousePressEvent(event)
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(event.rect(), Qt.white)
        painter.setFont(self.displayFont)
        redrawRect = event.rect()
        beginRow = redrawRect.top() // self.squareSize
        endRow = redrawRect.bottom() // self.squareSize
        beginColumn = redrawRect.left() // self.squareSize
        endColumn = redrawRect.right() // self.squareSize
        painter.setPen(Qt.gray)
        for row in range(beginRow, endRow + 1):
            for column in range(beginColumn, endColumn + 1):
                painter.drawRect(column * self.squareSize,
                        row * self.squareSize, self.squareSize,
                        self.squareSize)
        fontMetrics = QFontMetrics(self.displayFont)
        painter.setPen(Qt.black)
        for row in range(beginRow, endRow + 1):
            for column in range(beginColumn, endColumn + 1):
                key = row * self.columns + column
                painter.setClipRect(column * self.squareSize,
                        row * self.squareSize, self.squareSize,
                        self.squareSize)
                if key == self.lastKey:
                    painter.fillRect(column * self.squareSize + 1,
                            row * self.squareSize + 1, self.squareSize,
                            self.squareSize, Qt.red)
                key_ch = self._chr(key)
                painter.drawText(column * self.squareSize + (self.squareSize // 2) - fontMetrics.width(key_ch) // 2,
                 row * self.squareSize + 4 + fontMetrics.ascent(),
                 key_ch)
    @staticmethod
    def _chr(codepoint):
            # Python v3.
            return chr(codepoint)
    def setColumns(self, columns):
        self.columns = columns
        self.adjustSize()
        self.update()
class AboutDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(AboutDialog, self).__init__(*args, **kwargs)
        self.setWindowTitle(self.tr("About BunnyPad"))
        self.setWindowIcon(QIcon(os.path.join('./bunnypad.png')))
        layout = QVBoxLayout(self)
        title = QLabel(self.tr("BunnyPad™"))
        font = title.font()
        font.setPointSize(20)
        title.setFont(font)
        layout.addWidget(title)
        logo = QLabel()
        logo.setPixmap(QPixmap(os.path.join('./bunnypad.png')))
        layout.addWidget(logo)
        layout.addWidget(QLabel(self.tr("A Notepad Clone named in part after Innersloth's Off-Topic Regular, PBbunnypower [aka Bunny]")))
        layout.addWidget(QLabel(self.tr("Copyright © 2023-2024 GSYT Productions, LLC\nCopyright © 2024 The BunnyPad Contributors")))
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
            original_phrase # Original phrase as the 11th possibility
            ]
        selected_anagram = random.choice(anagrams)
        phrases = [self.tr("\"It was a pleasure to [learn]\""),
                   self.tr("\"So it was the hand that started it all ... \nHis hands had been infected, and soon it would be his arms ... \nHis hands were ravenous.\""),
                   self.tr("Hopping past opinions"),
                   self.tr("\"Is it true that a long time ago, firemen used to put out fires and not burn books?\""),
                   self.tr("\"Fahrenheit 451, the temperature at which paper spontaneously combusts\""),
                   self.tr("\"Do you want to know what's inside all these books? Insanity. The Eels want to measure their place in the universe,\n so they turn to these novels about non-existent people. Or worse, philosophers. \n Look, here's Spinoza. One expert screaming down another expert's throat. \"We have free will. No, all of our actions are predetermined.\" \nEach one says the opposite, and a man comes away lost, feeling more bestial and lonely than before. \nNow, if you don't want a person unhappy, you don't give them two sides of a question to worry about. Just give 'em one.. Better yet, none.\""),
                   "バニーパッド",
                   selected_anagram]
        random_phrase = random.choice(phrases)
        layout.addWidget(QLabel(random_phrase))
        layout.addWidget(QLabel(self.tr("Developer Information: \n Build: ") + current_version + self.tr("\n Internal Name: ") + "Codename PBbunnypower Notepad Variant Bun Valley" + self.tr("\n Engine: PrettyFonts")))
        layout.addWidget(QLabel(self.tr("::WARNING:: This is an unstable build. There will be bugs.")))
        layout.addWidget(QLabel(self.tr("You are running BunnyPad on " )+ display_os))
        layout.addWidget(QLabel(self.tr("BunnyPad is installed at ") + current_directory))
        for i in range(layout.count()):
            layout.itemAt(i).setAlignment(Qt.AlignmentFlag.AlignHCenter)
        #Add click event for PBbunnypower easter egg
        logo.mousePressEvent = self.activate_PBbunnypower_easter_egg
        #logo.mousePressEvent = oops_egg().exec()
    def activate_PBbunnypower_easter_egg(self, event):
        # PBbunnypower easter egg code
        msg_box = QMessageBox()
        msg_box.setWindowTitle(self.tr("Message to PBbunnypower"))
        msg_box.setWindowIcon(QIcon(os.path.join('./bunnypad.png')))
        msg_box.setText(self.tr("BunnyPad is successful. We did it. People might try to destroy it, but we will not back down."))
        msg_box.exec()
class SystemInfoDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(SystemInfoDialog, self).__init__(*args, **kwargs)
        self.setWindowTitle(self.tr("System Information"))
        self.setWindowIcon(QIcon(os.path.join('./bunnypad.png')))
        layout = QVBoxLayout(self)
        title = QLabel(self.tr("System Information"))
        font = title.font()
        font.setPointSize(20)
        title.setFont(font)
        layout.addWidget(title)
        logo = QLabel()
        logo.setPixmap(QPixmap(os.path.join('./bunnypad.png')))
        layout.addWidget(logo)
        layout.addWidget(QLabel(systeminfo))
        layout.addWidget(QLabel(self.tr("Operating System: ") + display_os))
        layout.addWidget(QLabel(self.tr("Installation Directory: ") + current_directory))
        for i in range(layout.count()):
            layout.itemAt(i).setAlignment(Qt.AlignmentFlag.AlignHCenter)       
class CreditsDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(CreditsDialog, self).__init__(*args, **kwargs)
        self.setWindowTitle(self.tr("About BunnyPad's Team"))
        self.setWindowIcon(QIcon(os.path.join('./bunnypad.png')))
        layout = QVBoxLayout(self)
        title = QLabel(self.tr("The Team Behind BunnyPad™"))
        font = title.font()
        font.setPointSize(20)
        title.setFont(font)
        layout.addWidget(title)
        logo = QLabel()
        logo.setPixmap(QPixmap(os.path.join('./gsyt.png')))
        layout.addWidget(logo)
        layout.addWidget(QLabel(self.tr("GarryStraitYT: Lead Developer; PBbunnypower (Bunny): Main icon design, tester, project dedicated to her \n\n") + "I-San: " + self.tr("Beta Tester\nDinoDude: Github contributor \nBunnyFndr: Icon Finder and Bug Tester")))
        for i in range(layout.count()):
            layout.itemAt(i).setAlignment(Qt.AlignmentFlag.AlignHCenter)
        # Add click event for escargot easter egg
        logo.mousePressEvent = self.alan_egg
    def alan_egg(self, event):
        AlanWalkerWIAEgg().exec()
class FeatureNotReady(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Feature Not Ready: Work In Progress"))
        self.setWindowIcon(QIcon(os.path.join('bunnypad.png')))
        layout = QVBoxLayout(self)
        title = QLabel(self.tr("BunnyPad™"))
        font = title.font()
        font.setPointSize(20)
        title.setFont(font)
        logo = QLabel()
        logo.setPixmap(QPixmap(os.path.join('bunnypad.png')))
        message = QLabel(self.tr("The requested feature is either incomplete or caused instabilities during testing and has been disabled until further notice. We apologize for the inconvenience."))
        ok_button = QPushButton(self.tr("OK"))
        ok_button.clicked.connect(self.accept)
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(logo, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(message, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(ok_button, alignment=Qt.AlignmentFlag.AlignHCenter)
        # Add click event for song quote easter egg
        logo.mousePressEvent = self.activate_see_you_again_easter_egg
    def activate_see_you_again_easter_egg(self, event):
        song = (self.tr("How can we not talk about family when family's all that we got? \n"
                "Everything I went through, you were standing there by my side, \n"
                "And now you gon' be with me for the last ride."))
        msg_box = QMessageBox()
        msg_box.setWindowIcon(QIcon(os.path.join('bunnypad.png')))
        msg_box.setWindowTitle(self.tr("See You Again"))
        msg_box.setText(song)
        msg_box.exec()
class TheCakeIsALie(QDialog):
    def __init__(self, parent=None):
        super(TheCakeIsALie, self).__init__(parent)
        self.setWindowTitle(self.tr("Error: Cake_Is_Lie"))
        self.setWindowIcon(QIcon(os.path.join('./images/nocake.png')))
        layout = QVBoxLayout(self)
        title = QLabel(self.tr("A Critical Error Has Occurred"))
        font = title.font()
        font.setPointSize(20)
        title.setFont(font)
        logo = QLabel()
        logo.setPixmap(QPixmap(os.path.join('./images/nocake.png')))
        message = QLabel(self.tr("Unfortunately, there is no cake. You have fallen for a trap. Where we promised a tasty dessert, there is instead deception. In other words, THE CAKE IS A LIE!"))
        ok_button = QPushButton(self.tr("OK"))
        ok_button.clicked.connect(self.accept)
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(logo, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(message, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(ok_button, alignment=Qt.AlignmentFlag.AlignHCenter)
        # Add click event for the other easter egg
        logo.mousePressEvent = self.momentum_easteregg
    def momentum_easteregg(self, event):
        quote = self.tr("Momentum, a function of mass and velocity, is conserved between portals. In layman's terms, speedy thing goes in, speedy thing comes out.")
        msg_box = QMessageBox()
        msg_box.setWindowIcon(QIcon(os.path.join('./bunnypad.png')))
        msg_box.setWindowTitle(self.tr("Momentum and Portals"))
        msg_box.setText(quote)
        msg_box.exec()
class ContactUs(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle(self.tr("Contact BunnyPad Support"))
        self.setWindowIcon(QIcon(os.path.join('./bunnypad.png')))
        layout = QVBoxLayout(self)
        title = QLabel(self.tr("BunnyPad™"))
        font = title.font()
        font.setPointSize(20)
        title.setFont(font)
        layout.addWidget(title)
        logo = QLabel()
        logo.setPixmap(QPixmap(os.path.join('./bunnypad.png')))
        layout.addWidget(logo)
        info_label = QLabel("Website: <a href='http://bunnypad.eclipse.cx' style=\"color: #0078D7;\">http://bunnypad.eclipse.cx/</a> <br> GSYT Productions Server: <a href='https://guilded.gg/gsyt-productions' style=\"color: #0078D7;\">https://guilded.gg/gsyt-productions</a> <br> BunnyPad CarrotPatch Server: <a href='https://guilded.gg/bunnypad' style=\"color: #0078D7;\">https://guilded.gg/bunnypad</a><br>BunnyPad Donation Link: <a href='https://throne.com/bunnypad' style=\"color: #0078D7;\">https://throne.com/bunnypad</a> <br> Text Us: +1 (814) 204-2333")
        info_label.setTextFormat(Qt.TextFormat.RichText)
        info_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        info_label.setOpenExternalLinks(True)
        layout.addWidget(info_label)
        logo.mousePressEvent = self.activate_galaxynote7_easter_egg
        ok_button = QPushButton(self.tr("OK"))
        ok_button.clicked.connect(self.accept)
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(logo, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(info_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(ok_button, alignment=Qt.AlignmentFlag.AlignHCenter)
    def activate_galaxynote7_easter_egg(self, event):
        # galaxynote7 easter egg code
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Galaxy Note 7")
        msg_box.setWindowIcon(QIcon(os.path.join('./bunnypad.png')))
        msg_box.setText(self.tr("So I heard that the") + "Samsung Galaxy Note 7" + self.tr("was the bomb, rather literally"))
        msg_box.exec()
class DownloadOptions(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Download Options"))
        self.setWindowIcon(QIcon(QPixmap('./bunnypad.png')))
        main_layout = QVBoxLayout(self)
        # Text label
        text_label = QLabel(self.tr("Where do you want to go today?\n\nChoose one of the available download options:"))
        main_layout.addWidget(text_label)
        # Buttons layout (2x2 grid)
        buttons_layout = QGridLayout()
        main_layout.addLayout(buttons_layout)
        # Map of shortened forms to full names
        button_names = {
            "Latest Stable Release": "Latest Stable Release",
            "Latest Stable Source": "Latest Stable Source",
            "Latest CarrotPatch Build": "Latest CarrotPatch Build",
            "IconPacks": "IconPacks",
            "Stylesheets": "Stylesheets",
            "r3dfox Download": "r3dfox Download"
        }
        # Create buttons and add them to the grid
        row, col = 0, 0
        for full_name, object_name in button_names.items():
            button = QPushButton(full_name)
            button.setObjectName(object_name)
            button.clicked.connect(getattr(self, f"on_{object_name.replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '')}_clicked"))
            buttons_layout.addWidget(button, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1
        # LCD number widget
        self.lcd_number = QLCDNumber()
        self.lcd_number.setObjectName("EasterEgg_DownloadOptions")
        self.lcd_number.setSegmentStyle(QLCDNumber.SegmentStyle.Flat)
        self.lcd_number.setDigitCount(5)
        self.lcd_number.display(42069)
        main_layout.addWidget(self.lcd_number)
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.reject)
        main_layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)
    @pyqtSlot()
    def on_Latest_Stable_Release_clicked(self):
        url = "https://garrystraityt.itch.io/bunnypad"
        webbrowser.open(url)
    @pyqtSlot()
    def on_Latest_Stable_Source_clicked(self):
         url = "https://github.com/GSYT-Productions/BunnyPad-SRC/"
         webbrowser.open(url)
    @pyqtSlot()
    def on_Latest_CarrotPatch_Build_clicked(self):
        url = "https://github.com/GSYT-Productions/BunnyPad-SRC/tree/latest-carrotpatch"
        webbrowser.open(url)
    @pyqtSlot()
    def on_IconPacks_clicked(self):
        url = "https://gsyt-productions.github.io/BunnyPadCustomizer/IconPacks"
        webbrowser.open(url)
    @pyqtSlot()
    def on_Stylesheets_clicked(self):
        url = "https://gsyt-productions.github.io/BunnyPadCustomizer/stylesheets"
        webbrowser.open(url)
    @pyqtSlot()
    def on_r3dfox_Download_clicked(self):
        url = "https://github.com/Eclipse-Community/r3dfox/releases/"
        webbrowser.open(url)
class AlanWalkerWIAEgg(QDialog):
    def __init__(self, *args, **kwargs):
        super(AlanWalkerWIAEgg, self).__init__(*args, **kwargs)
        self.setWindowTitle(self.tr("BunnyPad"))
        self.setWindowIcon(QIcon(os.path.join('./bunnypad.png')))
        layout = QVBoxLayout(self)
        title = QLabel(self.tr("BunnyPad™"))
        font = title.font()
        font.setPointSize(20)
        title.setFont(font)
        layout.addWidget(title)
        logo = QLabel()
        logo.setPixmap(QPixmap(os.path.join('./bunnypad.png')))
        layout.addWidget(logo)
        layout.addWidget(QLabel(self.tr("\"I'm not playing by the rules if they were made by you\"")))
        for i in range(layout.count()):
            layout.itemAt(i).setAlignment(Qt.AlignmentFlag.AlignHCenter)
        # Add click event for escargot easter egg
        logo.mousePressEvent = self.activate_escargot_easter_egg
    def activate_escargot_easter_egg(self, event):
        msg_box = QMessageBox()
        layout = QVBoxLayout(self)
        msg_box.setWindowTitle(self.tr("Snails"))
        msg_box.setWindowIcon(QIcon(os.path.join('./bunnypad.png')))
        logo = QLabel()
        logo.setPixmap(QPixmap(os.path.join('./bunnypad.png')))
        layout.addWidget(logo)
        msg_box.setText("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n")
        msg_box.exec()
class UpdateChecker(QThread):
    update_check_completed = pyqtSignal(dict)

    def __init__(self, repo_owner, repo_name, use_pre_release):
        super().__init__()
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.use_pre_release = use_pre_release

    def run(self):
        release_info = self.check_for_updates()
        self.update_check_completed.emit(release_info)

    def get_latest_release(self):
        url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/releases"
        try:
            response = requests.get(url)
        except Exception as e:
            logger.error("Error fetching releases: %s", e)
            return None

        if response.status_code == 200:
            releases = response.json()
            for release in releases:
                # Respect pre-release flag.
                if (self.use_pre_release and release.get('prerelease', False)) or (not self.use_pre_release and not release.get('prerelease', False)):
                    assets = release.get('assets', [])
                    if assets:
                        asset = assets[0]
                        return {
                            'version': release.get('tag_name'),
                            'url': asset.get('browser_download_url'),
                            'name': asset.get('name'),
                            'prerelease': release.get('prerelease', False),
                            'tag_name': release.get('tag_name')
                        }
        else:
            logger.error("Failed to fetch releases. Status code: %s", response.status_code)
        return None

    def check_for_updates(self):
        latest_release = self.get_latest_release()
        if latest_release:
            latest_version = latest_release['version']
            if current_version != latest_version:
                return latest_release
        return None

class Downloader(QThread):
    progress = pyqtSignal(int, int, int)  # total size, downloaded size, percentage
    download_complete = pyqtSignal(str)

    def __init__(self, url, filename):
        super().__init__()
        self.url = url
        self.filename = filename

    def run(self):
        try:
            response = requests.get(self.url, stream=True)
        except Exception as e:
            logger.error("Download error: %s", e)
            return

        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0

        try:
            with open(self.filename, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
                        downloaded_size += len(chunk)
                        percentage = int(100 * downloaded_size / total_size) if total_size else 0
                        self.progress.emit(total_size, downloaded_size, percentage)
        except Exception as e:
            logger.error("Error writing file: %s", e)
            return

        self.download_complete.emit(self.filename)


class UpdateModule(QWidget):
    def __init__(self, repo_owner, repo_name):
        super().__init__()
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.use_pre_release = False

        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()

        # Localize the label text.
        self.label = QLabel(self.tr("Press 'Check for Updates' to begin."), self)
        self.layout.addWidget(self.label)

        self.progress_bar = QProgressBar(self)
        self.layout.addWidget(self.progress_bar)

        self.check_updates_button = QPushButton(self.tr("Check for Updates"), self)
        self.check_updates_button.clicked.connect(self.check_for_updates)
        self.layout.addWidget(self.check_updates_button)

        self.pre_release_checkbox = QCheckBox(self.tr("Include Pre-release Builds"), self)
        self.pre_release_checkbox.stateChanged.connect(self.toggle_pre_release)
        self.layout.addWidget(self.pre_release_checkbox)

        self.setLayout(self.layout)

    def toggle_pre_release(self, state):
        self.use_pre_release = bool(state)

    def check_for_updates(self):
        self.update_checker = UpdateChecker(self.repo_owner, self.repo_name, self.use_pre_release)
        self.update_checker.update_check_completed.connect(self.on_update_check_completed)
        self.update_checker.start()

    def on_update_check_completed(self, release_info):
        if release_info:
            prompt = self.tr("A new version ({version}) is available. Do you want to download it?").format(
                version=release_info['version'])
            reply = QMessageBox.question(
                self,
                self.tr("Update Available"),
                prompt,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.download_update(release_info)
        else:
            QMessageBox.information(self, self.tr("No Update"), self.tr("You are using the latest version."))
            self.label.setText(self.tr("No updates available."))

    def download_update(self, release_info):
        # Get a suitable directory based on the platform and user permissions.
        download_dir = self.get_download_directory(release_info['name'], release_info['tag_name'])
        download_path = os.path.join(download_dir, release_info['name'])

        self.label.setText(self.tr("Downloading update..."))
        self.downloader = Downloader(release_info['url'], download_path)
        self.downloader.progress.connect(self.update_progress)
        self.downloader.download_complete.connect(self.on_download_complete)
        self.downloader.start()

    @pyqtSlot(int, int, int)
    def update_progress(self, total_size, downloaded_size, percentage):
        self.progress_bar.setValue(percentage)
        self.label.setText(self.tr("Downloading update: {downloaded:.2f} MB / {total:.2f} MB").format(
            downloaded=downloaded_size / (1024 * 1024),
            total=total_size / (1024 * 1024)
        ))

    @pyqtSlot(str)
    def on_download_complete(self, filename):
        self.label.setText(self.tr("Download complete."))

        prompt_text = self.tr("Do you want to run the update now?")
        reply = QMessageBox.question(
            self,
            self.tr("Run Update"),
            prompt_text,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.run_update(filename)
        self.progress_bar.reset()

    def get_download_directory(self, release_name, tag_name):
        """
        Returns a directory where the update file can be downloaded and installed.
        Checks for writable system directories and falls back to user directories if needed.
        """
        target_dir = None
        platform = sys.platform

        # Define preferred install directories per platform.
        if platform.startswith("win"):
            program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
            target_dir = Path(program_files) / "BunnyPad"
        elif platform == "darwin":  # macOS
            target_dir = Path("/Applications") / "BunnyPad"
        else:  # Linux and other posix systems.
            target_dir = Path("/usr/local/bin") / "BunnyPad"

        if target_dir.exists() and os.access(str(target_dir), os.W_OK):
            return str(target_dir)
        else:
            parent_dir = target_dir.parent
            if os.access(str(parent_dir), os.W_OK):
                try:
                    target_dir.mkdir(parents=True, exist_ok=True)
                    return str(target_dir)
                except Exception as e:
                    logger.error("Unable to create directory %s: %s", target_dir, e)
            downloads = Path.home() / "Downloads"
            downloads.mkdir(parents=True, exist_ok=True)
            return str(downloads)

    def run_update(self, filename):
        """
        Run the downloaded update installer/executable.
        On Unix-like systems, we ensure the file is executable.
        On Windows, we only attempt to elevate if needed and if the user is allowed to.
        The user is informed why elevation might be required.
        After starting the update, the current process is terminated.
        """
        logger.info("Running update installer: %s", filename)

        if sys.platform != "win32":
            try:
                st = os.stat(filename)
                os.chmod(filename, st.st_mode | stat.S_IEXEC)
            except Exception as e:
                self.handle_error(self.tr("Error setting executable permissions: {error}").format(error=e))
                return

            try:
                subprocess.Popen([filename])
            except Exception as e:
                self.handle_error(self.tr("Error launching update: {error}").format(error=e))
                return

        else:
            try:
                is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            except Exception as e:
                logger.error("Error checking admin status: %s", e)
                is_admin = False

            file_path = Path(filename)
            parent_dir = file_path.parent
            needs_elevation = "program files" in str(parent_dir).lower()

            userdomain = os.environ.get("USERDOMAIN", "").lower()
            computername = os.environ.get("COMPUTERNAME", "").lower()
            likely_standard_user = (userdomain and computername and userdomain != computername)

            if needs_elevation and not is_admin and not likely_standard_user:
                reply = QMessageBox.question(
                    self,
                    self.tr("Elevation Required"),
                    self.tr("The update needs to be installed to a system folder that requires administrative privileges.\n"
                            "Would you like to allow the application to elevate its privileges?\n\n"
                            "Elevation is needed to write to a protected folder such as 'Program Files'."),
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes
                )
                if reply == QMessageBox.StandardButton.Yes:
                    try:
                        from elevate import elevate
                        logger.info("Attempting to elevate privileges...")
                        elevate(show_console=False)
                        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
                        if not is_admin:
                            self.handle_error(self.tr("Could not obtain administrative privileges."))
                            return
                    except Exception as e:
                        self.handle_error(self.tr("Elevation failed: {error}").format(error=e))
                        return
                else:
                    QMessageBox.information(self,
                                            self.tr("Proceeding Without Elevation"),
                                            self.tr("The update will be run without elevation. This might cause issues if installation requires admin rights."))

            try:
                subprocess.Popen([filename], shell=True)
            except Exception as e:
                self.handle_error(self.tr("Error launching update: {error}").format(error=e))
                return

        psutil.Process(os.getpid()).terminate()

    def handle_error(self, error_message):
        """Log an error, show a message box, and offer the user the option to view the error log."""
        logger.error(error_message)
        reply = QMessageBox.critical(
            self,
            self.tr("Error"),
            f"{error_message}\n\n{self.tr('Would you like to view the error log?')}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.open_log_file()

    def open_log_file(self):
        """Open the log file using the system's default text editor."""
        try:
            if sys.platform == 'win32':
                os.startfile(str(log_filename))
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', str(log_filename)])
            else:
                subprocess.Popen(['xdg-open', str(log_filename)])
        except Exception as e:
            logger.error("Could not open log file: %s", e)
            QMessageBox.critical(self, self.tr("Error"), self.tr("Could not open log file: {error}").format(error=e))
class Notepad(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(self.tr("Untitled - BunnyPad"))
        self.setWindowIcon(QIcon(os.path.join('bunnypad.png')))
        self.setGeometry(100, 100, 800, 600)
        self.file_path = None
        self.unsaved_changes_flag = False
        self.open_file_ran = False
        self.save_file_ran = False
        # Define repository details
        repo_owner = "GSYT-Productions"
        repo_name = "BunnyPad-SRC"
        self.update_module = UpdateModule(repo_owner, repo_name)
        self.textedit = QTextEdit(self)
        self.textedit.textChanged.connect(self.handle_text_changed)
        # Set up text edit widget
        self.textedit.setAcceptRichText(False)
        self.setCentralWidget(self.textedit)
        self.setAcceptDrops(True)
        # Create menu bar
        menubar = QMenuBar(self)
        self.setMenuBar(menubar)
        # Create File menu
        file_menu = QMenu(self.tr("File"), self)
        menubar.addMenu(file_menu)
        # Create New action
        new_action = QAction(QIcon("images/new.png"), self.tr("New"), self)
        new_action.setStatusTip(self.tr("Creates a new file."))
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        # Create Open action
        open_action = QAction(QIcon("images/open.png"), self.tr("Open..."), self)
        open_action.setStatusTip(self.tr("Opens a document."))
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        # Create Save action
        save_action = QAction(QIcon("images/save.png"), self.tr("Save"), self)
        save_action.setStatusTip(self.tr("Saves the document."))
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        # Create Save As action
        save_as_action = QAction(QIcon("images/saveas.png"), self.tr("Save As..."), self)
        save_as_action.setStatusTip(self.tr("Saves the document as the chosen file"))
        save_as_action.triggered.connect(self.save_file_as)
        save_as_action.setShortcut('Ctrl+Shift+S')
        file_menu.addAction(save_as_action)
        # Add separator
        file_menu.addSeparator()
        # Create Print to PDF action
        print_to_pdf_action = QAction(QIcon("images/pdf.png"), self.tr("Print to PDF..."), self)
        print_to_pdf_action.setStatusTip(self.tr("Save the document as a PDF file."))
        print_to_pdf_action.triggered.connect(self.print_to_pdf)
        print_to_pdf_action.setShortcut('Ctrl+Shift+P')
        file_menu.addAction(print_to_pdf_action)
        print_action = QAction(QIcon(os.path.join('images', 'printer.png')), self.tr("Print..."), self)
        print_action.setStatusTip(self.tr("Print current page"))
        print_action.triggered.connect(self.file_print)
        print_action.setShortcut('Ctrl+P')
        file_menu.addAction(print_action)
        # Add separator
        file_menu.addSeparator()
        # Create Exit action
        exit_action = QAction(QIcon("images/exit.png"), self.tr("Exit"), self)
        exit_action.setStatusTip(self.tr("Exits BunnyPad™"))
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        # Create Edit menu
        edit_menu = QMenu(self.tr("Edit"), self)
        menubar.addMenu(edit_menu)
        # Create Undo action
        undo_action = QAction(QIcon("images/undo.png"), self.tr("Undo"), self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self.textedit.undo)
        edit_menu.addAction(undo_action)
        # Create Redo action
        redo_action = QAction(QIcon("images/redo.png"), self.tr("Redo"), self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(self.textedit.redo)
        edit_menu.addAction(redo_action)
        # Add separator
        edit_menu.addSeparator()
        # Create Cut action
        cut_action = QAction(QIcon("images/cut.png"), self.tr("Cut"), self)
        cut_action.setStatusTip(self.tr("Moves selected text to clipboard"))
        cut_action.setShortcut("Ctrl+X")
        cut_action.triggered.connect(self.textedit.cut)
        edit_menu.addAction(cut_action)
        # Create Copy action
        copy_action = QAction(QIcon("images/copy.png"), self.tr("Copy"), self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.setStatusTip(self.tr("Copies the selected text to the clipboard."))
        copy_action.triggered.connect(self.textedit.copy)
        edit_menu.addAction(copy_action)
        # Create Paste action
        paste_action = QAction(QIcon("images/paste.png"), self.tr("Paste"), self)
        paste_action.setStatusTip(self.tr("Pastes the text currently in the clipboard."))
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(self.textedit.paste)
        edit_menu.addAction(paste_action)
        # Create Delete action
        delete_action = QAction(QIcon("images/delete.png"), self.tr("Delete"), self)
        delete_action.setStatusTip(self.tr("Deletes the character after the cursor position."))
        delete_action.setShortcut("Del")
        delete_action.triggered.connect(lambda: self.textedit.textCursor().deleteChar())
        edit_menu.addAction(delete_action)
        # Create Date/Time Action
        datetime_action = QAction(QIcon("images/datetime.png"), self.tr("Date and Time"), self)
        datetime_action.setStatusTip(self.tr("Inserts the current date and time, including milliseconds."))
        datetime_action.setShortcut("F5")
        datetime_action.triggered.connect(self.dateTime)
        edit_menu.addAction(datetime_action)
        # Add separator
        edit_menu.addSeparator()
        # Create Action for showing/hiding Character Map in Edit Menu
        toggle_character_map_action = QAction(QIcon("images/charmap.png"), self.tr("Character Map"), self, checkable=True)
        toggle_character_map_action.setChecked(False)
        toggle_character_map_action.setStatusTip(self.tr("Toggle Character Map"))
        toggle_character_map_action.setShortcut("Ctrl+M")
        toggle_character_map_action.toggled.connect(self.toggle_character_map)
        edit_menu.addAction(toggle_character_map_action)
        edit_menu.addSeparator()
        # Create Find action
        find_action = QAction(QIcon("images/find.png"), self.tr("Find..."), self)
        find_action.setShortcut("Ctrl+F")  # Ctrl+F
        find_action.setStatusTip(self.tr("Find a word..."))
        find_action.triggered.connect(self.find_function)
        edit_menu.addAction(find_action)
        # Go to line
        gtl_action = QAction(QIcon("images/find.png"), self.tr("Go To Line"), self)
        gtl_action.setShortcut("Ctrl+G")  # Ctrl+G
        gtl_action.setStatusTip(self.tr("Go to a specified line"))
        gtl_action.triggered.connect(self.go_to_line)
        # gtl_action.triggered.connect(self.FeatureNotReady)
        edit_menu.addAction(gtl_action)
        # Create Replace action
        replace_action = QAction(QIcon("images/replace.png"), self.tr("Replace..."), self)
        replace_action.setStatusTip(self.tr("Currently in development..."))
        replace_action.setShortcut("Ctrl+H")
        replace_action.triggered.connect(self.FeatureNotReady)
        # replace_action.triggered.connect(self.replace_function)
        edit_menu.addAction(replace_action)
        # Add separator
        edit_menu.addSeparator()
        # Create Select All action
        select_all_action = QAction(QIcon("images/selectall.png"), self.tr("Select All"), self)
        select_all_action.setStatusTip(self.tr("Select all the text in the current document."))
        select_all_action.setShortcut("Ctrl+A")
        select_all_action.triggered.connect(self.textedit.selectAll)
        edit_menu.addAction(select_all_action)
        # Create Format menu
        format_menu = QMenu(self.tr("Format"), self)
        menubar.addMenu(format_menu)
        # Create Word Wrap action
        word_wrap_action = QAction(QIcon("images/wordwrap.png"),self.tr("Word Wrap"), self)
        word_wrap_action.setStatusTip(self.tr("Toggles wrapping the words to the window."))
        word_wrap_action.setShortcut("Ctrl+W")
        word_wrap_action.setCheckable(True)
        word_wrap_action.setChecked(True)
        word_wrap_action.triggered.connect(self.toggle_word_wrap)
        format_menu.addAction(word_wrap_action)
        # Create Font action
        font_action = QAction(QIcon("images/font.png"),self.tr("Font..."), self)
        font_action.setStatusTip(self.tr("Change the current font."))
        font_action.setShortcut("Alt+F")
        font_action.triggered.connect(self.choose_font)
        format_menu.addAction(font_action)
        # Create View menu
        view_menu = QMenu(self.tr("View"), self)
        menubar.addMenu(view_menu)
        help_menu = self.menuBar().addMenu(self.tr("Help"))
        about_action = QAction(QIcon(os.path.join('images/info.png')), self.tr("About BunnyPad"), self)
        about_action.setStatusTip(self.tr("Find out more about BunnyPad"))
        about_action.setShortcut("Alt+H")
        about_action.triggered.connect(self.about)
        help_menu.addAction(about_action)
        system_action = QAction(QIcon(os.path.join('images/info.png')), self.tr("About Your System"), self)
        system_action.setStatusTip(self.tr("Find out more about BunnyPad's operating environment"))
        system_action.setShortcut("Shift+F1")
        system_action.triggered.connect(self.sysinfo)
        help_menu.addAction(system_action)
        credits_action = QAction(QIcon(os.path.join('images/team.png')), self.tr("Credits for BunnyPad"), self)
        credits_action.setStatusTip(self.tr("Find out more about BunnyPad's Team"))
        credits_action.setShortcut("Alt+C")
        credits_action.triggered.connect(self.credits)
        help_menu.addAction(credits_action)
        cake_action = QAction(QIcon(os.path.join('images/cake.png')), self.tr("Cake :D"), self)
        cake_action.setStatusTip(self.tr("Click here for some Cake"))
        cake_action.setShortcut("Alt+A")
        cake_action.triggered.connect(self.cake)
        help_menu.addAction(cake_action)
        contact_support_action = QAction(QIcon(os.path.join('images/support.png')), self.tr("Contact Us"), self)
        contact_support_action.setStatusTip(self.tr("Find out how to contact the team!"))
        contact_support_action.setShortcut("Alt+S")
        contact_support_action.triggered.connect(self.support)
        help_menu.addAction(contact_support_action)
        # For v11: Source Code Download (Added in v10 [Decipad] instead)
        download_action = QAction(QIcon("images/share.png"), self.tr("Download BunnyPad Tools"), self)
        download_action.setStatusTip(self.tr("For BunnyPad Users to Customize their BunnyPad"))
        download_action.setShortcut("Ctrl+J")
        download_action.triggered.connect(self.download)
        # download_action.triggered.connect(self.FeatureNotReady)
        help_menu.addAction(download_action)
        # Updater
        update_action = QAction(QIcon("images/update.png"), self.tr("Check For Updates"), self)
        update_action.setStatusTip(self.tr("Download The Latest Version directly in BunnyPad"))
        update_action.setShortcut("Alt+U")
        update_action.triggered.connect(self.check_for_updates)
        #update_action.triggered.connect(self.FeatureNotReady)
        help_menu.addAction(update_action)
        # Create the statusbar action
        statusbar_action = QAction(self.tr("Show statusbar"), self, checkable=True)
        statusbar_action.setStatusTip(self.tr("Toggle statusbar"))
        statusbar_action.setShortcut("Alt+Shift+S")
        statusbar_action.setChecked(True)
        statusbar_action.triggered.connect(self.toggle_statusbar)
        view_menu.addAction(statusbar_action)
        # Connect the statusbar action to the update_statusbar method
        statusbar_action.triggered.connect(self.update_statusbar)
        # Create Toolbar action
        toolbar_action = QAction("Toolbar", self, checkable=True)
        toolbar_action.setStatusTip(self.tr("Toggle toolbar"))
        toolbar_action.setShortcut("Alt+T")
        toolbar_action.setChecked(True)
        toolbar_action.triggered.connect(self.toggle_toolbar)
        view_menu.addAction(toolbar_action)
        # Create Toolbar
        self.toolbar = QToolBar(self)
        self.toolbar.setMovable(True)
        self.addToolBar(self.toolbar)
        # Add New action to Toolbar
        self.toolbar.addAction(new_action)
        # Add Open action to Toolbar
        self.toolbar.addAction(open_action)
        # Add Save action to Toolbar
        self.toolbar.addAction(save_action)
        # Add default print action to toolbar
        self.toolbar.addAction(print_action)
        # Add Separator to Toolbar
        self.toolbar.addSeparator()
        # Add Cut action to Toolbar
        self.toolbar.addAction(cut_action)
        # Add Copy action to Toolbar
        self.toolbar.addAction(copy_action)
        # Add Paste action to Toolbar
        self.toolbar.addAction(paste_action)
        # Add Separator to Toolbar
        self.toolbar.addSeparator()
        # Add Undo action to Toolbar
        self.toolbar.addAction(undo_action)
        # Add Redo action to Toolbar
        self.toolbar.addAction(redo_action)
        # Add Separator to Toolbar
        # Add Find action to Toolbar
        self.toolbar.addAction(find_action)
        # Add Replace action to Toolbar
        self.toolbar.addAction(replace_action)
        # Add Separator to Toolbar
        self.toolbar.addSeparator()
        self.toolbar.addAction(cake_action)
        # Add Separator to Toolbar
        self.toolbar.addSeparator()
        # Add Font action to Toolbar
        self.toolbar.addAction(font_action)
        self.toolbar.addSeparator()
        # Create Action for showing/hiding Character Map in Edit Toolbar
        self.toggle_character_map_toolbar_action = QAction(QIcon("images/charmap.png"), self.tr("Character Map"), self, checkable=True)
        self.toggle_character_map_toolbar_action.setShortcut("Ctrl+M")
        self.toggle_character_map_toolbar_action.setStatusTip(self.tr("Toggle Character Map"))
        self.toggle_character_map_toolbar_action.toggled.connect(self.toggle_character_map)
        self.toolbar.addAction(self.toggle_character_map_toolbar_action)
        self.toolbar.addSeparator()
        # Create Status Bar
        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)
        # Show cursor position in status bar
        self.textedit.cursorPositionChanged.connect(self.update_statusbar)
        # Set initial status bar message
        self.statusbar.showMessage("Ln 1, Col 1", 5000)
        # Set initial text edit properties
        self.textedit.setTabStopDistance(40)
        self.textedit.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)  # Use the appropriate value here
        # Set main window properties
        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle(self.tr("Untitled - BunnyPad"))
        self.show()
    def new_file(self):
        """Create a new file."""
        def clearTEW(): # clear TextEditWidget
            # Clear text edit
            self.textedit.clear()
            # Reset file path and title
            self.file_path = None
            self.setWindowTitle(self.tr("Untitled - BunnyPad"))
            self.unsaved_changes_flag = False  # Reset flag after creation of new file
        # Check if there are unsaved changes
        if not self.unsaved_changes_flag:
            clearTEW()
        else:
            self.warn_unsaved_changes()
            clearTEW()
    def open_file(self):
        def file_open():
            file_types = "Text Files (*.txt);;Log Files (*.log);;Info files (*.nfo);;Batch files (*.bat);;Windows Command Script files (*.cmd);;VirtualBasicScript files (*.vbs);;JSON files (*.json);;Python Source files (*.py);;All Supported File Types (*.txt *.log *.nfo *.bat *.cmd *.vbs *.json *.py);;All Files (*.*)"
            file_path, _ = QFileDialog.getOpenFileName(self, self.tr("Open File"), "", file_types)
            if file_path:
                try:
                    with open(file_path, 'r') as file:
                        text = file.read()
                        self.textedit.setText(text)
                        self.file_path = file_path
                        self.setWindowTitle(self.tr(f"{os.path.basename(file_path)} - BunnyPad"))
                        self.open_file_ran = True
                        self.save_file_ran = True
                    if file_path.endswith(('.json', '.py')):
                        QMessageBox.warning(self, self.tr("Warning"), self.tr("Auto-indentation and syntax highlighting are currently unavailable for JSON and Python files."))
                except UnicodeDecodeError:
                    QMessageBox.critical(self, self.tr("Error"), self.tr("Unicode Error: Cannot open file"))
        if not self.unsaved_changes_flag:
            file_open()
        else:
            self.warn_unsaved_changes()
            file_open()
    def save_file(self):
        """Save the file."""
        if not self.file_path:
            self.save_file_as()
            return
        with open(self.file_path, "w") as f:
            f.write(self.textedit.toPlainText())
        self.setWindowTitle(self.tr(f"{os.path.basename(self.file_path)} - BunnyPad"))
        self.unsaved_changes_flag = False  # Reset flag after saving
        self.save_file_ran = True
    def closeEvent(self, event):
       # Show a message box before closing
       reply = QMessageBox.question(self,
                                    self.tr("Confirm Exit"),
                                    self.tr("Are you sure you want to quit?"),
                                    QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
                                    QMessageBox.StandardButton.Cancel)
       if reply == QMessageBox.StandardButton.Ok:
           if self.unsaved_changes_flag == False:
               event.accept
           else:
               self.warn_unsaved_changes()
               event.accept()
       else:
          event.ignore()
    def handle_text_changed(self):
        self.unsaved_changes_flag = True
        if self.open_file_ran == True or self.save_file_ran == True:
            self.setWindowTitle(self.tr(f"*{os.path.basename(self.file_path)} - BunnyPad"))
        else:
            self.setWindowTitle(self.tr("*Untitled - BunnyPad"))
    def check_saved_changes(self):
        return not self.unsaved_changes_flag
    def save_file_as(self):
        # options = QFileDialog.Option.DontUseNativeDialog
        file_path, selected_filter = QFileDialog.getSaveFileName(self, self.tr("Save As"), "", "Text Files (*.txt);;Log Files (*.log);; Info files (*.nfo);; Batch files (*.bat);; Windows Command Script files (*.cmd);; VirtualBasicScript files (*.vbs);; JSON files (*.json);; All Files (*.*)") #, options=options)
        if file_path:
            # Extract file extension from the selected filter using regular expressions
            file_extension_match = re.search(r'\(\*\.(\w+)\)', selected_filter)
            if file_extension_match:
                file_extension = '.' + file_extension_match.group(1)
                # Append the file extension to the file path if it's not already there
                if not file_path.endswith(file_extension):
                    file_path += file_extension
            self.file_path = file_path
            self.save_file()
    def warn_unsaved_changes(self):
        ret = QMessageBox.warning(self, "BunnyPad", self.tr("The document has been modified. Would you like to save your changes?"), QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel)
        if ret == QMessageBox.StandardButton.Save:
            return self.save_file()
        elif ret == QMessageBox.StandardButton.Cancel:
            return False
        else:
            return True
    def file_print(self):
        dlg = QPrintDialog()
        if dlg.exec():
            self.textedit.print(dlg.printer())
    def update_statusbar(self):
        """Update status bar with cursor position."""
        cursor = self.textedit.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber() + 1
        self.statusbar.showMessage(f"Ln {line}, Col {col}", 5000)
    def toggle_word_wrap(self):
        self.textedit.setLineWrapMode(not self.textedit.lineWrapMode())
    def choose_font(self):
        font, ok = QFontDialog.getFont()
        if ok:
            self.textedit.setFont(font)
    def toggle_toolbar(self):
        self.toolbar.setVisible(not self.toolbar.isVisible())
    def toggle_statusbar(self):
        self.statusbar.setVisible(not self.statusbar.isVisible())
    def about(self):
        AboutDialog().exec()
    def credits(self):
        CreditsDialog().exec()
    def sysinfo(self):
        SystemInfoDialog().exec()
    def FeatureNotReady(self):
        FeatureNotReady().exec()
    def cake(self):
        TheCakeIsALie().exec()
    def support(self):
        ContactUs().exec()
    def download(self):
        DownloadOptions().exec()
    def toggle_character_map(self, checked):
        character_dock.setVisible(checked)
    def insert_character(self, character):
        self.textedit.insertPlainText(character)
    def print_to_pdf(self):
        file_path, selected_filter = QFileDialog.getSaveFileName(self, self.tr("Print to PDF [Save as]"), "", self.tr("PDF File (*.pdf)"))
        if file_path:
            # Extract file extension from the selected filter using regular expressions
            file_extension_match = re.search(r'\(\*\.(\w+)\)', selected_filter)
            if file_extension_match:
                file_extension = '.' + file_extension_match.group(1)
                # Append the file extension to the file path if it's not already there
                if not file_path.endswith(file_extension):
                    file_path += file_extension
            text = self.textedit.toPlainText()
            save_as_pdf(text, file_path)
    def dateTime(self):
        cdate = str(datetime.datetime.now())
        self.textedit.append(cdate)
    def go_to_line(self):
        line_number, ok = QInputDialog.getInt(self, self.tr("Go to Line"), self.tr("Enter line number:"), value=1)
        cursor = self.textedit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        cursor.movePosition(QTextCursor.MoveOperation.Down, QTextCursor.MoveMode.MoveAnchor, line_number - 1)
        # Set the cursor as the new cursor for the QTextEdit
        self.textedit.setTextCursor(cursor)
        # Ensure the target line is visible
        self.textedit.ensureCursorVisible()
    def find_function(self):
        def find_word(word):
            cursor = self.textedit.document().find(word)
            if not cursor.isNull():
                self.textedit.setTextCursor(cursor)
                self.textedit.ensureCursorVisible()
        word_to_find, ok = QInputDialog.getText(
            self,
            self.tr("Find Word"),
            self.tr("Enter the word you want to find:")
        )
        if ok and word_to_find:
            find_word(word_to_find)
    def replace_function(self):
        QMessageBox.warning(
            self,
            self.tr("Replace Function - Warning"),
            self.tr(
                "The Replace feature is functional but may not work perfectly in some cases. "
                "For example, words can be cut off and/or some data can be lost. We are working towards fixing this issue."
            ),
            QMessageBox.StandardButton.Ok
        )
        def replace_word(old_word, new_word):
            cursor = self.textedit.textCursor()
            document = self.textedit.document()
            cursor.beginEditBlock()  # Begin a block of edits for undo support
            cursor.movePosition(QTextCursor.MoveOperation.Start)  # Start from the beginning of the document
            replacement_count = 0  # Track the number of replacements

            while True:
                # Find the next occurrence of the old_word
                cursor = document.find(old_word, cursor, QTextDocument.FindFlag.FindWholeWords)
                if cursor.isNull():  # No more matches found
                    break
                cursor.insertText(new_word)  # Replace the word
                replacement_count += 1

            cursor.endEditBlock()  # End the block of edits
            return replacement_count

        # Get the word to replace
        old_word, ok1 = QInputDialog.getText(
            self,
            self.tr("Replace Word"),
            self.tr("Enter the word you want to replace:")
        )
        if ok1 and old_word.strip():  # Ensure old_word is valid
            # Get the replacement word
            new_word, ok2 = QInputDialog.getText(
                self,
                self.tr("Replace With"),
                self.tr("Enter the new word:")
            )
            if ok2:
                # Perform the replacement and provide feedback
                replaced_count = replace_word(old_word, new_word)
                QMessageBox.information(
                    self,
                    self.tr("Replace Completed"),
                    self.tr(f"Replaced {replaced_count} occurrence(s) of '{old_word}' with '{new_word}'.")
                )
    def check_for_updates(self):
        self.update_module.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName("BunnyPad")
    app.setOrganizationName("GSYT Productions")
    BunnyPad = Notepad()
    app.setStyle("Fusion")
    file = QFile("stylesheet.qss")
    file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text)
    stream = QTextStream(file)
    app.setStyleSheet(stream.readAll())
    # Create the Character Map Widget and add it to the Notepad application
    character_map = CharacterWidget()
    character_map.characterSelected.connect(BunnyPad.insert_character)
    character_map_layout = QVBoxLayout()
    character_map_layout.addWidget(character_map)
    character_map_widget = QWidget()
    character_map_widget.setLayout(character_map_layout)
    character_dock = QDockWidget(QCoreApplication.translate("MainWindow", "Character Map"), BunnyPad)
    character_dock.setWidget(character_map_widget)
    character_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
    character_dock.hide()  # Initially hide the widget
    BunnyPad.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, character_dock)
    display_os = identify_os()
    current_directory = show_current_directory()
    systeminfo = get_system_info()
    BunnyPad.show()
    sys.exit(app.exec())
