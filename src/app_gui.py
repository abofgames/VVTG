"""
GUI for VHDL Testbench Generator.
Handles window creation, widgets, layout, and user interactions.
"""
import tkinter as tk
from tkinter import filedialog

from gui.entries import DurationEntry
from gui.wave_gen import WaveGenCanvas
from app_logic import TestbenchLogic


class VHDLTestbenchGUI:
    
    def __init__(self, file_path=None):
        self.file_path = file_path
        self.logic = TestbenchLogic()
        
        # Create window
        self._create_window()
        
        self.high_time = tk.IntVar()
        self.high_time.set(10)
        self.low_time = tk.IntVar()
        self.low_time.set(10)
        self.test_length = tk.IntVar()
        self.test_length.set(400)
        self.segment_duration = tk.IntVar()
        self.segment_duration.set(20)
        
        # Component file name
        self.component_file_name = tk.StringVar()

        if self.file_path:
            self.component_file_name.set(self.file_path)
            self.logic.load_vhdl_file(self.file_path)
        else:
            self.component_file_name.set(self.logic.get_default_vhdl_file())
        
        # Waveform canvas
        self.wave_canvas = None
        self.dynamic_widgets = []
        
        # Create widgets
        self._create_widgets()
        
        # Load default file

    
    def _create_window(self):
        """Create main window."""
        self.root = tk.Tk()
        self.root.title("Easy VHDL Test Bench Generator")
        self.root.state("zoomed")  # Windows only
                                                                             
    def _create_widgets(self):
        # Title
        label = tk.Label(self.root, text="Easy VHDL Test Bench Generator", font=("Arial", 14))
        label.pack(pady=20)
        
        # Entry frame for timing controls
        entry_frame = tk.Frame(self.root)
        entry_frame.pack(side="top", pady=20)
        
        # Timing entries
        high_time_entry = DurationEntry(entry_frame, label_text="High Time :", var=self.high_time)
        high_time_entry.pack(pady=5, anchor="w")
        
        low_time_entry = DurationEntry(entry_frame, label_text="Low Time :", var=self.low_time)
        low_time_entry.pack(pady=5, anchor="w")
        
        test_length_entry = DurationEntry(entry_frame, label_text="Test Length :", var=self.test_length)
        test_length_entry.pack(pady=5, anchor="w")
        
        segment_duration_entry = DurationEntry(entry_frame, label_text="Segment Duration :", var=self.segment_duration)
        segment_duration_entry.pack(pady=5, anchor="w")
        
        # File selection frame
        file_frame = tk.Frame(entry_frame)
        file_entry_label = tk.Label(file_frame, text="File Name :")
        file_entry_label.pack(side="left")

        file_loc_entry = tk.Entry(file_frame, textvariable=self.component_file_name)
        file_loc_entry.pack(side="left")
        
        browse_button = tk.Button(file_frame, text="Browse", command=self._on_browse_clicked)
        browse_button.pack(side="left", padx=5)
        file_frame.pack(pady=5, anchor="w")
        
        # Submit button
        submit_button = tk.Button(entry_frame, text="Submit", command=self._on_submit_clicked)
        submit_button.pack(pady=5)
    
    def _load_default_file(self):
        """Load default VHDL file at startup."""
        default_file = self.component_file_name.get()
        if default_file:
            self.logic.load_vhdl_file(default_file)
    
    def _on_browse_clicked(self):
        """Handle Browse button click."""
        filename = filedialog.askopenfilename(
            initialdir=".",
            title="Select VHDL Component File",
            filetypes=[("VHDL files", "*.vhd"), ("All files", "*.*")]
        )
        
        if filename:
            self.component_file_name.set(filename)
            result = self.logic.load_vhdl_file(filename)
            
            if result:
                self._refresh_waveform_editor()
    
    def _on_submit_clicked(self):
        """Handle Submit button click - creates/refreshes waveform editor."""
        self._load_default_file()
        self._refresh_waveform_editor()
    
    def _on_generate_clicked(self):
        """Handle Generate button click - generates testbench and runs simulation."""
        if not self.wave_canvas:
            print("ERROR: Waveform canvas not initialized.")
            return
        
        # Collect timing configuration
        timing_config = {
            'high_time': self.high_time.get(),
            'low_time': self.low_time.get(),
            'test_length': self.test_length.get(),
            'segment_duration': self.segment_duration.get()
        }
        
        # Generate testbench
        self.logic.generate_testbench(self.wave_canvas, timing_config)
    
    def _refresh_waveform_editor(self):
        """Create or recreate the waveform editor canvas."""
        if self.dynamic_widgets:
            widget = self.dynamic_widgets.pop()
            widget.destroy()
        
        # Create new canvas
        self._create_waveform_canvas()

    def _create_waveform_canvas(self):
        """Create waveform editor canvas with vertical scroll support."""
        # Get port names from loaded file
        num_ports = self.logic.get_input_port_names()
        port_types = self.logic.get_input_port_types()

        if not num_ports:
            print("ERROR: No ports found. Load a VHDL file first.")
            return

        # Create scrollable container
        scroll_container = tk.Frame(self.root)
        scroll_container.pack(pady=20, fill="both", expand=True)

        canvas = tk.Canvas(scroll_container)
        scrollbar = tk.Scrollbar(scroll_container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="both")
        canvas.pack(side="left", fill="both", expand=True)

        # Frame inside canvas to hold WaveGenCanvas
        inner_frame = tk.Frame(canvas)
        canvas_window = canvas.create_window((0, 0), window=inner_frame, anchor="nw")

        def resize_inner(event):
            canvas.itemconfig(canvas_window, width=event.width)

        canvas.bind("<Configure>", resize_inner)

        # Update scroll region when content changes
        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        inner_frame.bind("<Configure>", on_configure)

        # Create waveform canvas inside the scrollable frame
        self.wave_canvas = WaveGenCanvas(
            inner_frame,
            self.high_time.get(),
            self.low_time.get(),
            self.test_length.get(),
            self.segment_duration.get(),
            num_ports,
            port_types
        )
        self.wave_canvas.pack(pady=20, fill="both", expand=True)

        # Add Generate button to canvas
        generate_btn = tk.Button(
            self.wave_canvas,
            text="Generate",
            command=self._on_generate_clicked
        )
        generate_btn.pack(pady=20)

        self.dynamic_widgets.append(self.wave_canvas)

    def run(self):
        """Start the GUI main loop."""
        self.root.mainloop()
