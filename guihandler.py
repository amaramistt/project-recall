import tkinter
from tkinter import ttk

# Create the app class
class App:
    def __init__(self, master):
        # Set the master (the root window) to width and height
        master.geometry("600x400")
        # Create a label using ttk, give it master and text
        self.label = ttk.Label(master, text="Hello, World!")
        # Place it in the window a row, column
        self.label.grid(row=0, column=0)
        # Create a label using ttk, give it master and text and set the command callback to pressed
        self.button = ttk.Button(master, text="Press Me!", command=self.pressed)
        # Place it in the window a row, column
        self.button.grid(row=1, column=1)
        # Create a label, give it master but no text
        self.press = ttk.Label(master)
        # Place it in the window a row, column
        self.press.grid(row=1, column=0)
        # Bind the ctrl+e key command callback to exit
        master.bind("<Control_L> e", exit)

    def pressed(self):
        # If button is pressed, then set press text to Hello there user! 
        self.press.config(text="Hello there user!")

# Make the master (root window)
root = tk.Tk()
# Make the app and pass it the master (root window)
app = App(root)
# Run the master (root window)
root.mainloop()