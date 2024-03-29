import tkinter as tk
import os
from tkinter import font as tkFont

def main_menu():
    # Create the main window
    root = tk.Tk()
    root.title("Main Menu")

    # Make it full screen
    root.attributes('-fullscreen', True)

    # Define a large font
    button_font = tkFont.Font(family='Helvetica', size=24, weight='bold')

    # Function to exit the program
    def quit_program():
        root.destroy()

    # Function to shutdown the system
    def shutdown_system():
        os.system("sudo shutdown now")

    # Frame to contain the buttons, expanded in both directions
    button_frame = tk.Frame(root)
    button_frame.pack(expand=True, fill=tk.BOTH)

    # Configure the button_frame to expand and fill space
    button_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
    button_frame.grid_rowconfigure(0, weight=1)

    # Create and pack buttons to fill the frame horizontally
    buttons = [
        ("Measure", lambda: print("Measure")),
        ("Calibrate", lambda: print("Calibrate")),
        ("Update", lambda: print("Update")),
        ("Shutdown", shutdown_system)
    ]

    for i, (text, command) in enumerate(buttons):
        button = tk.Button(button_frame, text=text, font=button_font, command=command)
        button.grid(row=0, column=i, sticky='nsew', padx=20, pady=200)

    root.mainloop()

if __name__ == "__main__":
    main_menu()
