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


def main():
    """Hauptfunktion mit interaktiver Konsole"""
    import sys
    
    # Parse command-line arguments
    device = None
    if len(sys.argv) > 1:
        try:
            device = int(sys.argv[1])
            print(f"Verwende Audio-Device: {device}")
        except ValueError:
            print(f"Fehler: '{sys.argv[1]}' ist keine gültige Device-ID")
            print("Verwendung: python3 dtmf_player.py [device_id]")
            sys.exit(1)
    
    player = DTMFPlayer(device=device)
    
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
