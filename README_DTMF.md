# DTMF Tone Generator

Python-Script zum Generieren und Abspielen von DTMF-Tönen (Dual-Tone Multi-Frequency).

## Installation

Installiere die benötigten Python-Pakete:

```bash
pip install numpy sounddevice
```

## Verwendung

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
# Telefonnummer wählen
python3 dtmf_player.py
DTMF> 0664123456

# DTMF-Befehl senden
DTMF> *10#

# Mit Pausen
DTMF> *1 234#

# Audio-Devices anzeigen
DTMF> devices

# Zu anderem Device wechseln
DTMF> device 3

# Script mit spezifischem Device starten
python3 dtmf_player.py 5
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