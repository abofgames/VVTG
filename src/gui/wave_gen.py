import tkinter as tk

class WaveGenCanvas(tk.Frame):
    def __init__(self, parent, high_ns, low_ns, test_ns, segment_ns, num_overlays=None, data_types=None, pixels_per_ns=4, **kwargs):
        super().__init__(parent, **kwargs)

        self.high_ns = high_ns
        self.low_ns = low_ns
        self.test_ns = test_ns
        self.segment_ns = segment_ns
        self.pixels_per_ns = pixels_per_ns
        self.canvas_height = 50
        self.num_overlays = num_overlays
        self.data_types = data_types

        self.overlay_canvases = []
        self.highlighted_segments = [[] for _ in range(len(self.num_overlays))]
        self.highlighted_segments_values = [{} for _ in range(len(self.num_overlays))]

        # Zoom controls
        zoom_frame = tk.Frame(self)
        zoom_frame.pack(pady=5)

        tk.Button(zoom_frame, text="Zoom In", command=self.zoom_in).pack(side="left", padx=5)
        tk.Button(zoom_frame, text="Zoom Out", command=self.zoom_out).pack(side="left", padx=5)

        # Scrollable canvas frame
        canvas_frame = tk.Frame(self)
        canvas_frame.pack(fill="x")

        self.scrollbar = tk.Scrollbar(canvas_frame, orient="horizontal")
        self.scrollbar.pack(side="top", fill="x")

        clck_frame = tk.Frame(canvas_frame)
        clck_frame.pack(fill="x")
        clck_label = tk.Label(clck_frame, text="clock", width=20)
        clck_label.pack(side="left")

        # Waveform canvas
        self.canvas = tk.Canvas(clck_frame, height=self.canvas_height, bg="black",
                                xscrollcommand=self.scrollbar.set)
        self.canvas.pack(fill="x", expand=True)

        # Overlay canvases
        for i in range(len(self.num_overlays)):
            line_frame = tk.Frame(canvas_frame)
            line_frame.pack(fill="x")
            name_label = tk.Label(line_frame, text=num_overlays[i], width=20)
            name_label.pack(side="left")
            overlay = tk.Canvas(line_frame, height=self.canvas_height, bg="black",
                                xscrollcommand=self.scrollbar.set)
            overlay.pack(fill="x", expand=True)
            overlay.bind("<Button-1>", lambda e, idx=i: self.on_click(e, idx))
            self.overlay_canvases.append(overlay)

        # Link scrollbar to all canvases
        self.scrollbar.config(command=self.sync_scroll)

        self.draw_wave()
        self.draw_all_overlays()

    def draw_wave(self):
        self.canvas.delete("all")
        canvas_width = int(self.test_ns * self.pixels_per_ns)
        self.canvas.config(scrollregion=(0, 0, canvas_width, self.canvas_height))

        x = 0
        while x < canvas_width:
            low_width = int(self.low_ns * self.pixels_per_ns)
            self.canvas.create_rectangle(x, self.canvas_height - 4, x + low_width, self.canvas_height, fill="green",
                                         outline="green")
            x += low_width

            high_width = int(self.high_ns * self.pixels_per_ns)
            self.canvas.create_rectangle(x, 4, x + high_width, self.canvas_height, fill="green",
                                         outline="green")
            x += high_width

    def draw_all_overlays(self):
        for i in range(len(self.num_overlays)):
            if self.data_types[i] == 'STD_LOGIC':
                self.draw_overlay(i)
            else:
                print(self.highlighted_segments_values[i])
                self.draw_overlay(i, self.highlighted_segments_values[i])

    def draw_overlay(self, index, label_dict=None):
        canvas = self.overlay_canvases[index]
        canvas.delete("all")
        canvas_width = int(self.test_ns * self.pixels_per_ns)
        canvas.config(scrollregion=(0, 0, canvas_width, self.canvas_height))

        for segment_index in self.highlighted_segments[index]:
            segment_start_ns = segment_index * self.segment_ns
            segment_start_x = int(segment_start_ns * self.pixels_per_ns)
            segment_width = int(self.segment_ns * self.pixels_per_ns)

            # Draw the blue rectangle
            canvas.create_rectangle(
                segment_start_x, 0,
                segment_start_x + segment_width, self.canvas_height,
                fill="blue", outline=""
            )

            # If label_dict is provided and has a label for this segment
            if label_dict and segment_index in label_dict:
                canvas.create_text(
                    segment_start_x + segment_width // 2,
                    self.canvas_height // 2,
                    text=label_dict[segment_index],
                    fill="white"
                )

    def on_click(self, event, overlay_index):
        canvas = self.overlay_canvases[overlay_index]
        x_canvas = canvas.canvasx(event.x)
        time_ns = int(x_canvas / self.pixels_per_ns)
        segment_index = time_ns // self.segment_ns

        if segment_index in self.highlighted_segments[overlay_index]:
            self.highlighted_segments[overlay_index].remove(segment_index)
            if segment_index in self.highlighted_segments_values[overlay_index]:
                self.highlighted_segments_values[overlay_index].pop(segment_index)
        else:
            if self.data_types[overlay_index] == 'STD_LOGIC':
                self.highlighted_segments[overlay_index].append(segment_index)
            else:
                self.open_popup(overlay_index, self.data_types[overlay_index], segment_index)
        print(self.highlighted_segments_values)
        self.draw_overlay(overlay_index)

    def zoom_in(self):
        self.pixels_per_ns *= 2
        self.draw_wave()
        self.draw_all_overlays()

    def zoom_out(self):
        self.pixels_per_ns /= 2
        self.draw_wave()
        self.draw_all_overlays()

    def sync_scroll(self, *args):
        self.canvas.xview(*args)
        for overlay in self.overlay_canvases:
            overlay.xview(*args)

    def get_highlighted_segments(self):
        return self.highlighted_segments

    def get_highlighted_segments_value(self):
        return self.highlighted_segments_values

    def open_popup(self, overlay_index, data_type, segment_index):
        popup = PopupWindow(self, self.receive_result, overlay_index, data_type, segment_index)

    def receive_result(self, overlay_index, result, segment_index):
        self.highlighted_segments_values[overlay_index][segment_index] = result
        self.highlighted_segments[overlay_index].append(segment_index)
        self.draw_overlay(overlay_index, self.highlighted_segments_values[overlay_index])
        print(self.highlighted_segments_values)


class PopupWindow:
    def __init__(self, parent, callback, overlay_index, data_type, segment_index):
        self.overlay_index = overlay_index
        self.segment_index = segment_index
        self.top = tk.Toplevel(parent)
        self.top.title(f"enter {data_type} value")
        self.callback = callback

        self.label = tk.Label(self.top, text=f"     enter value of {data_type} :    ")
        self.label.pack(pady=10)
        self.entry = tk.Entry(self.top)
        self.entry.pack(pady=10)

        submit_btn = tk.Button(self.top, text="Submit", command=self.submit)
        submit_btn.pack(pady=10)

    def submit(self):
        result = self.entry.get()
        self.callback(self.overlay_index, result, self.segment_index)
        self.top.destroy()