"""Starter template for a BadUSB IDE add-on."""

ADDON_NAME = "Mein Plugin (Vorlage)"
ADDON_VERSION = "1.0.0"
ADDON_DESCRIPTION = "Grundgerüst für ein eigenes BadUSB-IDE-Plugin"


def register(ide):
    """Wird beim Aktivieren des Plugins aufgerufen."""
    from PyQt6.QtGui import QAction

    action = QAction("Mein Plugin: Hallo", ide)
    action.triggered.connect(
        lambda: ide.statusBar().showMessage("Mein Plugin funktioniert!", 5000)
    )
    ide.addAddonAction(action)


def unregister(ide):
    """Optionale Aufräumarbeiten beim Deaktivieren."""
    pass


def configure(ide):
    """Optionaler Einstellungsdialog."""
    from PyQt6.QtWidgets import QMessageBox

    QMessageBox.information(
        ide,
        ADDON_NAME,
        "Das ist eine Vorlage. Passe ADDON_NAME und register(ide) an.",
    )
