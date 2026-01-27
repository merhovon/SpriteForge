# Building Windows Executable (.exe)

Dieses Dokument beschreibt, wie Sie eine eigenständige Windows-Executable für SpriteForge erstellen und auf GitHub bereitstellen können.

## ⭐ Option 1: `flet pack` (EMPFOHLEN!)

**Flet hat einen eingebauten Befehl, der PyInstaller unter der Haube verwendet** - am einfachsten!

### Einfachste Methode

```bash
# Minimale Version
flet pack spriteforge/app.py

# Mit allen Options
flet pack spriteforge/app.py \
  --name SpriteForge \
  --icon assets/icon.ico \
  --product-name "SpriteForge" \
  --product-version "1.0.0" \
  --file-description "Forge your sprites with precision" \
  --company-name "merhovon"
```

**Vorteile:**
- ✅ Automatische Flet-Konfiguration
- ✅ Alle benötigten hiddenimports automatisch
- ✅ Keine manuelle .spec-Datei nötig
- ✅ Getestet und offiziell unterstützt
- ✅ Cross-Platform (Windows, macOS, Linux)

### Wichtige flet pack Optionen

```bash
--name              # Name der .exe Datei
--icon              # Icon-Datei (.ico für Windows)
--onedir / -D       # Ordner statt einzelne Datei (schnellerer Start)
--product-name      # Anzeigename in Windows
--product-version   # Version (z.B. "1.0.0")
--file-description  # Beschreibung in Datei-Eigenschaften
--company-name      # Firmenname
--copyright         # Copyright-Text
--uac-admin         # Admin-Rechte erforderlich
--debug-console     # Console für Debugging anzeigen
--add-data          # Zusätzliche Dateien hinzufügen
--hidden-import     # Zusätzliche Python-Module
```

### Ausgabe

Die .exe befindet sich in `dist/SpriteForge.exe`

## Option 2: `flet build windows`

Noch einfacher - ein Befehl für alles:

```bash
flet build windows
```

Baut die App mit optimalen Einstellungen für Windows.

## Option 3: PyInstaller direkt

Wenn Sie mehr Kontrolle brauchen oder `flet pack` nicht funktioniert:

PyInstaller erstellt eigenständige Executables mit allen Abhängigkeiten.

### Installation

```bash
pip install pyinstaller
```

### Erstellen der .exe

#### Einzelne Datei (empfohlen für Distribution)

```bash
pyinstaller --onefile --windowed --name SpriteForge --icon=assets/icon.ico spriteforge/app.py
```

#### Mit sichtbarem Console-Window (für Debugging)

```bash
pyinstaller --onefile --name SpriteForge --icon=assets/icon.ico spriteforge/app.py
```

#### Mit separatem Ordner (schnellerer Start)

```bash
pyinstaller --onedir --windowed --name SpriteForge --icon=assets/icon.ico spriteforge/app.py
```

### PyInstaller Parameter

- `--onefile`: Erstellt eine einzelne .exe Datei
- `--onedir`: Erstellt einen Ordner mit .exe und Abhängigkeiten (schnellerer Start)
- `--windowed` / `-w`: Kein Console-Fenster (für GUI-Apps)
- `--name`: Name der Executable
- `--icon`: Icon-Datei (.ico)
- `--add-data`: Zusätzliche Dateien hinzufügen

### Erweiterte Konfiguration (.spec Datei)

Für komplexere Builds erstellen Sie eine .spec Datei:

```bash
pyinstaller --onefile --windowed --name SpriteForge spriteforge/app.py
# Bearbeiten Sie die generierte SpriteForge.spec Datei
pyinstaller SpriteForge.spec
```

Beispiel `SpriteForge.spec`:

```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['spriteforge/app.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['flet', 'numpy', 'PIL'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SpriteForge',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico'
)
```

## Option 2: cx_Freeze

Alternative zu PyInstaller, besonders gut für komplexe Projekte.

### Installation

```bash
pip install cx_Freeze
```

### Erstellen Sie setup.py für cx_Freeze

```python
from cx_Freeze import setup, Executable
import sys

# GUI-Anwendung (kein Console-Fenster)
base = "Win32GUI" if sys.platform == "win32" else None

build_exe_options = {
    "packages": ["flet", "numpy", "PIL"],
    "excludes": [],
    "include_files": []
}

setup(
    name="SpriteForge",
    version="1.0.0",
    description="Forge your sprites with precision",
    options={"build_exe": build_exe_options},
    executables=[Executable(
        "spriteforge/app.py",
        base=base,
        target_name="SpriteForge.exe",
        icon="assets/icon.ico"
    )]
)
```

### Build ausführen

```bash
python setup.py build
```

Die Executable befindet sich in `build/exe.win-amd64-3.10/`

## Option 3: Nuitka

Kompiliert Python-Code zu nativen Binaries (beste Performance).

```bash
pip install nuitka
```

```bash
python -m nuitka --onefile --windows-disable-console --enable-plugin=numpy --output-dir=dist spriteforge/app.py
```

## Icon erstellen

Erstellen Sie ein Icon für Ihre Anwendung:

1. Erstellen Sie ein PNG (256x256 oder 512x512)
2. Konvertieren Sie zu .ico:
   - Online: https://convertio.co/de/png-ico/
   - Oder mit Pillow:

```python
from PIL import Image
img = Image.open('logo.png')
img.save('icon.ico', format='ICO', sizes=[(256, 256)])
```

## Testen der Executable

```bash
# Führen Sie die .exe aus
dist/SpriteForge.exe

# Testen Sie mit einem Bild
dist/SpriteForge.exe path/to/image.png
```

## Verkleinern der Dateigröße

### UPX Kompression

```bash
# PyInstaller mit UPX
pyinstaller --onefile --windowed --upx-dir=C:\path\to\upx --name SpriteForge spriteforge/app.py
```

Download UPX: https://upx.github.io/

### Unnötige Pakete ausschließen

```bash
pyinstaller --onefile --windowed --exclude-module matplotlib --exclude-module scipy --name SpriteForge spriteforge/app.py
```

## GitHub Release erstellen

### 1. Build die Executable

```bash
pyinstaller --onefile --windowed --name SpriteForge-Windows spriteforge/app.py
```

### 2. Erstellen Sie ein Release auf GitHub

```bash
# Tag erstellen
git tag -a v1.0.0 -m "Version 1.0.0"
git push origin v1.0.0
```

### 3. Upload auf GitHub

1. Gehen Sie zu: https://github.com/merhovon/SpriteForge/releases
2. Klicken Sie "Draft a new release"
3. Wählen Sie Tag: v1.0.0
4. Titel: "SpriteForge v1.0.0"
5. **Upload der .exe**:
   - Ziehen Sie `dist/SpriteForge-Windows.exe` in den Assets-Bereich
   - Oder klicken Sie "Attach binaries"
6. Fügen Sie Release-Notes hinzu:

```markdown
## SpriteForge v1.0.0

### Downloads

**Windows:**
- 📦 [SpriteForge-Windows.exe](link) - Standalone executable, keine Installation nötig

**Alle Plattformen:**
- 🐍 `pip install spriteforge` - Installation via pip

### Neue Features
- Sprite-Extraktion mit moderner GUI
- Einzigartige Farb-Erkennung
- Transparente Sprite-Generierung
- Cross-Platform Support

### System Requirements
- Windows 10 oder höher
- Keine Python-Installation nötig (für .exe)
```

### 4. Automatisches Build mit GitHub Actions (mit flet pack)

Erstellen Sie `.github/workflows/build-exe.yml`:

```yaml
name: Build Windows Executable

on:
  release:
    types: [created]
  workflow_dispatch:

jobs:
  build:
    runs-on: windows-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install flet
    
    - name: Build executable with flet pack
      run: |
        flet pack spriteforge/app.py --name SpriteForge-v${{ github.ref_name }} --icon assets/icon.ico --product-version "1.0.0"
    
    - name: Upload artifact
      uses: actions/upload-artifact@v3
      with:
        name: SpriteForge-Windows
        path: dist/SpriteForge-*.exe
    
    - name: Upload to Release
      if: github.event_name == 'release'
      uses: softprops/action-gh-release@v1
      with:
        files: dist/SpriteForge-*.exe
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Troubleshooting

### Flet Import Fehler

Wenn Flet nicht gefunden wird, fügen Sie zu .spec hinzu:

```python
hiddenimports=['flet', 'flet.core', 'flet.utils'],
```

### NumPy Fehler

```python
hiddenimports=['numpy', 'numpy.core._dtype_ctypes'],
```

### "VCRUNTIME140.dll fehlt"

Benutzer müssen Visual C++ Redistributable installieren:
- Download: https://learn.microsoft.com/cpp/windows/latest-supported-vc-redist

Oder binden Sie die DLL ein:

```bash
pyinstaller --onefile --windowed --add-binary "C:\Windows\System32\vcruntime140.dll;." spriteforge/app.py
```

### Antivirensoftware blockt .exe

Das ist normal für neue .exe Dateien. Lösungen:

1. **Code Signing Certificate** kaufen (ca. 100-500€/Jahr)
2. **Dokumentieren Sie es** in der README
3. Benutzer können Source-Code verwenden: `pip install spriteforge`

## Best Practices

1. ✅ **Testen Sie die .exe** auf einem sauberen Windows-System ohne Python
2. ✅ **Dateigröße prüfen** - sollte unter 50-100 MB sein
3. ✅ **Virustotal.com** - Scannen Sie die Datei vor der Veröffentlichung
4. ✅ **Changelog** - Dokumentieren Sie Änderungen in jeder Version
5. ✅ **SHA256 Checksums** - Fügen Sie Checksums zum Release hinzu:

```bash
# Windows PowerShell
Get-FileHash dist/SpriteForge-Windows.exe -Algorithm SHA256
```

6. ✅ **Mehrere Formate** - Bieten Sie .exe und pip an
7. ✅ **Automatisches Testen** - CI/CD für jeden Build

## Zusammenfassung

**Schnellstart mit flet pack (EMPFOHLEN):**
```bash
# 1. Flet installieren (falls noch nicht)
pip install flet

# 2. Executable bauen mit flet pack
flet pack spriteforge/app.py --name SpriteForge --icon assets/icon.ico

# 3. Testen
dist/SpriteForge.exe

# 4. Auf GitHub hochladen als Release Asset
```

**Alternative mit PyInstaller direkt:**
```bash
# 1. PyInstaller installieren
pip install pyinstaller

# 2. Executable bauen
pyinstaller --onefile --windowed --name SpriteForge spriteforge/app.py

# 3. Testen
dist/SpriteForge.exe
```

**Empfohlene Workflow:**
- Entwickeln mit `python -m spriteforge.app`
- Für Releases: `flet pack` oder GitHub Actions (automatisch)
- Beide Distributionsmethoden anbieten: .exe UND pip

## Ressourcen

- **Flet Pack Docs**: https://flet.dev/docs/cli/flet-pack (OFFIZIELLE Methode!)
- Flet Build: https://flet.dev/docs/publish
- PyInstaller Docs: https://pyinstaller.org/
- cx_Freeze: https://cx-freeze.readthedocs.io/
- Nuitka: https://nuitka.net/
- GitHub Actions: https://docs.github.com/actions
- Code Signing: https://learn.microsoft.com/windows/win32/seccrypto/cryptography-tools

---

**Hinweis:** Die .exe-Datei ist ca. 30-70 MB groß, da alle Python-Bibliotheken eingebettet sind. Das ist normal für Python GUI-Anwendungen.
