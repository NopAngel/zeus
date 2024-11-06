import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QAction, QFileDialog
from PyQt5.QtGui import QColor, QTextCharFormat, QSyntaxHighlighter
from PyQt5.QtCore import QTimer, Qt, QRegularExpression

class Highlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlightingRules = []

        # Definir colores para la sintaxis
        keywordFormat = QTextCharFormat()
        keywordFormat.setForeground(QColor(204, 120, 50))  # Color para palabras clave
        keywords = ["def", "class", "import", "from", "as", "if", "else", "elif", "while", "for", "return", "in", "not", "and", "or","const","'","{","}","[","]","0","*",".","log","#","<",">","/"]
        self.highlightingRules += [(r'\b' + keyword + r'\b', keywordFormat) for keyword in keywords]

        # Formato para comentarios
        commentFormat = QTextCharFormat()
        commentFormat.setForeground(QColor(100, 100, 100))  # Color para comentarios
        self.highlightingRules.append((r'#.*', commentFormat))

        # Formato para cadenas de texto
        stringFormat = QTextCharFormat()
        stringFormat.setForeground(QColor(204, 120, 50))  # Color para cadenas de texto
        self.highlightingRules.append((r'\".*?\"', stringFormat))  # Cadenas entre comillas dobles

    def highlightBlock(self, text):
        for pattern, fmt in self.highlightingRules:
            expression = QRegularExpression(pattern)
            matchIterator = expression.globalMatch(text)  # Obtener el iterador de coincidencias
            while matchIterator.hasNext():  # Verificar si hay más coincidencias
                match = matchIterator.next()  # Obtener la siguiente coincidencia
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)

class CodeEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()
        self.autoSaveTimer = QTimer(self)
        self.autoSaveTimer.timeout.connect(self.autoSave)
        self.autoSaveTimer.start(5000)  # Guardar cada 5 segundos

    def initUI(self):
        self.setWindowTitle('Editor de Código')
        self.setGeometry(100, 100, 800, 600)

        # Configurar el tema oscuro
        self.setStyleSheet("background-color: #282c34; color: #abb2bf;")  # Fondo oscuro y texto claro

        self.textEdit = QTextEdit(self)
        self.textEdit.setStyleSheet("background-color: #282c34; color: #abb2bf;")  # Fondo oscuro y texto claro
        self.setCentralWidget(self.textEdit)

        # Aplicar el resaltador de sintaxis
        self.highlighter = Highlighter(self.textEdit.document())

        # Crear acciones para el menú
        openFile = QAction('Abrir', self)
        openFile.triggered.connect(self.openFile)

        saveFile = QAction('Guardar', self)
        saveFile.triggered.connect(self.saveFile)

        # Crear la barra de menú
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('Archivo')
        fileMenu.addAction(openFile)
        fileMenu.addAction(saveFile)

    def openFile(self):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getOpenFileName(self, "Abrir Archivo", "", "Python Files (*.py);;All Files (*)", options=options)
        if filename:
            with open(filename, 'r') as f:
                self.textEdit.setPlainText(f.read())
            self.currentFile = filename  # Guardar el archivo actual

    def saveFile(self):
        try:
            if hasattr(self, 'currentFile'):
                print(f"Guardando en: {self.currentFile}")  # Imprimir la ruta del archivo
                with open(self.currentFile, 'w') as f:
                    f.write(self.textEdit.toPlainText())
            else:
                self.saveAsFile()
        except Exception as e:
            print(f"Error al guardar el archivo: {e}")

    def saveAsFile(self):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getSaveFileName(self, "Guardar Archivo", "", "Python Files (*.py);;All Files (*)", options=options)
        if filename:
            self.currentFile = filename
            self.saveFile()

    def autoSave(self):
        if hasattr(self, 'currentFile'):
            self.saveFile()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    editor = CodeEditor()
    editor.show()
    sys.exit(app.exec_())