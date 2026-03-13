# DTMF Tone Generator

Python-Script zum Generieren und Abspielen von DTMF-Tönen (Dual-Tone Multi-Frequency).

## Installation

Installiere die benötigten Python-Pakete:

```bash
pip install numpy sounddevice
```

## Verwendung

### Command-Line-Optionen

```bash
# Interaktiver Modus
python3 dtmf_player.py

# Mit spezifischem Audio-Device
python3 dtmf_player.py -d 5

# Test-Datei ausführen
python3 dtmf_player.py -f dtmf_test

# Test-Datei mit spezifischem Device
python3 dtmf_player.py -d 5 -f dtmf_test

# Audio-Devices auflisten
python3 dtmf_player.py --list-devices

# Hilfe anzeigen
python3 dtmf_player.py -h
```

**Parameter:**
- `-d DEVICE_ID, --device DEVICE_ID` - Audio-Device ID verwenden
- `-f FILE, --file FILE` - Test-Datei mit DTMF-Sequenzen ausführen
- `--list-devices` - Zeigt verfügbare Audio-Devices

### Test-Datei Format

Eine Test-Datei enthält DTMF-Sequenzen mit Verzögerungen:

```
delay=1
*1111#
delay=2
*2220#
delay=0.5
*01#
```

Format:
- `delay=<sekunden>` - Wartezeit in Sekunden (kann Dezimalzahl sein)
- Nächste Zeile: DTMF-Sequenz die ausgegeben wird
- Leere Zeilen und Zeilen mit `#` am Anfang werden ignoriert

### Interaktiver Modus

Starte das Script:

```bash
python3 dtmf_player.py
```

Dann kannst du DTMF-Sequenzen eingeben:

```
DTMF> *1234#
DTMF> 01123456789
DTMF> *21#
DTMF> devices      # Zeigt verfügbare Audio-Devices
DTMF> device 5     # Wechselt zum Audio-Device 5
DTMF> quit         # Beendet das Programm
```

### Als Modul verwenden

```python
from dtmf_player import DTMFPlayer

# Player erstellen
player = DTMFPlayer()

# Einzelne Sequenz abspielen
player.play_sequence("*1234#")

# Einzelnes Zeichen abspielen
player.play_char("5")

# Eigene Einstellungen
player = DTMFPlayer(
    sample_rate=44100,      # Abtastrate
    tone_duration=0.2,      # Ton-Dauer in Sekunden
    pause_duration=0.05     # Pause zwischen Tönen
)
```

## Unterstützte Zeichen

- Ziffern: `0-9`
- Sonderzeichen: `*` und `#`
- Erweiterte Zeichen: `A`, `B`, `C`, `D`
- Leerzeichen: Längere Pause

## DTMF-Frequenzen

```
       1209 Hz  1336 Hz  1477 Hz  1633 Hz
697 Hz    1        2        3        A
770 Hz    4        5        6        B
852 Hz    7        8        9        C
941 Hz    *        0        #        D
```

## Beispiele

```bash
# Interaktiver Modus
python3 dtmf_player.py
DTMF> 0664123456

# DTMF-Befehl senden
python3 dtmf_player.py
DTMF> *10#

# Mit Pausen
python3 dtmf_player.py
DTMF> *1 234#

# Audio-Devices anzeigen
python3 dtmf_player.py
DTMF> devices

# Zu anderem Device wechseln
python3 dtmf_player.py
DTMF> device 3

# Script mit spezifischem Device starten
python3 dtmf_player.py -d 5

# Test-Datei ausführen
python3 dtmf_player.py -f dtmf_test

# Test-Datei mit spezifischem Device
python3 dtmf_player.py -d 5 -f dtmf_test

# Alle verfügbaren Audio-Devices auflisten
python3 dtmf_player.py --list-devices
```

### Beispiel Test-Datei

Erstelle eine Datei `dtmf_test` mit folgendem Inhalt:

```
# Test-Sequenz für Beacon-Controller
# Format: delay=<sekunden> gefolgt von DTMF-Sequenz

# LED einschalten
delay=1
*01#

# Warten und LED ausschalten
delay=3
*00#

# 10 GHz Band einschalten
delay=1
*11#

# Kurz warten
delay=2
*10#

# Mehrere Ports testen
delay=1
*21#
delay=1
*31#
delay=2
*20#
delay=1
*30#
```

Ausführen mit:
```bash
python3 dtmf_player.py -f dtmf_test
```

## Troubleshooting

### Kein Ton hörbar

1. Prüfe verfügbare Audio-Devices:
   ```
   DTMF> devices
   ```

2. Wechsle zu einem anderen Audio-Device:
   ```
   DTMF> device 5
   ```
   (wobei 5 die Device-ID aus der Liste ist)

3. Oder starte das Script direkt mit einer Device-ID:
   ```bash
   python3 dtmf_player.py 5
   ```

4. Standard-Audio-Device im Code ändern:
   ```python
   import sounddevice as sd
   sd.default.device = 5  # Device-ID
   ```

5. Lautstärke prüfen

### PyAudio Alternative

Falls sounddevice nicht funktioniert, kann alternativ PyAudio verwendet werden:

```bash
pip install pyaudio
```

Dann im Code `import sounddevice as sd` durch entsprechenden PyAudio-Code ersetzen.

### Über sox

AUDIODEV=plughw:5,0 play -r 48000 -b 16 -c 1 -n synth 0.2 sin 697 sin 1209 vol 0.5