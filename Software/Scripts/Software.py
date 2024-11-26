import tkinter as tk

# Create the main window
root = tk.Tk()

# Set the window title
root.title("White Screen")

# Set the window to full screen
root.attributes('-fullscreen', True)

# Set the background color to white
root.configure(bg='white')

# Add a key binding to close the application (e.g., pressing "Escape")
root.bind("<Escape>", lambda event: root.destroy())

# Run the application
root.mainloop()
