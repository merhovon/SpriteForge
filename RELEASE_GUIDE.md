# Release Guide - SpriteForge

Dieser Guide erklärt, wie Sie ein neues Release mit automatisch gebauter .exe erstellen.

## 🚀 Release erstellen (mit automatischer .exe)

### Schritt 1: Version vorbereiten

1. **Version in Code aktualisieren:**

```python
# spriteforge/__init__.py
__version__ = "1.0.1"  # Neue Version
```

2. **CHANGELOG.md aktualisieren:**

```markdown
## [1.0.1] - 2026-01-28

### Added
- Neue Feature XYZ

### Fixed
- Bug ABC behoben
```

3. **Committen:**

```bash
git add .
git commit -m "Bump version to 1.0.1"
git push origin main
```

### Schritt 2: Release auf GitHub erstellen

#### Methode A: GitHub Web Interface (Einfach)

1. Gehen Sie zu: https://github.com/merhovon/SpriteForge/releases
2. Klicken Sie **"Draft a new release"**
3. **Tag:** `v1.0.1` (wichtig: mit "v" Präfix!)
4. **Target:** `main`
5. **Title:** `SpriteForge v1.0.1`
6. **Description:** Kopieren Sie aus CHANGELOG.md

```markdown
## SpriteForge v1.0.1

### ✨ Neue Features
- Feature XYZ hinzugefügt

### 🐛 Bugfixes
- Problem ABC behoben

### 📦 Downloads

Die Windows .exe wird automatisch gebaut und in wenigen Minuten verfügbar sein.

**Installation:**
- **Windows:** Laden Sie `SpriteForge-v1.0.1-Windows.exe` herunter
- **Python/pip:** `pip install spriteforge==1.0.1`
```

7. ✅ Klicken Sie **"Publish release"**

#### Methode B: Kommandozeile (für Profis)

```bash
# Tag erstellen
git tag -a v1.0.1 -m "Release v1.0.1

- Neue Feature XYZ
- Bug ABC behoben"

# Push Tag
git push origin v1.0.1

# GitHub CLI (optional)
gh release create v1.0.1 --title "SpriteForge v1.0.1" --notes-file CHANGELOG.md
```

### Schritt 3: Automatischer Build (passiert von selbst!)

**Der GitHub Actions Workflow wird automatisch gestartet:**

1. ⏳ Windows .exe wird gebaut (ca. 5-10 Minuten)
2. ⏳ Linux Version wird gebaut (optional)
3. ⏳ macOS .app wird gebaut (optional)
4. ✅ Dateien werden automatisch zum Release hochgeladen

**Fortschritt verfolgen:**
- https://github.com/merhovon/SpriteForge/actions
- Sie sehen "Build and Release Windows Executable" Workflow laufen

### Schritt 4: Verifizieren

Nach ~5-10 Minuten:

1. Gehen Sie zurück zu: https://github.com/merhovon/SpriteForge/releases/tag/v1.0.1
2. Sie sehen jetzt:
   - ✅ `SpriteForge-v1.0.1-Windows.exe` (~30-70 MB)
   - ✅ SHA256 Checksum in der Beschreibung
   - ✅ (Optional) Linux und macOS Versionen

3. **Testen Sie die .exe:**
   - Laden Sie herunter
   - Führen Sie aus
   - Verifizieren Sie, dass sie funktioniert

## 🔧 Workflow konfigurieren

### Was wird automatisch gebaut?

Der Workflow in `.github/workflows/release-build.yml` baut:

- ✅ **Windows .exe** - Immer
- ⚠️ **Linux binary** - Optional (auskommentieren wenn nicht gewünscht)
- ⚠️ **macOS .app/.dmg** - Optional (auskommentieren wenn nicht gewünscht)

### Nur Windows bauen

Wenn Sie nur Windows wollen, löschen Sie die `build-linux` und `build-macos` Jobs:

```yaml
# Nur das behalten:
jobs:
  build-windows:
    runs-on: windows-latest
    # ... rest des Jobs
```

### Workflow manuell testen

Ohne Release zu erstellen:

1. Gehen Sie zu: https://github.com/merhovon/SpriteForge/actions
2. Wählen Sie "Build and Release Windows Executable"
3. Klicken Sie "Run workflow"
4. Wählen Sie Branch: `main`
5. ✅ "Run workflow"

Die .exe wird als Artifact gespeichert (7 Tage), nicht als Release.

## 📋 Checkliste vor Release

- [ ] Version in `spriteforge/__init__.py` aktualisiert
- [ ] `CHANGELOG.md` aktualisiert
- [ ] Code getestet lokal
- [ ] Alle Änderungen committed und gepusht
- [ ] GitHub Actions Workflow existiert (`.github/workflows/release-build.yml`)
- [ ] Release Notes vorbereitet

## 🐛 Troubleshooting

### Workflow läuft nicht

**Problem:** Release erstellt, aber kein Workflow startet

**Lösung:**
1. Prüfen Sie, ob `.github/workflows/release-build.yml` existiert
2. Prüfen Sie, ob Tag mit "v" beginnt (z.B. `v1.0.1`)
3. Gehen Sie zu Actions und suchen Sie nach Fehlern

### Build schlägt fehl

**Problem:** Workflow läuft, aber Build schlägt fehl

**Lösungen:**

1. **Dependencies fehlen:**
   ```yaml
   # In workflow prüfen:
   pip install -r requirements.txt
   ```

2. **Flet pack Fehler:**
   - Lokal testen: `flet pack spriteforge/app.py`
   - Fehlermeldung lesen in Actions Log

3. **Import Fehler:**
   ```yaml
   # Zu workflow hinzufügen:
   --hidden-import PIL
   --hidden-import numpy
   ```

### .exe ist zu groß

**Problem:** .exe ist >100 MB

**Lösungen:**

1. **UPX Kompression aktivieren:**
   ```yaml
   flet pack spriteforge/app.py --pyinstaller-build-args "--upx-dir=PATH/TO/UPX"
   ```

2. **Unnötige Pakete ausschließen:**
   ```yaml
   flet pack spriteforge/app.py --pyinstaller-build-args "--exclude-module matplotlib"
   ```

### Windows Defender blockt .exe

**Problem:** Antivirus warnt bei Download

**Das ist normal!** Lösungen:

1. **Dokumentieren Sie es** in README:
   ```markdown
   ⚠️ Windows Defender SmartScreen kann warnen, da die .exe nicht signiert ist.
   Das ist normal für neue Open-Source Software. Klicken Sie "Weitere Informationen" → "Trotzdem ausführen".
   ```

2. **Code Signing** (kostet Geld):
   - Kaufen Sie Code Signing Certificate (~100-500€/Jahr)
   - [Anleitung](https://learn.microsoft.com/windows/win32/seccrypto/cryptography-tools)

3. **Bieten Sie Alternativen:**
   - Source Code: `git clone ...`
   - Python Installation: `pip install spriteforge`

## 📊 Release-Statistiken

Nach dem Release können Sie sehen:

- 📥 Download-Zahlen: https://github.com/merhovon/SpriteForge/releases
- 📈 Traffic: https://github.com/merhovon/SpriteForge/graphs/traffic
- ⭐ Stars: https://github.com/merhovon/SpriteForge/stargazers

## 🔄 Workflow-Datei Erklärung

```yaml
on:
  release:
    types: [published]  # Startet wenn Release veröffentlicht wird
  workflow_dispatch:    # Erlaubt manuelles Starten

jobs:
  build-windows:
    runs-on: windows-latest  # Windows VM
    
    steps:
    - uses: actions/checkout@v4  # Code herunterladen
    - uses: actions/setup-python@v5  # Python installieren
    - run: pip install flet  # Dependencies installieren
    - run: flet pack ...  # .exe bauen
    - uses: softprops/action-gh-release@v1  # Zu Release hochladen
```

## 📚 Weitere Ressourcen

- [GitHub Actions Docs](https://docs.github.com/actions)
- [GitHub Releases Docs](https://docs.github.com/repositories/releasing-projects-on-github)
- [Flet Pack Docs](https://flet.dev/docs/cli/flet-pack)
- [Semantic Versioning](https://semver.org/)

---

**Wichtig:** Beim ersten Release können Sie die .exe auch manuell hochladen, falls der Workflow noch nicht konfiguriert ist. Aber mit diesem Workflow ist es ab dem zweiten Release vollautomatisch! 🎉
