# pico-mp-bake-mn  

Bakencontroller OE5RNL / OE5NVL

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

Konfiguration über die serielle Schnittstelle (9600 8 1 none none) 
Eingabe: Enter


![console](https://github.com/oe5rnl/pico-mp-bake-mn/blob/master/1.png?raw=true)

Edit Allgemeine Parameter (Eingabe: a)

![console](https://github.com/oe5rnl/pico-mp-bake-mn/blob/master/edit_allgemein.png?raw=true)

Edit Port (Eingabe: Port Nummer)

![console](https://github.com/oe5rnl/pico-mp-bake-mn/blob/master/edit_port.png?raw=true)


Weitere Befehle:

c Für Konfig anzeigen

s für Save (normalerweise nicht notwendig. Es Änderungen werden automatisch gespeichert)

r für Reset (normalerweise nicht notwendig)


GPIO für Ports:

Die Festlegung der gpios für die Ports erfolgt in der Struktur config.c

Beispiel:

{'id':'0','Name':'LED',   'Mode':'B','gpio':'25','On': '01','Off':'00','Port On':'1', 'CW Off':'03','CW On':'04'},

Realisiert mit Raspberry Pi Pico und Micropython 1.16
