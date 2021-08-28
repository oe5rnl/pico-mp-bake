# pico-mp-bake-mn

Bakencontroller 

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
* Die Struktur der DTMF Befehle laut: * cmd #
* cmd sind die Ziffern 0-9 A-D (Achtung: D wird auch durch eine zweite Harware ausgewertet!)

* Ein Port kann Ein oder ausgeschalten werden


![consoles://github.com/oe5rnl/pico-mp-bake-mn/edit/master//1.png=true)
