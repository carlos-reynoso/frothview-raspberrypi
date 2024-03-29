import tkinter as tk
import os
import subprocess
import sys

def main():
    root = tk.Tk()
    root.title("Main Menu")

    # Get screen width and height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Set window size and position to simulate maximized window
    root.geometry(f"{screen_width}x{screen_height}+0+0")

    # Define function to execute command in a new terminal
    def run_command_in_terminal(command):
        subprocess.Popen(['x-terminal-emulator', '-e', command])

    # Define button commands
    button_commands = {
        "Measure": lambda: run_command_in_terminal("python measure_velocity.py"),
        "Calibrate": lambda: os.system("python QR_calibrate.py"),
        "Shutdown": lambda: os.system("sudo shutdown now"),
        "Exit": lambda: sys.exit()  # Use sys.exit to quit the application
    }

    # Button texts
    button_texts = ["Measure", "Calibrate", "Shutdown", "Exit"]

    # Create and pack buttons
    for text in button_texts:
        command = button_commands.get(text, lambda: None)
        tk.Button(root, text=text, command=command).pack(side=tk.LEFT, padx=10, pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
