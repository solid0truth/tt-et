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
        tools_menu.add_command(label="Remove TESTSCRIPT-ID Content", command=self.remove_testscript_id)

        # Toolbar
        toolbar = ttk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        ttk.Label(toolbar, text="Current Directory:").pack(side=tk.LEFT, padx=5)
        self.dir_label = ttk.Label(toolbar, text="", relief=tk.SUNKEN)
        self.dir_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        ttk.Button(toolbar, text="Browse...", command=self.change_directory).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Refresh", command=self.refresh).pack(side=tk.LEFT, padx=5)

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
        self.context_menu.add_command(label="Remove TESTSCRIPT-ID", command=self.remove_testscript_id)

        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<Double-1>", self.on_double_click)

    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        self.root.bind("<Control-c>", lambda e: self.copy_files())
        self.root.bind("<Control-x>", lambda e: self.cut_files())
        self.root.bind("<Control-v>", lambda e: self.paste_files())
        self.root.bind("<F5>", lambda e: self.refresh())

    def load_directory(self, directory: str):
        """Load subdirectories and .pkg files from directory"""
        self.current_dir = directory
        self.dir_label.config(text=directory)

        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

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

        except PermissionError:
            messagebox.showerror("Error", f"Permission denied: {directory}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load directory: {str(e)}")

    def extract_testscript_id(self, filepath: str) -> str:
        """Extract TESTSCRIPT-ID from XML file"""
        try:
            tree = etree.parse(filepath)
            root = tree.getroot()

            # Find TESTSCRIPT-ID element (handle namespaces)
            # Try multiple XPath queries to handle different XML structures
            testscript_elements = root.xpath(
                "//TESTSCRIPT-ID | //*[local-name()='TESTSCRIPT-ID']"
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
        """Get list of selected file paths"""
        selected_items = self.tree.selection()
        files = []

        for item in selected_items:
            values = self.tree.item(item, "values")
            if values and values[0] != "..":
                filepath = os.path.join(self.current_dir, values[0])
                if os.path.isfile(filepath):
                    files.append(filepath)

        return files

    def copy_files(self):
        """Copy selected files to clipboard"""
        files = self.get_selected_files()
        if files:
            self.clipboard = files
            self.clipboard_operation = "copy"
            self.status_bar.config(text=f"Copied {len(files)} file(s)")
        else:
            messagebox.showwarning("Warning", "No files selected")

    def cut_files(self):
        """Cut selected files to clipboard"""
        files = self.get_selected_files()
        if files:
            self.clipboard = files
            self.clipboard_operation = "cut"
            self.status_bar.config(text=f"Cut {len(files)} file(s)")
        else:
            messagebox.showwarning("Warning", "No files selected")

    def paste_files(self):
        """Paste files from clipboard"""
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
                        filename = f"{base}_copy{counter}{ext}"
                        dest_file = os.path.join(self.current_dir, filename)
                        counter += 1

                if self.clipboard_operation == "copy":
                    shutil.copy2(source_file, dest_file)
                elif self.clipboard_operation == "cut":
                    shutil.move(source_file, dest_file)

            operation = "Copied" if self.clipboard_operation == "copy" else "Moved"
            self.status_bar.config(text=f"{operation} {len(self.clipboard)} file(s)")

            # Clear clipboard if cut operation
            if self.clipboard_operation == "cut":
                self.clipboard = []
                self.clipboard_operation = None

            # Refresh view
            self.refresh()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to paste files: {str(e)}")

    def remove_testscript_id(self):
        """Remove content from TESTSCRIPT-ID tags in selected files"""
        files = self.get_selected_files()

        if not files:
            messagebox.showwarning("Warning", "No files selected")
            return

        # Confirm action
        response = messagebox.askyesno(
            "Confirm",
            f"Remove TESTSCRIPT-ID content from {len(files)} file(s)?\n\n"
            "This will empty the <TESTSCRIPT-ID> tags but keep the tags themselves."
        )

        if not response:
            return

        success_count = 0
        error_count = 0

        for filepath in files:
            try:
                # Parse XML
                tree = etree.parse(filepath)
                root = tree.getroot()

                # Find all TESTSCRIPT-ID elements
                testscript_elements = root.xpath(
                    "//TESTSCRIPT-ID | //*[local-name()='TESTSCRIPT-ID']"
                )

                if testscript_elements:
                    for element in testscript_elements:
                        # Clear the text content
                        element.text = ""

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

            except Exception as e:
                error_count += 1
                print(f"Error processing {filepath}: {str(e)}")

        # Show results
        message = f"Successfully processed {success_count} file(s)"
        if error_count > 0:
            message += f"\nFailed to process {error_count} file(s)"

        messagebox.showinfo("Results", message)
        self.status_bar.config(text=f"Removed TESTSCRIPT-ID from {success_count} file(s)")

        # Refresh view
        self.refresh()


def main():
    root = tk.Tk()
    app = PKGFileExplorer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
