#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DTMF Tone Generator
Generiert DTMF-Töne und gibt sie auf einem Audio-Device aus

pip install numpy
pip install sounddevice
"""

import numpy as np
import sounddevice as sd
import time
import argparse
import sys
import os


class DTMFPlayer:
    def __init__(self, sample_rate=44100, tone_duration=0.2, pause_duration=0.05, device=None):
        """
        DTMF Tone Player
        
        Args:
            sample_rate: Abtastrate in Hz (Standard: 44100)
            tone_duration: Dauer eines Tons in Sekunden (Standard: 0.2)
            pause_duration: Pause zwischen Tönen in Sekunden (Standard: 0.05)
            device: Audio Device ID (None = Standard-Device)
        """
        self.sample_rate = sample_rate
        self.tone_duration = tone_duration
        self.pause_duration = pause_duration
        self.device = device
        
        # Setze Standard-Device wenn angegeben
        if device is not None:
            sd.default.device = device
        
        # DTMF Frequenz-Matrix
        # Format: Zeichen -> (niedrige Frequenz, hohe Frequenz)
        self.dtmf_freqs = {
            '1': (697, 1209),
            '2': (697, 1336),
            '3': (697, 1477),
            'A': (697, 1633),
            
            '4': (770, 1209),
            '5': (770, 1336),
            '6': (770, 1477),
            'B': (770, 1633),
            
            '7': (852, 1209),
            '8': (852, 1336),
            '9': (852, 1477),
            'C': (852, 1633),
            
            '*': (941, 1209),
            '0': (941, 1336),
            '#': (941, 1477),
            'D': (941, 1633),
        }
    
    def generate_tone(self, low_freq, high_freq, duration=None):
        """
        Generiert einen DTMF-Ton mit zwei Frequenzen
        
        Args:
            low_freq: Niedrige Frequenz in Hz
            high_freq: Hohe Frequenz in Hz
            duration: Dauer in Sekunden (optional)
            
        Returns:
            numpy array mit Audio-Sample
        """
        if duration is None:
            duration = self.tone_duration
            
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        
        # Generiere beide Frequenzen
        tone_low = np.sin(2 * np.pi * low_freq * t)
        tone_high = np.sin(2 * np.pi * high_freq * t)
        
        # Addiere und normalisiere
        tone = (tone_low + tone_high) / 2
        
        # Füge Fade-In/Fade-Out hinzu um Klicks zu vermeiden
        fade_samples = int(0.005 * self.sample_rate)  # 5ms fade
        fade_in = np.linspace(0, 1, fade_samples)
        fade_out = np.linspace(1, 0, fade_samples)
        
        tone[:fade_samples] *= fade_in
        tone[-fade_samples:] *= fade_out
        
        return tone
    
    def generate_silence(self, duration=None):
        """
        Generiert Stille
        
        Args:
            duration: Dauer in Sekunden (optional)
            
        Returns:
            numpy array mit Nullen
        """
        if duration is None:
            duration = self.pause_duration
            
        return np.zeros(int(self.sample_rate * duration))
    
    def play_char(self, char):
        """
        Spielt einen einzelnen DTMF-Ton
        
        Args:
            char: Zeichen ('0'-'9', '*', '#', 'A'-'D')
        """
        char = char.upper()
        
        if char not in self.dtmf_freqs:
            print(f"Warnung: '{char}' ist kein gültiges DTMF-Zeichen")
            return
        
        low_freq, high_freq = self.dtmf_freqs[char]
        tone = self.generate_tone(low_freq, high_freq)
        
        # Spiele den Ton
        sd.play(tone, self.sample_rate)
        sd.wait()
        
        # Pause nach dem Ton
        silence = self.generate_silence()
        sd.play(silence, self.sample_rate)
        sd.wait()
    
    def play_sequence(self, sequence):
        """
        Spielt eine Sequenz von DTMF-Tönen
        
        Args:
            sequence: String mit DTMF-Zeichen (z.B. "*1234#")
        """
        print(f"Spiele DTMF-Sequenz: {sequence}")
        
        for char in sequence:
            if char == ' ':
                # Längere Pause bei Leerzeichen
                silence = self.generate_silence(duration=0.5)
                sd.play(silence, self.sample_rate)
                sd.wait()
            else:
                self.play_char(char)
        
        print("Fertig!")
    
    def list_audio_devices(self):
        """Listet alle verfügbaren Audio-Devices auf"""
        print("\nVerfügbare Audio-Devices:")
        print("-" * 60)
        devices = sd.query_devices()
        for i, dev in enumerate(devices):
            if isinstance(dev, dict):
                name = dev.get('name', 'Unknown')
                channels = dev.get('max_output_channels', 0)
                if channels > 0:
                    marker = " <-- aktuell" if i == sd.default.device[1] else ""
                    print(f"  [{i:2d}] {name} ({channels} Kanäle){marker}")
        print("-" * 60)
        print("Verwendung: device <id>")
    
    def play_test_file(self, filename):
        """
        Liest und führt eine Test-Datei aus
        
        Format der Datei:
            delay=<sekunden>
            <dtmf_sequenz>
            delay=<sekunden>
            <dtmf_sequenz>
            ...
        
        Args:
            filename: Pfad zur Test-Datei
        """
        if not os.path.exists(filename):
            print(f"Fehler: Datei '{filename}' nicht gefunden")
            return False
        
        print(f"\n{'='*60}")
        print(f"Führe Test-Datei aus: {filename}")
        print(f"{'='*60}\n")
        
        try:
            with open(filename, 'r') as f:
                lines = f.readlines()
            
            i = 0
            step = 1
            while i < len(lines):
                line = lines[i].strip()
                
                if not line or line.startswith('#'):
                    # Überspringe leere Zeilen und Kommentare
                    i += 1
                    continue
                
                if line.startswith('delay='):
                    # Verzögerung extrahieren
                    try:
                        delay = float(line.split('=')[1])
                        print(f"[Schritt {step}] Warte {delay} Sekunden...")
                        time.sleep(delay)
                        
                        # Nächste Zeile sollte die DTMF-Sequenz sein
                        i += 1
                        if i < len(lines):
                            sequence = lines[i].strip()
                            if sequence and not sequence.startswith('#'):
                                print(f"[Schritt {step}] ", end="")
                                self.play_sequence(sequence)
                                step += 1
                    except (ValueError, IndexError) as e:
                        print(f"Fehler beim Parsen von Zeile {i+1}: {line}")
                        print(f"  {e}")
                
                i += 1
            
            print(f"\n{'='*60}")
            print(f"Test-Datei abgeschlossen!")
            print(f"{'='*60}\n")
            return True
            
        except Exception as e:
            print(f"Fehler beim Lesen der Datei: {e}")
            return False


def main():
    """Hauptfunktion mit interaktiver Konsole"""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='DTMF Tone Generator - Erzeugt und spielt DTMF-Töne',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  %(prog)s                    # Interaktiver Modus
  %(prog)s -d 5               # Interaktiv mit Audio-Device 5
  %(prog)s -f dtmf_test       # Führe Test-Datei aus
  %(prog)s -d 5 -f dtmf_test  # Device 5 mit Test-Datei

Test-Datei Format:
  delay=<sekunden>
  <dtmf_sequenz>
  delay=<sekunden>
  <dtmf_sequenz>
  ...
        """
    )
    
    parser.add_argument('-d', '--device', 
                        type=int, 
                        metavar='DEVICE_ID',
                        help='Audio-Device ID (siehe --list-devices)')
    
    parser.add_argument('-f', '--file', 
                        type=str, 
                        metavar='FILE',
                        help='Test-Datei mit DTMF-Sequenzen ausführen')
    
    parser.add_argument('--list-devices', 
                        action='store_true',
                        help='Zeigt verfügbare Audio-Devices und beendet')
    
    args = parser.parse_args()
    
    # Liste Devices und beende
    if args.list_devices:
        temp_player = DTMFPlayer()
        temp_player.list_audio_devices()
        sys.exit(0)
    
    # Erstelle Player mit optionalem Device
    device = args.device
    if device is not None:
        print(f"Verwende Audio-Device: {device}")
    
    player = DTMFPlayer(device=device)
    
    # Wenn Test-Datei angegeben, führe sie aus und beende
    if args.file:
        success = player.play_test_file(args.file)
        sys.exit(0 if success else 1)
    
    # Ansonsten: Interaktiver Modus
    print("=" * 60)
    print("DTMF Tone Generator")
    print("=" * 60)
    print("\nUnterstützte Zeichen: 0-9, *, #, A-D")
    print("Beispiel: *1234#")
    print("\nBefehle:")
    print("  <Sequenz>    - Spielt die DTMF-Sequenz")
    print("  devices      - Zeigt verfügbare Audio-Devices")
    print("  device <id>  - Wechselt zum Audio-Device <id>")
    print("  quit         - Beendet das Programm")
    print("=" * 60)
    
    while True:
        try:
            command = input("\nDTMF> ").strip()
            
            if not command:
                continue
            
            if command.lower() in ['quit', 'exit', 'q']:
                print("Auf Wiedersehen!")
                break
            
            elif command.lower() == 'devices':
                player.list_audio_devices()
            
            elif command.lower().startswith('device '):
                try:
                    new_device = int(command.split()[1])
                    player = DTMFPlayer(device=new_device)
                    print(f"Wechsel zu Audio-Device: {new_device}")
                except (ValueError, IndexError):
                    print("Fehler: Verwendung: device <id>")
                except Exception as e:
                    print(f"Fehler beim Wechseln des Devices: {e}")
            
            else:
                player.play_sequence(command)
        
        except KeyboardInterrupt:
            print("\n\nProgramm wurde unterbrochen.")
            break
        except Exception as e:
            print(f"Fehler: {e}")


if __name__ == "__main__":
    main()
