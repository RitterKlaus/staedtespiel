# Städtespiel

Ein rundenbasiertes Fantasy-Strategiespiel mit zufällig erzeugter Karte, Städten und Einheiten.

## Voraussetzungen

- Python 3.10 oder neuer

## Einrichtung

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Spiel starten

```bash
.venv/bin/python game.py
```

## Spielprinzip

- Die Karte wird beim ersten Start zufällig erzeugt und beim Beenden gespeichert.
- Der Spieler startet mit einer zufällig zugewiesenen Stadt und 10 Gold.
- Städte produzieren pro Spielzug Gold (nur eigene Städte).
- In eigenen Städten können Einheiten rekrutiert werden (Späher, Kämpfer, Ritter).
- Ein Klick auf ein Feld zeigt Geländetyp, Stadtinfo und vorhandene Einheiten in der Sidebar.
- **Nächster Spielzug** — Gold einsammeln und rekrutierte Einheiten erhalten.
- **Spiel beenden** — Spielstand wird gespeichert.
