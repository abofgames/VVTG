"""Core modules package."""
from .ports import extract
from .generate import make_copy, replace
from .command import run_ghdl_analyze, run_ghdl_elaborate, run_ghdl_simulate, run_gtkwave

__all__ = [
    'extract',
    'make_copy', 
    'replace',
    'run_ghdl_analyze',
    'run_ghdl_elaborate',
    'run_ghdl_simulate',
    'run_gtkwave'
]
