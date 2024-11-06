import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QAction, QFileDialog, QVBoxLayout, QWidget, QTreeView, QFileSystemModel, QInputDialog, QMessageBox
from PyQt5.QtGui import QColor, QTextCharFormat, QSyntaxHighlighter
from PyQt5.QtCore import QTimer, Qt, QRegularExpression, QModelIndex, QFileInfo

class Highlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlightingRules = []
        self.setTheme("dark")  # Establecer tema inicial
        self.createHighlightingRules()

    def createHighlightingRules(self):
        keywordFormat = QTextCharFormat()
        keywordFormat.setForeground(self.themeColor)  # Color para palabras clave
        keywords = ["def", "class", "import", "from", "as", "if", "else", "elif", "while", "for", "return", "in", "not", "and", "or", "const", "'", "{", "}", "[", "]", "0", "*", ".", "log", "#", "<", ">", "/"]
        self.highlightingRules += [(r'\b' + keyword + r'\b', keywordFormat) for keyword in keywords]

        # Formato para comentarios
        commentFormat = QTextCharFormat()
        commentFormat.setForeground(QColor(100, 100, 100))  # Color para comentarios
        self.highlightingRules.append((r'#.*', commentFormat))

        # Formato para cadenas de texto
        stringFormat = QTextCharFormat()
        stringFormat.setForeground(self.themeColor)  # Color para cadenas de texto
        self.highlightingRules.append((r'\".*?\"', stringFormat))  # Cadenas entre comillas dobles

    def setTheme(self, theme):
        if theme == "dark":
            self.themeColor = QColor(204, 120, 50)  # Color para palabras clave y cadenas
            self.backgroundColor = "#282c34"
            self.textColor = "#abb2bf"
        elif theme == "light":
            self.themeColor = QColor(0, 0, 0)  # Color para palabras clave y cadenas
            self.backgroundColor = "#ffffff"
            self.textColor = "#000000"
        self.createHighlightingRules()

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
        self.snippets = {}  # Diccionario para almacenar snippets
        self.initUI()
        self.autoSaveTimer = QTimer(self)
        self.autoSaveTimer.timeout.connect(self.autoSave)
        self.autoSaveTimer.start(5000)  # Guardar cada 5 segundos

    def initUI(self):
        self.setWindowTitle('Editor de Código')
        self.setGeometry(100, 100, 800, 600)

        # Configurar el tema oscuro
        self.setStyleSheet("background-color: #282c34; color: #abb2bf;")  # Fondo oscuro y texto claro

        # Crear un widget central y un layout horizontal
        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)
        layout = QVBoxLayout(centralWidget)

        # Crear el panel lateral para archivos
        self.fileTree = QTreeView(self)
        self.fileModel = QFileSystemModel()
        self.fileModel.setRootPath('')  # Establecer la ruta raíz
        self.fileTree.setModel(self.fileModel)
        self.fileTree.setRootIndex(self.fileModel.index(''))  # Mostrar la raíz del sistema de archivos
        self.fileTree.clicked.connect(self.on_file_clicked)  # Conectar la señal de clic
        layout.addWidget(self.fileTree)

        # Crear el área de texto para el editor
        self.textEdit = QTextEdit(self)
        self.textEdit.setStyleSheet("background-color: #282c34; color: #abb2bf;")  # Fondo oscuro y texto claro
        layout.addWidget(self.textEdit)

        # Aplicar el resaltador de sintaxis
        self.highlighter = Highlighter(self.textEdit.document())

        # Crear acciones para el menú
        openFile = QAction('Abrir', self)
        openFile.triggered.connect(self.openFile)

        saveFile = QAction('Guardar', self)
        saveFile.triggered.connect(self.saveFile)

        changeTheme = QAction('Cambiar Tema', self)
        changeTheme.triggered.connect(self.showThemeDialog)

        addSnippet = QAction('Agregar Snippet', self)
        addSnippet.triggered.connect(self.addSnippet)

        insertSnippet = QAction('Insertar Snippet', self)
        insertSnippet.triggered.connect(self.insertSnippet)

        # Crear la barra de menú
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('Archivo')
        fileMenu.addAction(openFile)
        fileMenu.addAction(saveFile)
        fileMenu.addAction(changeTheme)
        fileMenu.addAction(addSnippet)
        fileMenu.addAction(insertSnippet)

        # Conectar atajos de teclado para cambiar el tema
        self.textEdit.setFocusPolicy(Qt.StrongFocus)

    def keyPressEvent(self, event):
        if event.modifiers() == (Qt.ControlModifier | Qt.ShiftModifier):
            if event.key() == Qt.Key_P:  # Ctrl + Shift + P
                self.showThemeDialog()
        else:
            super().keyPressEvent(event)  # Permitir que el QTextEdit maneje la entrada de texto

    def showThemeDialog(self):
        themes = ["dark", "light"]
        theme, ok = QInputDialog.getItem(self, "Seleccionar Tema", "Selecciona un tema:", themes, 0, False)
        if ok and theme:
            self.highlighter.setTheme(theme)
            self.updateEditorStyle(theme)

    def updateEditorStyle(self, theme):
        if theme == "dark":
            self.setStyleSheet("background-color: #282c34; color: #abb2bf;")  # Fondo oscuro y texto claro
            self.textEdit.setStyleSheet("background-color: #282c34; color: #abb2bf;")  # Fondo oscuro y texto claro
        elif theme == "light":
            self.setStyleSheet("background-color: #ffffff; color: #000000;")  # Fondo claro y texto oscuro
            self.textEdit.setStyleSheet("background-color: #ffffff; color: #000000;")  # Fondo claro y texto oscuro

    def on_file_clicked(self, index: QModelIndex):
        # Obtener la ruta del archivo seleccionado
        file_path = self.fileModel.filePath(index)
        if self.fileModel.isDir(index):
            return  # No hacer nada si es un directorio
        # Abrir el archivo en el editor
        with open(file_path, 'r') as f:
            self.textEdit.setPlainText(f.read())
        self.currentFile = file_path  # Guardar el archivo actual
        self.updateFileTree(file_path)  # Actualizar el árbol de archivos

    def openFile(self):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getOpenFileName(self, "Abrir Archivo", "", "Python Files (*.py);;All Files (*)", options=options)
        if filename:
            with open(filename, 'r') as f:
                self.textEdit.setPlainText(f.read())
            self.currentFile = filename  # Guardar el archivo actual
            self.updateFileTree(filename)  # Actualizar el árbol de archivos

    def updateFileTree(self, filename):
        # Obtener el directorio del archivo abierto y establecerlo como raíz del modelo
        directory = QFileInfo(filename).absolutePath()
        self.fileModel.setRootPath(directory)
        self.fileTree.setRootIndex(self.fileModel.index(directory))  # Mostrar el directorio actual en el árbol

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

    def addSnippet(self):
        snippet_name, ok1 = QInputDialog.getText(self, "Agregar Snippet", "Nombre del Snippet:")
        if ok1 and snippet_name:
            snippet_code, ok2 = QInputDialog.getMultiLineText(self, "Agregar Snippet", "Código del Snippet:")
            if ok2:
                self.snippets[snippet_name] = snippet_code
                QMessageBox.information(self, "Snippet Agregado", f"Snippet '{snippet_name}' agregado exitosamente.")

    def insertSnippet(self):
        if not self.snippets:
            QMessageBox.warning(self, "Sin Snippets", "No hay snippets disponibles.")
            return
        snippet_name, ok = QInputDialog.getItem(self, "Insertar Snippet", "Selecciona un Snippet:", list(self.snippets.keys()), 0, False)
        if ok and snippet_name:
            self.textEdit.insertPlainText(self.snippets[snippet_name])  # Insertar el snippet en el editor

if __name__ == '__main__':
    app = QApplication(sys.argv)
    editor = CodeEditor()
    editor.show()
    sys.exit(app.exec_())