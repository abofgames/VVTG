import subprocess
import os

def run_ghdl_analyze(GHDL, file_path):
    cmd = [GHDL, "-a", file_path]
    subprocess.run(cmd, check=True)

def run_ghdl_elaborate(GHDL, entity_name):
    cmd = [GHDL, "-e", entity_name]
    subprocess.run(cmd, check=True)

def run_ghdl_simulate(GHDL, entity_name, wave_file=None):
    if wave_file is None:
        wave_file = os.path.join("workspace", "wave.ghw")
    cmd = [GHDL, "-r", entity_name, f"--wave={wave_file}"]
    subprocess.run(cmd, check=True)

def run_gtkwave(GTKWAVE, wave_file=None):
    if wave_file is None:
        wave_file = os.path.join("workspace", "wave.ghw")
    cmd = [GTKWAVE, wave_file]
    subprocess.run(cmd, check=True)

