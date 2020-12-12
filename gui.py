import tkinter as tk
from tkinter.filedialog import askopenfilename
from tkinter import messagebox, filedialog

from saturn_routes.run import run_analysis
import pathlib

root = tk.Tk()
root.title("Strategic route mapper")
BACKGROUND_COLOUR = "#d6d6d6"
FOREGROUND_COLOUR = "#512d6d"


class RouteMapper:

    def __init__(self, main):
        myFrame = tk.Frame(main)
        myFrame.grid()

        self.data_files, self.directories = [None, None], [None, None, None]
        self.error_message = None

        self.intro = tk.Label(main, text="Select the files containing the strategic data, GIS data and then click run:",
                              fg=FOREGROUND_COLOUR, font=("", 15, "bold")).grid(row=0, columnspan=2, padx=10,pady=10)

        self.strategic_data = tk.Button(main, text="Choose strategic data file", command=lambda: self.choose_data(0),
                                        bg=BACKGROUND_COLOUR,
                                        fg=FOREGROUND_COLOUR, highlightcolor=FOREGROUND_COLOUR, font=("", 15))
        self.gis_data = tk.Button(main, text="Choose GIS data file", command=lambda: self.choose_data(1),
                                  bg=BACKGROUND_COLOUR,
                                  fg=FOREGROUND_COLOUR, highlightcolor=FOREGROUND_COLOUR, font=("", 15))
        self.link_input_btn = tk.Button(main, text="Select link input folder", command=lambda: self.choose_directory(0),
                                  bg=BACKGROUND_COLOUR,
                                  fg=FOREGROUND_COLOUR, highlightcolor=FOREGROUND_COLOUR, font=("", 15))
        self.link_output_btn = tk.Button(main, text="Select link output folder", command=lambda: self.choose_directory(1),
                                  bg=BACKGROUND_COLOUR,
                                  fg=FOREGROUND_COLOUR, highlightcolor=FOREGROUND_COLOUR, font=("", 15))
        self.link_fail_btn = tk.Button(main, text="Select link fail folder", command=lambda: self.choose_directory(2),
                                  bg=BACKGROUND_COLOUR,
                                  fg=FOREGROUND_COLOUR, highlightcolor=FOREGROUND_COLOUR, font=("", 15))
        self.run_button = tk.Button(main, text="Run", command=self.run_analysis, bg=BACKGROUND_COLOUR,
                                fg=FOREGROUND_COLOUR, highlightcolor=FOREGROUND_COLOUR, font=("", 15))

        self.strategic_data.grid(row= 1, column=0, pady=10, rowspan=2)
        self.gis_data.grid(row= 2, column=0, pady=10, rowspan=2)
        self.link_input_btn.grid(row=1, column=1, pady=10)
        self.link_output_btn.grid(row=2, column=1, pady=10)
        self.link_fail_btn.grid(row=3,column=1, pady=10)
        self.run_button.grid(row=4, pady=10, columnspan=2)

    def choose_data(self, index):
        self.data_files[index] = pathlib.Path(
            askopenfilename(title="Choose the strategic data file", filetypes=[("Excel files", ".xls .xlsx")]))
        if index == 0:
            self.strategic_data.config(fg="green")
        else:
            self.gis_data.config(fg="green")

    def choose_directory(self, index):
        self.directories[index] = filedialog.askdirectory()
        if index == 0:
            self.link_input_btn.config(fg="green")
        elif index == 1:
            self.link_output_btn.config(fg="green")
        else:
            self.link_fail_btn.config(fg="green")

    def run_analysis(self):
        try:
            run_analysis(*self.data_files, *self.directories)
        except ValueError:
            self.error_message = messagebox.showerror("Error", "Ensure you have selected the appropriate strategic data & GIS data.")


a = RouteMapper(root)

root.mainloop()
