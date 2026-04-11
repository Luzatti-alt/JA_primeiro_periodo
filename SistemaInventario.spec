# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app\\ui\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('app/ui/imgs', 'app/ui/imgs'), ('app/data', 'app/data')],
    hiddenimports=['sqlalchemy', 'sqlalchemy.dialects.sqlite', 'pyside6', 'PySide6.QtCore', 'PySide6.QtWidgets', 'PySide6.QtGui'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SistemaInventario',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['app\\ui\\imgs\\ideia_de_logo_app_JA.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SistemaInventario',
)
