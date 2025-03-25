# BuchDashboard

Dashboard für eine Übersicht der Preise von gebrauchten Büchern bei verschiedenen Onlinehändlern.

![image](https://github.com/user-attachments/assets/c3eb41f2-8215-4520-88da-dec13d9a14f8)

Über den Add Book-Button können Bücher hinzugefügt werden. Dazu muss ein Titel sowie eine ISBN eingetragen werden. Mit einem Klick auf Refresh oder auf Refresh All (für alle Bücher) werden die Preise von den Onlinehändlern eingeholt und angezeigt. 

### Händler konfigurieren

Die Händler sind in der Config-Datei konfigurierbar, die sich in `$XDG_CONFIG_HOME/buchdashboard/config.json` befindet. (`$XDG_CONFIG_HOME` ist normalerweise `/home/username/.config`). 

Exemplarisch hat dabei der Händler AbeBooks den Eintrag 

```"abebooks": "https://www.abebooks.de/servlet/SearchResults?ch_sort=t&cm_sp=sort-_-SRP-_-Results&ds=20&kn={isbn}&rollup=on&sortby=2"```, 

wobei `{isbn}` durch das Programm dann offensichtlich durch die ISBN des jeweiligen Buches ersetzt wird. 

Anmerkung: Zusätzlich muss momentan in `app/main.py` leider noch angepasst werden, aus welchem HTML-Tag der Preis extrahiert werden soll, was sich perspektivisch noch ändern wird.

Die Bücher werden in einer einfachen JSON-Datei in `$XDG_CONFIG_HOME/buchdashboard/books.json` gespeichert.

### Bauen und Starten

Empfohlen ist die Benutzung über den mitgelieferten Nix-Flake. Dazu den [Nix](https://nixos.org/download/)-Paketmanager installieren. BuchDashboard kann dann mit 

```
git clone https://github.com/janmartchouk/buchdashboard.git
cd buchdashboard
nix run
```

gestartet werden. Alternativ können die dependencies manuell via pip installiert und das Programm über `python3 app/main.py` gestartet werden.
