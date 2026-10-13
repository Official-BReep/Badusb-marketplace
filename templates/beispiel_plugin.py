"""Minimal example plugin for the BadUSB IDE marketplace."""

PLUGIN_NAME = "Marketplace-Beispiel2"
PLUGIN_VERSION = "1.0.0"
PLUGIN_DESCRIPTION = "Zeigt eine kurze Statusmeldung an."


def register(ide):
    from PyQt6.QtGui import QAction

    action = QAction("Beispiel-Plugin: Hallo", ide)
    action.triggered.connect(
        lambda: ide.statusBar().showMessage("Beispiel-Plugin aktiviert.", 5000)
    )
    ide.addAddonAction(action)


def unregister(ide):
    pass
