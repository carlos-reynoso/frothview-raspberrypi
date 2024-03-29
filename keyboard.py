import cv2
import numpy as np
import time
import tkinter as tk

# Define a function to create a numeric keypad instead of using the simpledialog
def get_numeric_input(title, prompt):
    def on_button_press(value):
        if value == 'Enter':
            user_input.set(entry.get())  # Set the user_input variable with the entry value
            keypad.destroy()
        elif value == 'Clear':
            entry.delete(0, tk.END)
        else:
            entry.insert(tk.END, value)  # Insert the button's value at the end of the text entry

    keypad = tk.Tk()
    keypad.title(title)
    
    # Variable to store user input
    user_input = tk.StringVar(keypad)
    
    tk.Label(keypad, text=prompt).grid(row=0, column=0, columnspan=3)
    
    entry = tk.Entry(keypad, textvariable=user_input, justify='right')
    entry.grid(row=1, column=0, columnspan=3)
    
    # Numeric Buttons
    buttons = [
        ('1', 2, 0), ('2', 2, 1), ('3', 2, 2),
        ('4', 3, 0), ('5', 3, 1), ('6', 3, 2),
        ('7', 4, 0), ('8', 4, 1), ('9', 4, 2),
        ('Clear', 5, 0), ('0', 5, 1), ('Enter', 5, 2),
    ]
    
    for (text, row, col) in buttons:
        action = lambda x=text: on_button_press(x)
        tk.Button(keypad, text=text, command=action).grid(row=row, column=col, sticky='ew')

    keypad.mainloop()
    return user_input.get()  # Return the value when the window is closed
