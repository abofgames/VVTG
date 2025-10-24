"""
Business Logic for VHDL Testbench Generator.
Handles configuration, VHDL parsing, testbench generation, and simulation.
"""
import os
import sys
import shutil

from core.ports import extract, extract_component_names
from core.generate import make_copy, replace
from core.command import run_ghdl_analyze, run_ghdl_elaborate, run_ghdl_simulate, run_gtkwave


class TestbenchLogic:
    """Handles all testbench generation and simulation logic."""
    
    def __init__(self):
        # Configuration
        self.base_dir = self._get_base_dir()
        self.workspace_dir = os.path.join(self.base_dir, "workspace")
        
        # Check if workspace exists
        os.makedirs(self.workspace_dir, exist_ok=True)
        
        # Ghdl and gtkwave paths detection
        self.ghdl = self._find_ghdl()
        self.gtkwave = self._find_gtkwave()
        
        # States
        self.component_file_path = None
        self.file_data = None
        self.used_component = None
        self.entity_name = None
        self.num_ports = []
        self.port_type = []
    
    def _get_base_dir(self):
        """
        Get the base directory of the application.
        
        Returns:
            str: Absolute path to project root
        """
        if getattr(sys, 'frozen', False):
            # Running as compiled app
            return os.path.dirname(sys.executable)
        else:
            # Running as script - go up one level from src/
            return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    def _find_ghdl(self):
        """
        Find GHDL executable.
        """
        # Try system PATH first
        system_ghdl = shutil.which("ghdl")
        if system_ghdl:
            return system_ghdl
        else : 
            print("GHDL not found in system PATH.")
        
        
        if sys.platform.startswith("win"):
            ghdl_exe = os.path.join(self.base_dir, "ghdl/bin", "ghdl.exe")
        else:
            ghdl_exe = os.path.join(self.base_dir, "ghdl/bin", "ghdl")

        return ghdl_exe if os.path.exists(ghdl_exe) else None

    def _find_gtkwave(self):
        """
        Find GTKWave executable.
        
        Returns:
            str: Path to GTKWave or None
        """
        # Try system PATH 
        system_gtkwave = shutil.which("gtkwave")
        if system_gtkwave:
            return system_gtkwave
        
        # Try bundled version
        if sys.platform.startswith("win"):
            gtkwave_exe = os.path.join(self.base_dir, "gtkwave/gtkwave64/bin", "gtkwave.exe")
        else:
            gtkwave_exe = os.path.join(self.base_dir, "gtkwave/gtkwave64/bin", "gtkwave")

        return gtkwave_exe if os.path.exists(gtkwave_exe) else None

    def get_default_vhdl_file(self):
        """
        Get path to default VHDL file.
        
        Returns:
            str: Path to default file in workspace
        """
        return os.path.join(self.workspace_dir, "my_register.vhd")
    
    def load_vhdl_file(self, file_path):
        """
        Load and parse a VHDL file.
        
        Args:
            file_path: Path to VHDL component file
            
        Returns:
            tuple: (input_ports, output_ports, entity_name) or None on error
        """
        try:
            if not os.path.exists(file_path):
                print(f"ERROR: File not found: {file_path}")
                return None
            
            # Store absolute path
            self.component_file_path = os.path.abspath(file_path)
            
            # Parse VHDL file
            self.file_data = extract(file_path)
            self.used_component = extract_component_names(file_path)
            self.port_type = list(self.file_data[0].values())
            self.num_ports = list(self.file_data[0].keys())
            self.entity_name = self.file_data[2]
            
            print(f"Loaded: {os.path.basename(file_path)} from {os.path.dirname(file_path)}")
            return self.file_data
            
        except Exception as e:
            print(f"ERROR loading file: {e}")
            return None

    def get_input_port_names(self):
        """
        Get list of input port names.
        """
        return self.num_ports

    def get_input_port_types(self):
        """
        Get list of input port data types.
        """
        return self.port_type
    
    def generate_testbench(self, waveform_canvas, timing_config):
        """
        Generate testbench file and run simulation.
        """
        try:
            if not waveform_canvas:
                print("ERROR: Waveform not initialized.")
                return False
            
            if not self.ghdl:
                print("ERROR: GHDL not found.")
                return False
            
            if not self.component_file_path:
                print("ERROR: No component file loaded.")
                return False
            
            if not os.path.exists(self.component_file_path):
                print(f"ERROR: Component file not found: {self.component_file_path}")
                return False
            
            # Setup paths
            component_dir = os.path.dirname(self.component_file_path)
            tb_file_path = os.path.join(component_dir, self.entity_name[1] + '.vhd')
            wave_file = os.path.join(component_dir, self.entity_name[0] + '_wave.ghw')
            
            # Generate testbench template
            make_copy(os.path.join(component_dir, self.entity_name[1]))
            
            # Replace entity placeholders
            replace(tb_file_path, 'ENTITY_NAME_TB', self.entity_name[1])
            replace(tb_file_path, 'ENTITY_NAME', self.entity_name[0])
            
            # Replace timing parameters
            replace(tb_file_path, 'XHIGH_TIME', str(timing_config['high_time']))
            replace(tb_file_path, 'XLOW_TIME', str(timing_config['low_time']))
            replace(tb_file_path, 'XTEST_LENGTH', str(timing_config['test_length']))
            replace(tb_file_path, 'XCHANGE_TIME', str(timing_config['segment_duration']))
            
            # Generate port declarations
            self._generate_port_strings(tb_file_path)
            
            # Generate stimulus loop
            self._generate_stimulus_loop(tb_file_path, waveform_canvas, timing_config)
            
            # Run simulation
            success = self._run_simulation(component_dir, tb_file_path, wave_file)
            
            if success:
                print(f"\n✓ Simulation complete!")
                print(f"  Testbench: {tb_file_path}")
                print(f"  Waveform:  {wave_file}\n")
                
                # Try to launch GTKWave
                self._launch_gtkwave(wave_file)
            
            return success
            
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _generate_port_strings(self, tb_file_path):
        """
        Generate and replace port-related strings in testbench.
        """
        port_string = ""
        signal_string = ""
        portmap_string = ""
        
        # Input ports
        for name, dtype in self.file_data[0].items():
            port_string += f';\n{name}  : in {dtype}'
            if dtype=='STD_LOGIC':
                signal_string += f'\nsignal    {name} : {dtype}:= \'0\';'
            else:
                signal_string += f'\nsignal    {name} : {dtype}:= (others => \'0\');'
            portmap_string += f',\n{name}    =>{name}'
        
        # Output ports
        for name, dtype in self.file_data[1].items():
            port_string += f';\n{name}  : out {dtype}'
            signal_string += f'\nsignal    {name} : {dtype};'
            portmap_string += f',\n{name}    =>{name}'
        
        replace(tb_file_path, 'XPORTS', port_string)
        replace(tb_file_path, 'XSIGNALS', signal_string)
        replace(tb_file_path, 'XPORTMAP', portmap_string)
    
    def _generate_stimulus_loop(self, tb_file_path, waveform_canvas, timing_config):
        """
        Generate stimulus process loop from waveform data.
        """
        segments = waveform_canvas.get_highlighted_segments()
        segment_value = waveform_canvas.get_highlighted_segments_value()
        
        loop_string = ""
        num_segments = int(timing_config['test_length'] / timing_config['segment_duration'])
        
        for i in range(num_segments):
            for j in range(len(self.num_ports)):
                if i in segments[j]:
                    if self.port_type[j] == 'STD_LOGIC':
                        loop_string += f"{self.num_ports[j]}<= '1';\n"
                    else:
                        loop_string += f"{self.num_ports[j]}<= \"{segment_value[j].get(i)}\";\n"
                else:
                    if self.port_type[j] == 'STD_LOGIC':
                        loop_string += f"{self.num_ports[j]}<= '0';\n"
                    else:
                        loop_string += f"{self.num_ports[j]}<= (others => '0');\n"
            loop_string += "wait for DATA_CHANGE_TIME;\n"
        
        replace(tb_file_path, 'XLOOP', loop_string)
    
    def _run_simulation(self, component_dir, tb_file_path, wave_file):
        """
        Run GHDL analysis, elaboration, and simulation.
        """
        original_cwd = os.getcwd()
        print(f"Changing to directory: {component_dir}")
        
        try:
            os.chdir(component_dir)
            
            # GHDL workflow
            for i in self.used_component:
                run_ghdl_analyze(self.ghdl, os.path.basename(i + ".vhd"))
            run_ghdl_analyze(self.ghdl, os.path.basename(self.component_file_path))
            run_ghdl_analyze(self.ghdl, os.path.basename(tb_file_path))
            run_ghdl_elaborate(self.ghdl, self.entity_name[1])
            run_ghdl_simulate(self.ghdl, self.entity_name[1], os.path.basename(wave_file))
            
            return True
            
        finally:
            os.chdir(original_cwd)
    
    def _launch_gtkwave(self, wave_file):
        """
        Try to launch GTKWave viewer.
        """
        if not self.gtkwave:
            print("Note: GTKWave not found")
            return
        
        try:
            run_gtkwave(self.gtkwave, wave_file)
        except Exception as e:
            print(f"Note: Could not launch GTKWave")
            print(f"Open waveform manually with: gtkwave {wave_file}\n")
