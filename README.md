🛡️ SecBuddy
Dein lokaler Sicherheits-Assistent für den Alltag.
SecBuddy hilft dir, Passwörter zu prüfen, Phishing zu erkennen und Fakeshops zu entlarven – einfach, verständlich und ohne dass sensible Daten unnötig das Gerät verlassen.

✨ Features
🔑 Passwörter

Passwort-Generator mit konfigurierbarer Länge, Sonderzeichen und Zahlen
Passphrasen-Generator – merkbare Wörter mit Trennzeichen
Lokaler Stärke-Check (Entropie, Muster, Länge)
HaveIBeenPwned-Abgleich – prüft ob dein Passwort in einem Datenleck auftaucht (k-Anonymität – das Passwort verlässt das Gerät nie)

👤 Account

E-Mail-Check – prüft eine Adresse auf bekannte Datenlecks via HaveIBeenPwned

🎣 Phishing

URL & Absender-Check – heuristische Analyse auf Phishing-Merkmale (vollständig lokal)
Rufnummer-Check – erkennt bekannte Betrugs- und Premiummuster + Tellows-Verknüpfung
Text-Scan – analysiert Nachrichten lokal auf Betrugsmerkmale
QR-Check – URL aus QR-Code per Eingabe oder Bild-Scan prüfen

🛒 Fakeshop

Fakeshop-Detector – Heuristik + WHOIS-Domain-Alter + optionaler VirusTotal-Check
Absender-Scanner – erkennt E-Mail-Spoofing-Merkmale

🔒 Datenschutz

EXIF-Entferner – löscht Metadaten aus Fotos lokal (JPEG/PNG)

⚙️ Sonstiges

Dark / Hell / System-Modus
Hilfe-Seite mit Suchfunktion und Wissens-Center
Rotierende Sicherheitstipps auf der Startseite
Automatischer Update-Check beim Start


📥 Download & Installation

Unter Releases die aktuelle SecBuddy.exe herunterladen
Starten – keine Installation nötig
Optional: VirusTotal API Key in den Einstellungen hinterlegen


⚠️ Windows Defender kann beim ersten Start eine Warnung anzeigen – das ist normal bei unsignierten Apps. Einfach "Trotzdem ausführen" klicken.


🔑 Optionaler API Key
Für den erweiterten Fakeshop-Check wird ein kostenloser VirusTotal API Key benötigt. Ohne Key läuft der Fakeshop-Detector weiterhin – nur mit Heuristik und WHOIS-Analyse.

⚠️ Bekannte Einschränkungen

Windows only – macOS und Linux folgen in einer späteren Version
VirusTotal – erfordert einen eigenen API Key für den vollen Fakeshop-Check
E-Mail-Check – prüft nur Datenlecks, keine Spam-Reputation oder Existenzprüfung
Rufnummer-Check – kein öffentliches Behörden-API verfügbar, daher lokal + Tellows-Link
EXIF-Entferner – aktuell nur JPEG/PNG, noch keine PDFs oder Office-Dateien
Hell-Modus – Hintergrundflächen wechseln erst nach Neustart vollständig
Passwort-, E-Mail- und Fakeshop-Checks benötigen eine Internetverbindung


🔒 Datenschutz
SecBuddy ist darauf ausgelegt, so wenig Daten wie möglich nach außen zu senden:

Passwörter verlassen das Gerät nie im Klartext (k-Anonymität via HaveIBeenPwned)
Phishing- und Text-Analysen laufen vollständig lokal
EXIF-Entfernung passiert ausschließlich auf deinem Gerät
Beim ersten Start kannst du optionale anonyme Nutzungsstatistiken aktivieren oder ablehnen


🗺️ Roadmap

 macOS & Linux Support
 EXIF-Entfernung für PDFs und Office-Dateien
 Erweiterte Rufnummer-Datenbank
 Hell-Modus Bugfix
