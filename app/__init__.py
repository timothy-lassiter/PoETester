try:
    from ._version import version as VERSION
except ImportError:
    VERSION = "DEV"


ORGANIZATION_NAME = "My Organization"
DOMAIN_NAME = "example.com"
APP_NAME = "My App"


def run():
    import sys
    import locale
    from PySide6.QtWidgets import QApplication
    from app.widgets.mainwindow import MainWindow

    locale.setlocale(locale.LC_ALL, "")

    QApplication.setOrganizationName(ORGANIZATION_NAME)
    QApplication.setOrganizationDomain(DOMAIN_NAME)
    QApplication.setApplicationName(APP_NAME)
    QApplication.setApplicationVersion(VERSION)

    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())
