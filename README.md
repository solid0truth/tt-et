# PKG File Explorer

A Windows Explorer-like Python application for managing and processing XML-based `.pkg` files.

## Features

- **File Explorer Interface**: Browse directories with subfolder navigation
- **Editable Directory Path**: Paste or type directory paths directly in the address bar and press Enter
- **Subfolder Support**: View and navigate through folder hierarchies, with .pkg file counts shown for each folder
- **TESTSCRIPT-ID Display**: Automatically extracts and displays `<TESTSCRIPT-ID>` values from XML files
- **Remove tm-info Tag**: Instant batch operation to remove entire `<tm-info>` tag including `<TESTSCRIPT-ID>` (no confirmation required)
- **Undo Support**: Full undo capability with Ctrl+Z to restore files after removal operations
- **File Operations**: Copy, cut, and paste files with keyboard shortcuts
- **Clean GUI**: Built with tkinter for cross-platform compatibility

## Requirements

- Python 3.7 or higher
- Dependencies listed in `requirements.txt`

## Installation

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Building Windows Executable

To create a standalone .exe file that runs without Python installed:

### Quick Build

```bash
# Install PyInstaller
pip install pyinstaller

# Run the build script
python build_windows.py
```

The executable will be created at `dist/PKGFileExplorer.exe`

### Manual Build

```bash
pyinstaller --onefile --windowed --name=PKGFileExplorer --hidden-import=lxml.etree pkg_file_explorer.py
```

For detailed build instructions, troubleshooting, and advanced options, see [BUILD.md](BUILD.md).

### Distribution

Simply copy `dist/PKGFileExplorer.exe` to any Windows computer and run it - no Python installation required!

## Usage

### Running the Application

```bash
python pkg_file_explorer.py
```

Or make it executable:
```bash
chmod +x pkg_file_explorer.py
./pkg_file_explorer.py
```

### Using the Application

1. **Browse Directories**:
   - **Paste path directly**: Edit the "Current Directory" field and press Enter to navigate to a path
   - Click "Browse..." button to select a directory containing `.pkg` files
   - Click "↑ Up" button or press Backspace/Alt+Up to navigate to parent directory
   - Double-click ".." to navigate to parent directory
   - Double-click any folder to navigate into it

2. **View Files and Folders**:
   - Folders are shown first with a 📁 icon and the count of .pkg files they contain
   - .pkg files are shown below folders with a 📄 icon
   - The "TESTSCRIPT-ID" column displays the value from each file's XML
   - The status bar shows the count of folders and .pkg files in the current directory

3. **Select Files**:
   - Click to select a single file
   - Ctrl+Click to select multiple files
   - Shift+Click to select a range of files

4. **File Operations**:
   - **Copy**: Select files and press `Ctrl+C` or use Edit menu
   - **Cut**: Select files and press `Ctrl+X` or use Edit menu
   - **Paste**: Navigate to destination and press `Ctrl+V` or use Edit menu

5. **Remove tm-info Tag**:
   - Select one or more `.pkg` files
   - Click the "Remove <tm-info>" toolbar button, or
   - Use Tools menu → Remove <tm-info> Tag, or
   - Right-click → Remove <tm-info>
   - The entire `<tm-info>` tag (including `<TESTSCRIPT-ID>`) will be removed instantly
   - Press `Ctrl+Z` or click "↶ Undo" to restore if needed

### Keyboard Shortcuts

- `Ctrl+C`: Copy selected files
- `Ctrl+X`: Cut selected files
- `Ctrl+V`: Paste files
- `Ctrl+Z`: Undo last tm-info tag removal
- `F5`: Refresh current directory
- `Backspace` or `Alt+Up`: Navigate to parent directory

### Toolbar Buttons

- **↑ Up**: Navigate to parent directory
- **Browse...**: Open directory browser to select a different folder
- **Refresh**: Reload the current directory contents
- **Remove <tm-info>**: Remove entire tm-info tag from selected files (instant, no confirmation)
- **↶ Undo**: Restore files from the last tm-info tag removal operation

### Undo Feature

The application includes a powerful undo system for tm-info tag removal operations:

- **No confirmation dialogs**: Remove operations execute instantly for faster workflow
- **Automatic backup**: Original file content is automatically saved before modification
- **Easy restoration**: Press `Ctrl+Z` or click the "↶ Undo" button to restore files
- **Status feedback**: The status bar shows operation results and reminds you about undo availability
- **Multiple operations**: The undo button remains enabled as long as there are operations to undo

**How it works:**
1. Select files and click "Remove <tm-info>"
2. Changes are applied instantly, original content is saved
3. Status bar shows: "Removed <tm-info> tag from X file(s). Press Ctrl+Z to undo."
4. Press `Ctrl+Z` or click "↶ Undo" to restore the original content
5. The undo button becomes disabled when there's nothing left to undo

## Testing

Sample `.pkg` files are provided in the `sample_pkg_files/` directory for testing:

**Root level:**
- `test_script_1.pkg` - Basic test package with TESTSCRIPT-ID: TS-2024-001
- `test_script_2.pkg` - Test package with TESTSCRIPT-ID: TS-2024-002
- `test_script_3.pkg` - Test package with TESTSCRIPT-ID: TS-2024-003
- `empty_testscript.pkg` - Package with empty TESTSCRIPT-ID

**Subfolders:**
- `subfolder1/test_sub1.pkg` - Test package with TESTSCRIPT-ID: TS-SUB1-001
- `subfolder2/test_sub2.pkg` - Test package with TESTSCRIPT-ID: TS-SUB2-001
- `subfolder2/nested/test_nested.pkg` - Test package with TESTSCRIPT-ID: TS-NESTED-001

To test the application:
1. Run the application
2. Browse to the `sample_pkg_files/` directory
3. View the TESTSCRIPT-ID values in the file list
4. Double-click on folders to navigate into subfolders
5. Test the remove tm-info tag feature on one or more files (instant, no confirmation)
6. Test the undo feature by pressing Ctrl+Z or clicking the "↶ Undo" button
7. Test copy/cut/paste operations across different folders

## File Structure

```
.
├── pkg_file_explorer.py    # Main application
├── requirements.txt         # Python dependencies
├── README.md               # This file
└── sample_pkg_files/       # Sample .pkg files for testing
    ├── test_script_1.pkg
    ├── test_script_2.pkg
    ├── test_script_3.pkg
    ├── empty_testscript.pkg
    ├── subfolder1/
    │   └── test_sub1.pkg
    └── subfolder2/
        ├── test_sub2.pkg
        └── nested/
            └── test_nested.pkg
```

## Technical Details

### XML Structure

The application expects `.pkg` files with XML structure containing a `<tm-info>` tag with nested `<TESTSCRIPT-ID>` element:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<TestPackage xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <tm-info>
        <TESTSCRIPT-ID xsi:type="string">TS-2024-001</TESTSCRIPT-ID>
    </tm-info>
    <!-- Other elements -->
</TestPackage>
```

### Remove tm-info Tag Operation

When you use the "Remove <tm-info>" feature:
- The application finds all `<tm-info>` tags in selected files
- Removes the entire tag including all nested elements (like `<TESTSCRIPT-ID>`)
- Preserves all other XML structure
- Writes the modified XML back to the file

**Before:**
```xml
<TestPackage>
    <tm-info>
        <TESTSCRIPT-ID xsi:type="string">TS-2024-001</TESTSCRIPT-ID>
    </tm-info>
    <Name>Sample Test</Name>
</TestPackage>
```

**After:**
```xml
<TestPackage>
    <Name>Sample Test</Name>
</TestPackage>
```

## Dependencies

- **lxml**: XML parsing and manipulation library

## Troubleshooting

### "No files found"
- Make sure you're browsing a directory that contains `.pkg` files
- The application only shows files with the `.pkg` extension

### "Permission denied"
- Ensure you have read/write permissions for the directory and files
- Try running from a directory where you have full permissions

### "Error parsing XML"
- Check that your `.pkg` files are valid XML
- The TESTSCRIPT-ID column will show an error message for malformed files

## License

This project is provided as-is for managing XML-based `.pkg` test script files.

## Future Enhancements

Potential features for future versions:
- Drag and drop file support
- Search/filter functionality
- Bulk rename operations
- Export file list to CSV
- Preview XML content in a panel
- Undo/redo for remove operations
