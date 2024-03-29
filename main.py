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

    # Make the window full screen
    root.attributes("-fullscreen", True)

    # Define function to execute command in a new terminal
    def run_command_in_terminal(command):
        subprocess.Popen(['x-terminal-emulator', '-e', command]).detach()
        root.destroy()

    # Define button commands
    button_commands = {
        "Measure": lambda: run_command_in_terminal("python measure_velocity.py"),
        "Calibrate": lambda: run_command_in_terminal("python QR_calibrate.py"),
        "Shutdown": lambda: os.system("sudo shutdown now"),
        "Exit": lambda: sys.exit()  # Use sys.exit to quit the application
    }

    # Button texts
    button_texts = ["Measure", "Calibrate", "Shutdown", "Exit"]

    # Create a frame for the buttons
    button_frame = tk.Frame(root)
    button_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)  # Add padding

    # Create and pack buttons within the frame
    for text in button_texts:
        command = button_commands.get(text, lambda: None)
        btn = tk.Button(button_frame, text=text, command=command)
        btn.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)  # Add padding

    root.mainloop()

if __name__ == "__main__":
    main()
