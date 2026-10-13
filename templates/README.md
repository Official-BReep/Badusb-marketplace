# Plugin-Vorlagen

Dieser Ordner enthält Startvorlagen, aus denen Entwickler eigene Plugins für die BadUSB IDE erstellen können.

## Verwendung

1. Öffne `plugin_template.py` und kopiere die Datei in einen eigenen Arbeitsordner.
2. Ändere `ADDON_NAME` und ergänze die gewünschte Funktionalität in `register(ide)`.
3. Teste das Plugin in einer sicheren Umgebung.
4. Füge eine eigene `README.md` hinzu und veröffentliche das fertige Plugin anschließend beispielsweise im Ordner `plugins/`.

## Schnittstelle

- `register(ide)`: wird beim Aktivieren aufgerufen.
- `unregister(ide)`: optional, für Aufräumarbeiten beim Deaktivieren.
- `configure(ide)` oder `open_settings(ide)`: optional, für einen Einstellungsdialog.

**Hinweis:** Der aktuelle Katalog erkennt auch Vorlagendateien, wenn sie `register(ide)` enthalten. Er unterscheidet Vorlagen und fertige Plugins noch nicht in getrennten Kategorien. Beim Installieren wird nur die gewählte `.py`-Datei kopiert.
