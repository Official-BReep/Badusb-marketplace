# Plugins

Lege hier fertige, installierbare Plugins ab. Der Marketplace durchsucht Unterordner rekursiv; der genaue Ordnername ist nicht entscheidend.

- Eine Plugin-Datei muss `def register(ide):` enthalten.
- `ADDON_NAME` ist optional und steuert den angezeigten Namen.
- Lege nach Möglichkeit eine `README.md` neben die Plugin-Datei, damit Nutzer die Beschreibung vor der Installation ansehen können.
- Da die IDE beim Installieren derzeit nur die ausgewählte Python-Datei kopiert, müssen Plugins eigenständig sein.

Prüfe jedes Plugin vor der Veröffentlichung und beschreibe Zweck, Nutzung, Berechtigungen und bekannte Einschränkungen in der README.
