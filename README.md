# IX Atlas für VRChat

GitHub Pages veröffentlicht die freigegebenen Daten aus dem WordPress-Atlas von Immersive X. Die Buchliste enthält die öffentlichen Nutzernamen und die Koordinaten der Cover in den Sammelbildern. GitHub Actions überträgt die Daten als ein Pages-Paket.

- Buchliste unter `manifest.json`
- Sammelbilder unter `pages/{pageIndex}.png`

Der Workflow **Publish IX Atlas** prüft WordPress viermal pro Stunde. Über **Actions → Publish IX Atlas → Run workflow** lässt sich die Übertragung manuell anstoßen. Ein zurückgezogenes Buch verschwindet mit der nächsten erfolgreichen Veröffentlichung des aktualisierten WordPress-Exports. Zwischengespeicherte Daten können kurz länger sichtbar bleiben.
