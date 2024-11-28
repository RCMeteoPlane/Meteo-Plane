import tkinter as tk
import os

def spawn_text():
    """Create a new 'Hello, World!' label on the screen."""
    label = tk.Label(root, text="Hello, World!", bg='white', fg='black', font=("Arial", 20))
    label.place(x=50, y=50 + 30 * len(labels))  # Place each label slightly below the previous one
    labels.append(label)

# Create the main window
root = tk.Tk()
root.title("White Screen with Hello World")
root.attributes('-fullscreen', True)
root.configure(bg='white')

# List to keep track of the labels
labels = []

# Add a button to spawn "Hello, World!" text
button = tk.Button(root, text="Spawn Hello, World!", command=spawn_text, font=("Arial", 14))
button.place(x=50, y=50)

# Add a key binding to close the application (e.g., pressing "Escape")
root.bind("<Escape>", lambda event: root.destroy(), os._exit(0)
)

# Run the application
root.mainloop()