# ADD - Astronomisches Dämmerungs Diagramm

Dieses Projekt erstellt ein Diagramm für Astrophotographen, das die verschiedenen Phasen der astronomischen Dämmerung visualisiert.<br>
Dabei wird die jeweilige Helligkeit des Mondes berücksichtigt. Es basiert auf Python und verwendet Bibliotheken wie `skyfield, matplotlib, usw.` zur Berechnung und Darstellung.
<br>
<br>
<br>
Hauptfenster:
<img src="DOC/Main Window.png" alt="Hauptfenster" width="300px" style="display: block; margin: 0 auto">
Diagramm:
<br>
<img src="DOC/Dämmerungsdiagramm April 2025 (Wien Lat 48.21 Lon 16.36).png" alt="Diagramm"  style="display: block; margin: 0 auto">
<br>
<br>

Das Programm wurde mit Hilfe von KI erstellt, und ist mein erster Versuch, etwas nützliches zu erstellen.<br>
Der Grund ist, dass ich leider nur ein sehr begrenztes Python-Wissen habe, und ohne Hilfe nicht in der Lage gewesen wäre, eine so komplexe Aufgabe zu verwirklichen.<br>
Ich habe Ende 2024 begonnen ein Script zu schreiben, und habe dann versucht, es mit Hilfe von `Copilot` fertig zustellen.<br> 
Leider scheiterte ich damals daran. Mitte April 2025 startete ich einen neuen Versuch, diesmal liess ich das bereits vorhandene, nicht funktionierende, Script von `Gemini` analysieren und korrigieren.<br>
Der Unterschied war enorm! In diesem halben Jahr machten die KIs einen enormen Entwicklungssprung, das Script funktionierte in groben Zügen.<br>
Das Finetuning erfolgte dann wieder inline in VScode mit `Copilot`.

## Voraussetzungen

- Python 3.x
- Abhängigkeiten aus der Datei `requirements.txt`

## Installation

1. Klone das Repository:
    ```bash
    git clone <repository-url>
    ```
2. Installiere die Abhängigkeiten:
    ```bash
    pip install -r requirements.txt
    ```

## Nutzung

Führe das Skript aus, um das Diagramm zu generieren:
```bash
python main.py
```

Das Diagramm wird als Bilddatei gespeichert oder direkt angezeigt.

## Lizenz

Dieses Projekt steht unter der [MIT-Lizenz](LICENSE).