# pico-mp-bake-mn

Bakencontroller für OE5XBM

Funktionen

* 7 Ausgänge
* Steuerung über DTMF
* Jeder Ausgang kann Bake oder Schalter sein
* Alle Baken haben den gleichen Zeitablauf und den gleichen Bakentext
* Timing: Träger ein, Träger für die Teit PRE aus, Morsen, Träger für die Zeit POST aus, dann wieder Träger ein 
* Configuration über die serielle Schnittstelle (nur putty etc nitwendig, kein Clientprogramm mehr)
* Die Einstellungen werden in einer Datei config.json gespeichert
* Watchdog mit 8 Sekunden

Befehle
* Die Stroktur der DTMF Befehle laut: * cmd #
* cmd sind die Ziffern 0-9
' Ein Port kann EIn oder ausgeschalten 
