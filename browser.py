import sys
import os
from urllib.parse import quote_plus, urlparse
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile, QWebEngineSettings
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QIcon, QAction, QKeySequence
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QLineEdit, QPushButton,
    QFileDialog, QMessageBox, QMenu, QDialog, QVBoxLayout,
    QListWidget, QListWidgetItem, QTabWidget
)

# -------------------- CONFIG --------------------
HOME_URL = os.environ.get("DESI_HOME_URL", "http://127.0.0.1:5000")
SEARCH_PATH = "/search?q="
APP_NAME = "SwaDesi Browser"
APP_ICON_PATH = os.path.join("static", "logo.png")
CUSTOM_USER_AGENT = "INDIBrowser/1.0 (+India-first; Chromium-QtWebEngine)"
# ------------------------------------------------

def is_probable_url(text: str) -> bool:
    text = text.strip()
    if not text:
        return False
    parsed = urlparse(text)
    if parsed.scheme in ("http", "https"):
        return True
    if " " not in text and "." in text:
        return True
    return False

# -------------------- Custom Page --------------------
class WebEnginePage(QWebEnginePage):
    def createWindow(self, _type):
        # Open links in a new tab
        new_tab_view = QWebEngineView()
        new_tab_view.setPage(WebEnginePage(new_tab_view))
        main_window = QApplication.activeWindow()
        idx = main_window.tabs.addTab(new_tab_view, "New Tab")
        main_window.tabs.setCurrentIndex(idx)
        return new_tab_view.page()


# -------------------- Main Window --------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.history = []
        self.downloads = []

        self.setWindowTitle(APP_NAME)
        if os.path.exists(APP_ICON_PATH):
            self.setWindowIcon(QIcon(APP_ICON_PATH))

        # Web profile
        profile = QWebEngineProfile.defaultProfile()
        profile.setHttpUserAgent(CUSTOM_USER_AGENT)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)

        # Start with homepage
        self.new_tab(HOME_URL)

        # Address bar
        self.addr = QLineEdit()
        self.addr.setPlaceholderText("Type URL or search…")
        self.addr.returnPressed.connect(self.navigate_from_address)

        # Toolbar
        tb = QToolBar("Navigation")
        tb.setMovable(False)
        self.addToolBar(tb)

        back_act = QAction("◀", self)
        back_act.triggered.connect(lambda: self.current_view().back())
        tb.addAction(back_act)

        fwd_act = QAction("▶", self)
        fwd_act.triggered.connect(lambda: self.current_view().forward())
        tb.addAction(fwd_act)

        reload_act = QAction("⟳", self)
        reload_act.triggered.connect(lambda: self.current_view().reload())
        tb.addAction(reload_act)

        home_act = QAction("🏠", self)
        home_act.triggered.connect(lambda: self.current_view().load(QUrl(HOME_URL)))
        tb.addAction(home_act)

        tb.addSeparator()
        tb.addWidget(self.addr)

        go_btn = QPushButton("Go")
        go_btn.clicked.connect(self.navigate_from_address)
        tb.addWidget(go_btn)

        # 3-dot menu
        menu_button = QPushButton("⋮", self)
        menu_button.setFixedWidth(30)
        menu = QMenu()
        new_tab_action = QAction("New Tab", self)
        incognito_tab_action = QAction("New Incognito Tab", self)
        history_action = QAction("History", self)
        downloads_action = QAction("Downloads", self)
       
        menu.addAction(new_tab_action)
        menu.addAction(incognito_tab_action)
        menu.addAction(history_action)
        menu.addAction(downloads_action)
        
        menu_button.setMenu(menu)
        self.addToolBar("Menu").addWidget(menu_button)

        new_tab_action.triggered.connect(lambda: self.new_tab(HOME_URL))
        incognito_tab_action.triggered.connect(self.incognito_tab)
        history_action.triggered.connect(self.show_history)
        downloads_action.triggered.connect(self.show_downloads)
        

        # Shortcuts
        self.addr_shortcut = QAction(self)
        self.addr_shortcut.setShortcut(QKeySequence("Ctrl+L"))
        self.addr_shortcut.triggered.connect(lambda: (self.addr.setFocus(), self.addr.selectAll()))
        self.addAction(self.addr_shortcut)

        open_act = QAction("Open File", self)
        open_act.setShortcut(QKeySequence("Ctrl+O"))
        open_act.triggered.connect(self.open_file)
        self.addAction(open_act)

        # Update address bar on tab change
        self.tabs.currentChanged.connect(self.on_tab_changed)

    def current_view(self):
        return self.tabs.currentWidget()

    # ---------- Tabs ----------
    def new_tab(self, url=None):
        browser = QWebEngineView()
        browser.setPage(WebEnginePage(browser))
        browser.settings().setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
        browser.settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        browser.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)

        if url:
            browser.load(QUrl(url))
        else:
            browser.setHtml("<h2>New Tab</h2>")

        index = self.tabs.addTab(browser, "New Tab")
        self.tabs.setCurrentIndex(index)

        # Update tab title dynamically
        browser.titleChanged.connect(lambda title, idx=index: self.tabs.setTabText(idx, title))
        browser.urlChanged.connect(self.on_url_changed)

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)

    # ---------- Menu Actions ----------
    def show_history(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("History")
        layout = QVBoxLayout()
        list_widget = QListWidget()

        for url in self.history:
            item = QListWidgetItem(url)
            list_widget.addItem(item)

        clear_btn = QPushButton("Clear All")
        clear_btn.clicked.connect(lambda: self.clear_history(list_widget, dlg))

        layout.addWidget(list_widget)
        layout.addWidget(clear_btn)
        dlg.setLayout(layout)
        dlg.exec()

    def clear_history(self, list_widget, dialog):
        confirm = QMessageBox.question(self, "Confirm", "Clear all history?")
        if confirm == QMessageBox.StandardButton.Yes:
            self.history.clear()
            list_widget.clear()
        dialog.accept()
    def incognito_tab(self):
        QMessageBox.information(self, "Incognito Tab", "Incognito tab feature not implemented yet.")

    def show_downloads(self):
        QMessageBox.information(self, "Downloads", "\n".join(self.downloads) or "No downloads yet.")

    # ---------- Navigation ----------
    def on_url_changed(self, qurl: QUrl):
        self.addr.setText(qurl.toString())
        url = qurl.toString()
        if url not in self.history:
            self.history.append(url)

    def on_tab_changed(self, index):
        view = self.current_view()
        if view:
            self.addr.setText(view.url().toString())

    def navigate_from_address(self):
        text = self.addr.text().strip()
        if not text:
            return
        if is_probable_url(text):
            if not urlparse(text).scheme:
                text = "http://" + text
            self.current_view().load(QUrl(text))
        else:
            url = f"{HOME_URL.rstrip('/')}{SEARCH_PATH}{quote_plus(text)}"
            self.current_view().load(QUrl(url))

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open HTML File", "", "HTML Files (*.html *.htm);;All Files (*)")
        if path:
            self.current_view().load(QUrl.fromLocalFile(path))


# -------------------- Entry --------------------
def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.resize(1200, 800)
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
