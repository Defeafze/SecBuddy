import sys
import customtkinter as ctk
from app import config
from app.utils import monitoring, consent, i18n
from app.utils import config as user_config
from app.app import SecBuddyApp

if __name__ == "__main__":
    i18n.init()
    
    saved_mode = user_config.get("appearance_mode", "Dark")
    ctk.set_appearance_mode(saved_mode)
    ctk.set_default_color_theme("blue")

    app = SecBuddyApp()
    app.update()  # Fenster vollständig aufbauen bevor Dialog positioniert wird

    # Einwilligung abfragen wenn nicht bereits akzeptiert
    if not consent.is_accepted():
        accepted = consent.show_dialog(app)
        if accepted:
            consent.save(True)
        else:
            app.destroy()
            sys.exit(0)

    # Sentry starten
    if consent.is_accepted():
        monitoring.init(config.SENTRY_DSN, config.APP_VERSION)

    app.mainloop()
