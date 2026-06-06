from typing import Callable, Optional
import customtkinter as ctk
from app import theme
from app.pages.base_page import BasePage

_PROBLEMS = [
    # ── Passwörter ────────────────────────────────────────────────────────────
    {
        "icon": "🎲", "category": "passwort",
        "title": "Ich brauche ein neues, sicheres Passwort",
        "hint":  "Passwort-Generator — erstellt ein zufälliges Passwort auf Knopfdruck.",
        "page":  "password_generator",
    },
    {
        "icon": "🔤", "category": "passwort",
        "title": "Ich will ein Passwort, das ich mir merken kann",
        "hint":  "Passphrasen-Generator — erstellt ein sicheres Passwort aus zufälligen Wörtern.",
        "page":  "passphrase_generator",
    },
    {
        "icon": "💪", "category": "passwort",
        "title": "Ich will wissen wie stark mein Passwort ist",
        "hint":  "Passwort-Stärke-Check — zeigt sofort Kriterien und Verbesserungsvorschläge.",
        "page":  "password_strength",
    },
    # ── Account ───────────────────────────────────────────────────────────────
    {
        "icon": "🔑", "category": "account",
        "title": "Mein Passwort könnte gestohlen worden sein",
        "hint":  "Passwort-Check — prüft ob dein Passwort in einem Datenleck auftauchte.",
        "page":  "password_check",
    },
    {
        "icon": "📋", "category": "account",
        "title": "Meine E-Mail könnte in einem Datenleck sein",
        "hint":  "E-Mail-Check — zeigt welche Dienste betroffen waren und was gestohlen wurde.",
        "page":  "email_check",
    },
    # ── Phishing ──────────────────────────────────────────────────────────────
    {
        "icon": "🔗", "category": "phishing",
        "title": "Ich möchte einen Link auf Phishing/Malware prüfen",
        "hint":  "URL & Absender-Check — prüft die URL gegen Googles Bedrohungsdatenbank.",
        "page":  "phishing_check",
    },
    {
        "icon": "📞", "category": "phishing",
        "title": "Ich habe einen Anruf von einer verdächtigen Nummer",
        "hint":  "Rufnummer-Check — erkennt Premium-, Wangiri- und Betrugs-Nummern.",
        "page":  "phone_check",
    },
    {
        "icon": "📝", "category": "phishing",
        "title": "Ich habe eine verdächtige SMS oder Nachricht bekommen",
        "hint":  "Text-Scan — analysiert Nachrichten auf Phishing- und Betrugsmerkmale.",
        "page":  "scam_check",
    },
    {
        "icon": "📷", "category": "phishing",
        "title": "Ich habe einen QR-Code und bin nicht sicher ob er sicher ist",
        "hint":  "QR-Check — analysiert die URL hinter einem QR-Code auf Phishing-Merkmale.",
        "page":  "qr_check",
    },
    # ── Datenschutz ───────────────────────────────────────────────────────────
    {
        "icon": "🖼️", "category": "datenschutz",
        "title": "Ich möchte versteckte Daten aus meinen Fotos entfernen",
        "hint":  "EXIF-Daten entfernen — löscht GPS-Standort, Kameramodell und andere Metadaten.",
        "page":  "exif_remover",
    },
    # ── Fakeshop ──────────────────────────────────────────────────────────────
    {
        "icon": "🛒", "category": "fakeshop",
        "title": "Ich weiß nicht ob ein Onlineshop seriös ist",
        "hint":  "Fakeshop-Detector — analysiert die Shop-Adresse auf Betrugsmerkmale + VirusTotal.",
        "page":  "fakeshop_detector",
    },
    {
        "icon": "✉️", "category": "fakeshop",
        "title": "Die E-Mail des Absenders sieht verdächtig aus",
        "hint":  "Absender-Scanner — prüft E-Mail-Adressen auf Phishing- und Fake-Shop-Muster.",
        "page":  "sender_scanner",
    },
]

_ARTICLES = [
    # ── Passwörter ────────────────────────────────────────────────────────────
    {
        "icon": "🔑", "category": "passwort",
        "title": "Warum starke Passwörter so wichtig sind",
        "body": [
            "Ein Passwort ist wie ein Schlüssel zu deinem digitalen Leben. Wer ihn hat, kann sich als du ausgeben — bei deiner E-Mail, deiner Bank, überall.",
            "Was Hacker machen:",
            [
                'Automatisierte Programme probieren Millionen häufiger Passwörter durch: "123456", "passwort", Geburtsdaten, Haustiernamen.',
                "Wenn ein Dienst gehackt wird, werden gestohlene Passwörter sofort auf anderen Seiten ausprobiert.",
                "Ein einziges schwaches oder wiederverwendetes Passwort kann alles kompromittieren.",
            ],
            "Die wichtigsten Regeln:",
            [
                "Länge schlägt Komplexität: 16 Zeichen sind besser als 8 Zeichen mit Sonderzeichen.",
                "Für jeden Dienst ein eigenes Passwort — niemals dasselbe zweimal.",
                "Merken musst du dir nur noch ein einziges: das Masterpasswort deines Passwort-Managers.",
                "Unser Generator erstellt sichere Passwörter auf Knopfdruck — direkt hier in der App.",
            ],
        ],
    },
    {
        "icon": "🎲", "category": "passwort",
        "title": "Wie erstelle ich ein sicheres Passwort?",
        "body": [
            "Ein gutes Passwort ist lang, zufällig und einzigartig — du musst es dir aber nicht merken. Dafür gibt es Passwort-Manager und unseren Generator.",
            "Was ein sicheres Passwort ausmacht:",
            [
                "Mindestens 16 Zeichen — je länger, desto besser.",
                "Groß- und Kleinbuchstaben, Zahlen und Sonderzeichen gemischt.",
                "Keine Wörter aus dem Wörterbuch, keine persönlichen Daten wie Geburtstage oder Namen.",
                "Für jeden Dienst ein eigenes — niemals dasselbe Passwort zweimal nutzen.",
            ],
            "Die einfachste Methode:",
            [
                "Nutze unseren Passwort-Generator — ein Klick, ein sicheres Passwort.",
                "Speichere es in einem Passwort-Manager (z. B. Bitwarden, KeePass) — kostenlos und sicher.",
                "Du brauchst dir dann nur noch ein einziges Masterpasswort zu merken.",
            ],
        ],
    },
    {
        "icon": "🔐", "category": "passwort",
        "title": "Zwei-Faktor-Authentifizierung (2FA) — einfach erklärt",
        "body": [
            "2FA bedeutet: Du brauchst zwei Dinge zum Einloggen — dein Passwort und einen Code, den du in genau diesem Moment auf dein Handy bekommst. Selbst wenn jemand dein Passwort stiehlt, kommt er ohne dein Handy nicht rein.",
            "Stell es dir so vor:",
            [
                "Dein Passwort ist wie die Haustür — wer einen Schlüssel hat, kommt rein.",
                "Mit 2FA brauchst du zusätzlich einen Code, der sich jede Minute ändert.",
                "Selbst ein Einbrecher mit Schlüsselkopie scheitert — weil er den Code nicht hat.",
            ],
            "Wo solltest du 2FA aktivieren?",
            [
                "E-Mail-Konto (das wichtigste überhaupt — fast alles läuft darüber).",
                "Online-Banking und PayPal.",
                "Amazon, eBay und andere Shops.",
                "Social Media: Instagram, Facebook usw.",
                "Zu finden unter: Einstellungen → Sicherheit → Zwei-Faktor-Authentifizierung.",
            ],
        ],
    },
    # ── Account ───────────────────────────────────────────────────────────────
    {
        "icon": "🚨", "category": "account",
        "title": "Ich wurde gehackt — was jetzt?",
        "body": [
            "Ruhig bleiben. Schnell handeln, aber nicht in Panik. Die meisten Schäden lassen sich begrenzen, wenn du jetzt die richtigen Schritte machst.",
            "Sofortmaßnahmen:",
            [
                "Passwort des betroffenen Kontos sofort ändern — von einem anderen, sicheren Gerät.",
                "Wenn du dasselbe Passwort woanders nutzt: dort ebenfalls sofort ändern.",
                "2FA aktivieren, falls noch nicht geschehen.",
                "Aktive Sitzungen abmelden (meist unter Einstellungen → Sicherheit → Angemeldete Geräte).",
            ],
            "Nachsorge:",
            [
                "Prüfe ob verdächtige Aktionen stattfanden: Bestellungen, Überweisungen, gesendete Mails.",
                "Wenn Bankdaten betroffen: sofort bei der Bank anrufen — Nummer auf der Karte oder der offiziellen Website.",
                "Wenn dein E-Mail-Konto gehackt wurde: Freunde und Familie warnen.",
                "Erstattet eine Anzeige bei der Polizei, wenn dir finanzieller Schaden entstanden ist.",
            ],
        ],
    },
    # ── Phishing ──────────────────────────────────────────────────────────────
    {
        "icon": "🎣", "category": "phishing",
        "title": "Was ist Phishing?",
        "body": [
            'Phishing ist der Versuch, dich mit einer gefälschten Nachricht oder Webseite zu täuschen — um an dein Passwort, deine Bankdaten oder andere persönliche Infos zu kommen. Der Name kommt vom englischen "fishing" (Angeln).',
            "So erkennst du Phishing:",
            [
                'Dringlichkeit: "Dein Konto wird gesperrt — reagiere sofort!" — Stress soll dich unvorsichtig machen.',
                'Falscher Absender: Die Mail sieht aus wie von PayPal, kommt aber von "paypa1-support.xyz".',
                'Gefälschte Links: Der Text sagt "paypal.com", der Link führt aber woanders hin.',
                "Rechtschreib- und Grammatikfehler — viele Phishing-Mails sind schlecht übersetzt.",
            ],
            "Was du tun solltest:",
            [
                "Niemals auf Links in verdächtigen Mails klicken. Die Webseite lieber selbst eintippen.",
                "Unseren URL & Absender-Check nutzen, bevor du auf irgendetwas klickst.",
                "Den Text-Scan nutzen um verdächtige Nachrichten zu analysieren.",
            ],
        ],
    },
    {
        "icon": "📞", "category": "phishing",
        "title": "Telefonbetrug — Wangiri und falsche Behörden",
        "body": [
            "Telefonbetrug ist auf dem Vormarsch. Zwei besonders häufige Maschen: Wangiri (einmal anklingeln) und falsche Behörden/Unternehmen.",
            "Wangiri-Betrug:",
            [
                "Du bekommst einen Anruf aus dem Ausland, der nach einem Klingeln abbricht.",
                "Wenn du zurückrufst, landest du auf einer teuren Premium-Nummer.",
                "Erkennungszeichen: unbekannte internationale Vorwahl, nur ein Klingeln.",
                "Regel: Nummern aus unbekannten Ländern nie zurückrufen.",
            ],
            "Falsche Behörden und Unternehmen:",
            [
                "Angebliche Polizei, Finanzamt, Microsoft oder Banken rufen an und verlangen Zahlung oder Daten.",
                "Echte Behörden fordern NIEMALS Zahlung per Telefon oder Gutscheinkarten.",
                "Im Zweifel: Auflegen und die offizielle Nummer selbst suchen und zurückrufen.",
                "Unseren Rufnummer-Check nutzen um bekannte Betrugs-Nummern zu identifizieren.",
            ],
        ],
    },
    # ── Fakeshop ──────────────────────────────────────────────────────────────
    {
        "icon": "🛒", "category": "fakeshop",
        "title": "Fake-Shops erkennen — worauf achten?",
        "body": [
            "Fake-Shops sehen aus wie echte Online-Shops — sie schicken aber entweder gar nichts oder gefälschte Ware. Mit ein paar Checks erkennst du die meisten, bevor du bestellst.",
            "Woran du einen Fake-Shop erkennst:",
            [
                "Extreme Rabatte: 80 % auf Markenware ist fast immer Betrug.",
                "Komische Web-Adresse: 'adidas-outlet-sale-2024.de' statt 'adidas.de'.",
                "Kein Impressum oder vage Angaben: Pflicht für jeden deutschen Shop.",
                "Nur Vorkasse: Kein PayPal, keine Kreditkarte — nur Überweisung.",
                "Keine HTTPS-Verschlüsselung: Das Schloss-Symbol fehlt.",
            ],
            "Was du tun solltest:",
            [
                "Unseren Fakeshop-Detector nutzen — er prüft die Adresse, Domain-Alter und VirusTotal.",
                "Den Absender-Scanner für verdächtige Shop-E-Mails nutzen.",
                "Den Shop-Namen bei Google mit 'Erfahrungen' oder 'Betrug' suchen.",
                "Im Zweifel lieber beim offiziellen Markenshop kaufen.",
            ],
        ],
    },
    {
        "icon": "✉️", "category": "fakeshop",
        "title": "E-Mail-Spoofing — wenn Absender gefälscht werden",
        "body": [
            "E-Mail-Spoofing bedeutet: Der Anzeige-Name im Postfach sieht aus wie von Amazon oder PayPal — aber die echte Absenderadresse dahinter ist eine komplett andere.",
            "So funktioniert es:",
            [
                "E-Mail-Programme zeigen oft nur den Anzeigenamen ('Amazon Kundenservice'), nicht die echte Adresse.",
                "Die echte Adresse könnte 'fraud@random-domain.xyz' sein — sichtbar nur beim Aufklappen.",
                "Gefälschte Domains wie 'amazon-hilfe.de' oder 'paypal-service.net' wirken täuschend echt.",
            ],
            "Wie du dich schützt:",
            [
                "Im E-Mail-Programm immer die vollständige Absenderadresse prüfen — nicht nur den Anzeigenamen.",
                "Unseren Absender-Scanner nutzen um die Adresse zu analysieren.",
                "Bei der kleinsten Unsicherheit: die offizielle Webseite direkt eintippen, nicht auf Links klicken.",
            ],
        ],
    },
    # ── Passphrase ────────────────────────────────────────────────────────────
    {
        "icon": "🔤", "category": "passwort",
        "title": "Passphrase vs. Passwort — was ist sicherer?",
        "body": [
            "Ein klassisches Passwort wie 'X#9kL!2m' ist stark, aber kaum zu merken. Eine Passphrase wie 'Apfel-Tiger-Mauer-27' ist länger, genauso sicher — und du kannst sie dir tatsächlich merken.",
            "Warum Passphrases so stark sind:",
            [
                "Sicherheit kommt hauptsächlich aus der Länge. 4 zufällige Wörter ergeben ~20 Zeichen — mehr als die meisten 'komplexen' Kurz-Passwörter.",
                "Entropie zählt: 4 Wörter aus einer Liste von 200 = ~50 Bits Entropie. Zum Vergleich: 8 zufällige Zeichen = ~48 Bits.",
                "Das Gehirn kann sich Wörter viel besser merken als zufällige Zeichenfolgen — das Passwort aufzuschreiben entfällt.",
            ],
            "Wann lieber ein klassisches Passwort:",
            [
                "Wenn der Dienst Sonderzeichen vorschreibt und Leerzeichen oder Bindestriche nicht erlaubt.",
                "Für Accounts in einem Passwort-Manager — dort brauchst du dir die Passwörter nicht merken.",
                "Beide Arten sind sicher, wenn sie zufällig und lang genug sind. Der Generator hier hilft bei beiden.",
            ],
        ],
    },
    # ── QR-Phishing ───────────────────────────────────────────────────────────
    {
        "icon": "📷", "category": "phishing",
        "title": "QR-Phishing (Quishing) — wie Betrüger QR-Codes missbrauchen",
        "body": [
            "QR-Codes sind praktisch — und genau deshalb ein neues Werkzeug für Betrüger. Der Angriff heißt 'Quishing' (QR + Phishing) und ist auf dem Vormarsch.",
            "Wie Quishing funktioniert:",
            [
                "Betrüger ersetzen echte QR-Codes durch gefälschte — zum Beispiel auf Parkautomaten, Flyern oder in E-Mails.",
                "Das Scannen öffnet sofort einen Browser. Viele E-Mail-Filter und Antivirus-Programme prüfen QR-Code-Inhalte nicht.",
                "Die Zielseite sieht oft täuschend echt aus — Banking-Login, Paketdienst, Amazon oder PayPal.",
            ],
            "Wo QR-Phishing vorkommt:",
            [
                "Parkautomaten und Ladestationen: Aufkleber mit falschem QR-Code über den echten.",
                "E-Mails: 'Bestätige dein Konto' mit QR-Code statt Link — um E-Mail-Filter zu umgehen.",
                "Flyer und Plakate: Gefälschte Gewinnspiele, Rabattaktionen.",
                "Pakete: Falscher QR-Code zum angeblichen Zollformular.",
            ],
            "So schützt du dich:",
            [
                "QR-Code nur scannen, wenn du der Quelle vertraust — auf dem Parkautomaten nach Überklebungen suchen.",
                "Nach dem Scannen: NICHT sofort tippen. Die URL in SecBuddy prüfen.",
                "Niemals Login-Daten auf einer Seite eingeben, die du per QR-Code geöffnet hast, ohne die URL geprüft zu haben.",
            ],
        ],
    },
    # ── Datenschutz ───────────────────────────────────────────────────────────
    {
        "icon": "🔍", "category": "datenschutz",
        "title": "Was sind EXIF-Daten und warum sind sie gefährlich?",
        "body": [
            "EXIF steht für Exchangeable Image File Format — ein Standard, der Metadaten in Bilddateien speichert. Diese Daten sind unsichtbar, können aber sehr viel über dich verraten.",
            "Was in einem typischen Smartphone-Foto stecken kann:",
            [
                "GPS-Koordinaten: Genaue Längen- und Breitengrade — oft auf wenige Meter genau.",
                "Datum und Uhrzeit der Aufnahme.",
                "Gerätehersteller und -modell (z. B. 'Apple iPhone 15 Pro').",
                "Software-Version und Kamera-Einstellungen.",
                "Manchmal: Name des Fotografen (aus Geräteprofil).",
            ],
            "Wann ist das ein Problem?",
            [
                "Du postest ein Foto aus deiner Wohnung — jemand liest die GPS-Daten und kennt deine Adresse.",
                "Journalisten, Aktivisten oder Opfer von Stalking können so geortet werden.",
                "Täter nutzen EXIF-Daten von Fotos um herauszufinden, wo jemand regelmäßig ist.",
                "Auch bei Verkaufsplattformen: Fotos von Gegenständen enthalten oft Heimatadresse.",
            ],
            "Gut zu wissen:",
            [
                "Viele soziale Netzwerke (Instagram, Twitter/X, WhatsApp) entfernen EXIF beim Upload automatisch.",
                "E-Mail-Anhänge, direkte Weitergabe (AirDrop, USB) oder Clouds wie iCloud/Google Drive behalten EXIF.",
                "Mit dem EXIF-Entferner in SecBuddy kannst du Metadaten vor dem Teilen entfernen — lokal, ohne Upload.",
            ],
        ],
    },
    {
        "icon": "🛡️", "category": "datenschutz",
        "title": "Digitale Privatsphäre — 5 einfache Maßnahmen",
        "body": [
            "Du musst kein Experte sein um deine Privatsphäre online zu schützen. Diese fünf Schritte helfen sofort.",
            None,
            [
                "EXIF aus Fotos entfernen, bevor du sie per E-Mail oder Messenger verschickst — besonders bei Bildern aus dem Zuhause.",
                "QR-Codes immer prüfen, bevor du die enthaltene URL öffnest. SecBuddy hat dafür den QR-Check.",
                "Standortfreigabe für Apps auf das Notwendigste reduzieren — Einstellungen → Datenschutz → Ortungsdienste.",
                "Für verschiedene Dienste verschiedene E-Mail-Adressen nutzen — kostenlos z. B. mit SimpleLogin oder Addy.io.",
                "Regelmäßig prüfen, welche Apps Zugriff auf Kamera, Mikrofon und Kontakte haben — und unnötige Freigaben entfernen.",
            ],
        ],
    },
    # ── Weitere Artikel ───────────────────────────────────────────────────────
    {
        "icon": "🗄️", "category": "passwort",
        "title": "Was ist ein Passwort-Manager?",
        "body": [
            "Ein Passwort-Manager ist ein Programm, das alle deine Passwörter sicher speichert und verwaltet. "
            "Du merkst dir nur noch ein einziges Masterpasswort — den Rest erledigt der Manager.",
            "Was ein Passwort-Manager kann:",
            [
                "Unbegrenzt viele einzigartige Passwörter speichern und abrufen.",
                "Beim Login automatisch das richtige Passwort einfügen.",
                "Neue, zufällige Passwörter generieren — ähnlich wie unser Generator hier.",
                "Passwörter zwischen Geräten synchronisieren (optional, je nach Anbieter).",
            ],
            "Empfehlenswerte kostenlose Optionen:",
            [
                "Bitwarden — Open Source, kostenlos, Cloud-Sync, sehr empfehlenswert.",
                "KeePass — Lokal auf dem Gerät, kein Cloud-Sync, maximale Kontrolle.",
                "Apple Schlüsselbund / Google Passwort-Manager — integriert, einfach, aber plattformgebunden.",
            ],
            "Ist das nicht riskant? Alles an einem Ort?",
            [
                "Ein starkes Masterpasswort + 2FA auf dem Manager ist sicherer als 20 schwache Passwörter.",
                "Ohne Manager nutzen die meisten dasselbe schwache Passwort überall — das ist das eigentliche Risiko.",
            ],
        ],
    },
    {
        "icon": "🌐", "category": "passwort",
        "title": "Was ist ein VPN — und wann brauche ich es?",
        "body": [
            "Ein VPN (Virtual Private Network) verschlüsselt deine Internetverbindung und leitet sie durch einen "
            "Server in einem anderen Land. Deine echte IP-Adresse bleibt verborgen.",
            "Wann ein VPN sinnvoll ist:",
            [
                "Im öffentlichen WLAN (Café, Hotel, Bahn): Ein VPN schützt vor Mitlesen durch andere im Netzwerk.",
                "Wenn du geografische Einschränkungen umgehen möchtest (z. B. Streaming-Inhalte).",
                "Wenn du von Behörden oder ISPs nicht beobachtet werden möchtest.",
            ],
            "Wann ein VPN NICHT hilft:",
            [
                "Gegen Phishing oder Malware — ein VPN schützt nicht vor gefährlichen Links oder Dateien.",
                "Es macht dich nicht anonym: Der VPN-Anbieter selbst sieht deinen Traffic.",
                "Auf Seiten mit HTTPS ist deine Verbindung auch ohne VPN verschlüsselt.",
            ],
            "Worauf beim Anbieter achten:",
            [
                "No-Log-Policy: Der Anbieter speichert keine Verbindungsdaten.",
                "Bekannte Anbieter: Mullvad, ProtonVPN (kostenlos verfügbar), NordVPN.",
                "Kostenlose VPNs oft mit Vorsicht genießen — sie verdienen oft durch Datenweitergabe.",
            ],
        ],
    },
    {
        "icon": "🛍️", "category": "fakeshop",
        "title": "Sicheres Online-Shopping — Checkliste",
        "body": [
            "Vor jedem Kauf in einem unbekannten Shop: Diese Punkte in 2 Minuten durchgehen.",
            "Checkliste vor der Bestellung:",
            [
                "✅  HTTPS in der Adresszeile — Schloss-Symbol vorhanden?",
                "✅  Impressum mit vollständiger Firmenadresse vorhanden?",
                "✅  AGB und Widerrufsrecht vorhanden und lesbar?",
                "✅  Mindestens eine seriöse Zahlungsmethode (PayPal, Kreditkarte, Rechnung)?",
                "✅  Shop-Name bei Google + 'Erfahrungen' gesucht?",
                "✅  Preis realistisch? 80 % Rabatt auf Markenware ist fast immer Betrug.",
                "✅  Domain prüfen: Stimmt die Adresse mit der echten Marke überein?",
                "✅  SecBuddy Fakeshop-Detector zur Sicherheit laufen lassen.",
            ],
            "Wenn du bereits bestellt hast und betrogen wurdest:",
            [
                "Zahlung sofort bei der Bank oder PayPal anfechten (Chargeback).",
                "Anzeige bei der Polizei erstatten — auch online möglich.",
                "Verbraucherzentrale kontaktieren: Sie helfen kostenlos weiter.",
            ],
        ],
    },
    {
        "icon": "🧠", "category": "phishing",
        "title": "Social Engineering — mehr als nur Phishing",
        "body": [
            "Social Engineering bedeutet: Menschen statt Technik manipulieren. "
            "Betrüger nutzen Psychologie — Vertrauen, Angst, Dringlichkeit — um an Daten oder Geld zu kommen.",
            "Die häufigsten Formen:",
            [
                "Phishing (E-Mail/SMS): Gefälschte Nachrichten von scheinbar echten Absendern.",
                "Vishing (Telefon): Anrufe von 'Banken', 'Microsoft-Support' oder 'Behörden'.",
                "Pretexting: Betrüger erfinden eine Geschichte ('Ich bin IT-Support') um Infos zu erfragen.",
                "Quid-pro-quo: 'Wir helfen dir kostenlos' — als Gegenleistung für Zugangsdaten.",
                "Tailgating: Physisch in gesicherte Bereiche folgen (weniger relevant im Alltag).",
            ],
            "Die psychologischen Hebel, die Betrüger nutzen:",
            [
                "Dringlichkeit: 'Sofort handeln!' — damit du nicht nachdenken kannst.",
                "Autorität: 'Ich bin vom Finanzamt' — Respekt vor Institutionen ausnutzen.",
                "Angst: 'Dein Konto wird gesperrt' — Panik führt zu unbedachten Aktionen.",
                "Neugier oder Gier: 'Du hast gewonnen' — emotionale Reaktion vor Vernunft.",
            ],
            "Goldene Regel:",
            [
                "Jede unerwartete Kontaktaufnahme, die Daten, Geld oder Zugriffsrechte verlangt — immer hinterfragen.",
                "Im Zweifel: Auflegen, den offiziellen Kanal suchen, und dort direkt nachfragen.",
            ],
        ],
    },
    # ── Neue Artikel ─────────────────────────────────────────────────────────
    {
        "icon": "🌐", "category": "phishing",
        "title": "Was tun wenn ich auf einen Phishing-Link geklickt habe?",
        "body": [
            "Ruhig bleiben — ein Klick allein reicht meist nicht aus um sofort Schaden anzurichten. Entscheidend ist was du in den nächsten Minuten tust.",
            "Sofortmaßnahmen (in dieser Reihenfolge):",
            [
                "Kein Login-Formular ausfüllen und keine Daten eingeben — Seite sofort schließen.",
                "WLAN kurz trennen und wieder verbinden — unterbricht mögliche laufende Downloads.",
                "Prüfen ob sich etwas heruntergeladen hat: Downloads-Ordner kontrollieren, nichts öffnen.",
                "Falls du Zugangsdaten eingegeben hast: Passwort des betroffenen Kontos sofort ändern.",
                "Falls du Zahlungsdaten eingegeben hast: Bank sofort anrufen.",
            ],
            "Wenn du nur geklickt aber nichts eingegeben hast:",
            [
                "Meistens passiert nichts — moderne Browser blockieren die meisten Drive-by-Downloads.",
                "Trotzdem: Antivirusprogramm einen Scan laufen lassen.",
                "Passwort des Kontos ändern aus dem der Link kam (z. B. E-Mail, WhatsApp).",
                "In den nächsten Tagen auf ungewöhnliche Kontobewegungen achten.",
            ],
            "Langfristig schützen:",
            [
                "SecBuddy Betrugs-Check nutzen — verdächtige Links prüfen BEVOR man klickt.",
                "Browser und Betriebssystem aktuell halten — Sicherheitslücken werden so geschlossen.",
                "2FA aktivieren — schützt Accounts auch wenn Zugangsdaten gestohlen wurden.",
            ],
        ],
    },
    {
        "icon": "📶", "category": "passwort",
        "title": "Öffentliches WLAN — was ist sicher, was nicht?",
        "body": [
            "Freies WLAN im Café, Hotel oder Bahnhof ist praktisch — aber auch ein bekanntes Angriffsziel. Mit einfachen Regeln kannst du es trotzdem sicher nutzen.",
            "Was im öffentlichen WLAN passieren kann:",
            [
                "Man-in-the-Middle-Angriff: Jemand im gleichen Netz kann unverschlüsselten Datenverkehr mitlesen.",
                "Fake-Hotspot: Ein Angreifer erstellt ein WLAN namens 'Hotel_Free' — wer sich verbindet, schickt alle Daten durch dessen Gerät.",
                "Automatische Verbindung: Dein Gerät verbindet sich mit bekannten Netznamen — auch mit gefälschten.",
            ],
            "Was trotzdem sicher ist:",
            [
                "Alle Seiten mit HTTPS (Schloss-Symbol) — der Inhalt ist verschlüsselt, selbst wenn jemand mithört.",
                "Banking-Apps mit eigener Verschlüsselung — diese bauen ihre eigene Verbindung auf.",
                "Lesen von Nachrichtenseiten, Wikipedia, YouTube — keine sensiblen Daten.",
            ],
            "Was du vermeiden solltest:",
            [
                "Login auf wichtigen Konten ohne 2FA — Passwort könnte abgefangen werden.",
                "Sensible Dokumente senden oder empfangen.",
                "Automatische WLAN-Verbindung aktiviert lassen — unter Einstellungen deaktivieren.",
            ],
            "Goldene Regel:",
            [
                "Im öffentlichen WLAN: Nur Seiten mit HTTPS nutzen. Für Banken und E-Mails: Mobilfunknetz bevorzugen oder VPN nutzen.",
            ],
        ],
    },
    {
        "icon": "📸", "category": "datenschutz",
        "title": "Privatsphäre beim Teilen von Fotos — worauf achten?",
        "body": [
            "Fotos teilen wir täglich — in Chats, per Mail, auf Verkaufsplattformen. Was die meisten nicht wissen: Fotos enthalten oft mehr Informationen als sichtbar ist.",
            "Unsichtbare Risiken in Fotos:",
            [
                "EXIF-Daten: Jedes Smartphone-Foto enthält GPS-Koordinaten, Gerätename und Aufnahmezeit.",
                "Hintergrundinformationen: Hausnummern, Straßenschilder, Autokennzeichen im Bild.",
                "Metadaten in Dokumenten: Ähnlich wie bei Fotos — Word- oder PDF-Dateien enthalten oft Autorenname und Bearbeitungshistorie.",
            ],
            "Wann ist das ein Problem?",
            [
                "Fotos von Gegenständen auf eBay-Kleinanzeigen → EXIF enthält Heimatadresse.",
                "Selfie aus dem Homeoffice an Kollegen → GPS-Standort deiner Wohnung im Bild.",
                "Journalisten, Aktivisten, Opfer von Stalking: Besondere Vorsicht bei jedem geteilten Foto.",
                "Kinder-Fotos: Schulmäßige Einbindung von GPS-Daten in jedem Bild.",
            ],
            "Wann sind Fotos automatisch sicher?",
            [
                "Instagram, WhatsApp, Facebook — diese Plattformen entfernen EXIF beim Upload automatisch.",
                "Direkt gesendete Fotos (E-Mail, AirDrop, USB) behalten EXIF dagegen komplett.",
            ],
            "Lösung:",
            [
                "SecBuddy EXIF-Entferner nutzen — entfernt alle Metadaten lokal, kein Upload nötig.",
                "Alternativ: Foto vor dem Senden kurz als Screenshot aufnehmen — Screenshots enthalten keine EXIF-Daten.",
            ],
        ],
    },
    {
        "icon": "🔓", "category": "account",
        "title": "Mein Konto wurde gehackt — so erkennst du es früh",
        "body": [
            "Konten werden oft gehackt ohne dass der Besitzer es sofort merkt. Frühe Erkennung minimiert den Schaden erheblich.",
            "Typische Anzeichen eines gehackten Kontos:",
            [
                "Du bekommst Login-Benachrichtigungen von unbekannten Geräten oder Orten.",
                "Freunde berichten von seltsamen Nachrichten oder Beiträgen von dir.",
                "Unbekannte Käufe, Abbuchungen oder Bestellungen auf deinem Namen.",
                "Dein Passwort funktioniert plötzlich nicht mehr — der Angreifer hat es geändert.",
                "Unbekannte Apps haben Zugriff auf dein Konto (sichtbar unter Einstellungen → Verbundene Apps).",
            ],
            "Sofortmaßnahmen:",
            [
                "Passwort des Kontos sofort ändern — von einem anderen, vertrauenswürdigen Gerät.",
                "2FA aktivieren falls noch nicht vorhanden.",
                "Alle aktiven Sitzungen abmelden (unter Einstellungen → Sicherheit → Angemeldete Geräte).",
                "Verbundene Apps und Berechtigungen prüfen und unbekannte entfernen.",
            ],
            "Proaktiver Schutz:",
            [
                "E-Mail-Adresse regelmäßig im SecBuddy E-Mail-Check prüfen — zeigt bekannte Datenlecks.",
                "Passwort-Check nutzen — prüft ob dein Passwort in Datenlecks auftauchte.",
                "Für jeden Dienst ein eigenes Passwort — verhindert Domino-Effekt bei einem Leak.",
            ],
        ],
    },
    # ── Allgemein ─────────────────────────────────────────────────────────────
    {
        "icon": "🛡️", "category": "passwort",
        "title": "5 Dinge, die dich sofort sicherer machen",
        "body": [
            "Vollständige Sicherheit gibt es nicht — aber mit diesen fünf Schritten bist du besser geschützt als die meisten.",
            None,
            [
                "Nutze für jeden Dienst ein eigenes Passwort. Kein Copy-Paste.",
                "Aktiviere 2FA überall wo es geht — besonders bei E-Mail und Banking.",
                "Klicke niemals auf Links in unerwarteten Mails oder SMS. Immer selbst eintippen.",
                "Halte dein Betriebssystem und deine Apps aktuell — Updates schließen Sicherheitslücken.",
                "Prüfe verdächtige Nachrichten mit dem Text-Scan, bevor du reagierst.",
            ],
        ],
    },
]

_TABS = [
    ("Alle",           None),
    ("🔑 Passwörter",  "passwort"),
    ("👤 Account",     "account"),
    ("🎣 Phishing",    "phishing"),
    ("🛒 Fakeshop",    "fakeshop"),
    ("🔒 Datenschutz", "datenschutz"),
]


class HelpPage(BasePage):
    def __init__(self, parent: ctk.CTkFrame) -> None:
        super().__init__(parent)
        self._expanded: dict = {}
        self._build()

    def set_navigate(self, fn: Callable) -> None:
        self._navigate = fn

    def show_with_category(self, cat_id: str) -> None:
        """Wählt den Tab für cat_id vor und filtert. Wird von app.py aufgerufen."""
        for label, cid in _TABS:
            if cid == cat_id:
                self._cat_var.set(label)
                self._filter()
                return

    def _build(self) -> None:
        scroll = ctk.CTkScrollableFrame(self, fg_color=theme.BG_MAIN, corner_radius=0)
        scroll.pack(fill="both", expand=True)

        inner = ctk.CTkFrame(scroll, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=36, pady=28)

        ctk.CTkLabel(
            inner, text="Hilfe",
            font=theme.FONT_TITLE, text_color=theme.TEXT_PRIMARY, anchor="w",
        ).pack(fill="x")
        ctk.CTkLabel(
            inner,
            text="Beschreibe dein Problem – wir zeigen dir das passende Tool.",
            font=theme.FONT_BODY, text_color=theme.TEXT_SECONDARY, anchor="w",
        ).pack(fill="x", pady=(4, 16))

        # ── Suche ──────────────────────────────────────────────────────────
        self._search_var = ctk.StringVar()
        ctk.CTkEntry(
            inner, textvariable=self._search_var,
            placeholder_text='🔍  z. B. "Passwort", "Phishing", "Shop" ...',
            font=theme.FONT_BODY,
            fg_color=theme.BG_SURFACE, border_color=theme.BORDER,
            text_color=theme.TEXT_PRIMARY,
            height=44, corner_radius=theme.RADIUS,
        ).pack(fill="x", pady=(0, 12))
        self._search_var.trace_add("write", lambda *_: self._filter())

        # ── Kategorie-Tabs ──────────────────────────────────────────────────
        self._cat_var = ctk.StringVar(value="Alle")
        ctk.CTkSegmentedButton(
            inner,
            values=[t[0] for t in _TABS],
            variable=self._cat_var,
            command=lambda _: self._filter(),
            font=theme.FONT_SMALL,
            fg_color=theme.BG_SURFACE,
            selected_color=theme.ACCENT,
            selected_hover_color=theme.ACCENT_HOVER,
            unselected_color=theme.BG_SURFACE,
            unselected_hover_color=theme.BORDER,
            text_color=theme.TEXT_PRIMARY,
            text_color_disabled=theme.TEXT_MUTED,
        ).pack(fill="x", pady=(0, 20))

        # ── Problem-Karten ──────────────────────────────────────────────────
        self._cards_frame = ctk.CTkFrame(inner, fg_color="transparent")
        self._cards_frame.pack(fill="both", expand=True)
        self._render_cards(_PROBLEMS)

        # ── Wissens-Center ──────────────────────────────────────────────────
        ctk.CTkFrame(inner, height=1, fg_color=theme.BORDER).pack(fill="x", pady=(28, 0))
        ctk.CTkLabel(
            inner, text="Wissens-Center",
            font=theme.FONT_HEADING, text_color=theme.TEXT_PRIMARY, anchor="w",
        ).pack(anchor="w", pady=(16, 4))
        ctk.CTkLabel(
            inner,
            text="Kurze Erklärungen zu den wichtigsten Sicherheitsthemen.",
            font=theme.FONT_SMALL, text_color=theme.TEXT_SECONDARY, anchor="w",
        ).pack(anchor="w", pady=(0, 12))

        self._articles_frame = ctk.CTkFrame(inner, fg_color="transparent")
        self._articles_frame.pack(fill="x")
        self._render_articles(_ARTICLES)

    # ── Filter ──────────────────────────────────────────────────────────────

    def _filter(self) -> None:
        q      = self._search_var.get().lower()
        cat    = self._cat_var.get()
        cat_id = next((c for lbl, c in _TABS if lbl == cat), None)

        problems = [
            p for p in _PROBLEMS
            if (cat_id is None or p["category"] == cat_id)
            and (not q or q in p["title"].lower() or q in p["hint"].lower())
        ]
        self._render_cards(problems)

        articles = [
            a for a in _ARTICLES
            if (cat_id is None or a["category"] == cat_id)
            and (not q or q in a["title"].lower() or self._article_matches(a, q))
        ]
        self._render_articles(articles)

    @staticmethod
    def _article_matches(article: dict, q: str) -> bool:
        for item in article["body"]:
            if item is None:
                continue
            if isinstance(item, str) and q in item.lower():
                return True
            if isinstance(item, list) and any(q in b.lower() for b in item):
                return True
        return False

    # ── Problem-Karten ───────────────────────────────────────────────────────

    def _render_cards(self, problems: list) -> None:
        for w in self._cards_frame.winfo_children():
            w.destroy()
        if not problems:
            ctk.CTkLabel(
                self._cards_frame,
                text="Keine Treffer — anderen Tab oder Suchbegriff versuchen.",
                font=theme.FONT_BODY, text_color=theme.TEXT_MUTED,
            ).pack(pady=20)
            return

        for p in problems:
            card = ctk.CTkFrame(
                self._cards_frame, fg_color=theme.BG_SURFACE, corner_radius=theme.RADIUS,
            )
            card.pack(fill="x", pady=6)

            ctk.CTkLabel(
                card, text=p["icon"],
                font=("Segoe UI", 26), text_color=theme.ACCENT, width=48,
            ).pack(side="left", padx=(16, 4), pady=16)

            mid = ctk.CTkFrame(card, fg_color="transparent")
            mid.pack(side="left", fill="both", expand=True, padx=8, pady=12)
            ctk.CTkLabel(
                mid, text=p["title"],
                font=theme.FONT_SUBHEADING, text_color=theme.TEXT_PRIMARY, anchor="w",
            ).pack(fill="x")
            ctk.CTkLabel(
                mid, text=p["hint"],
                font=theme.FONT_SMALL, text_color=theme.TEXT_SECONDARY, anchor="w",
            ).pack(fill="x")

            if p.get("page") and self._navigate:
                ctk.CTkButton(
                    card, text="Öffnen  →", width=100, height=34,
                    font=theme.FONT_SMALL,
                    fg_color=theme.ACCENT, hover_color=theme.ACCENT_HOVER,
                    text_color="white", corner_radius=theme.RADIUS,
                    command=lambda pg=p["page"]: self._navigate(pg),
                ).pack(side="right", padx=16)

    # ── Wissens-Center ───────────────────────────────────────────────────────

    def _render_articles(self, articles: list) -> None:
        for w in self._articles_frame.winfo_children():
            w.destroy()
        if not articles:
            ctk.CTkLabel(
                self._articles_frame,
                text="Keine Artikel für diese Auswahl.",
                font=theme.FONT_BODY, text_color=theme.TEXT_MUTED,
            ).pack(pady=20)
            return
        for article in articles:
            self._article_accordion(self._articles_frame, article)

    def _article_accordion(self, parent: ctk.CTkFrame, article: dict) -> None:
        key = article["title"]
        if key not in self._expanded:
            self._expanded[key] = False

        outer = ctk.CTkFrame(parent, fg_color=theme.BG_SURFACE, corner_radius=theme.RADIUS)
        outer.pack(fill="x", pady=5)

        header = ctk.CTkFrame(outer, fg_color="transparent", cursor="hand2")
        header.pack(fill="x")

        ctk.CTkLabel(
            header, text=article["icon"],
            font=("Segoe UI", 18), text_color=theme.ACCENT, width=40,
        ).pack(side="left", padx=(14, 4), pady=12)
        ctk.CTkLabel(
            header, text=article["title"],
            font=theme.FONT_SUBHEADING, text_color=theme.TEXT_PRIMARY, anchor="w",
        ).pack(side="left", fill="x", expand=True)

        arrow = ctk.CTkLabel(header, text="▼", font=theme.FONT_SMALL,
                             text_color=theme.TEXT_MUTED, width=30)
        arrow.pack(side="right", padx=14)

        body_frame = ctk.CTkFrame(outer, fg_color="transparent")
        self._fill_body(body_frame, article["body"])

        if self._expanded[key]:
            body_frame.pack(fill="x")
            arrow.configure(text="▲")

        def toggle(k=key, body=body_frame, arr=arrow) -> None:
            self._expanded[k] = not self._expanded[k]
            if self._expanded[k]:
                body.pack(fill="x")
                arr.configure(text="▲")
            else:
                body.pack_forget()
                arr.configure(text="▼")

        for w in (header, arrow, *header.winfo_children()):
            w.bind("<Button-1>", lambda _e, t=toggle: t())

    def _fill_body(self, parent: ctk.CTkFrame, body: list) -> None:
        ctk.CTkFrame(parent, fg_color=theme.BORDER, height=1).pack(fill="x", padx=14)
        content = ctk.CTkFrame(parent, fg_color="transparent")
        content.pack(fill="x", padx=18, pady=(10, 16))

        for item in body:
            if item is None:
                continue
            if isinstance(item, str) and not item.endswith(":"):
                ctk.CTkLabel(
                    content, text=item, font=theme.FONT_SMALL,
                    text_color=theme.TEXT_SECONDARY, anchor="w",
                    justify="left", wraplength=600,
                ).pack(anchor="w", pady=(0, 8))
            elif isinstance(item, str) and item.endswith(":"):
                ctk.CTkLabel(
                    content, text=item,
                    font=("Segoe UI", 11, "bold"), text_color=theme.TEXT_PRIMARY, anchor="w",
                ).pack(anchor="w", pady=(6, 4))
            elif isinstance(item, list):
                for bullet in item:
                    row = ctk.CTkFrame(content, fg_color="transparent")
                    row.pack(fill="x", pady=2)
                    ctk.CTkLabel(row, text="•", font=theme.FONT_SMALL,
                                 text_color=theme.ACCENT, width=16).pack(side="left", anchor="n", pady=1)
                    ctk.CTkLabel(row, text=bullet, font=theme.FONT_SMALL,
                                 text_color=theme.TEXT_SECONDARY, anchor="w",
                                 justify="left", wraplength=580).pack(side="left", fill="x", expand=True)
