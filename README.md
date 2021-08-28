# pico-mp-bake-mn

Bakencontroller 

Funktionen

* 7 Ausgänge
* Steuerung über DTMF
* Jeder Ausgang (Port) kann Bake oder Schalter sein
* Alle Baken haben den gleichen Zeitablauf und den gleichen Bakentext
* Timing: Träger ein, Träger für die Zeit PRE aus, Morsen, Träger für die Zeit POST aus, dann wieder Träger ein 
* Configuration über die serielle Schnittstelle (nur putty oä. mit 9600 81n notwendig, kein Clientprogramm mehr erforderlich)
* Die Einstellungen werden in der Datei config.json am rpi pico gespeichert
* Watchdog mit 8 Sekunden

DTMF Befehle
* Die Struktur der DTMF Befehle laut: * cmd #
* Die Werte für einen Befehl sind unabhängig von der Portnummer 
* cmd sind die Ziffern 0-9 A-D (Achtung: D wird auch durch eine zweite Harware ausgewertet!)

* Ein Port kann Ein oder ausgeschalten werden 
* Die Ausgabe des Morsetextes kann für n Sekunden unerbunden werden.

Konfiguration über die serielle Schnittstelle

![consoles](https://github.com/oe5rnl/pico-mp-bake-mn/edit/master/1.png=true)


Realisiert mit Raspberry Pi Pico und Micropython 1.16
