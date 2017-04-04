import sys, aiohttp, asyncio
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

__author__ = "Alan Baumgartner"

class ImportDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(self.windowFlags() ^ Qt.WindowContextHelpButtonHint)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowTitle('Import Usernames')
        layout = QGridLayout()

        self.file_label = QLabel('Filename')
        self.file_text = QLineEdit()

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(self.file_label, 0, 0)
        layout.addWidget(self.file_text, 0, 1)

        layout.addWidget(buttons, 1, 0, 2, 0)

        self.setLayout(layout)
        self.setGeometry(400, 400, 300, 60)

    @staticmethod
    def getFileInfo():
        dialog = ImportDialog()
        result = dialog.exec_()
        return dialog.file_text.text(), result == QDialog.Accepted


class ExportDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(self.windowFlags() ^ Qt.WindowContextHelpButtonHint)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowTitle('Export Usernames')
        layout = QGridLayout()

        self.file_label = QLabel('Filename')
        self.file_text = QLineEdit()

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(self.file_label, 0, 0)
        layout.addWidget(self.file_text, 0, 1)

        layout.addWidget(buttons, 1, 0, 2, 0)

        self.setLayout(layout)
        self.setGeometry(400, 400, 300, 60)

    @staticmethod
    def getFileInfo():
        dialog = ExportDialog()
        result = dialog.exec_()
        return dialog.file_text.text(), result == QDialog.Accepted


class Checker(QThread):

    #Signal Variables.
    update = pyqtSignal(object)
    pupdate = pyqtSignal(object)
    count = 0

    #Global Variables.
    URL = 'https://www.twitter.com/{}'

    def __init__(self):
        super().__init__()

    async def check_usernames(self, username, sem, session, lock):
        #Checks username availability
        async with sem:
            try:
                async with session.get(self.URL.format(username)) as resp:
                    assert resp.status == 404
                    self.update.emit(username)
            except:
                pass

            finally:
                with await lock:
                    self.count += 1
                self.pupdate.emit(self.count)

    async def main(self):
        #Packs all usernames into a tasklist
        sem = asyncio.BoundedSemaphore(50)
        lock = asyncio.Lock()
        async with aiohttp.ClientSession() as session:
            usernames = get_usernames()
            tasks = [self.check_usernames(username, sem, session, lock) for username in usernames]
            await asyncio.gather(*tasks)

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.main())
        finally:
            loop.close()

class App(QMainWindow):
 
    def __init__(self):

        #Declares some constructor variables.
        super().__init__()
        self.title = 'Twitter Username Checker'
        self.left = 300
        self.top = 300
        self.width = 500
        self.height = 500
        self.initUI()

    def initUI(self):

        #Setup layout.
        wid = QWidget(self)
        self.setCentralWidget(wid)
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
 
        layout = QGridLayout()
        wid.setLayout(layout)
 
        #Create Widgets.
        menu_bar = self.menuBar()

        menu = menu_bar.addMenu("File")

        import_action = QAction("Import Usernames", self)
        import_action.triggered.connect(self.import_usernames)

        export_action = QAction("Export Usernames", self)
        export_action.triggered.connect(self.export_usernames)

        quit_action = QAction("Close", self)
        quit_action.triggered.connect(self.quit)

        menu.addAction(import_action)
        menu.addAction(export_action)
        menu.addAction(quit_action)

        self.start_button = QPushButton('Start')
        self.start_button.clicked.connect(self.start_clicked)

        self.stop_button = QPushButton('Stop')
        self.stop_button.clicked.connect(self.stop_clicked)

        self.input_text = QTextEdit()
        self.output_text = QTextEdit()

        input_label = QLabel('Usernames to Check')
        input_label.setAlignment(Qt.AlignCenter)

        output_label = QLabel('Available Usernames')
        output_label.setAlignment(Qt.AlignCenter)

        self.progress_bar = QProgressBar()
 
        #Add widgets to the window.
        layout.addWidget(input_label, 0, 0)
        layout.addWidget(output_label, 0, 1)
        layout.addWidget(self.input_text, 1, 0)
        layout.addWidget(self.output_text, 1, 1)
        layout.addWidget(self.start_button, 2, 0)
        layout.addWidget(self.stop_button, 2, 1)
        layout.addWidget(self.progress_bar, 3, 0, 4, 0)
		
    #When the start button is clicked, start the checker thread.
    def start_clicked(self):
        usernames = get_usernames()
        self.progress_bar.setMaximum(len(usernames))
        self.output_text.setText('')
        self.thread = Checker()
        self.thread.update.connect(self.update_text)
        self.thread.pupdate.connect(self.update_progress)
        self.thread.start()

    #When the stop button is clicked, terminate the checker thread.
    def stop_clicked(self):
        try:
            self.thread.terminate()
        except:
            pass
 
    #When the checker thread emits a signal, update the output textbox.
    def update_text(self, text):
        self.output_text.append(str(text))

    #When the checker thread emits a signal, update the progress bar.
    def update_progress(self, val):
        self.progress_bar.setValue(val)

    #Saves usernames from the output text.
    def export_usernames(self):
        exportDialog = ExportDialog()
        filename, result = exportDialog.getFileInfo()
        if result:
            try:
                proxies = self.output_text.toPlainText()
                proxies = proxies.strip()
                with open(filename, "w") as a:
                    a.write(proxies)
            except:
                pass
        else:
            pass

    def import_usernames(self):
        importDialog = ImportDialog()
        filename, result = importDialog.getFileInfo()
        if result:
            try:
                with open(filename, "r") as f:
                    out = f.read()
                    self.input_text.setText(out)
            except:
                pass
        else:
            pass

    def quit(self):
        sys.exit()

if __name__ == "__main__":

    def get_usernames():
        proxies = window.input_text.toPlainText()
        proxies = proxies.strip()
        proxies = proxies.split('\n')
        return proxies

    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec_())