
ADDON_NAME = "Mein Plugin (Vorlage)"
ADDON_VERSION = "1.0.0"
ADDON_DESCRIPTION = "Vorlage für ein eigenes BadUSB-IDE-Plugin"


def register(ide):
    """Wird beim Aktivieren des Plugins aufgerufen."""
    ide.statusBar().showMessage(
        f"{ADDON_NAME} wurde aktiviert."
    )


def unregister(ide):
    """Optional: Ressourcen beim Deaktivieren freigeben."""
    pass
