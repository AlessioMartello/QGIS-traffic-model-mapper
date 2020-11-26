import tkinter as tk
from tkinter.filedialog import askopenfilename
from run import run_analysis
import pathlib

root = tk.Tk()
root.title("Strategic route mapper")
root.geometry("650x300")
BACKGROUND_COLOUR = "#d6d6d6"
FOREGROUND_COLOUR = "#512d6d"

class RouteMapper:

    def __init__(self, main):
        myFrame = tk.Frame(main)
        myFrame.pack()
        self.intro = tk.Label(main, text="Select the files containing the stategic data, GIS data and then click run:",
                        fg=FOREGROUND_COLOUR, font=("", 15, "bold")).pack()
        self.strategic_data = tk.Button(main, text="Choose strategic data file", command=self.choose_data, bg=BACKGROUND_COLOUR,
                                  fg=FOREGROUND_COLOUR, highlightcolor=FOREGROUND_COLOUR, font=("", 15)).pack(pady=20)
        self.gis_data = tk.Button(main, text="Choose GIS data file", command=self.choose_data, bg=BACKGROUND_COLOUR,
                                  fg=FOREGROUND_COLOUR, highlightcolor=FOREGROUND_COLOUR, font=("", 15)).pack(pady=20)
        self.run_button = tk.Button(main, text="Run", command=lambda: self.run_analysis(self.strategic_data, self.gis_data), bg=BACKGROUND_COLOUR,
                                  fg=FOREGROUND_COLOUR, highlightcolor=FOREGROUND_COLOUR, font=("", 15)).pack(pady=20)

    def choose_data(self):
        data_file = askopenfilename(title="Choose the strategic data file", filetypes=[("Excel files", ".xls .xlsx")])
        return data_file

    def run_analysis(self, strategic_data_file, qgis_file):
        run_analysis(strategic_data_file, qgis_file)


a = RouteMapper(root)

root.mainloop()


