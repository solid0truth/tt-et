# PKG File Explorer

A Windows Explorer-like Python application for managing and processing XML-based `.pkg` files.

## Features

- **File Explorer Interface**: Browse directories with subfolder navigation
- **Subfolder Support**: View and navigate through folder hierarchies, with .pkg file counts shown for each folder
- **TESTSCRIPT-ID Display**: Automatically extracts and displays `<TESTSCRIPT-ID>` values from XML files
- **Remove TESTSCRIPT-ID Content**: Batch operation to clear content from `<TESTSCRIPT-ID>` tags
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

5. **Remove TESTSCRIPT-ID Content**:
   - Select one or more `.pkg` files
   - Click the "Remove TESTSCRIPT-ID" toolbar button, or
   - Use Tools menu → Remove TESTSCRIPT-ID Content, or
   - Right-click → Remove TESTSCRIPT-ID
   - Confirm the operation
   - The content inside `<TESTSCRIPT-ID>` tags will be cleared (tags remain)

### Keyboard Shortcuts

- `Ctrl+C`: Copy selected files
- `Ctrl+X`: Cut selected files
- `Ctrl+V`: Paste files
- `F5`: Refresh current directory
- `Backspace` or `Alt+Up`: Navigate to parent directory

### Toolbar Buttons

- **↑ Up**: Navigate to parent directory
- **Browse...**: Open directory browser to select a different folder
- **Refresh**: Reload the current directory contents
- **Remove TESTSCRIPT-ID**: Clear TESTSCRIPT-ID content from selected files

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
5. Test the remove TESTSCRIPT-ID feature on one or more files
6. Test copy/cut/paste operations across different folders

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

The application expects `.pkg` files with XML structure containing a `<TESTSCRIPT-ID>` element:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<TestPackage xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <TESTSCRIPT-ID xsi:type="string">TS-2024-001</TESTSCRIPT-ID>
    <!-- Other elements -->
</TestPackage>
```

### Remove TESTSCRIPT-ID Operation

When you use the "Remove TESTSCRIPT-ID Content" feature:
- The application finds all `<TESTSCRIPT-ID>` tags in selected files
- Clears the text content (sets to empty string)
- Preserves the XML tags and attributes
- Writes the modified XML back to the file

**Before:**
```xml
<TESTSCRIPT-ID xsi:type="string">TS-2024-001</TESTSCRIPT-ID>
```

**After:**
```xml
<TESTSCRIPT-ID xsi:type="string"></TESTSCRIPT-ID>
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
