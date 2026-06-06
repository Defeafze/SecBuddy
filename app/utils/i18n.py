"""Einfaches Übersetzungs-Modul für SecBuddy."""

from app.utils import config as _cfg

_lang: list[str] = ["de"]

_T: dict[str, dict[str, str]] = {
    "de": {
        "settings.title": "Einstellungen",
        "settings.subtitle": "App-Einstellungen anpassen.",
        "settings.appearance.title": "Darstellung",
        "settings.appearance.desc": (
            "Wechsle zwischen Dark Mode und Hell Mode. "
            "Die Änderung wird sofort übernommen."
        ),
        "settings.appearance.dark": "🌙  Dark",
        "settings.appearance.light": "☀️  Hell",
        "settings.appearance.system": "💻  System",
        "settings.appearance.hint.title": "ℹ️  Hinweis zum Hell-Modus",
        "settings.appearance.hint.body": (
            "Die meisten Schaltflächen und Felder wechseln sofort die Farbe. "
            "Hintergrundflächen werden beim nächsten App-Start vollständig angepasst."
        ),
        "settings.language.title": "Sprache",
        "settings.language.desc": "Die Sprachänderung wird beim nächsten App-Start übernommen.",
        "settings.language.de": "🇩🇪  Deutsch",
        "settings.language.en": "🇬🇧  Englisch",
        "settings.consent.title": "Datenschutz-Einwilligung",
        "settings.consent.accepted": "✅  Einwilligung erteilt – anonyme Berichte werden gesendet.",
        "settings.consent.declined": "🚫  Einwilligung abgelehnt – es werden keine Daten gesendet.",
        "settings.consent.accept_btn": "Zustimmen",
        "settings.consent.decline_btn": "Ablehnen",
        "consent.title": "Datenschutz-Einstellung",
        "consent.header": "🛡️  Kurze Frage vor dem Start",
        "consent.subtitle": "Darf SecBuddy anonyme Berichte senden, um besser zu werden?",
        "consent.collected": "Was würde gesendet werden:",
        "consent.yes1": "Fehlermeldungen bei Abstürzen — damit Bugs gefunden und behoben werden können.",
        "consent.yes2": "Welches Tool geöffnet wurde (z. B. 'Fakeshop-Detector') — damit wir wissen, was nützlich ist.",
        "consent.yes3": "App-Version und Betriebssystem — für die Fehlerdiagnose.",
        "consent.no1": "Eingaben wie URLs, Passwörter oder E-Mail-Adressen — niemals.",
        "consent.no2": "Dateinamen oder Bildinhalte — niemals.",
        "consent.no3": "Standort oder IP-Adresse — wird von Sentry automatisch nicht gespeichert.",
        "consent.saved": "Deine Entscheidung wird gespeichert und nicht erneut abgefragt.",
        "consent.accept_btn": "Ja, gerne helfen  ✓",
        "consent.decline_btn": "Nein danke",
    },
    "en": {
        "settings.title": "Settings",
        "settings.subtitle": "Customize your app settings.",
        "settings.appearance.title": "Appearance",
        "settings.appearance.desc": (
            "Switch between Dark Mode and Light Mode. "
            "The change is applied immediately."
        ),
        "settings.appearance.dark": "🌙  Dark",
        "settings.appearance.light": "☀️  Light",
        "settings.appearance.system": "💻  System",
        "settings.appearance.hint.title": "ℹ️  Note on Light Mode",
        "settings.appearance.hint.body": (
            "Most buttons and fields switch color immediately. "
            "Background areas are fully updated on the next app start."
        ),
        "settings.language.title": "Language",
        "settings.language.desc": "Language change takes effect on the next app start.",
        "settings.language.de": "🇩🇪  German",
        "settings.language.en": "🇬🇧  English",
        "settings.consent.title": "Privacy Consent",
        "settings.consent.accepted": "✅  Consent given – anonymous reports are being sent.",
        "settings.consent.declined": "🚫  Consent declined – no data is being sent.",
        "settings.consent.accept_btn": "Accept",
        "settings.consent.decline_btn": "Decline",
        "consent.title": "Privacy Settings",
        "consent.header": "🛡️  Quick question before we start",
        "consent.subtitle": "May SecBuddy send anonymous reports to help improve the app?",
        "consent.collected": "What would be sent:",
        "consent.yes1": "Crash reports — so bugs can be found and fixed.",
        "consent.yes2": "Which tool was opened (e.g. 'Fakeshop Detector') — so we know what's useful.",
        "consent.yes3": "App version and operating system — for error diagnosis.",
        "consent.no1": "Inputs like URLs, passwords, or email addresses — never.",
        "consent.no2": "Filenames or image contents — never.",
        "consent.no3": "Location or IP address — not stored by Sentry.",
        "consent.saved": "Your decision is saved and will not be asked again.",
        "consent.accept_btn": "Yes, happy to help  ✓",
        "consent.decline_btn": "No thanks",
    },
}


def init() -> None:
    """Lädt die gespeicherte Sprache aus der Config."""
    lang = _cfg.get("language", "de")
    set_language(lang)


def set_language(lang: str) -> None:
    _lang[0] = lang if lang in _T else "de"


def get_language() -> str:
    return _lang[0]


def t(key: str) -> str:
    lang = _lang[0]
    return _T.get(lang, _T["de"]).get(key, _T["de"].get(key, key))