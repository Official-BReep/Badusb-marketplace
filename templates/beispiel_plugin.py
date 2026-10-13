"""Minimales, gültiges Beispiel-Plugin für die BadUSB IDE.

Installation:
1. Diese Datei in den Plugin-Ordner der IDE kopieren oder über die
   Plugin-Verwaltung installieren.
2. Im Tab „Installierte Plugins“ auswählen und aktivieren.
3. Zum Testen im Menü „Erweiterungen“ den Eintrag „Vorlage: Hallo“ öffnen.

Plugins laufen mit den Rechten des IDE-Prozesses. Prüfe fremden Code vor dem
Aktivieren.
"""

from PyQt6.QtWidgets import QMessageBox, QInputDialog

ADDON_NAME = "BadUSB IDE – Plugin-Vorlage"
ADDON_DESCRIPTION = (
    "Sicheres Beispiel-Plugin mit Menüaktion und einfacher Konfiguration. "
    "Dient als Ausgangspunkt für eigene Erweiterungen."
)
ADDON_VERSION = "1.0.0"
PLUGIN_NAME = ADDON_NAME
PLUGIN_DESCRIPTION = ADDON_DESCRIPTION
PLUGIN_VERSION = ADDON_VERSION
VERSION = ADDON_VERSION

_MENU_LABEL = "Vorlage: Hallo"


def register(ide):
    """Wird von der IDE beim Aktivieren aufgerufen."""
    ide.register_menu_action(
        label=_MENU_LABEL,
        callback=lambda: _show_greeting(ide),
        menu="Erweiterungen",
    )


def _show_greeting(ide):
    """Zeigt eine harmlose Beispielaktion."""
    QMessageBox.information(
        ide,
        ADDON_NAME,
        "Hallo! Das Beispiel-Plugin wurde erfolgreich geladen.",
    )


def configure(ide):
    """Optionale Einstellungen, aufrufbar über die Plugin-Verwaltung."""
    value, accepted = QInputDialog.getText(
        ide,
        f"Einstellungen – {ADDON_NAME}",
        "Beispieltext (wird nicht dauerhaft gespeichert):",
        text="Hallo aus meinem Plugin!",
    )
    if accepted:
        QMessageBox.information(ide, "Plugin-Einstellung", value or "(leer)")


def unregister(ide):
    """Optionaler Aufräum-Hook.

    Die IDE entfernt die von register_menu_action registrierte Aktion beim
    Deaktivieren automatisch. Hier können bei eigenen Plugins zusätzliche
    Ressourcen freigegeben werden.
    """
    # In dieser Vorlage sind keine zusätzlichen Ressourcen zu bereinigen.
    return None
