try:
    from ._version import version as VERSION
except ImportError:
    from setuptools_scm import get_version

    VERSION = get_version()


# TODO: Update application information
APP_NAME = "PoE Tester"
APP_DESCRIPTION = "Application for testing PoE on Rugged Science computers"
APP_AUTHOR = "Timothy Lassiter"
DOMAIN_NAME = "ruggedscience.com"
ORGANIZATION_NAME = "Rugged Science"


def run():
    import locale
    import sys
    import os
    
    from PySide6.QtWidgets import QApplication

    from app.widgets.mainwindow import MainWindow

    locale.setlocale(locale.LC_ALL, "")

    QApplication.setOrganizationName(ORGANIZATION_NAME)
    QApplication.setOrganizationDomain(DOMAIN_NAME)
    QApplication.setApplicationName(APP_NAME)
    QApplication.setApplicationVersion(VERSION)

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    widget = MainWindow(sys.argv)
    widget.show()
    sys.exit(app.exec())
