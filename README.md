# IX Atlas für VRChat und Altspace

GitHub Pages veröffentlicht die freigegebenen Daten aus dem WordPress-Atlas von Immersive X. Die Buchliste enthält die öffentlichen Nutzernamen, Einbandfarben, Bildadressen und Cover-Koordinaten. GitHub Actions überträgt die Daten als zusammenhängendes Pages-Paket.

- Buchliste unter `manifest.json`
- VRChat-Sammelbilder mit acht Covern unter `pages/{pageIndex}.png`
- Altspace-Einzelcover mit 512 × 768 Pixeln unter `covers/{revision}/{index}.jpg`

Der Workflow **Publish IX Atlas** ist für eine Prüfung alle fünf Minuten eingerichtet. Unveränderte Kataloge werden ohne erneuten Bilddownload oder Pages-Upload übersprungen. Die Laufübersicht zeigt Zeitpunkt und Ergebnis jeder tatsächlichen Prüfung. GitHub-Zeitpläne können verspätet starten oder ausfallen; der Takt ist keine garantierte Aktualisierungsfrist. Siehe [GitHubs Hinweise zu Zeitplänen](https://docs.github.com/en/actions/how-tos/troubleshoot-workflows#scheduled-workflows-running-at-unexpected-times).

Über **Actions → Publish IX Atlas → Run workflow** lässt sich eine Übertragung sofort anstoßen. Ein zurückgezogenes Buch verschwindet mit der nächsten erfolgreichen Veröffentlichung des aktualisierten WordPress-Exports. Zwischengespeicherte Daten können kurz länger sichtbar bleiben.

Neue Weltinstanzen laden den veröffentlichten Katalog beim Start. In einer laufenden Instanz liest **REFRESH** den aktuellen GitHub-Stand ein; der Knopf startet keinen GitHub-Export. Neue oder geänderte Bücher benötigen keinen neuen Welt-Build.
