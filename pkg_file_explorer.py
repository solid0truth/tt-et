#!/usr/bin/env python3
"""
PKG File Explorer - A Windows Explorer-like GUI for managing .pkg XML files
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import shutil
from pathlib import Path
from lxml import etree
from typing import List, Optional, Dict


class PKGFileExplorer:
    def __init__(self, root):
        self.root = root
        self.root.title("PKG File Explorer")
        self.root.geometry("1200x700")

        # Clipboard for file operations
        self.clipboard: List[str] = []
        self.clipboard_operation = None  # 'copy' or 'cut'

        # Undo history for TESTSCRIPT-ID removal
        self.undo_history: List[Dict[str, str]] = []  # List of {filepath: original_content}

        # Selection anchor for Shift+Up/Down
        self.selection_anchor = None

        # Current directory
        self.current_dir = os.path.expanduser("~")

        # Setup UI
        self.setup_ui()

        # Bind keyboard shortcuts
        self.setup_shortcuts()

        # Load initial directory
        self.load_directory(self.current_dir)

    def setup_ui(self):
        """Setup the user interface"""
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Change Directory", command=self.change_directory)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Copy (Ctrl+C)", command=self.copy_files)
        edit_menu.add_command(label="Cut (Ctrl+X)", command=self.cut_files)
        edit_menu.add_command(label="Paste (Ctrl+V)", command=self.paste_files)

        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Remove <tm-info> Tag", command=self.remove_testscript_id)

        # Toolbar
        toolbar = ttk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        ttk.Label(toolbar, text="Current Directory:").pack(side=tk.LEFT, padx=5)
        self.dir_entry = ttk.Entry(toolbar)
        self.dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.dir_entry.bind("<Return>", self.on_dir_entry_return)

        ttk.Button(toolbar, text="↑ Up", command=self.navigate_up).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Browse...", command=self.change_directory).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Refresh", command=self.refresh).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Remove <tm-info>", command=self.remove_testscript_id).pack(side=tk.LEFT, padx=2)
        self.undo_button = ttk.Button(toolbar, text="↶ Undo", command=self.undo, state=tk.DISABLED)
        self.undo_button.pack(side=tk.LEFT, padx=2)

        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # File tree view
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")

        # Treeview with columns
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("filename", "testscript_id", "size", "modified"),
            show="tree headings",
            selectmode="extended",
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )

        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)

        # Configure columns
        self.tree.heading("#0", text="Type")
        self.tree.heading("filename", text="Filename")
        self.tree.heading("testscript_id", text="TESTSCRIPT-ID")
        self.tree.heading("size", text="Size")
        self.tree.heading("modified", text="Modified")

        self.tree.column("#0", width=50, minwidth=50)
        self.tree.column("filename", width=300, minwidth=200)
        self.tree.column("testscript_id", width=300, minwidth=200)
        self.tree.column("size", width=100, minwidth=80)
        self.tree.column("modified", width=150, minwidth=120)

        # Pack tree and scrollbars
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Status bar
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Context menu
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Copy", command=self.copy_files)
        self.context_menu.add_command(label="Cut", command=self.cut_files)
        self.context_menu.add_command(label="Paste", command=self.paste_files)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Remove <tm-info>", command=self.remove_testscript_id)

        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.bind("<Button-1>", self.on_single_click)

        # Bind Shift+Up/Down directly to tree to override default behavior
        self.tree.bind("<Shift-Up>", self.handle_shift_up)
        self.tree.bind("<Shift-Down>", self.handle_shift_down)

    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        self.root.bind("<Control-c>", lambda e: self.handle_copy(e))
        self.root.bind("<Control-x>", lambda e: self.handle_cut(e))
        self.root.bind("<Control-v>", lambda e: self.handle_paste(e))
        self.root.bind("<Control-z>", lambda e: self.undo())
        self.root.bind("<F5>", lambda e: self.refresh())
        self.root.bind("<BackSpace>", lambda e: self.handle_backspace(e))
        self.root.bind("<Alt-Up>", lambda e: self.navigate_up())
        self.root.bind("<Return>", lambda e: self.handle_enter(e))
        self.root.bind("<Delete>", lambda e: self.handle_delete(e))

    def handle_copy(self, event):
        """Handle Ctrl+C - only for file operations, not text editing"""
        focused = self.root.focus_get()
        if focused == self.dir_entry:
            # Let the Entry widget handle text copying
            return
        self.copy_files()

    def handle_cut(self, event):
        """Handle Ctrl+X - only for file operations, not text editing"""
        focused = self.root.focus_get()
        if focused == self.dir_entry:
            # Let the Entry widget handle text cutting
            return
        self.cut_files()

    def handle_paste(self, event):
        """Handle Ctrl+V - only for file operations, not text editing"""
        focused = self.root.focus_get()
        if focused == self.dir_entry:
            # Let the Entry widget handle text pasting
            return
        self.paste_files()

    def handle_backspace(self, event):
        """Handle Backspace - only for navigation, not text editing"""
        focused = self.root.focus_get()
        if focused == self.dir_entry:
            # Let the Entry widget handle text deletion
            return
        self.navigate_up()

    def handle_shift_up(self, event):
        """Handle Shift+Up key event and prevent default behavior"""
        self.select_previous()
        return "break"  # Prevent default treeview behavior

    def handle_shift_down(self, event):
        """Handle Shift+Down key event and prevent default behavior"""
        self.select_next()
        return "break"  # Prevent default treeview behavior

    def handle_enter(self, event):
        """Handle Enter key - navigate into selected folder"""
        # Don't interfere if directory entry has focus
        focused = self.root.focus_get()
        if focused == self.dir_entry:
            # Let the Entry widget handle Enter (navigate to typed path)
            return

        selection = self.tree.selection()
        if not selection:
            return

        # Get the first selected item
        item = selection[0]
        values = self.tree.item(item, "values")
        tags = self.tree.item(item, "tags")

        if values and values[0] == "..":
            # Navigate to parent directory
            parent_dir = os.path.dirname(self.current_dir)
            self.load_directory(parent_dir)
        elif "folder" in tags:
            # Navigate into subdirectory
            folder_name = values[0]
            folder_path = os.path.join(self.current_dir, folder_name)
            if os.path.isdir(folder_path):
                self.load_directory(folder_path)

    def handle_delete(self, event):
        """Handle Delete key - delete selected files with confirmation"""
        # Don't interfere if directory entry has focus
        focused = self.root.focus_get()
        if focused == self.dir_entry:
            # Let the Entry widget handle text deletion
            return

        files = self.get_selected_files()
        if not files:
            return

        # Show confirmation dialog
        file_count = len(files)
        if file_count == 1:
            message = f"Are you sure you want to delete:\n{os.path.basename(files[0])}?"
        else:
            message = f"Are you sure you want to delete {file_count} selected items?"

        result = messagebox.askyesno("Confirm Delete", message)

        if result:
            # Delete the files
            deleted_count = 0
            errors = []

            for file_path in files:
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        deleted_count += 1
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                        deleted_count += 1
                except Exception as e:
                    errors.append(f"{os.path.basename(file_path)}: {str(e)}")

            # Update status
            if errors:
                error_msg = "\n".join(errors)
                messagebox.showerror("Delete Errors", f"Failed to delete some items:\n{error_msg}")
                self.status_bar.config(text=f"Deleted {deleted_count} item(s), {len(errors)} failed")
            else:
                self.status_bar.config(text=f"Deleted {deleted_count} item(s)")

            # Refresh the view
            self.refresh()

    def select_previous(self):
        """Select previous item with Shift+Up (extend selection from anchor)"""
        # Don't interfere if directory entry has focus
        if self.root.focus_get() == self.dir_entry:
            return

        selection = self.tree.selection()
        all_items = self.tree.get_children()

        if not all_items:
            return

        if not selection:
            # No selection, select first item
            self.tree.selection_set(all_items[0])
            self.tree.focus(all_items[0])
            self.tree.see(all_items[0])
            self.selection_anchor = all_items[0]
            return

        # Set anchor if not already set
        if not self.selection_anchor or self.selection_anchor not in all_items:
            self.selection_anchor = selection[0]

        # Get focused item (where we currently are)
        focused_item = self.tree.focus()
        if not focused_item:
            focused_item = selection[-1]

        # Find indices
        try:
            anchor_idx = all_items.index(self.selection_anchor)
            focused_idx = all_items.index(focused_item)
        except ValueError:
            return

        # Move up one position
        new_focused_idx = max(0, focused_idx - 1)

        # Select range from anchor to new position
        start_idx = min(anchor_idx, new_focused_idx)
        end_idx = max(anchor_idx, new_focused_idx)

        # Clear selection and select the range
        self.tree.selection_set([all_items[i] for i in range(start_idx, end_idx + 1)])
        self.tree.focus(all_items[new_focused_idx])
        self.tree.see(all_items[new_focused_idx])

    def select_next(self):
        """Select next item with Shift+Down (extend selection from anchor)"""
        # Don't interfere if directory entry has focus
        if self.root.focus_get() == self.dir_entry:
            return

        selection = self.tree.selection()
        all_items = self.tree.get_children()

        if not all_items:
            return

        if not selection:
            # No selection, select first item
            self.tree.selection_set(all_items[0])
            self.tree.focus(all_items[0])
            self.tree.see(all_items[0])
            self.selection_anchor = all_items[0]
            return

        # Set anchor if not already set
        if not self.selection_anchor or self.selection_anchor not in all_items:
            self.selection_anchor = selection[0]

        # Get focused item (where we currently are)
        focused_item = self.tree.focus()
        if not focused_item:
            focused_item = selection[-1]

        # Find indices
        try:
            anchor_idx = all_items.index(self.selection_anchor)
            focused_idx = all_items.index(focused_item)
        except ValueError:
            return

        # Move down one position
        new_focused_idx = min(len(all_items) - 1, focused_idx + 1)

        # Select range from anchor to new position
        start_idx = min(anchor_idx, new_focused_idx)
        end_idx = max(anchor_idx, new_focused_idx)

        # Clear selection and select the range
        self.tree.selection_set([all_items[i] for i in range(start_idx, end_idx + 1)])
        self.tree.focus(all_items[new_focused_idx])
        self.tree.see(all_items[new_focused_idx])

    def load_directory(self, directory: str):
        """Load subdirectories and .pkg files from directory"""
        self.current_dir = directory
        # Update the entry field
        self.dir_entry.delete(0, tk.END)
        self.dir_entry.insert(0, directory)

        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Reset selection anchor since items changed
        self.selection_anchor = None

        try:
            # Add parent directory option
            if directory != "/":
                self.tree.insert("", "end", text="📁", values=("..", "", "", ""), tags=("parent",))

            # Get all items in directory
            all_items = os.listdir(directory)

            # Separate directories and .pkg files
            directories = []
            pkg_files = []

            for item in all_items:
                item_path = os.path.join(directory, item)
                if os.path.isdir(item_path):
                    directories.append(item)
                elif item.endswith('.pkg'):
                    pkg_files.append(item)

            # Sort both lists
            directories.sort()
            pkg_files.sort()

            # Add directories first
            for dirname in directories:
                dirpath = os.path.join(directory, dirname)
                try:
                    stat_info = os.stat(dirpath)
                    modified = self.format_time(stat_info.st_mtime)

                    # Count .pkg files in subdirectory
                    try:
                        pkg_count = len([f for f in os.listdir(dirpath) if f.endswith('.pkg')])
                        pkg_info = f"({pkg_count} .pkg files)" if pkg_count > 0 else ""
                    except:
                        pkg_info = ""

                    self.tree.insert(
                        "", "end",
                        text="📁",
                        values=(dirname, pkg_info, "<DIR>", modified),
                        tags=("folder",)
                    )
                except Exception as e:
                    # If error reading directory, still show it
                    self.tree.insert(
                        "", "end",
                        text="📁",
                        values=(dirname, "", "<DIR>", ""),
                        tags=("folder",)
                    )

            # Then add .pkg files
            for filename in pkg_files:
                filepath = os.path.join(directory, filename)

                try:
                    # Get file info
                    stat_info = os.stat(filepath)
                    size = self.format_size(stat_info.st_size)
                    modified = self.format_time(stat_info.st_mtime)

                    # Parse XML to get TESTSCRIPT-ID
                    testscript_id = self.extract_testscript_id(filepath)

                    # Insert into tree
                    self.tree.insert(
                        "", "end",
                        text="📄",
                        values=(filename, testscript_id, size, modified),
                        tags=("file",)
                    )
                except Exception as e:
                    # If error reading file, still show it
                    self.tree.insert(
                        "", "end",
                        text="📄",
                        values=(filename, f"Error: {str(e)}", "", ""),
                        tags=("file",)
                    )

            self.status_bar.config(text=f"Loaded {len(directories)} folders and {len(pkg_files)} .pkg files from {directory}")

            # Select first item by default
            all_items = self.tree.get_children()
            if all_items:
                first_item = all_items[0]
                self.tree.selection_set(first_item)
                self.tree.focus(first_item)
                self.tree.see(first_item)
                self.selection_anchor = first_item

        except PermissionError:
            messagebox.showerror("Error", f"Permission denied: {directory}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load directory: {str(e)}")

    def extract_testscript_id(self, filepath: str) -> str:
        """Extract TESTSCRIPT-ID from XML file"""
        try:
            tree = etree.parse(filepath)
            root = tree.getroot()

            # Find TESTSCRIPT-ID element (handle namespaces and case variations)
            # Try multiple XPath queries to handle different XML structures
            testscript_elements = root.xpath(
                "//TESTSCRIPT-ID | //*[local-name()='TESTSCRIPT-ID'] | "
                "//testscript-id | //*[local-name()='testscript-id']"
            )

            if testscript_elements:
                element = testscript_elements[0]
                return element.text if element.text else "<empty>"

            return "<not found>"
        except Exception as e:
            return f"<error: {str(e)[:30]}>"

    def format_size(self, size: int) -> str:
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    def format_time(self, timestamp: float) -> str:
        """Format timestamp"""
        from datetime import datetime
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M")

    def change_directory(self):
        """Change current directory"""
        directory = filedialog.askdirectory(initialdir=self.current_dir)
        if directory:
            self.load_directory(directory)

    def refresh(self):
        """Refresh current directory"""
        self.load_directory(self.current_dir)

    def navigate_up(self):
        """Navigate to parent directory"""
        parent_dir = os.path.dirname(self.current_dir)
        # Only navigate up if we're not at the root
        if parent_dir != self.current_dir:
            self.load_directory(parent_dir)
        else:
            self.status_bar.config(text="Already at root directory")

    def on_dir_entry_return(self, event):
        """Handle Enter key press in directory entry field"""
        directory = self.dir_entry.get().strip()

        if not directory:
            self.status_bar.config(text="Please enter a directory path")
            return

        # Expand home directory shortcut
        if directory.startswith("~"):
            directory = os.path.expanduser(directory)

        # Check if directory exists and is valid
        if os.path.isdir(directory):
            self.load_directory(directory)
        else:
            self.status_bar.config(text=f"Invalid directory: {directory}")
            # Restore current directory in entry field
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, self.current_dir)

    def on_single_click(self, event):
        """Handle single click - reset selection anchor for Shift+Up/Down"""
        # Get the clicked item
        item = self.tree.identify_row(event.y)
        if item:
            # Set this as the new anchor for shift-selection
            self.selection_anchor = item

    def on_double_click(self, event):
        """Handle double-click on tree item"""
        selection = self.tree.selection()
        if not selection:
            return

        item = selection[0]
        values = self.tree.item(item, "values")
        tags = self.tree.item(item, "tags")

        if values and values[0] == "..":
            # Navigate to parent directory
            parent_dir = os.path.dirname(self.current_dir)
            self.load_directory(parent_dir)
        elif "folder" in tags:
            # Navigate into subdirectory
            folder_name = values[0]
            folder_path = os.path.join(self.current_dir, folder_name)
            if os.path.isdir(folder_path):
                self.load_directory(folder_path)

    def show_context_menu(self, event):
        """Show context menu"""
        # Get item under cursor
        item = self.tree.identify_row(event.y)
        if item:
            # If the item is not already selected, select only this item
            # If it's already selected, keep the current multi-selection
            if item not in self.tree.selection():
                self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def get_selected_files(self) -> List[str]:
        """Get list of selected file and folder paths"""
        selected_items = self.tree.selection()
        files = []

        for item in selected_items:
            values = self.tree.item(item, "values")
            if values and values[0] != "..":
                filepath = os.path.join(self.current_dir, values[0])
                if os.path.exists(filepath):
                    files.append(filepath)

        return files

    def copy_files(self):
        """Copy selected files and folders to clipboard"""
        files = self.get_selected_files()
        if files:
            self.clipboard = files
            self.clipboard_operation = "copy"
            self.status_bar.config(text=f"Copied {len(files)} item(s)")
        else:
            messagebox.showwarning("Warning", "No items selected")

    def cut_files(self):
        """Cut selected files and folders to clipboard"""
        files = self.get_selected_files()
        if files:
            self.clipboard = files
            self.clipboard_operation = "cut"
            self.status_bar.config(text=f"Cut {len(files)} item(s)")
        else:
            messagebox.showwarning("Warning", "No items selected")

    def paste_files(self):
        """Paste files and folders from clipboard"""
        if not self.clipboard:
            messagebox.showwarning("Warning", "Clipboard is empty")
            return

        try:
            for source_file in self.clipboard:
                filename = os.path.basename(source_file)
                dest_file = os.path.join(self.current_dir, filename)

                # Handle name collision
                if os.path.exists(dest_file):
                    base, ext = os.path.splitext(filename)
                    counter = 1
                    while os.path.exists(dest_file):
                        if ext:
                            filename = f"{base}_copy{counter}{ext}"
                        else:
                            filename = f"{filename}_copy{counter}"
                        dest_file = os.path.join(self.current_dir, filename)
                        counter += 1

                if self.clipboard_operation == "copy":
                    if os.path.isdir(source_file):
                        shutil.copytree(source_file, dest_file)
                    else:
                        shutil.copy2(source_file, dest_file)
                elif self.clipboard_operation == "cut":
                    shutil.move(source_file, dest_file)

            operation = "Copied" if self.clipboard_operation == "copy" else "Moved"
            self.status_bar.config(text=f"{operation} {len(self.clipboard)} item(s)")

            # Clear clipboard if cut operation
            if self.clipboard_operation == "cut":
                self.clipboard = []
                self.clipboard_operation = None

            # Refresh view
            self.refresh()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to paste: {str(e)}")

    def remove_testscript_id(self):
        """Remove <tm-info> tag including TESTSCRIPT-ID from selected files"""
        files = self.get_selected_files()

        if not files:
            self.status_bar.config(text="No files selected")
            return

        # Filter to only .pkg files
        pkg_files = [f for f in files if os.path.isfile(f) and f.endswith('.pkg')]

        if not pkg_files:
            self.status_bar.config(text="No .pkg files selected")
            return

        # Store original content for undo
        undo_data = {}
        success_count = 0
        error_count = 0
        errors = []

        for filepath in pkg_files:
            try:
                # Read original content
                with open(filepath, 'rb') as f:
                    original_content = f.read()

                # Parse XML
                tree = etree.parse(filepath)
                root = tree.getroot()

                # Find all TM-INFO/tm-info elements (handle both uppercase and lowercase)
                tm_info_elements = root.xpath(
                    "//TM-INFO | //*[local-name()='TM-INFO'] | "
                    "//tm-info | //*[local-name()='tm-info']"
                )

                if tm_info_elements:
                    # Save original content for this file
                    undo_data[filepath] = original_content

                    for element in tm_info_elements:
                        # Remove the entire tm-info element from its parent
                        parent = element.getparent()
                        if parent is not None:
                            parent.remove(element)

                    # Write back to file
                    tree.write(
                        filepath,
                        encoding='utf-8',
                        xml_declaration=True,
                        pretty_print=True
                    )
                    success_count += 1
                else:
                    error_count += 1
                    errors.append(f"{os.path.basename(filepath)}: No <tm-info> tag found")

            except Exception as e:
                error_count += 1
                error_msg = str(e)
                errors.append(f"{os.path.basename(filepath)}: {error_msg}")
                print(f"Error processing {filepath}: {error_msg}")

        # Save undo data if we made changes
        if undo_data:
            self.undo_history.append(undo_data)
            self.undo_button.config(state=tk.NORMAL)

        # Update status bar with detailed feedback
        if success_count > 0:
            self.status_bar.config(text=f"Removed <tm-info> tag from {success_count} file(s). Press Ctrl+Z to undo.")
        elif errors:
            # Show first error in status bar
            self.status_bar.config(text=f"Failed: {errors[0]}")
            # Print all errors to console for debugging
            print("\nErrors during tm-info removal:")
            for error in errors:
                print(f"  - {error}")
        else:
            self.status_bar.config(text=f"No files to process")

        # Refresh view
        self.refresh()

    def undo(self):
        """Undo the last TESTSCRIPT-ID removal operation"""
        if not self.undo_history:
            self.status_bar.config(text="Nothing to undo")
            return

        # Get the last undo data
        undo_data = self.undo_history.pop()

        success_count = 0
        error_count = 0

        # Restore original content for each file
        for filepath, original_content in undo_data.items():
            try:
                with open(filepath, 'wb') as f:
                    f.write(original_content)
                success_count += 1
            except Exception as e:
                error_count += 1
                print(f"Error restoring {filepath}: {str(e)}")

        # Disable undo button if no more history
        if not self.undo_history:
            self.undo_button.config(state=tk.DISABLED)

        # Update status bar
        self.status_bar.config(text=f"Restored {success_count} file(s)")

        # Refresh view
        self.refresh()


def main():
    root = tk.Tk()
    app = PKGFileExplorer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
