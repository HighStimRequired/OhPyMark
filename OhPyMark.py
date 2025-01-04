import sys
import os
import markdown
import pdfkit

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QToolBar,
    QMenuBar,
    QAction,
    QFileDialog,
    QMessageBox,
    QDialog,
    QLineEdit,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QCheckBox,
    QColorDialog,
    QSplitter,
    QTextBrowser,
    QPlainTextEdit,
    QMenu
)
from PyQt5.QtCore import Qt, QTimer, QFileSystemWatcher

#
# DIALOG: Find & Replace
#
class FindReplaceDialog(QDialog):
    """Simple Find/Replace dialog for QPlainTextEdit."""
    def __init__(self, editor):
        super().__init__()
        self.editor = editor
        self.setWindowTitle("Find & Replace")
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Find
        find_layout = QHBoxLayout()
        find_label = QLabel("Find:")
        self.find_input = QLineEdit()
        find_layout.addWidget(find_label)
        find_layout.addWidget(self.find_input)

        # Replace
        replace_layout = QHBoxLayout()
        replace_label = QLabel("Replace:")
        self.replace_input = QLineEdit()
        replace_layout.addWidget(replace_label)
        replace_layout.addWidget(self.replace_input)

        # Case sensitivity
        self.case_checkbox = QCheckBox("Case Sensitive")

        # Buttons
        button_layout = QHBoxLayout()
        find_button = QPushButton("Find Next")
        replace_button = QPushButton("Replace")
        replace_all_button = QPushButton("Replace All")
        close_button = QPushButton("Close")

        find_button.clicked.connect(self.find_next)
        replace_button.clicked.connect(self.replace)
        replace_all_button.clicked.connect(self.replace_all)
        close_button.clicked.connect(self.close)

        button_layout.addWidget(find_button)
        button_layout.addWidget(replace_button)
        button_layout.addWidget(replace_all_button)
        button_layout.addWidget(close_button)

        layout.addLayout(find_layout)
        layout.addLayout(replace_layout)
        layout.addWidget(self.case_checkbox)
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def find_next(self):
        find_text = self.find_input.text()
        if not find_text:
            return

        doc_text = self.editor.toPlainText()
        cursor = self.editor.textCursor()
        start_pos = cursor.position()

        next_index = doc_text.find(find_text, start_pos)
        if next_index == -1:
            # Wrap around
            next_index = doc_text.find(find_text, 0)
            if next_index == -1:
                QMessageBox.information(self, "Not Found", f"'{find_text}' not found.")
                return

        self.highlight_text(next_index, len(find_text))

    def highlight_text(self, start, length):
        cursor = self.editor.textCursor()
        cursor.setPosition(start)
        cursor.movePosition(cursor.Right, cursor.KeepAnchor, length)
        self.editor.setTextCursor(cursor)

    def replace(self):
        # If nothing is selected, find next
        if not self.editor.textCursor().hasSelection():
            self.find_next()
        # Replace selection
        if self.editor.textCursor().hasSelection():
            self.editor.textCursor().insertText(self.replace_input.text())

    def replace_all(self):
        find_text = self.find_input.text()
        replace_text = self.replace_input.text()
        if not find_text:
            return

        doc_text = self.editor.toPlainText()
        if self.case_checkbox.isChecked():
            count = doc_text.count(find_text)
            new_text = doc_text.replace(find_text, replace_text)
        else:
            # naive case-insensitive approach
            lower_doc = doc_text.lower()
            lower_find = find_text.lower()
            count = lower_doc.count(lower_find)
            new_text = ""
            start = 0
            while True:
                idx = lower_doc.find(lower_find, start)
                if idx == -1:
                    new_text += doc_text[start:]
                    break
                new_text += doc_text[start:idx] + replace_text
                start = idx + len(find_text)

        self.editor.setPlainText(new_text)
        QMessageBox.information(self, "Replace All", f"Replaced {count} occurrences.")


#
# DIALOG: Preferences
#
class PreferencesDialog(QDialog):
    """Simple Preferences dialog for color picking or future expansions."""
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Preferences")
        self.parent = parent
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Example: color picker for main background
        pick_bg_color_layout = QHBoxLayout()
        pick_bg_color_label = QLabel("Background Color:")
        pick_bg_color_btn = QPushButton("Choose...")
        pick_bg_color_btn.clicked.connect(self.choose_bg_color)
        pick_bg_color_layout.addWidget(pick_bg_color_label)
        pick_bg_color_layout.addWidget(pick_bg_color_btn)

        layout.addLayout(pick_bg_color_layout)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)

        layout.addWidget(close_button)
        self.setLayout(layout)

    def choose_bg_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.parent.setStyleSheet(
                f"QMainWindow {{ background-color: {color.name()};}}"
            )


#
# MAIN: Markdown Editor
#
class MarkdownEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fancy Markdown Editor")
        self.setMinimumSize(1200, 700)

        self.current_file = None

        # Themes
        self.themes = {
            "Light": """
                QMainWindow {
                    background-color: #FFFFFF;
                    color: #000000;
                }
                QPlainTextEdit, QTextBrowser {
                    background-color: #FAFAFA;
                    color: #000000;
                    font-family: Consolas, monospace;
                    font-size: 14px;
                }
            """,
            "Dark": """
                QMainWindow {
                    background-color: #282C34;
                    color: #F0F0F0;
                }
                QPlainTextEdit, QTextBrowser {
                    background-color: #1E1E1E;
                    color: #F0F0F0;
                    font-family: Consolas, monospace;
                    font-size: 14px;
                }
            """,
            "Solarized": """
                QMainWindow {
                    background-color: #FDF6E3;
                    color: #657b83;
                }
                QPlainTextEdit, QTextBrowser {
                    background-color: #FDF6E3;
                    color: #657b83;
                    font-family: Consolas, monospace;
                    font-size: 14px;
                }
            """,
            "High Contrast": """
                QMainWindow {
                    background-color: #000000;
                    color: #FFFFFF;
                }
                QPlainTextEdit, QTextBrowser {
                    background-color: #000000;
                    color: #FFFFFF;
                    font-family: Consolas, monospace;
                    font-size: 14px;
                }
            """,
        }
        self.current_theme = "Light"
        self.setStyleSheet(self.themes[self.current_theme])

        # Keep track of last text for autosave
        self.last_text = ""

        # Build UI
        self.initUI()
        self.createMenus()
        self.createToolbars()

        # Context menu for text editor
        self.text_editor.setContextMenuPolicy(Qt.CustomContextMenu)
        self.text_editor.customContextMenuRequested.connect(self.show_context_menu)

        # File watcher for external changes
        self.file_watcher = QFileSystemWatcher(self)
        self.file_watcher.fileChanged.connect(self.on_file_changed)

        # Autosave timer
        self.autosave_timer = QTimer(self)
        self.autosave_timer.setInterval(60_000)  # 1 minute
        self.autosave_timer.timeout.connect(self.auto_save)
        self.autosave_timer.start()

    def initUI(self):
        # Left: Editor, Right: Preview
        self.text_editor = QPlainTextEdit()
        self.text_editor.setPlaceholderText("Write your Markdown here...")
        self.text_editor.textChanged.connect(self.on_text_changed)

        self.preview_browser = QTextBrowser()
        self.preview_browser.setOpenExternalLinks(True)

        splitter = QSplitter(self)
        splitter.addWidget(self.text_editor)
        splitter.addWidget(self.preview_browser)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)

        self.setCentralWidget(splitter)

    def createMenus(self):
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

        # ---------- FILE MENU ----------
        file_menu = menu_bar.addMenu("File")

        new_action = QAction("New", self)
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)

        open_action = QAction("Open...", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save As...", self)
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        import_image_action = QAction("Import Image...", self)
        import_image_action.triggered.connect(self.import_image)
        file_menu.addAction(import_image_action)

        file_menu.addSeparator()

        export_html_action = QAction("Export to HTML", self)
        export_html_action.triggered.connect(self.export_to_html)
        file_menu.addAction(export_html_action)

        export_pdf_action = QAction("Export to PDF", self)
        export_pdf_action.triggered.connect(self.export_to_pdf)
        file_menu.addAction(export_pdf_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # ---------- EDIT MENU ----------
        edit_menu = menu_bar.addMenu("Edit")

        find_replace_action = QAction("Find & Replace", self)
        find_replace_action.triggered.connect(self.open_find_replace)
        edit_menu.addAction(find_replace_action)

        # ---------- FORMAT MENU ----------
        format_menu = menu_bar.addMenu("Format")

        bold_action = QAction("Bold (Ctrl+B)", self)
        bold_action.setShortcut("Ctrl+B")
        bold_action.triggered.connect(lambda: self.insert_markdown("**", "**"))
        format_menu.addAction(bold_action)

        italic_action = QAction("Italic (Ctrl+I)", self)
        italic_action.setShortcut("Ctrl+I")
        italic_action.triggered.connect(lambda: self.insert_markdown("_", "_"))
        format_menu.addAction(italic_action)

        strikethrough_action = QAction("Strikethrough", self)
        strikethrough_action.triggered.connect(lambda: self.insert_markdown("~~", "~~"))
        format_menu.addAction(strikethrough_action)

        inline_code_action = QAction("Inline Code", self)
        inline_code_action.triggered.connect(lambda: self.insert_markdown("`", "`"))
        format_menu.addAction(inline_code_action)

        code_block_action = QAction("Code Block", self)
        code_block_action.triggered.connect(self.insert_code_block)
        format_menu.addAction(code_block_action)

        format_menu.addSeparator()

        heading1_action = QAction("Heading 1", self)
        heading1_action.triggered.connect(lambda: self.insert_heading(1))
        format_menu.addAction(heading1_action)

        heading2_action = QAction("Heading 2", self)
        heading2_action.triggered.connect(lambda: self.insert_heading(2))
        format_menu.addAction(heading2_action)

        heading3_action = QAction("Heading 3", self)
        heading3_action.triggered.connect(lambda: self.insert_heading(3))
        format_menu.addAction(heading3_action)

        format_menu.addSeparator()

        bullet_list_action = QAction("Bullet List", self)
        bullet_list_action.triggered.connect(self.insert_bullet_list)
        format_menu.addAction(bullet_list_action)

        numbered_list_action = QAction("Numbered List", self)
        numbered_list_action.triggered.connect(self.insert_numbered_list)
        format_menu.addAction(numbered_list_action)

        blockquote_action = QAction("Blockquote", self)
        blockquote_action.triggered.connect(self.insert_blockquote)
        format_menu.addAction(blockquote_action)

        table_action = QAction("Insert Table", self)
        table_action.triggered.connect(self.insert_table)
        format_menu.addAction(table_action)

        link_action = QAction("Insert Link", self)
        link_action.triggered.connect(self.insert_link)
        format_menu.addAction(link_action)

        # ---------- VIEW MENU ----------
        view_menu = menu_bar.addMenu("View")

        preferences_action = QAction("Preferences...", self)
        preferences_action.triggered.connect(self.open_preferences)
        view_menu.addAction(preferences_action)

        theme_submenu = view_menu.addMenu("Switch Theme")
        for theme_name in self.themes.keys():
            theme_action = QAction(theme_name, self)
            theme_action.triggered.connect(
                lambda checked, tn=theme_name: self.switch_theme(tn)
            )
            theme_submenu.addAction(theme_action)

    def createToolbars(self):
        """Create a simple toolbar for quick format actions."""
        toolbar = QToolBar("Formatting")
        self.addToolBar(Qt.TopToolBarArea, toolbar)

        # Example: just add Bold and Italic to the toolbar
        bold_tool_action = QAction("B", self)
        bold_tool_action.setToolTip("Bold (Ctrl+B)")
        bold_tool_action.triggered.connect(lambda: self.insert_markdown("**", "**"))
        toolbar.addAction(bold_tool_action)

        italic_tool_action = QAction("I", self)
        italic_tool_action.setToolTip("Italic (Ctrl+I)")
        italic_tool_action.triggered.connect(lambda: self.insert_markdown("_", "_"))
        toolbar.addAction(italic_tool_action)

        # Add more as needed
        code_tool_action = QAction("<>", self)
        code_tool_action.setToolTip("Inline Code")
        code_tool_action.triggered.connect(lambda: self.insert_markdown("`", "`"))
        toolbar.addAction(code_tool_action)

    #
    # CONTEXT MENU
    #
    def show_context_menu(self, pos):
        menu = QMenu(self)
        # A few quick actions
        bold_action = QAction("Bold", self)
        bold_action.triggered.connect(lambda: self.insert_markdown("**", "**"))
        menu.addAction(bold_action)

        italic_action = QAction("Italic", self)
        italic_action.triggered.connect(lambda: self.insert_markdown("_", "_"))
        menu.addAction(italic_action)

        # You can add more right-click actions here
        menu.exec_(self.text_editor.mapToGlobal(pos))

    #
    # FORMAT HELPERS
    #
    def insert_markdown(self, start_marker, end_marker):
        """
        Wrap selected text with specified markdown markers.
        If no text is selected, insert a placeholder.
        """
        cursor = self.text_editor.textCursor()
        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            cursor.insertText(f"{start_marker}{selected_text}{end_marker}")
        else:
            cursor.insertText(f"{start_marker}{end_marker}")
            cursor.movePosition(cursor.Left, cursor.MoveAnchor, len(end_marker))
            self.text_editor.setTextCursor(cursor)

    def insert_code_block(self):
        """
        Insert or wrap selection in triple-backtick code block.
        """
        cursor = self.text_editor.textCursor()
        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            cursor.insertText(f"```\n{selected_text}\n```")
        else:
            block_text = "```\nYour code here\n```"
            cursor.insertText(block_text)
            # Move cursor to inside block
            line_count = block_text.count("\n")
            cursor.movePosition(cursor.Up, cursor.MoveAnchor, line_count - 1)
            cursor.movePosition(cursor.StartOfLine, cursor.MoveAnchor)
            self.text_editor.setTextCursor(cursor)

    def insert_heading(self, level):
        prefix = "#" * level + " "
        cursor = self.text_editor.textCursor()
        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            cursor.insertText(f"{prefix}{selected_text}")
        else:
            cursor.insertText(f"{prefix}Heading {level}")
        self.text_editor.setTextCursor(cursor)

    def insert_bullet_list(self):
        """
        Inserts a basic multi-line bullet list or wraps selection.
        """
        cursor = self.text_editor.textCursor()
        if cursor.hasSelection():
            lines = cursor.selectedText().split('\u2029')  # QPlainTextEdit line separator
            bullet_lines = [f"* {line}" for line in lines]
            cursor.insertText("\n".join(bullet_lines))
        else:
            sample = "* Item 1\n* Item 2\n* Item 3"
            cursor.insertText(sample)

    def insert_numbered_list(self):
        """
        Inserts a basic multi-line numbered list.
        """
        cursor = self.text_editor.textCursor()
        if cursor.hasSelection():
            lines = cursor.selectedText().split('\u2029')
            numbered_lines = []
            for i, line in enumerate(lines, start=1):
                numbered_lines.append(f"{i}. {line}")
            cursor.insertText("\n".join(numbered_lines))
        else:
            sample = "1. Item 1\n2. Item 2\n3. Item 3"
            cursor.insertText(sample)

    def insert_blockquote(self):
        """
        Inserts or wraps text in blockquote syntax.
        """
        cursor = self.text_editor.textCursor()
        if cursor.hasSelection():
            lines = cursor.selectedText().split('\u2029')
            blockquote_lines = [f"> {line}" for line in lines]
            cursor.insertText("\n".join(blockquote_lines))
        else:
            sample = "> This is a blockquote"
            cursor.insertText(sample)

    def insert_table(self):
        """
        Inserts a basic markdown table skeleton.
        """
        sample = (
            "| Column1 | Column2 |\n"
            "|---------|---------|\n"
            "| Data1   | Data2   |\n"
        )
        self.text_editor.insertPlainText(sample)

    def insert_link(self):
        """
        Inserts or wraps text into a link syntax.
        """
        cursor = self.text_editor.textCursor()
        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            cursor.insertText(f"[{selected_text}](https://example.com)")
        else:
            cursor.insertText("[Link Text](https://example.com)")

    #
    # FILE OPERATIONS
    #
    def new_file(self):
        self.remove_file_watcher()
        self.current_file = None
        self.text_editor.clear()
        self.setWindowTitle("Fancy Markdown Editor - Untitled")

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Markdown File",
            "",
            "Markdown Files (*.md *.markdown);;All Files (*)"
        )
        if file_path:
            self.load_file(file_path)

    def load_file(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.text_editor.setPlainText(content)
            self.current_file = file_path
            self.setWindowTitle(f"Fancy Markdown Editor - {os.path.basename(file_path)}")
            self.update_preview()
            self.add_file_watcher(file_path)
        except Exception as e:
            QMessageBox.critical(self, "Open Error", str(e))

    def save_file(self):
        if self.current_file is None:
            self.save_file_as()
        else:
            self.write_to_file(self.current_file)

    def save_file_as(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Markdown File As",
            "",
            "Markdown Files (*.md *.markdown);;All Files (*)"
        )
        if file_path:
            self.write_to_file(file_path)

    def write_to_file(self, file_path):
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.text_editor.toPlainText())
            self.current_file = file_path
            self.setWindowTitle(f"Fancy Markdown Editor - {os.path.basename(file_path)}")
            self.add_file_watcher(file_path)
        except Exception as e:
            QMessageBox.critical(self, "Save Error", str(e))

    #
    # IMAGE IMPORT
    #
    def import_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Insert Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.gif *.bmp);;All Files (*)"
        )
        if file_path:
            insert_text = f"![Image]({file_path})"
            self.text_editor.insertPlainText(insert_text)
            self.update_preview()

    #
    # EXPORT: HTML
    #
    def export_to_html(self):
        md_text = self.text_editor.toPlainText()
        html_content = markdown.markdown(
            md_text,
            extensions=["extra", "toc", "tables", "pymdownx.highlight", "pymdownx.extra", "pymdownx.superfences"]
        )
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export to HTML",
            "",
            "HTML Files (*.html);;All Files (*)"
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(html_content)
                QMessageBox.information(self, "Export to HTML", f"Exported to {file_path} successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", str(e))

    #
    # EXPORT: PDF (pdfkit + wkhtmltopdf)
    #
    def export_to_pdf(self):
        md_text = self.text_editor.toPlainText()
        html_content = markdown.markdown(
            md_text,
            extensions=["extra", "toc", "tables", "pymdownx.highlight", "pymdownx.extra", "pymdownx.superfences"]
        )
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export to PDF",
            "",
            "PDF Files (*.pdf);;All Files (*)"
        )
        if file_path:
            try:
                pdfkit.from_string(html_content, file_path)
                QMessageBox.information(self, "Export to PDF", f"Exported to {file_path} successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", str(e))

    #
    # AUTOSAVE
    #
    def on_text_changed(self):
        # Update preview on every text change
        self.update_preview()

    def auto_save(self):
        """
        Autosave to a .autosave file if changes occurred since last autosave.
        """
        current_text = self.text_editor.toPlainText()
        if current_text != self.last_text and self.current_file:
            autosave_path = self.current_file + ".autosave"
            try:
                with open(autosave_path, "w", encoding="utf-8") as f:
                    f.write(current_text)
                # Optionally show a status or something
                # e.g., self.statusBar().showMessage(f"Autosaved to {autosave_path}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Autosave Error", str(e))

        # Remember this text for next check
        self.last_text = current_text

    #
    # FILE WATCHER
    #
    def add_file_watcher(self, file_path):
        self.remove_file_watcher()
        if os.path.isfile(file_path):
            self.file_watcher.addPath(file_path)

    def remove_file_watcher(self):
        watched = self.file_watcher.files()
        if watched:
            self.file_watcher.removePaths(watched)

    def on_file_changed(self, path):
        """
        Prompt user if they want to reload the file because of external changes.
        """
        if not os.path.isfile(path):
            return  # file might have been deleted or moved
        reply = QMessageBox.question(
            self,
            "File changed externally",
            f"The file '{os.path.basename(path)}' was modified outside this editor.\n"
            f"Reload it now and lose unsaved changes?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.load_file(path)

    #
    # LIVE PREVIEW
    #
    def update_preview(self):
        md_text = self.text_editor.toPlainText()
        html_content = markdown.markdown(
            md_text,
            extensions=["extra", "toc", "tables", "pymdownx.highlight", "pymdownx.extra", "pymdownx.superfences"]
        )
        self.preview_browser.setHtml(html_content)

    #
    # FIND & REPLACE
    #
    def open_find_replace(self):
        dialog = FindReplaceDialog(self.text_editor)
        dialog.exec_()

    #
    # PREFERENCES
    #
    def open_preferences(self):
        dialog = PreferencesDialog(self)
        dialog.exec_()

    #
    # THEME SWITCH
    #
    def switch_theme(self, theme_name):
        if theme_name in self.themes:
            self.setStyleSheet(self.themes[theme_name])
            self.current_theme = theme_name


def main():
    app = QApplication(sys.argv)
    editor = MarkdownEditor()
    editor.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
