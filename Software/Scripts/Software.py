import tkinter as tk
import cv2
from PIL import Image, ImageTk

def play_video():
    """Play video frame by frame."""
    # Open video file
    cap = cv2.VideoCapture("/Users/admin/Downloads/JOPORN_NET_41196_240p.mp4")  # Replace with your video file path
    
    def update_frame():
        ret, frame = cap.read()
        if ret:
            # Convert the frame to RGB (OpenCV uses BGR by default)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img = ImageTk.PhotoImage(img)
            
            # Update the image on the label
            label.config(image=img)
            label.image = img  # Keep a reference to the image
            
            # Call the function again after a short delay
            root.after(10, update_frame)
        else:
            cap.release()  # Release video capture when done

    # Start video playback
    update_frame()

# Create the main window
root = tk.Tk()
root.title("White Screen with Video")
root.attributes('-fullscreen', True)
root.configure(bg='white')

# Label to display video frames
label = tk.Label(root, bg='white')
label.pack()

# Button to play video
button = tk.Button(root, text="Play Video", command=play_video, font=("Arial", 14))
button.place(x=50, y=50)

# Add a key binding to close the application (e.g., pressing "Escape")
root.bind("<Escape>", lambda event: root.destroy())

# Run the application
root.mainloop()
