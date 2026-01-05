#!/usr/bin/env python3
"""
Build script for creating Windows executable using PyInstaller

Usage:
    python build_windows.py

Output:
    - dist/PKGFileExplorer.exe (single file executable)
    - dist/PKGFileExplorer/ (directory with all dependencies)
"""

import os
import sys
import subprocess
import shutil


def build_executable():
    """Build Windows executable using PyInstaller"""

    print("=" * 60)
    print("Building PKG File Explorer Windows Executable")
    print("=" * 60)

    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print(f"✓ PyInstaller {PyInstaller.__version__} found")
    except ImportError:
        print("✗ PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller installed")

    # Clean previous builds
    if os.path.exists("build"):
        print("Cleaning build directory...")
        shutil.rmtree("build")
    if os.path.exists("dist"):
        print("Cleaning dist directory...")
        shutil.rmtree("dist")

    # PyInstaller command
    # --onefile: Create a single executable file
    # --windowed: Don't show console window (GUI app)
    # --name: Name of the executable
    # --icon: Application icon (optional, add if you have one)
    # --clean: Clean PyInstaller cache

    pyinstaller_args = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=PKGFileExplorer",
        "--clean",
        # Add hidden imports for lxml
        "--hidden-import=lxml.etree",
        "--hidden-import=lxml._elementpath",
        "pkg_file_explorer.py"
    ]

    print("\nBuilding single-file executable...")
    print(f"Command: {' '.join(pyinstaller_args)}")
    print()

    try:
        subprocess.check_call(pyinstaller_args)
        print("\n" + "=" * 60)
        print("✓ Build successful!")
        print("=" * 60)
        print(f"\nExecutable created: dist/PKGFileExplorer.exe")
        print(f"Size: {os.path.getsize('dist/PKGFileExplorer.exe') / 1024 / 1024:.2f} MB")
        print("\nYou can distribute the .exe file to users who don't have Python installed.")

    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 60)
        print("✗ Build failed!")
        print("=" * 60)
        print(f"Error: {e}")
        sys.exit(1)


def build_directory():
    """Build directory distribution (faster startup)"""

    print("\n" + "=" * 60)
    print("Building directory distribution (optional)")
    print("=" * 60)

    pyinstaller_args = [
        "pyinstaller",
        "--onedir",
        "--windowed",
        "--name=PKGFileExplorer",
        "--clean",
        "--hidden-import=lxml.etree",
        "--hidden-import=lxml._elementpath",
        "pkg_file_explorer.py"
    ]

    print("\nBuilding directory distribution...")
    print("(This creates a folder with the .exe and dependencies)")
    print()

    try:
        subprocess.check_call(pyinstaller_args)
        print("\n✓ Directory distribution created: dist/PKGFileExplorer/")

    except subprocess.CalledProcessError as e:
        print(f"\n✗ Build failed: {e}")


if __name__ == "__main__":
    # Build single-file executable
    build_executable()

    # Optionally build directory distribution
    # Uncomment the line below if you want both versions
    # build_directory()

    print("\n" + "=" * 60)
    print("Build process complete!")
    print("=" * 60)
