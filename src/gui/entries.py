import tkinter as tk

class DurationEntry(tk.Frame):
    def __init__(self, parent, label_text="Value", var=None, default_value=0, **kwargs):
        super().__init__(parent, **kwargs)

        self.var = var if var else tk.IntVar(value=default_value)

        # Descriptive label
        self.label = tk.Label(self, text=label_text)
        self.label.pack(side="left", padx=(0, 5))

        # Entry field
        self.entry = tk.Entry(self, textvariable=self.var)
        self.entry.pack(side="left")

        # "ns" unit label
        self.unit_label = tk.Label(self, text="ns")
        self.unit_label.pack(side="left", padx=(5, 0))

    def get(self):
        return self.entry.get()

