# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('app/ui/imgs', 'app/ui/imgs'), ('app/data', 'app/data'), ('app/data/docs', 'app/data/docs'), ('app/assinaturas', 'app/assinaturas'), ('app/data/docs/comprovantes', 'app/data/docs/comprovantes')]
binaries = []
hiddenimports = ['ui.ContasUI', 'ui.ControleInventarioUI', 'ui.InventarioUI', 'ui.HistoricoUI', 'ui.ReverterUI', 'ui.DashBoardUI', 'ui.GerenciarFuncionarioUi', 'ui.ControleFunc', 'data.Inventario', 'data.docs.ComprovarCadastro', 'reportlab', 'matplotlib', 'pillow', 'sqlalchemy', 'sqlalchemy.dialects.sqlite', 'PySide6.QtCore', 'PySide6.QtWidgets', 'bcrypt', 'PySide6.QtGui', 'numpy', 'numpy.core', 'numpy.core._multiarray_umath']
tmp_ret = collect_all('numpy')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['app\\ui\\main.py'],
    pathex=['.', 'app'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tensorflow'],
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
