# Building Windows Executable

This guide explains how to create a standalone Windows executable (.exe) for the PKG File Explorer application.

## Prerequisites

- Python 3.7 or higher installed on Windows
- All dependencies installed (`pip install -r requirements.txt`)

## Quick Build

### Method 1: Using the Build Script (Recommended)

```bash
# Install PyInstaller
pip install pyinstaller

# Run the build script
python build_windows.py
```

The executable will be created at: `dist/PKGFileExplorer.exe`

### Method 2: Manual PyInstaller Command

```bash
# Install PyInstaller
pip install pyinstaller

# Build single-file executable
pyinstaller --onefile --windowed --name=PKGFileExplorer --hidden-import=lxml.etree --hidden-import=lxml._elementpath pkg_file_explorer.py
```

## Build Options

### Single File Executable (Recommended for Distribution)

**Pros:**
- Single .exe file - easy to distribute
- No installation required
- Users don't need Python installed

**Cons:**
- Slower startup (extracts to temp folder)
- Larger file size (~15-30 MB)

**Command:**
```bash
pyinstaller --onefile --windowed --name=PKGFileExplorer --hidden-import=lxml.etree pkg_file_explorer.py
```

### Directory Distribution (Faster Startup)

**Pros:**
- Faster startup time
- Easier to debug

**Cons:**
- Multiple files in a folder
- Less convenient to distribute

**Command:**
```bash
pyinstaller --onedir --windowed --name=PKGFileExplorer --hidden-import=lxml.etree pkg_file_explorer.py
```

## PyInstaller Flags Explained

- `--onefile`: Package everything into a single .exe file
- `--onedir`: Package into a directory with dependencies
- `--windowed`: Don't show console window (GUI application)
- `--name=PKGFileExplorer`: Name of the output executable
- `--hidden-import=lxml.etree`: Include lxml XML library
- `--clean`: Clean PyInstaller cache before building
- `--icon=icon.ico`: Add custom icon (optional, if you have one)

## Build Output

After building, you'll find:

```
dist/
├── PKGFileExplorer.exe          # Your standalone executable
build/                             # Build files (can be deleted)
PKGFileExplorer.spec              # PyInstaller spec file
```

## Distribution

To distribute your application:

1. **Single File Method:**
   - Copy `dist/PKGFileExplorer.exe` to any location
   - Users can run it directly without Python installed
   - No installation needed

2. **Directory Method:**
   - Zip the entire `dist/PKGFileExplorer/` folder
   - Users extract and run `PKGFileExplorer.exe`

## Adding an Icon (Optional)

1. Create or download a `.ico` file
2. Place it in the project directory (e.g., `icon.ico`)
3. Add to build command:
   ```bash
   pyinstaller --onefile --windowed --icon=icon.ico --name=PKGFileExplorer pkg_file_explorer.py
   ```

## Troubleshooting

### Missing Module Errors

If you get "module not found" errors when running the .exe:

```bash
pyinstaller --onefile --windowed --hidden-import=MODULE_NAME pkg_file_explorer.py
```

Replace `MODULE_NAME` with the missing module.

### Antivirus False Positives

PyInstaller executables sometimes trigger antivirus false positives. This is normal for:
- Newly created executables
- Unsigned executables

**Solutions:**
1. Add exception in antivirus software
2. Code sign the executable (requires certificate)
3. Submit to antivirus vendors as false positive

### Console Window Appears

If a console window appears behind your GUI:

```bash
# Use --windowed flag (already included)
pyinstaller --onefile --windowed pkg_file_explorer.py
```

### Large File Size

PyInstaller bundles Python and all dependencies. Typical size: 15-30 MB.

**To reduce size:**
1. Use `--onedir` instead of `--onefile`
2. Exclude unnecessary modules:
   ```bash
   pyinstaller --onefile --windowed --exclude-module=MODULE_NAME pkg_file_explorer.py
   ```
3. Use UPX compression (advanced):
   ```bash
   pyinstaller --onefile --windowed --upx-dir=PATH_TO_UPX pkg_file_explorer.py
   ```

## Advanced: Custom .spec File

For more control, edit `PKGFileExplorer.spec` after first build:

```python
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['pkg_file_explorer.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['lxml.etree', 'lxml._elementpath'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='PKGFileExplorer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # False = no console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
```

Then build with:
```bash
pyinstaller PKGFileExplorer.spec
```

## Testing the Executable

1. Navigate to `dist/` folder
2. Double-click `PKGFileExplorer.exe`
3. Test all features:
   - Directory navigation
   - File selection
   - TESTSCRIPT-ID removal
   - Undo functionality
   - Copy/paste operations

## Clean Build

To perform a clean build:

```bash
# Delete build artifacts
rmdir /s /q build dist
del PKGFileExplorer.spec

# Rebuild
python build_windows.py
```

## System Requirements for Executable

The generated .exe will run on:
- Windows 7 and later
- No Python installation required
- No additional dependencies required

## File Size Reference

Typical file sizes:
- Single .exe: 15-30 MB
- Directory distribution: 20-40 MB (spread across multiple files)

## Version Information

To add version information to the executable:

1. Create `version.txt`:
   ```
   VSVersionInfo(
     ffi=FixedFileInfo(
       filevers=(1, 0, 0, 0),
       prodvers=(1, 0, 0, 0),
       mask=0x3f,
       flags=0x0,
       OS=0x40004,
       fileType=0x1,
       subtype=0x0,
       date=(0, 0)
     ),
     kids=[
       StringFileInfo([
         StringTable(
           u'040904B0',
           [StringStruct(u'CompanyName', u'Your Company'),
           StringStruct(u'FileDescription', u'PKG File Explorer'),
           StringStruct(u'FileVersion', u'1.0.0.0'),
           StringStruct(u'ProductName', u'PKG File Explorer'),
           StringStruct(u'ProductVersion', u'1.0.0.0')])
       ]),
       VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
     ]
   )
   ```

2. Build with version info:
   ```bash
   pyinstaller --onefile --windowed --version-file=version.txt pkg_file_explorer.py
   ```
