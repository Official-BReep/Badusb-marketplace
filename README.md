# BadUSB IDE – Plugin Marketplace

Dieses Repository ist ein Sammelpunkt für Erweiterungen der BadUSB IDE. Der Marketplace der IDE durchsucht geklonte Git-Repositories rekursiv nach Python-Dateien, die eine passende `register(ide)`-Funktion bereitstellen.

## Repository-Struktur

```text
BadUSB-Marketplace/
├── README.md
├── plugins/
│   ├── README.md
│   └── beispiel_plugin.py
└── templates/
    ├── README.md
    └── plugin_template.py
```

## Ein Plugin veröffentlichen

1. Lege eine eigenständige `.py`-Datei im Repository ab, zum Beispiel unter `plugins/`.
2. Definiere `register(ide)`. Die IDE erkennt diese Funktion als Einstiegspunkt.
3. Setze optional `ADDON_NAME`, damit der Name im Katalog lesbar ist.
4. Lege eine `README.md` direkt neben die Plugin-Datei oder in einen übergeordneten Ordner. Die IDE kann diese vor der Installation anzeigen.
5. Committe und pushe die Änderungen. Nutzer können danach im Plugin-Manager den Katalog aktualisieren, um neue Plugins abzurufen.

## Plugin-Schnittstelle

```python
ADDON_NAME = "Mein Plugin"
ADDON_VERSION = "1.0.0"
ADDON_DESCRIPTION = "Kurze Beschreibung"

def register(ide):
    # Menüs, Aktionen oder Panels registrieren
    pass

def unregister(ide):
    # Optionale Aufräumarbeiten beim Deaktivieren
    pass
```

`configure(ide)` oder `open_settings(ide)` sind optionale Einstellungsfunktionen. Die aktuell verwendete Marketplace-Installation kopiert nur die ausgewählte `.py`-Datei. Plugins sollten daher eigenständig sein und keine zusätzlichen Dateien voraussetzen, sofern die IDE nicht entsprechend erweitert wurde.

## Aktualisieren und Abrufen

Die IDE speichert hinzugefügte Repository-URLs lokal in `~/.badusb_ide_addons/marketplace_repositories.json` und die geklonten Repositories unter `~/.badusb_ide_addons/marketplace/`. Über **Katalog aktualisieren** werden gespeicherte Repositories per `git pull --ff-only` aktualisiert und anschließend erneut nach Plugin-Dateien durchsucht. Alternativ aktualisiert **Alle Marktplatz-Repositories aktualisieren** die Quellen gesammelt.

## Sicherheit

Python-Plugins werden mit den Rechten des angemeldeten Benutzers ausgeführt. Sie können unter anderem Dateien lesen oder verändern und Netzwerkzugriffe durchführen. Prüfe den Quellcode und die README, bevor du ein Plugin installierst oder aktivierst. Installiere nur Quellen, denen du vertraust.

## Lizenz

Füge eine `LICENSE`-Datei hinzu, wenn du festlegen möchtest, unter welchen Bedingungen andere das Repository verwenden, verändern und weiterverbreiten dürfen. Verwende nur eine Lizenz, deren Bedingungen du akzeptierst.
