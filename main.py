import sys
import os
import json
import tempfile
import customtkinter as ctk
from app import config
from app.utils import monitoring, consent, i18n
from app.utils import config as user_config
from app.app import SecBuddyApp

_BLUE_THEME = {
    "CTk": {"fg_color": ["gray92", "gray14"]},
    "CTkToplevel": {"fg_color": ["gray92", "gray14"]},
    "CTkFrame": {"corner_radius": 6, "border_width": 0, "fg_color": ["gray86", "gray17"], "top_fg_color": ["gray81", "gray20"], "border_color": ["gray65", "gray28"]},
    "CTkButton": {"corner_radius": 6, "border_width": 0, "fg_color": ["#3B8ED0", "#1F6AA5"], "hover_color": ["#36719F", "#144870"], "border_color": ["#3E454A", "#949A9F"], "text_color": ["#DCE4EE", "#DCE4EE"], "text_color_disabled": ["gray74", "gray60"]},
    "CTkLabel": {"corner_radius": 0, "fg_color": "transparent", "text_color": ["gray10", "#DCE4EE"]},
    "CTkEntry": {"corner_radius": 6, "border_width": 2, "fg_color": ["#F9F9FA", "#343638"], "border_color": ["#979DA2", "#565B5E"], "text_color": ["gray10", "#DCE4EE"], "placeholder_text_color": ["gray52", "gray62"]},
    "CTkCheckBox": {"corner_radius": 6, "border_width": 3, "fg_color": ["#3B8ED0", "#1F6AA5"], "border_color": ["#3E454A", "#949A9F"], "hover_color": ["#3B8ED0", "#1F6AA5"], "checkmark_color": ["#DCE4EE", "gray90"], "text_color": ["gray10", "#DCE4EE"], "text_color_disabled": ["gray60", "gray45"]},
    "CTkSwitch": {"corner_radius": 1000, "border_width": 3, "button_length": 0, "fg_color": ["#939BA2", "#4A4D50"], "progress_color": ["#3B8ED0", "#1F6AA5"], "button_color": ["gray36", "#D5D9DE"], "button_hover_color": ["gray20", "gray100"], "text_color": ["gray10", "#DCE4EE"], "text_color_disabled": ["gray60", "gray45"]},
    "CTkRadioButton": {"corner_radius": 1000, "border_width_checked": 6, "border_width_unchecked": 3, "fg_color": ["#3B8ED0", "#1F6AA5"], "border_color": ["#3E454A", "#949A9F"], "hover_color": ["#36719F", "#144870"], "text_color": ["gray10", "#DCE4EE"], "text_color_disabled": ["gray60", "gray45"]},
    "CTkProgressBar": {"corner_radius": 1000, "border_width": 0, "fg_color": ["#939BA2", "#4A4D50"], "progress_color": ["#3B8ED0", "#1F6AA5"], "border_color": ["gray", "gray"]},
    "CTkSlider": {"corner_radius": 1000, "button_corner_radius": 1000, "border_width": 6, "button_length": 0, "fg_color": ["#939BA2", "#4A4D50"], "progress_color": ["gray40", "#AAB0B5"], "button_color": ["#3B8ED0", "#1F6AA5"], "button_hover_color": ["#36719F", "#144870"]},
    "CTkOptionMenu": {"corner_radius": 6, "fg_color": ["#3B8ED0", "#1F6AA5"], "button_color": ["#36719F", "#144870"], "button_hover_color": ["#27577D", "#203A4F"], "text_color": ["#DCE4EE", "#DCE4EE"], "text_color_disabled": ["gray74", "gray60"]},
    "CTkComboBox": {"corner_radius": 6, "border_width": 2, "fg_color": ["#F9F9FA", "#343638"], "border_color": ["#979DA2", "#565B5E"], "button_color": ["#979DA2", "#565B5E"], "button_hover_color": ["#6E7174", "#7A848D"], "text_color": ["gray10", "#DCE4EE"], "text_color_disabled": ["gray50", "gray45"]},
    "CTkScrollbar": {"corner_radius": 1000, "border_spacing": 4, "fg_color": "transparent", "button_color": ["gray55", "gray41"], "button_hover_color": ["gray40", "gray53"]},
    "CTkSegmentedButton": {"corner_radius": 6, "border_width": 2, "fg_color": ["#979DA2", "gray29"], "selected_color": ["#3B8ED0", "#1F6AA5"], "selected_hover_color": ["#36719F", "#144870"], "unselected_color": ["#979DA2", "gray29"], "unselected_hover_color": ["gray70", "gray41"], "text_color": ["#DCE4EE", "#DCE4EE"], "text_color_disabled": ["gray74", "gray60"]},
    "CTkTextbox": {"corner_radius": 6, "border_width": 0, "fg_color": ["#F9F9FA", "#1D1E1E"], "border_color": ["#979DA2", "#565B5E"], "text_color": ["gray10", "#DCE4EE"], "scrollbar_button_color": ["gray55", "gray41"], "scrollbar_button_hover_color": ["gray40", "gray53"]},
    "CTkScrollableFrame": {"label_fg_color": ["gray78", "gray23"]},
    "DropdownMenu": {"fg_color": ["gray90", "gray20"], "hover_color": ["gray75", "gray28"], "text_color": ["gray10", "gray90"]},
    "CTkFont": {"macOS": {"family": "SF Display", "size": 13, "weight": "normal"}, "Windows": {"family": "Roboto", "size": 13, "weight": "normal"}, "Linux": {"family": "Roboto", "size": 13, "weight": "normal"}}
}

if __name__ == "__main__":
    i18n.init()

    saved_mode = user_config.get("appearance_mode", "Dark")
    ctk.set_appearance_mode(saved_mode)

    if getattr(sys, "frozen", False):
        import shutil as _shutil

        # Tcl/Tk aus _MEIPASS in ein stabiles Verzeichnis kopieren,
        # weil _MEIPASS-Dateien von Antivirus oder NTFS-ACLs blockiert werden können.
        _tmp = tempfile.gettempdir()
        for _src_name, _env_key, _check_file in [
            ("_tcl_data", "TCL_LIBRARY", "auto.tcl"),
            ("_tk_data",  "TK_LIBRARY",  "tk.tcl"),
        ]:
            _src = os.path.join(sys._MEIPASS, _src_name)
            _dst = os.path.join(_tmp, f"secbuddy_{_src_name}")
            if os.path.isdir(_src) and not os.path.exists(os.path.join(_dst, _check_file)):
                _shutil.copytree(_src, _dst, dirs_exist_ok=True, copy_function=_shutil.copy)
            if os.path.isdir(_dst):
                os.environ[_env_key] = _dst

        _theme_path = os.path.join(_tmp, "secbuddy_blue_theme.json")
        with open(_theme_path, "w", encoding="utf-8") as _f:
            json.dump(_BLUE_THEME, _f)
        ctk.set_default_color_theme(_theme_path)
    else:
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
