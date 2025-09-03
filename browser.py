import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QKeySequence, QColor
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtNetwork import QNetworkProxy

class UltimateWaveMultiProxy(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MCLand Browser ILIYA")
        self.setGeometry(100, 100, 1400, 900)
        self.setWindowIcon(QIcon("google_logo_small.png"))

        self.dark_mode = False
        self.proxy_index = -1  # -1 یعنی هیچ پراکسی
        self.proxies = [
            ("51.79.144.66", 8080, QNetworkProxy.HttpProxy),
            ("45.94.176.15", 1080, QNetworkProxy.Socks5Proxy),
            ("51.158.123.35", 8811, QNetworkProxy.HttpProxy),
            ("167.71.5.83", 3128, QNetworkProxy.HttpProxy)
        ]

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.tabs.setMovable(True)
        self.tabs.currentChanged.connect(self.tab_animation)
        self.setCentralWidget(self.tabs)

        self.navbar = QToolBar()
        self.addToolBar(self.navbar)
        self.create_actions()

        self.add_new_tab(QUrl("https://www.google.com/?hl=en-GB"), "Google")
        self.apply_theme(animate=False)

        QShortcut(QKeySequence("F11"), self, self.toggle_fullscreen)
        QShortcut(QKeySequence("Ctrl+T"), self, self.add_new_tab)
        QShortcut(QKeySequence("Ctrl+W"), self, lambda: self.close_current_tab(self.tabs.currentIndex()))
        QShortcut(QKeySequence("Ctrl+R"), self, lambda: self.tabs.currentWidget().reload())

    def create_actions(self):
        back_btn = QAction("⟵", self)
        back_btn.triggered.connect(lambda: self.tabs.currentWidget().back())
        self.navbar.addAction(back_btn)

        forward_btn = QAction("⟶", self)
        forward_btn.triggered.connect(lambda: self.tabs.currentWidget().forward())
        self.navbar.addAction(forward_btn)

        reload_btn = QAction("⟳", self)
        reload_btn.triggered.connect(lambda: self.tabs.currentWidget().reload())
        self.navbar.addAction(reload_btn)

        home_btn = QAction("🏠", self)
        home_btn.triggered.connect(self.navigate_home)
        self.navbar.addAction(home_btn)

        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Search or type URL...")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.navbar.addWidget(self.url_bar)

        new_tab_btn = QAction("+", self)
        new_tab_btn.triggered.connect(lambda _: self.add_new_tab())
        self.navbar.addAction(new_tab_btn)

        theme_toggle_btn = QAction("🌓", self)
        theme_toggle_btn.triggered.connect(lambda: self.toggle_theme(animate=True))
        self.navbar.addAction(theme_toggle_btn)

        proxy_toggle_btn = QAction("🛡️ VPN", self)
        proxy_toggle_btn.triggered.connect(self.switch_proxy)
        self.navbar.addAction(proxy_toggle_btn)

    def switch_proxy(self):
        self.proxy_index += 1
        if self.proxy_index >= len(self.proxies):
            self.proxy_index = -1  # هیچ پراکسی
        profile = QWebEngineProfile.defaultProfile()
        if self.proxy_index == -1:
            profile.setHttpProxy(QNetworkProxy(QNetworkProxy.NoProxy))
        else:
            host, port, ptype = self.proxies[self.proxy_index]
            profile.setHttpProxy(QNetworkProxy(ptype, host, port))

    def apply_theme(self, animate=True):
        if self.dark_mode:
            self.setStyleSheet("""
                QMainWindow {background-color: #121212; color: #e0e0e0;}
                QToolBar {background-color: #1f1f1f; spacing: 6px; padding: 3px;}
                QLineEdit {background-color: #2c2c2c; color: #ffffff; border: 1px solid #444; border-radius: 8px; padding: 10px; font-size: 18px;}
                QTabWidget::pane {border: 0;}
                QTabBar::tab {background: #2c2c2c; color: #e0e0e0; padding: 10px; border-radius: 5px;}
                QTabBar::tab:selected {background: #3d3d3d; font-weight: bold;}
            """)
        else:
            self.setStyleSheet("""
                QMainWindow {background-color: #ffffff; color: #202124;}
                QToolBar {background-color: #f8f9fa; spacing: 6px; padding: 3px;}
                QLineEdit {background-color: #ffffff; color: #202124; border: 2px solid #dadce0; border-radius: 8px; padding: 10px; font-size: 18px;}
                QTabWidget::pane {border: 0;}
                QTabBar::tab {background: #e8eaed; color: #202124; padding: 10px; border-radius: 5px;}
                QTabBar::tab:selected {background: #ffffff; font-weight: bold;}
            """)

    def toggle_theme(self, animate=False):
        self.dark_mode = not self.dark_mode
        self.apply_theme(animate=animate)

    def add_new_tab(self, qurl=None, label="New Tab"):
        if qurl is None:
            qurl = QUrl("https://www.google.com/?hl=en-GB")
        browser = QWebEngineView()
        browser.setUrl(qurl)
        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)
        browser.urlChanged.connect(lambda q, browser=browser: self.update_url(q, browser))
        browser.settings().setAttribute(browser.settings().Accelerated2dCanvasEnabled, True)
        browser.settings().setAttribute(browser.settings().ScrollAnimatorEnabled, True)

    def tab_open_doubleclick(self, i):
        if i == -1:
            self.add_new_tab()

    def tab_animation(self, index):
        tab_bar = self.tabs.tabBar()
        tab_bar.setTabTextColor(index, QColor("#00aaff"))
        QTimer.singleShot(300, lambda: tab_bar.setTabTextColor(index, QColor("#ffffff") if self.dark_mode else QColor("#202124")))

    def current_tab_changed(self, i):
        qurl = self.tabs.currentWidget().url()
        self.update_url(qurl, self.tabs.currentWidget())

    def close_current_tab(self, i):
        if self.tabs.count() < 2:
            return
        self.tabs.removeTab(i)

    def navigate_home(self):
        self.tabs.currentWidget().setUrl(QUrl("https://www.google.com/?hl=en-GB"))

    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith("http"):
            url = "https://www.google.com/search?q=" + url.replace(" ", "+")
        self.tabs.currentWidget().setUrl(QUrl(url))

    def update_url(self, q, browser=None):
        if browser != self.tabs.currentWidget():
            return
        self.url_bar.setText(q.toString())

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

app = QApplication(sys.argv)
QApplication.setApplicationName("مرورگر ایلیا Ultimate-VPN-Pro 😎")
window = UltimateWaveMultiProxy()
window.show()
sys.exit(app.exec_())

