import tkinter as tk
import os
   

# Create the main window
root = tk.Tk()
root.title("Meteo Plane")
root.attributes('-fullscreen', True)
root.configure(bg='black')

# List to keep track of the labels
labels = []
label = tk.Label(root, text="Temperature:", bg = 'black',fg='white', font=("Arial", 20))
label.place(x=50, y=50)
labels.append(label)
label1 = tk.Label(root, text="Pressure:", bg = 'black',fg='white', font=("Arial", 20))
label1.place(x=300,y=50)
# Add a button to spawn "Hello, World!" text


# Add a key binding to close the application (e.g., pressing "Escape")
root.bind("<Escape>", lambda event: root.destroy() )

# Run the application
root.mainloop()