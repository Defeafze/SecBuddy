import customtkinter as ctk
from app import config
from app.utils import monitoring, consent
from app.app import SecBuddyApp

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    app = SecBuddyApp()

    # Einwilligung beim ersten Start abfragen
    if not consent.has_decided():
        accepted = consent.show_dialog(app)
        consent.save(accepted)

    # Sentry nur starten wenn zugestimmt wurde
    if consent.is_accepted():
        monitoring.init(config.SENTRY_DSN, config.APP_VERSION)

    app.mainloop()
