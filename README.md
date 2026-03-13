
# Bakencontroller OE5RNL / OE5NVL

History:

* 2021-09-05 Version: 1.0b 

        initial version

* 2026-03-13 Version: 1.0c 

        Umstellung auf Micropython RPI_PICO-20251209-v1.27.0.uf2
        Backspace mit  0x7f und 0x08 für putty und minicom
        dtmf_player.py zum Testen des DTMF Dekoders hinzu

# Funktionen

* 7 Ausgänge
* Steuerung über DTMF oder serielle Schnittstelle
* Jeder Ausgang (Port) kann Bake oder Schalter sein
* Alle Baken haben den gleichen Zeitablauf und den gleichen Bakentext
* Timing: Träger ein, Träger für die Zeit PRE aus, Morsen, Träger für die Zeit POST aus, dann wieder Träger ein 
* Configuration über die serielle Schnittstelle (nur putty oä. mit 9600 81n notwendig, kein Clientprogramm mehr erforderlich)
* Die Einstellungen werden in der Datei config.json am rpi pico gespeichert
* Watchdog mit 60 Sekunden

# DTMF Befehle
* Die Struktur der DTMF Befehle laut: * cmd #
* Die Werte für einen Befehl sind unabhängig von der Portnummer 
* cmd sind die Ziffern 0-9 A-D (Achtung: D wird auch durch eine zweite Harware ausgewertet!)

* Ein Port kann Ein oder ausgeschalten werden 
* Die Ausgabe des Morsetextes kann für n Sekunden unerbunden werden.


# Konfiguration des Controllers (Schnittstelle)

Die Konfiguration erfolgt über die serielle Schnittstelle UART(0) am Raspberry Pi Pico. 

Der UART (Achtung 3,3V !!!) verwendet die Pins:

```
GPIO 0 (Pin 1) - TX
GPIO 1 (Pin 2) - RX
```

Schnittstellenparameter: 

```
Baudrate:  9600
Datenbits: 8 
Stopbits:  1 
Parity:    none 
Protokoll: none
```

Die serielle Schnittstelle am USB Stecker wird nur zum hochladen des Programmes verwendet.

# Bedienung des Controllers (Schnittstelle)

Eingabe: Enter


![console](https://github.com/oe5rnl/pico-mp-bake-mn/blob/master/picture/1.png?raw=true)

Edit Allgemeine Parameter (Eingabe: a)

![console](https://github.com/oe5rnl/pico-mp-bake-mn/blob/master/picture/edit_allgemein.png?raw=true)

Edit Port (Eingabe: Port Nummer)

![console](https://github.com/oe5rnl/pico-mp-bake-mn/blob/master/picture/edit_port.png?raw=true)


Weitere Befehle:
```
c Für Konfig anzeigen
s für Save (normalerweise nicht notwendig. 
  Änderungen werden automatisch gespeichert)
r für Reset (normalerweise nicht notwendig)
```

GPIO für Ports:

Die initiale Festlegung der gpios für die Ports erfolgt in der Struktur self.c

Beispiel:

{'id':'0','Name':'LED',   'Mode':'B','gpio':'25','On': '01','Off':'00','Port On':'1', 'CW Off':'03','CW On':'04'},


Die aktuellen Werte werden am controller in der Datei config.json gespeichert.

