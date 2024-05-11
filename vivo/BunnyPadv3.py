### GSYT Productions Codename PBbpNotepad Variant Dinero ###
### Adds credits dialogue box. Last version with moveable toolbar ###
### Long live PBbunnypower, the source of inspiration for this application. Without her awesome personality, BunnyPad would have never existed ###
### "Legends die when they are forgotten. They are forgotten when they are replaced. Instead of thinking about legends, become one" - Bunny ###
### Build completed 06 May 2023, 05:20 MVT. Compiled 06 May 2023, 05:30 MVT ###


from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtPrintSupport import *
import os
import sys
class AboutDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(AboutDialog, self).__init__(*args, **kwargs)
        QBtn = QDialogButtonBox.Ok  # No cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.setWindowTitle("About BunnyPad")
        self.setWindowIcon(QIcon(os.path.join('images', 'bunnypad.png')))
        layout = QVBoxLayout()
        title = QLabel("BunnyPad™")
        font = title.font()
        font.setPointSize(20)
        title.setFont(font)
        layout.addWidget(title)
        logo = QLabel()
        logo.setPixmap(QPixmap(os.path.join('images', 'bunnypad.png')))
        layout.addWidget(logo)
        layout.addWidget(QLabel("A Notepad Clone named in part after Innersloth's Off-Topic Regular, PBbunnypower [aka Bunny]"))
        layout.addWidget(QLabel("Copyright © 2023 GSYT Productions, LLC"))
        layout.addWidget(QLabel("Bunny, the reason why I dedicated this to you was because it reminded me of your brilliance"))
        layout.addWidget(QLabel("No matter what, Bunny, you'll always be my best friend."))
        for i in range(0, layout.count()):
            layout.itemAt(i).setAlignment(Qt.AlignHCenter)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)
class CreditsDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(CreditsDialog, self).__init__(*args, **kwargs)
        QBtn = QDialogButtonBox.Ok  # No cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.setWindowTitle("About BunnyPad's Team")
        self.setWindowIcon(QIcon(os.path.join('images', 'bunnypad.png')))
        layout = QVBoxLayout()
        title = QLabel("The Team Behind BunnyPad™")
        font = title.font()
        font.setPointSize(20)
        title.setFont(font)
        layout.addWidget(title)
        logo = QLabel()
        logo.setPixmap(QPixmap(os.path.join('images', 'bunnypad.png')))
        layout.addWidget(logo)
        layout.addWidget(QLabel("GarryStraitYT: Lead Developer \n PBbunnypower (Bunny): Main icon design; tester; project dedicated to her"))
        layout.addWidget(QLabel("Groove: Beta Tester \n RealCartfren: Mac Port Manager (only person i know with a Mac) \n Something Pingable (I-San): Tester \n Tai - Created CarrotPatch Build icon"))
        layout.addWidget(QLabel("FireCube (FireCubeStudios): Helped get it off the ground and known by a few people, owner of Developer Sanctuary"))
        for i in range(0, layout.count()):
            layout.itemAt(i).setAlignment(Qt.AlignHCenter)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)
class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()
        self.editor = QPlainTextEdit()
        fixedfont = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        fixedfont.setPointSize(12)
        self.editor.setFont(fixedfont)
        self.path = None
        layout.addWidget(self.editor)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        file_toolbar = QToolBar("File")
        file_toolbar.setIconSize(QSize(14, 14))
        self.addToolBar(file_toolbar)
        file_menu = self.menuBar().addMenu("&File")
        open_file_action = QAction(QIcon(os.path.join('images', 'blue-folder-open-document.png')), "Open file...", self)
        open_file_action.setStatusTip("Open file")
        open_file_action.triggered.connect(self.file_open)
        file_menu.addAction(open_file_action)
        file_toolbar.addAction(open_file_action)
        save_file_action = QAction(QIcon(os.path.join('images', 'disk.png')), "Save", self)
        save_file_action.setStatusTip("Save current page")
        save_file_action.triggered.connect(self.file_save)
        file_menu.addAction(save_file_action)
        file_toolbar.addAction(save_file_action)
        saveas_file_action = QAction(QIcon(os.path.join('images', 'disk--pencil.png')), "Save As...", self)
        saveas_file_action.setStatusTip("Save current page to specified file")
        saveas_file_action.triggered.connect(self.file_saveas)
        file_menu.addAction(saveas_file_action)
        file_toolbar.addAction(saveas_file_action)
        # Create Exit action
        exit_action = QAction(QIcon("images/exit.png"), "Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        edit_toolbar = QToolBar("Edit")
        edit_toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(edit_toolbar)
        edit_menu = self.menuBar().addMenu("&Edit")
        undo_action = QAction(QIcon(os.path.join('images', 'arrow-curve-180-left.png')), "Undo", self)
        undo_action.setStatusTip("Undo last change")
        undo_action.triggered.connect(self.editor.undo)
        edit_menu.addAction(undo_action)
        redo_action = QAction(QIcon(os.path.join('images', 'arrow-curve.png')), "Redo", self)
        redo_action.setStatusTip("Redo last change")
        redo_action.triggered.connect(self.editor.redo)
        edit_toolbar.addAction(redo_action)
        edit_menu.addAction(redo_action)
        edit_menu.addSeparator()
        cut_action = QAction(QIcon(os.path.join('images', 'scissors.png')), "Cut", self)
        cut_action.setStatusTip("Cut selected text")
        cut_action.triggered.connect(self.editor.cut)
        edit_toolbar.addAction(cut_action)
        edit_menu.addAction(cut_action)
        copy_action = QAction(QIcon(os.path.join('images', 'document-copy.png')), "Copy", self)
        copy_action.setStatusTip("Copy selected text")
        copy_action.triggered.connect(self.editor.copy)
        edit_toolbar.addAction(copy_action)
        edit_menu.addAction(copy_action)
        paste_action = QAction(QIcon(os.path.join('images', 'clipboard-paste-document-text.png')), "Paste", self)
        paste_action.setStatusTip("Paste from clipboard")
        paste_action.triggered.connect(self.editor.paste)
        edit_toolbar.addAction(paste_action)
        edit_menu.addAction(paste_action)
        select_action = QAction(QIcon(os.path.join('images', 'selection-input.png')), "Select all", self)
        select_action.setStatusTip("Select all text")
        select_action.triggered.connect(self.editor.selectAll)
        edit_menu.addAction(select_action)
        edit_menu.addSeparator()
        wrap_action = QAction(QIcon(os.path.join('images', 'arrow-continue.png')), "Wrap text to window", self)
        wrap_action.setStatusTip("Toggle wrap text to window")
        wrap_action.setCheckable(True)
        wrap_action.setChecked(True)
        wrap_action.triggered.connect(self.edit_toggle_wrap)
        edit_menu.addAction(wrap_action)
        help_menu = self.menuBar().addMenu("&Help")
        about_action = QAction(QIcon(os.path.join('images', 'question.png')), "About BunnyPad", self)
        about_action.setStatusTip("Find out more about BunnyPad")  # Hungry!
        about_action.triggered.connect(self.about)
        help_menu.addAction(about_action)
        credits_action = QAction(QIcon(os.path.join('images', 'question.png')), "Credits for BunnyPad", self)
        credits_action.setStatusTip("Find out more about BunnyPad's Team")  # Hungry!
        credits_action.triggered.connect(self.credits)
        help_menu.addAction(credits_action)
        self.update_title()
        self.show()
    def dialog_critical(self, s):
        dlg = QMessageBox(self)
        dlg.setText(s)
        dlg.setIcon(QMessageBox.Critical)
        dlg.show()
    def file_open(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open file", "", "Text documents (*.txt)")
        if path:
            try:
                with open(path, 'rU') as f:
                    text = f.read()
            except Exception as e:
                self.dialog_critical(str(e))
            else:
                self.path = path
                self.editor.setPlainText(text)
                self.update_title()
    def file_save(self):
        if self.path is None:
            return self.file_saveas()
        self._save_to_path(self.path)
    def file_saveas(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save file", "", "Text documents (*.txt)")
        if not path:
            return
        self._save_to_path(path)
    def _save_to_path(self, path):
        text = self.editor.toPlainText()
        try:
            with open(path, 'w') as f:
                f.write(text)
        except Exception as e:
            self.dialog_critical(str(e))
        else:
            self.path = path
            self.update_title()
    def closeEvent(self, event):
       # Show a message box before closing
       reply = QMessageBox.question(self,
                                    "Confirm Exit",
                                    "Are you sure you want to quit?",
                                    QMessageBox.Ok | QMessageBox.Cancel,
                                    QMessageBox.Cancel)
       if reply == QMessageBox.Ok:
           save = QMessageBox.question(self,
                                    "Confirm Save",
                                    "Do you want to save the document? (Note, if the document is blank, just say 'no'.)",
                                    QMessageBox.Yes | QMessageBox.No,
                                    QMessageBox.No)
           if reply == QMessageBox.Yes:
               self.save
           else:
               pass
           event.accept()
          
       else:
          event.ignore()
    def about(self):
        dlg = AboutDialog()
        dlg.exec_()       
    def credits(self):
        dlg = CreditsDialog()
        dlg.exec_()
    def update_title(self):
        self.setWindowTitle("%s - BunnyPad" % (os.path.basename(self.path) if self.path else "Untitled"))
        self.setWindowIcon(QIcon(os.path.join('images', 'bunnypad.png')))
    def edit_toggle_wrap(self):
        self.editor.setLineWrapMode( 1 if self.editor.lineWrapMode() == 0 else 0 )
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName("BunnyPad")
    app.setOrganizationName("GSYT Productions")
    window = MainWindow()
    app.exec_()
