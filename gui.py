import tkinter as tk
from tkinter.filedialog import askopenfilename
from tkinter import messagebox

from run import run_analysis
import pathlib

root = tk.Tk()
root.title("Strategic route mapper")
# root.geometry("650x300")
BACKGROUND_COLOUR = "#d6d6d6"
FOREGROUND_COLOUR = "#512d6d"


class RouteMapper:

    def __init__(self, main):
        myFrame = tk.Frame(main)
        myFrame.pack()
        self.data_files = [None, None]
        self.error_message = None
        self.intro = tk.Label(main, text="Select the files containing the strategic data, GIS data and then click run:",
                              fg=FOREGROUND_COLOUR, font=("", 15, "bold"), padx=20, pady=10).pack()
        self.strategic_data = tk.Button(main, text="Choose strategic data file", command=lambda: self.choose_data(0),
                                        bg=BACKGROUND_COLOUR,
                                        fg=FOREGROUND_COLOUR, highlightcolor=FOREGROUND_COLOUR, font=("", 15)).pack(
            pady=20)
        self.gis_data = tk.Button(main, text="Choose GIS data file", command=lambda: self.choose_data(1),
                                  bg=BACKGROUND_COLOUR,
                                  fg=FOREGROUND_COLOUR, highlightcolor=FOREGROUND_COLOUR, font=("", 15)).pack(pady=20)
        self.run_button = tk.Button(main, text="Run", command=self.run_analysis, bg=BACKGROUND_COLOUR,
                                fg=FOREGROUND_COLOUR, highlightcolor=FOREGROUND_COLOUR, font=("", 15)).pack(pady=20)

    def choose_data(self, index):
        self.data_files[index] = pathlib.Path(
            askopenfilename(title="Choose the strategic data file", filetypes=[("Excel files", ".xls .xlsx")]))

    def run_analysis(self):
        try:
            run_analysis(*self.data_files)
        except ValueError:
            self.error_message = messagebox.showerror("Error", "Ensure you have selected the appropriate strategic data & GIS data.")


a = RouteMapper(root)

root.mainloop()
