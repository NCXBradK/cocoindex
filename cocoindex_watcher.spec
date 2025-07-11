# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for CocoIndex Standalone Watcher
"""

import os
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Define the application
a = Analysis(
    ['standalone_watcher.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        # Include any data files if needed
    ],
    hiddenimports=[
        'watchdog',
        'watchdog.observers',
        'watchdog.events',
        'cocoindex',
        'cocoindex.cli',
        'cocoindex._engine',
        'pkg_resources.py2_warn',
        'pkg_resources.markers',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary modules to reduce size
        'matplotlib',
        'PIL',
        'tkinter',
        'test',
        'unittest',
        'pydoc',
        'doctest',
        'difflib',
        'inspect',
        'calendar',
        'pdb',
        'bdb',
        'cmd',
        'pprint',
        'email',
        'html',
        'http',
        'urllib',
        'xml',
        'xmlrpc',
        'ctypes.test',
        'distutils',
        'lib2to3',
        'multiprocessing',
        'concurrent',
        'asyncio',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Remove duplicates
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Create the executable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='cocoindex-watcher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

# For macOS, create an app bundle
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='CocoIndex Watcher.app',
        icon=None,
        bundle_identifier='io.cocoindex.watcher',
        info_plist={
            'NSHighResolutionCapable': 'True',
            'CFBundleShortVersionString': '1.0.0',
            'CFBundleVersion': '1.0.0',
            'NSPrincipalClass': 'NSApplication',
        },
    ) 