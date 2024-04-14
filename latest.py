"""
 ____                          ____           _ 
| __ ) _   _ _ __  _ __  _   _|  _ \ __ _  __| |
|  _ \| | | | '_ \| '_ \| | | | |_) / _` |/ _` |
| |_) | |_| | | | | | | | |_| |  __/ (_| | (_| |
|____/ \__,_|_| |_|_| |_|\__, |_|   \__,_|\__,_|
                         |___/                  
                         Mini Changelog: Fixed missing Find function in Edit menu; Begin framework for GoToLine function.
"""

try:
    import sys, os, time, platform, distro, unicodedata, textwrap, datetime, re, random
    from PyQt6.QtCore import *
    from fpdf import FPDF
    from PyQt6.QtWidgets import QApplication, QMainWindow, QTextEdit, QFileDialog, QWidget, QDialog, QMenuBar, QMenu, QToolBar, QStatusBar, QVBoxLayout, QDockWidget, QLabel, QToolTip, QPushButton, QFontDialog, QMessageBox, QInputDialog
    from PyQt6.QtGui import QTextCursor, QIcon, QFont, QPixmap, QPainter, QFontMetrics, QAction, QColor
    from PyQt6.QtPrintSupport import QPrintDialog
except:
    from os import system as cmd
    cmd("pip install PyQt6 distro fpdf")
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
        display_OS = f"Linux {linux_distro_name} {linux_distro_version} - Version: {linux_version}"
    elif os_name == "Darwin":
        mac_version = platform.mac_ver()[0]
        mac_platform = "Silicon" if platform.processor() == "arm" else "Intel"
        display_OS = f"macOS {mac_version} - Platform: {mac_platform}"
    elif os_name == "Windows":
        win_version = platform.release()
        win_variant = platform.win32_edition()
        if win_variant is None:
            win_variant = "(Wine Environment?)"
        display_OS = f"Windows {win_version} {win_variant}"
    else:
        display_OS = "Unknown OS"
    return display_OS

class CharacterWidget(QWidget):
    characterSelected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
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

    def setColumns(self, columns):
        self.columns = columns
        self.adjustSize()
        self.update()

    def sizeHint(self):
        return QSize(self.columns * self.squareSize, int((65536 / self.columns) * self.squareSize))

    def mouseMoveEvent(self, event):
        widgetPosition = self.mapFromGlobal(event.globalPosition().toPoint())
        key = (widgetPosition.y() // self.squareSize) * self.columns + widgetPosition.x() // self.squareSize
        text = '<p>Character: <span style="font-size: 24pt; font-family: %s">%s</span><p>Value: 0x%x' % (
            self.displayFont.family(), self._chr(key), key)
        QToolTip.showText(event.globalPosition().toPoint(), text, self)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.lastKey = (event.pos().y() // self.squareSize) * self.columns + event.pos().x() // self.squareSize
            key_ch = self._chr(self.lastKey)
            if unicodedata.category(key_ch) != 'Cn':
                self.characterSelected.emit(key_ch)
            self.update()
        else:
            super().mousePressEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(event.rect(), QColor("white"))
        painter.setFont(self.displayFont)
        redrawRect = event.rect()
        beginRow = redrawRect.top() // self.squareSize
        endRow = redrawRect.bottom() // self.squareSize
        beginColumn = redrawRect.left() // self.squareSize
        endColumn = redrawRect.right() // self.squareSize
        painter.setPen(QColor("gray"))
        for row in range(beginRow, endRow + 1):
            for column in range(beginColumn, endColumn + 1):
                painter.drawRect(column * self.squareSize,
                                 row * self.squareSize, self.squareSize,
                                 self.squareSize)
        fontMetrics = QFontMetrics(self.displayFont)
        painter.setPen(QColor("black"))
        for row in range(beginRow, endRow + 1):
            for column in range(beginColumn, endColumn + 1):
                key = row * self.columns + column
                painter.setClipRect(column * self.squareSize,
                                    row * self.squareSize, self.squareSize,
                                    self.squareSize)
                if key == self.lastKey:
                    painter.fillRect(column * self.squareSize + 1,
                                     row * self.squareSize + 1, self.squareSize,
                                     self.squareSize, QColor("red"))
                key_ch = self._chr(key)
                painter.drawText(column * self.squareSize + (self.squareSize // 2) - fontMetrics.horizontalAdvance(
                    key_ch) // 2,
                                 row * self.squareSize + 4 + fontMetrics.ascent(),
                                 key_ch)

    @staticmethod
    def _chr(codepoint):
        # Python v3.
        return chr(codepoint)


class AboutDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(AboutDialog, self).__init__(*args, **kwargs)
        self.setWindowTitle("About BunnyPad")
        self.setWindowIcon(QIcon(os.path.join('./bunnypad.png')))
        layout = QVBoxLayout(self)
        title = QLabel("BunnyPad™")
        font = title.font()
        font.setPointSize(20)
        title.setFont(font)
        layout.addWidget(title)
        logo = QLabel()
        logo.setPixmap(QPixmap(os.path.join('./bunnypad.png')))
        layout.addWidget(logo)
        layout.addWidget(QLabel("A Notepad Clone named in part after Innersloth's Off-Topic Regular, PBbunnypower [aka Bunny]"))
        layout.addWidget(QLabel("Copyright © 2023-2024 GSYT Productions, LLC"))
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
        phrases = ["``It was a pleasure to [learn]``",
                   "``So it was the hand that started it all ... \nHis hands had been infected, and soon it would be his arms ... \nHis hands were ravenous.``",
                   "Hopping past opinions",
                   "``Is it true that a long time ago, firemen used to put out fires and not burn books?``",
                   "``Fahrenheit 451, the temperature at which paper spontaneously combusts``",
                   "``Do you want to know what's inside all these books? Insanity. The Eels want to measure their place in the universe,\n so they turn to these novels about non-existent people. Or worse, philosophers. \n Look, here's Spinoza. One expert screaming down another expert's throat. \"We have free will. No, all of our actions are predetermined.\" \nEach one says the opposite, and a man comes away lost, feeling more bestial and lonely than before. \nNow, if you don't want a person unhappy, you don't give them two sides of a question to worry about. Just give 'em one.. Better yet, none.``",
                   "``what a thing human is, one have a no loyalty and second have hope of it lmao`` - ItzAzan",
                   selected_anagram]
        random_phrase = random.choice(phrases)
        layout.addWidget(QLabel(random_phrase))
        layout.addWidget(QLabel("Developer Information: \n Build: v10.0.22000.1 \n Internal Name: Codename PBbunnypower Notepad Variant Decipad \n Engine: PrettyFonts\n Channel: FreshlyPlanted"))
        layout.addWidget(QLabel("You are running BunnyPad on " + display_text))
        for i in range(layout.count()):
            layout.itemAt(i).setAlignment(Qt.AlignmentFlag.AlignHCenter)
        #Add click event for PBbunnypower easter egg
        logo.mousePressEvent = self.activate_PBbunnypower_easter_egg
        #logo.mousePressEvent = oops_egg().exec()
    def activate_PBbunnypower_easter_egg(self, event):
        # PBbunnypower easter egg code
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Message to PBbunnypower")
        msg_box.setWindowIcon(QIcon(os.path.join('./bunnypad.png')))
        msg_box.setText("BunnyPad's become so popular that it's controversial within the tech community. I guess it was done by my Python fluency. The initial opinions, we blew them away. We work hard and then we play; I can do this all dang day.")
        msg_box.exec()
class CreditsDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(CreditsDialog, self).__init__(*args, **kwargs)
        self.setWindowTitle("About BunnyPad's Team")
        self.setWindowIcon(QIcon(os.path.join('./bunnypad.png')))
        layout = QVBoxLayout(self)
        title = QLabel("The Team Behind BunnyPad™")
        font = title.font()
        font.setPointSize(20)
        title.setFont(font)
        layout.addWidget(title)
        logo = QLabel()
        logo.setPixmap(QPixmap(os.path.join('./gsyt.png')))
        layout.addWidget(logo)
        layout.addWidget(QLabel("GarryStraitYT: Lead Developer; PBbunnypower (Bunny): Main icon design, tester, project dedicated to her \n\nI-San: Beta Tester\n Tai: Assisted with CarrotPatch Icon \n FireCube (FireCubeStudios): Helped get it off the ground and known by a few people, owner of DevSanc \n ZeRoTeCh00: said kind words about BunnyPad during his stream on 2 September 2023 \n ByPad: Porting the app to Linux, clean-room reverse engineering the app \n DinoDude: Github contributor"))
        for i in range(layout.count()):
            layout.itemAt(i).setAlignment(Qt.AlignmentFlag.AlignHCenter)
        # Add click event for escargot easter egg
        logo.mousePressEvent = self.activate_escargot_easter_egg
    def activate_escargot_easter_egg(self, event):
        # galaxynote7 easter egg code
        msg_box = QMessageBox()
        layout = QVBoxLayout(self)
        msg_box.setWindowTitle("Snails")
        msg_box.setWindowIcon(QIcon(os.path.join('./bunnypad.png')))
        logo = QLabel()
        logo.setPixmap(QPixmap(os.path.join('./bunnypad.png')))
        layout.addWidget(logo)
        msg_box.setText("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n")
        msg_box.exec()
class FeatureNotReady(QDialog):
    def __init__(self, parent=None):
        super(FeatureNotReady, self).__init__(parent)
        self.setWindowTitle("Feature Not Ready; Work In Progress")
        self.setWindowIcon(QIcon(os.path.join('./bunnypad.png')))
        layout = QVBoxLayout(self)
        title = QLabel("BunnyPad™")
        font = title.font()
        font.setPointSize(20)
        title.setFont(font)
        logo = QLabel()
        logo.setPixmap(QPixmap(os.path.join('./bunnypad.png')))
        message = QLabel("The requested feature caused instabilities during the tests, and has been disabled until they can be fixed. Sorry.")
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(logo, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(message, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(ok_button, alignment=Qt.AlignmentFlag.AlignHCenter)
        # Add click event for song quote easter egg
        logo.mousePressEvent = self.activate_see_you_again_easter_egg
    def activate_see_you_again_easter_egg(self, event):
        song = "It's been a long day without you my friend \n and I'll tell you all about it when I see you again \n We've come a long way from where we began \n and I'll tell you all about it when I see you again \n when I see you again"
        msg_box = QMessageBox()
        msg_box.setWindowIcon(QIcon(os.path.join('./bunnypad.png')))
        msg_box.setWindowTitle("See you again")
        msg_box.setText(song)
        msg_box.exec()
class TheCakeIsALie(QDialog):
    def __init__(self, parent=None):
        super(TheCakeIsALie, self).__init__(parent)
        self.setWindowTitle("Error: Cake_Is_Lie")
        self.setWindowIcon(QIcon(os.path.join('./images/nocake.png')))
        layout = QVBoxLayout(self)
        title = QLabel("A Critical Error Has Occurred")
        font = title.font()
        font.setPointSize(20)
        title.setFont(font)
        logo = QLabel()
        logo.setPixmap(QPixmap(os.path.join('./images/nocake.png')))
        message = QLabel("Unfortunately, there is no cake. You have fallen for a trap. Where we promised a tasty dessert, there is instead deception. In other words, THE CAKE IS A LIE!")
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(logo, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(message, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(ok_button, alignment=Qt.AlignmentFlag.AlignHCenter)
        # Add click event for the other easter egg
        logo.mousePressEvent = self.momentum_easteregg
    def momentum_easteregg(self, event):
        quote = "Momentum, a function of mass and velocity, is conserved between portals. In layman's terms, speedy thing goes in, speedy thing comes out."
        msg_box = QMessageBox()
        msg_box.setWindowIcon(QIcon(os.path.join('./bunnypad.png')))
        msg_box.setWindowTitle("Momentum and Portals")
        msg_box.setText(quote)
        msg_box.exec()
class ContactUs(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("Contact BunnyPad Support")
        self.setWindowIcon(QIcon(os.path.join('./bunnypad.png')))
        layout = QVBoxLayout(self)
        title = QLabel("BunnyPad™")
        font = title.font()
        font.setPointSize(20)
        title.setFont(font)
        layout.addWidget(title)
        logo = QLabel()
        logo.setPixmap(QPixmap(os.path.join('./bunnypad.png')))
        layout.addWidget(logo)
        info_label = QLabel("Website: <a href='https://gsyt-productions.github.io/'>https://gsyt-productions.github.io/</a> <br> GSYT Productions Server: <a href='https://guilded.gg/gsyt-productions'>https://guilded.gg/gsyt-productions</a> <br> BunnyPad CarrotPatch Server: <a href='https://guilded.gg/bunnypad'>https://guilded.gg/bunnypad</a> <br> Text Us: +1 (814) 204-2333")
        info_label.setTextFormat(Qt.TextFormat.RichText)
        info_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        info_label.setOpenExternalLinks(True)
        layout.addWidget(info_label)
        logo.mousePressEvent = self.activate_galaxynote7_easter_egg
    def activate_galaxynote7_easter_egg(self, event):
        # galaxynote7 easter egg code
        msg_box = QMessageBox()
        layout = QVBoxLayout(self)
        msg_box.setWindowTitle("Galaxy Note 7")
        msg_box.setWindowIcon(QIcon(os.path.join('./bunnypad.png')))
        logo = QLabel()
        logo.setPixmap(QPixmap(os.path.join('./bunnypad.png')))
        layout.addWidget(logo)
        msg_box.setText("So I heard that the Samsung Galaxy Note 7 was the bomb, rather literally")
        msg_box.exec()
class Notepad(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Untitled - BunnyPad")
        self.setWindowIcon(QIcon(os.path.join('./bunnypad.png')))
        self.setGeometry(100, 100, 800, 600)
        self.file_path = None
        self.unsaved_changes_flag = False
        self.open_file_ran = False
        self.save_file_ran = False
        self.textedit = QTextEdit(self)
        self.textedit.textChanged.connect(self.handle_text_changed)
        self.setStyleSheet("""
        /* Set the background color of icons */
        QLabel[icon="true"] {
            background-color: #0078D7;
            }
        /* Set the background color of toolbars */
        QToolBar {
            background-color: #0078D7;
            }
        /* Set the background color of the window */
        QMainWindow {
            background-color: #8C49F0;
            }
        /* Set the color of the titlebar text */
        QMainWindow::title {
            color: white;
            }
        /* Set the color of the titlebar background */
        QMainWindow::titleBar {
            background-color: #8C49F0;
            }
        /* Set the background color of the status bar */
        QStatusBar {
            color: white;
            background-color: #0078D7;
            }
        /* Set the background color of menus */
        QMenuBar {
            background-color: #8C49F0;
            }
        /* Set the text color of menus */
        QMenuBar::item {
            color: white;
            }
        /* Set the background color of menu items */
        QMenu {
            background-color: #6AA5F3;
            }
        /* Set the text color of menu items */
        QMenu::item {
            color: white;
            }
        /* Set the background color of dialog windows */
        QDialog {
            background-color: #8C49F0;
            }
        /* Set the text color of dialog windows */
        QDialog QLabel {
            color: white;
            }
        """)
        # I am a friggin idiot!
        # Set up text edit widget
        # self.textedit = self.textedit.setAcceptRichText(True)
        self.setCentralWidget(self.textedit)
        # Create menu bar
        menubar = QMenuBar(self)
        self.setMenuBar(menubar)
        # Create File menu
        file_menu = QMenu("File", self)
        menubar.addMenu(file_menu)
        # Create New action
        new_action = QAction(QIcon("images/new.png"), "New", self)
        new_action.setStatusTip("Creates a new file.")
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        # Create Open action
        open_action = QAction(QIcon("images/open.png"), "Open...", self)
        open_action.setStatusTip("Opens a document.")
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        # Create Save action
        save_action = QAction(QIcon("images/save.png"), "Save", self)
        save_action.setStatusTip("Saves the document.")
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        # Create Save As action
        save_as_action = QAction(QIcon("images/saveas.png"), "Save As...", self)
        save_as_action.setStatusTip("Saves the document as the chosen file")
        save_as_action.triggered.connect(self.save_file_as)
        save_as_action.setShortcut('Ctrl+Shift+S')
        file_menu.addAction(save_as_action)
        # Add separator
        file_menu.addSeparator()
        # Create Print to PDF action
        print_to_pdf_action = QAction(QIcon("images/pdf.png"), "Print to PDF...", self)
        print_to_pdf_action.setStatusTip("Save the document as a PDF file.")
        print_to_pdf_action.triggered.connect(self.print_to_pdf)
        print_to_pdf_action.setShortcut('Ctrl+Shift+P')
        file_menu.addAction(print_to_pdf_action)
        print_action = QAction(QIcon(os.path.join('images', 'printer.png')), "Print...", self)
        print_action.setStatusTip("Print current page")
        print_action.triggered.connect(self.file_print)
        print_action.setShortcut('Ctrl+P')
        file_menu.addAction(print_action)
        # Add separator
        file_menu.addSeparator()
        # Create Exit action
        exit_action = QAction(QIcon("images/exit.png"), "Exit", self)
        exit_action.setStatusTip("Exits BunnyPad™")
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        # The Salamander eats its own tail.
        # Create Edit menu
        edit_menu = QMenu("Edit", self)
        menubar.addMenu(edit_menu)
        # Create Undo action
        undo_action = QAction(QIcon("images/undo.png"), "Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self.textedit.undo)
        edit_menu.addAction(undo_action)
        # Create Redo action
        redo_action = QAction(QIcon("images/redo.png"), "Redo", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(self.textedit.redo)
        edit_menu.addAction(redo_action)
        # Add separator
        edit_menu.addSeparator()
        # Create Cut action
        cut_action = QAction(QIcon("images/cut.png"), "Cut", self)
        cut_action.setStatusTip("Moves selected text to clipboard")
        cut_action.setShortcut("Ctrl+X")
        cut_action.triggered.connect(self.textedit.cut)
        edit_menu.addAction(cut_action)
        # Create Copy action
        copy_action = QAction(QIcon("images/copy.png"), "Copy", self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.setStatusTip("Copies the selected text to the clipboard.")
        copy_action.triggered.connect(self.textedit.copy)
        edit_menu.addAction(copy_action)
        # Create Paste action
        paste_action = QAction(QIcon("images/paste.png"), "Paste", self)
        paste_action.setStatusTip("Pastes the text currently in the clipboard.")
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(self.textedit.paste)
        edit_menu.addAction(paste_action)
        # Create Delete action
        delete_action = QAction(QIcon("images/delete.png"), "Delete", self)
        delete_action.setStatusTip("Deletes the character after the cursor position.")
        delete_action.setShortcut("Del")
        delete_action.triggered.connect(lambda: self.textedit.textCursor().deleteChar())
        edit_menu.addAction(delete_action)
        # Create Date/Time Action
        datetime_action = QAction(QIcon("images/datetime.png"), "Date and Time", self)
        datetime_action.setStatusTip("Inserts the current date and time, including milliseconds.")
        datetime_action.setShortcut("F5")
        datetime_action.triggered.connect(self.dateTime)
        edit_menu.addAction(datetime_action)
        # Add separator
        edit_menu.addSeparator()
        # Create Action for showing/hiding Character Map in Edit Menu
        toggle_character_map_action = QAction(QIcon("images/charmap.png"), "Character Map", self, checkable=True)
        toggle_character_map_action.setChecked(False)
        toggle_character_map_action.setStatusTip("Toggle Character Map")
        toggle_character_map_action.setShortcut("Ctrl+M")
        toggle_character_map_action.toggled.connect(self.toggle_character_map)
        edit_menu.addAction(toggle_character_map_action)
        edit_menu.addSeparator()
        # Create Find action
        find_action = QAction(QIcon("images/find.png"), "Find...", self)
        find_action.setShortcut("Ctrl+F")  # Ctrl+F
        find_action.setStatusTip("Find a word...")
        find_action.triggered.connect(self.find_function)
        edit_menu.addAction(find_action)
        # Go to line
        gtl_action = QAction(QIcon("images/find.png"), "Go To Line", self)
        gtl_action.setShortcut("Ctrl+G")  # Ctrl+G
        gtl_action.setStatusTip("Go to a specified line")
        # gtl_action.triggered.connect(self.go_to_line)
        gtl_action.triggered.connect(self.FeatureNotReady)
        edit_menu.addAction(gtl_action)
        # Create Replace action
        replace_action = QAction(QIcon("images/replace.png"), "Replace...", self)
        replace_action.setStatusTip("Currently in development...")
        replace_action.setShortcut("Ctrl+H")
        replace_action.triggered.connect(self.FeatureNotReady)
        edit_menu.addAction(replace_action)
        # Add separator
        edit_menu.addSeparator()
        # Create Select All action
        select_all_action = QAction(QIcon("images/selectall.png"), "Select All", self)
        select_all_action.setStatusTip("Select all the text in the current document.")
        select_all_action.setShortcut("Ctrl+A")
        select_all_action.triggered.connect(self.textedit.selectAll)
        edit_menu.addAction(select_all_action)
        # Create Format menu
        format_menu = QMenu("Format", self)
        menubar.addMenu(format_menu)
        # Create Word Wrap action
        word_wrap_action = QAction(QIcon("images/wordwrap.png"),"Word Wrap", self)
        word_wrap_action.setStatusTip("Toggles wrapping the words to the window.")
        word_wrap_action.setShortcut("Ctrl+W")
        word_wrap_action.setCheckable(True)
        word_wrap_action.setChecked(True)
        word_wrap_action.triggered.connect(self.toggle_word_wrap)
        format_menu.addAction(word_wrap_action)
        # Create Font action
        font_action = QAction(QIcon("images/font.png"),"Font...", self)
        font_action.setStatusTip("Change the current font.")
        font_action.setShortcut("Alt+F")
        font_action.triggered.connect(self.choose_font)
        format_menu.addAction(font_action)
        # Create View menu
        view_menu = QMenu("View", self)
        menubar.addMenu(view_menu)
        help_menu = self.menuBar().addMenu("&Help")
        about_action = QAction(QIcon(os.path.join('images/info.png')), "About BunnyPad", self)
        about_action.setStatusTip("Find out more about BunnyPad")  # Hungry!
        about_action.setShortcut("Alt+H")
        about_action.triggered.connect(self.about)
        help_menu.addAction(about_action)
        credits_action = QAction(QIcon(os.path.join('images/team.png')), "Credits for BunnyPad", self)
        credits_action.setStatusTip("Find out more about BunnyPad's Team")  # Hungry!
        credits_action.setShortcut("Alt+C")
        credits_action.triggered.connect(self.credits)
        help_menu.addAction(credits_action)
        cake_action = QAction(QIcon(os.path.join('images/cake.png')), "Cake :D", self)
        cake_action.setStatusTip("Click here for some Cake")  # Hungry!
        cake_action.setShortcut("Alt+A")
        cake_action.triggered.connect(self.cake)
        help_menu.addAction(cake_action)
        contact_support_action = QAction(QIcon(os.path.join('images/support.png')), "Contact Us", self)
        contact_support_action.setStatusTip("Find out how to contact the team!")  # Hungry!
        contact_support_action.setShortcut("Alt+S")
        contact_support_action.triggered.connect(self.support)
        help_menu.addAction(contact_support_action)
        # For v11: Source Code Download
        source_action = QAction(QIcon("./bpdl.png"), "Download the latest source code", self)
        source_action.setStatusTip("For BunnyPad v11+")
        source_action.setShortcut("Ctrl+J")
        source_action.triggered.connect(self.FeatureNotReady)
        help_menu.addAction(source_action)
        # Create the statusbar action
        statusbar_action = QAction("Show statusbar", self, checkable=True)
        statusbar_action.setStatusTip("Toggle statusbar")
        statusbar_action.setShortcut("Alt+Shift+S")
        statusbar_action.setChecked(True)
        statusbar_action.triggered.connect(self.toggle_statusbar)
        view_menu.addAction(statusbar_action)
        # Connect the statusbar action to the update_statusbar method
        statusbar_action.triggered.connect(self.update_statusbar)
        # Create Toolbar action
        toolbar_action = QAction("Toolbar", self, checkable=True)
        toolbar_action.setStatusTip("Toggle toolbar")
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
        self.toggle_character_map_toolbar_action = QAction(QIcon("images/charmap.png"), "Character Map", self, checkable=True)
        self.toggle_character_map_toolbar_action.setShortcut("Ctrl+M")
        self.toggle_character_map_toolbar_action.setStatusTip("Toggle Character Map")
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
        self.setWindowTitle("Untitled - BunnyPad")
        self.show()

    def new_file(self):
        """Create a new file."""
        def clearTEW(): # clear TextEditWidget
            # Clear text edit
            self.textedit.clear()
            # Reset file path and title
            self.file_path = None
            self.setWindowTitle("Untitled - BunnyPad")
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
            file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", file_types)
            if file_path:
                try:
                    with open(file_path, 'r') as file:
                        text = file.read()
                        self.textedit.setText(text)
                        self.file_path = file_path
                        self.setWindowTitle(f"{os.path.basename(file_path)} - BunnyPad")
                        self.open_file_ran = True
                    if file_path.endswith(('.json', '.py')):
                        QMessageBox.warning(self, "Warning", "Auto-indentation and syntax highlighting are currently unavailable for JSON and Python files.")
                except UnicodeDecodeError:
                    QMessageBox.critical(self, "Error", "Unicode Error: Cannot open file")
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
        self.setWindowTitle(f"{os.path.basename(self.file_path)} - BunnyPad")
        self.unsaved_changes_flag = False  # Reset flag after saving
        self.save_file_ran = True
    def closeEvent(self, event):
       # Show a message box before closing
       reply = QMessageBox.question(self,
                                    "Confirm Exit",
                                    "Are you sure you want to quit?",
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
            self.setWindowTitle(f"*{os.path.basename(self.file_path)} - BunnyPad")
        else:
            self.setWindowTitle("*Untitled - BunnyPad")

    def check_saved_changes(self):
        return not self.unsaved_changes_flag

    def save_file_as(self):
        # options = QFileDialog.Option.DontUseNativeDialog
        file_path, selected_filter = QFileDialog.getSaveFileName(self, "Save As", "", "Text Files (*.txt);;Log Files (*.log);; Info files (*.nfo);; Batch files (*.bat);; Windows Command Script files (*.cmd);; VirtualBasicScript files (*.vbs);; JSON files (*.json);; All Files (*.*)") #, options=options)
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
        ret = QMessageBox.warning(self, "BunnyPad", "The document has been modified.\nDo you want to save your changes?", QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel)
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

    def FeatureNotReady(self):
        FeatureNotReady().exec()

    def cake(self):
        TheCakeIsALie().exec()

    def support(self):
        ContactUs().exec()

    def toggle_character_map(self, checked):
        character_dock.setVisible(checked)

    def insert_character(self, character):
        self.textedit.insertPlainText(character)

    def print_to_pdf(self):
        file_path, selected_filter = QFileDialog.getSaveFileName(self, "Print to PDF [Save as]", "", "PDF File (*.pdf)")
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
        line_number, ok = QInputDialog.getInt(self, "Go to Line", "Enter line number:", value=1)
        cursor = self.textedit.textCursor()
        cursor.movePosition(QTextCursor.Start)
        cursor.movePosition(QTextCursor.Down, QTextCursor.MoveAnchor, line_number - 1)
        # Set the cursor as the new cursor for the QTextEdit
        self.textedit.setTextCursor(cursor)
        # Ensure the target line is visible
        self.textedit.ensureCursorVisible()
    def find_function(self):
        def find_word(word):
            cursor = self.textEdit.document().find(word)

            if not cursor.isNull():
                self.textEdit.setTextCursor(cursor)
                self.textEdit.ensureCursorVisible()

        word_to_find, ok = QInputDialog.getText(
            self,
            "Find Word",
            "Enter the word you want to find:"
        )
        if ok and word_to_find:
            find_word(word_to_find)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName("BunnyPad")
    app.setOrganizationName("GSYT Productions")
    BunnyPad = Notepad()
    app.setStyle("Fusion")
    # Create Character Map Widget and add it to the Notepad application
    character_map = CharacterWidget()
    character_map.characterSelected.connect(BunnyPad.insert_character)
    character_map_layout = QVBoxLayout()
    character_map_layout.addWidget(character_map)
    character_map_widget = QWidget()
    character_map_widget.setLayout(character_map_layout)
    character_dock = QDockWidget("Character Map", BunnyPad)
    character_dock.setWidget(character_map_widget)
    character_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
    character_dock.hide()  # Set the widget to be initially hidden
    BunnyPad.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, character_dock)
    display_text = identify_os()
    BunnyPad.show()
    sys.exit(app.exec())
