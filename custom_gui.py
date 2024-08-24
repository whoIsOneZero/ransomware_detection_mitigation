import os
import tkinter
import tkinter.messagebox
import customtkinter
from customtkinter import filedialog
from monitor import DirectoryMonitor
from sample_handler import single_sample
import concurrent.futures
import threading

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # configure window
        self.title("RansomShield")
        self.geometry(f"{1100}x{580}")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # create sidebar frame with widgets
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

        # create tabview
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

        # Configure the "Upload Sample" tab
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
            state="disabled",  # Initially disabled
        )
        self.submit_button.grid(row=1, column=2, padx=20, pady=20)

        # Configure the "Monitor Directory" tab
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

        # set default values
        self.appearance_mode_optionemenu.set("Dark")
        self.scaling_optionemenu.set("100%")

    def upload_sample_event(self):

        # print("Upload sample button clicked")
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

            # Enable the submit button
            self.submit_button.configure(state="normal")

    def submit_sample_event(self):
        if self.filepath:
            # Create a new top-level window to overlay the main window
            self.loading_window = customtkinter.CTkToplevel(self)
            self.loading_window.geometry("300x100")  # Adjust size as needed
            self.loading_window.title("Processing...")

            # Position it in the center of the main window
            self.loading_window.transient(self)
            self.loading_window.grab_set()

            # Disable main window interaction
            self.loading_window.update_idletasks()
            x = (self.winfo_screenwidth() // 2) - (300 // 2)
            y = (self.winfo_screenheight() // 2) - (100 // 2)
            self.loading_window.geometry(f"+{x}+{y}")

            # Create a loading indicator inside the top-level window
            self.loading_bar = customtkinter.CTkProgressBar(
                self.loading_window, mode="indeterminate"
            )
            self.loading_bar.pack(pady=20, padx=20)
            self.loading_bar.start()

            # Refresh the UI to show the loading bar
            self.update()

            # Run the sample processing in a separate thread
            self.executor = concurrent.futures.ThreadPoolExecutor()
            future = self.executor.submit(self.process_sample_in_background)

            # Schedule a function to check the result
            self.after(100, self.check_processing_result, future)

        else:
            tkinter.messagebox.showwarning("Error", "No file selected.")

    def process_sample_in_background(self):
        """This method runs in a separate thread"""
        analysis_result = single_sample.handle_sample(self.filepath)

        # print(f"The result {analysis_result}")

        return analysis_result

    def check_processing_result(self, future):
        if future.done():
            self.loading_bar.stop()
            self.loading_window.destroy()  # Close the loading window

            try:
                # Get the result of the processing
                _result = future.result()

                print(f"The reslult: {_result}")

                if _result == 0:  # Ransomware detected
                    if tkinter.messagebox.askyesno(
                        "Ransomware Detected",
                        "The sample is classified as ransomware. Do you want to delete it?",
                    ):
                        os.remove(self.filepath)  # Delete the file
                        tkinter.messagebox.showinfo(
                            "Deleted", "The file has been deleted."
                        )
                    else:
                        tkinter.messagebox.showinfo(
                            "Not Deleted", "The file was not deleted."
                        )
                """ else:
                    tkinter.messagebox.showinfo(
                        "Success", "Sample submitted for analysis!"
                    ) """

            except Exception as e:
                tkinter.messagebox.showerror("Error", f"An error occurred: {str(e)}")
        else:
            # If the processing is not yet done, check again after 100ms
            self.after(100, self.check_processing_result, future)

    def monitor_directory_event(self):

        folder_selected = filedialog.askdirectory()

        # Start monitoring
        if folder_selected:
            dir_monitor = DirectoryMonitor(directory=folder_selected)
            dir_monitor.start_monitoring()

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)


if __name__ == "__main__":
    app = App()
    app.mainloop()
