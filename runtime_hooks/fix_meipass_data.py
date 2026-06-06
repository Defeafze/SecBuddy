import os, sys, io, tempfile, builtins, json

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # ── sys.stdout/stderr: windowed apps have None, causing AttributeError ───
    # customtkinter's font fallback handler tries to print warnings on load failure.
    if sys.stdout is None:
        sys.stdout = io.StringIO()
    if sys.stderr is None:
        sys.stderr = io.StringIO()

    _LOREM = (
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor '
        'incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud '
        'exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure '
        'dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. '
        'Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt '
        'mollit anim id est laborum.\n'
    )

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
    _BLUE_JSON = json.dumps(_BLUE_THEME)

    _tmp = tempfile.gettempdir()

    # ── Tcl/Tk: copy to stable %TEMP% while _MEIPASS is intact ─────────────
    try:
        import shutil as _sh
        for _name, _check in [('_tcl_data', 'auto.tcl'), ('_tk_data', 'tk.tcl')]:
            _src = os.path.join(sys._MEIPASS, _name)
            _dst = os.path.join(_tmp, f'secbuddy_{_name}')
            if os.path.isdir(_src) and not os.path.exists(os.path.join(_dst, _check)):
                _sh.copytree(_src, _dst, dirs_exist_ok=True, copy_function=_sh.copy)
    except Exception:
        pass

    # ── CTK fonts: copy to stable %TEMP% ────────────────────────────────────
    _ctk_fonts_stable = os.path.join(_tmp, 'secbuddy_ctk_fonts')
    try:
        import shutil as _sh
        _ctk_fonts_src = os.path.join(sys._MEIPASS, 'customtkinter', 'assets', 'fonts')
        if os.path.isdir(_ctk_fonts_src):
            os.makedirs(_ctk_fonts_stable, exist_ok=True)
            for _ff in os.listdir(_ctk_fonts_src):
                _ff_src = os.path.join(_ctk_fonts_src, _ff)
                _ff_dst = os.path.join(_ctk_fonts_stable, _ff)
                if not os.path.exists(_ff_dst) and os.path.isfile(_ff_src):
                    _sh.copy(_ff_src, _ff_dst)
    except Exception:
        pass

    # ── os.path.isdir patch: pyi_rth__tkinter.py isdir check always passes ──
    _tcl_path = os.path.join(sys._MEIPASS, '_tcl_data')
    _tk_path  = os.path.join(sys._MEIPASS, '_tk_data')
    _fake_ok  = {_tcl_path, _tk_path}
    _orig_isdir = os.path.isdir

    def _patched_isdir(path):
        if path in _fake_ok:
            return True
        return _orig_isdir(path)

    os.path.isdir = _patched_isdir

    # ── builtins.open patch: redirect AV-quarantined files to stable copies ─
    _orig_open = builtins.open

    def _patched_open(file, mode='r', *args, **kwargs):
        try:
            return _orig_open(file, mode, *args, **kwargs)
        except (FileNotFoundError, PermissionError, OSError):
            try:
                _fp = str(file) if not isinstance(file, int) else ''
                _m  = str(mode)
                if 'w' not in _m and 'a' not in _m:
                    if _fp.endswith('blue.json'):
                        return io.StringIO(_BLUE_JSON)
                    if _fp.endswith('Lorem ipsum.txt'):
                        return io.StringIO(_LOREM)
                    if _fp.lower().endswith(('.ttf', '.otf')):
                        _stable = os.path.join(_ctk_fonts_stable, os.path.basename(_fp))
                        if os.path.exists(_stable):
                            return _orig_open(_stable, mode, *args, **kwargs)
            except Exception:
                pass
            raise

    builtins.open = _patched_open

    # ── pathlib patch: belt-and-suspenders for Lorem ipsum.txt ──────────────
    try:
        from pathlib import Path as _Path
        _orig_read_text = _Path.read_text

        def _patched_read_text(self, *args, **kwargs):
            try:
                return _orig_read_text(self, *args, **kwargs)
            except FileNotFoundError:
                if self.name == 'Lorem ipsum.txt':
                    return _LOREM
                raise

        _Path.read_text = _patched_read_text
    except Exception:
        pass
