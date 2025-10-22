"""
VHDL Testbench Generator - Main Entry Point

"""
from app_gui import VHDLTestbenchGUI
import sys

file_path = sys.argv[1] if len(sys.argv) > 1 else None


if __name__ == "__main__":
    app = VHDLTestbenchGUI(file_path=file_path)
    app.run()