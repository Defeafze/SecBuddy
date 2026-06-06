# -*- mode: python ; coding: utf-8 -*-
import certifi as _certifi
import os as _os
import shutil as _shutil

# Pre-copy Tcl/Tk files from WindowsApps to a local directory so PyInstaller
# can bundle them without App-Package file-access restrictions.
_tcl_base = r'C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3568.0_x64__qbz5n2kfra8p0\tcl'
_tcl_local = _os.path.join(SPECPATH, 'build', '_tcl_local')
_tk_local  = _os.path.join(SPECPATH, 'build', '_tk_local')

for _src, _dst in [
    (_os.path.join(_tcl_base, 'tcl8.6'), _tcl_local),
    (_os.path.join(_tcl_base, 'tk8.6'),  _tk_local),
]:
    if _os.path.exists(_dst):
        _shutil.rmtree(_dst)
    _shutil.copytree(_src, _dst, copy_function=_shutil.copy)

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        (_certifi.where(), 'certifi'),
        (_tcl_local, '_tcl_data'),
        (_tk_local,  '_tk_data'),
    ],
    hiddenimports=[
        'charset_normalizer',
        'charset_normalizer.md__mypyc',
        'idna',
        'sentry_sdk',
        'sentry_sdk.integrations',
        'sentry_sdk.metrics',
        'cv2.gapi',
        'cv2.mat_wrapper',
        'cv2.misc',
        'cv2.typing',
        'cv2.utils',
    ],
    hookspath=['hooks'],
    hooksconfig={},
    runtime_hooks=['runtime_hooks/fix_meipass_data.py', 'runtime_hooks/fix_certifi.py'],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='SecBuddy',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['assets\\icon.ico'],
)
