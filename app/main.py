import os
import tkinter
import tkinter.messagebox
import customtkinter
from customtkinter import filedialog
from sample_handler import single_sample
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import concurrent.futures

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("RansomShield")
        self.geometry("1100x580")

        # Configure grid layout (4x4)
        self.configure_grid()

        # Create sidebar frame with widgets
        self.create_sidebar_frame()

        # Create tabview
        self.create_tabview()

        # Initialize observer
        self.observer = None

    def configure_grid(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

    def create_sidebar_frame(self):
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        # Sidebar widgets
        self.logo_label = customtkinter.CTkLabel(
            self.sidebar_frame,
            text="RansomShield",
            font=customtkinter.CTkFont(size=20, weight="bold"),
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.create_sidebar_options()

    def create_sidebar_options(self):
        self.appearance_mode_label = customtkinter.CTkLabel(
            self.sidebar_frame, text="Appearance Mode:", anchor="w"
        )
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(
            self.sidebar_frame,
            values=["Light", "Dark", "System"],
            command=self.change_appearance_mode_event,
        )
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))

        self.scaling_label = customtkinter.CTkLabel(
            self.sidebar_frame, text="UI Scaling:", anchor="w"
        )
        self.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(
            self.sidebar_frame,
            values=["80%", "90%", "100%", "110%", "120%"],
            command=self.change_scaling_event,
        )
        self.scaling_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))

    def create_tabview(self):
        self.tabview = customtkinter.CTkTabview(self)
        self.tabview.grid(
            row=0,
            column=1,
            columnspan=2,
            rowspan=2,
            padx=(20, 20),
            pady=(20, 20),
            sticky="nsew",
        )

        self.tabview.add("Upload Sample")
        self.tabview.add("Monitor Directory")

        self.configure_upload_tab()
        self.configure_monitor_tab()

    def configure_upload_tab(self):
        self.upload_label = customtkinter.CTkLabel(
            self.tabview.tab("Upload Sample"), text="Upload and Analyze a Sample"
        )
        self.upload_label.grid(row=0, column=0, padx=20, pady=20)

        self.upload_button = customtkinter.CTkButton(
            self.tabview.tab("Upload Sample"),
            text="Select File",
            command=self.upload_sample_event,
        )
        self.upload_button.grid(row=1, column=0, padx=20, pady=20)

        self.submit_button = customtkinter.CTkButton(
            self.tabview.tab("Upload Sample"),
            text="Submit",
            command=self.submit_sample_event,
            state="disabled",
        )
        self.submit_button.grid(row=1, column=2, padx=20, pady=20)

        # Label to display selected file information
        self.file_info_label = customtkinter.CTkLabel(
            self.tabview.tab("Upload Sample"), text="No file selected."
        )
        self.file_info_label.grid(row=2, column=0, columnspan=3, padx=20, pady=10)

    def configure_monitor_tab(self):
        self.monitor_label = customtkinter.CTkLabel(
            self.tabview.tab("Monitor Directory"),
            text="Monitor a Directory for Changes",
        )
        self.monitor_label.grid(row=0, column=0, padx=20, pady=20)

        self.monitor_button = customtkinter.CTkButton(
            self.tabview.tab("Monitor Directory"),
            text="Select Directory",
            command=self.monitor_directory_event,
        )
        self.monitor_button.grid(row=1, column=0, padx=20, pady=20)

        self.appearance_mode_optionemenu.set("Dark")
        self.scaling_optionemenu.set("100%")

    def upload_sample_event(self):
        self.filepath = filedialog.askopenfilename(
            filetypes=[
                ("Executable files", "*.exe"),
                ("DLL files", "*.dll"),
                ("PDF files", "*.pdf"),
                ("Word documents", "*.doc;*.docx"),
                ("Binary files", "*.bin"),
            ],
        )
        if self.filepath:
            self.file_info_label.configure(
                text=f"Selected File: {os.path.basename(self.filepath)}"
            )

            self.submit_button.configure(state="normal")

    def submit_sample_event(self):
        if self.filepath:
            self.show_loading_window()
            self.executor = concurrent.futures.ThreadPoolExecutor()
            future = self.executor.submit(self.process_sample_in_background)
            self.after(100, self.check_processing_result, future)
        else:
            tkinter.messagebox.showwarning("Error", "No file selected.")

    def show_loading_window(self):
        self.loading_window = customtkinter.CTkToplevel(self)
        self.loading_window.geometry("300x100")
        self.loading_window.title("Processing...")
        self.loading_window.transient(self)
        self.loading_window.grab_set()
        self.center_window(self.loading_window, 300, 100)

        self.loading_bar = customtkinter.CTkProgressBar(
            self.loading_window, mode="indeterminate"
        )
        self.loading_bar.pack(pady=20, padx=20)
        self.loading_bar.start()

        self.update()

    def center_window(self, window, width, height):
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f"+{x}+{y}")

    def process_sample_in_background(self, filepath=None):
        if filepath:
            return single_sample.handle_sample(filepath)
        return single_sample.handle_sample(self.filepath)

    def check_processing_result(self, future):
        if future.done():
            self.loading_bar.stop()
            self.loading_window.destroy()
            try:
                result = future.result()
                self.handle_result(result)
            except Exception as e:
                tkinter.messagebox.showerror("Error", f"An error occurred: {str(e)}")
        else:
            self.after(100, self.check_processing_result, future)

    def handle_result(self, analysis_result):

        if analysis_result == 0:
            if tkinter.messagebox.askyesno(
                "Ransomware Detected!",
                """Warning: A ransomware sample has been detected on your system.
                \nDo you want to delete the sample?""",
            ):
                os.remove(self.filepath)
                tkinter.messagebox.showinfo(
                    "Deleted",
                    """The file has been deleted. Please take the following actions immediately:
                    \n1. Disconnect from the internet.
                    \n2. Do not open any suspicious files.
                    \n3. Run a full system scan using your antivirus software.""",
                )
            else:
                tkinter.messagebox.showinfo(
                    "Not Deleted",
                    """The file was not deleted. Please take the following actions immediately:
                    \n1. Disconnect from the internet.
                    \n2. Do not open any suspicious files.
                    \n3. Run a full system scan using your antivirus software.""",
                )
        else:
            tkinter.messagebox.showinfo(
                "No Threat Detected",
                "The sample is not classified as ransomware. No malicious activity detected.",
            )

    def monitor_directory_event(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            if self.observer:
                self.observer.stop()

            self.observer = Observer()
            event_handler = FileMonitorHandler(self.process_sample_in_background)
            self.observer.schedule(event_handler, folder_selected, recursive=False)
            self.observer.start()

            tkinter.messagebox.showinfo(
                "Monitoring", f"Monitoring {folder_selected} for changes."
            )

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)


class FileMonitorHandler(FileSystemEventHandler):
    def __init__(self, process_sample):
        self.process_sample = process_sample

    def on_created(self, event):
        if not event.is_directory:
            future = concurrent.futures.ThreadPoolExecutor().submit(
                self.process_sample, event.src_path
            )
            future.result()


if __name__ == "__main__":
    app = App()
    app.mainloop()
