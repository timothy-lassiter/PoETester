try:
    from ._version import version as VERSION
except ImportError:
    from setuptools_scm import get_version

    VERSION = get_version()


ORGANIZATION_NAME = "My Organization"
DOMAIN_NAME = "example.com"
APP_NAME = "My App"


def run():
    import locale
    import sys

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
