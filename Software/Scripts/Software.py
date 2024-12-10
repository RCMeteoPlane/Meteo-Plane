import tkinter as tk
from tkinter import messagebox
import serial
import threading
import sys

# Replace these with your actual serial ports
ESP1_PORT = "/dev/cu.usbserial-14310"  # Replace with the port for the first ESP32
ESP2_PORT = "/dev/cu.usbserial-14320"  # Replace with the port for the second ESP32
BAUD_RATE1 = 115200  # Baud rate for ESP1
BAUD_RATE2 = 115200  # Baud rate for ESP2 (GPS module)

# Global dictionaries to store label references for both ESP32s
labels_esp1 = {}
labels_esp2 = {}

def read_from_esp1():
    """Read and parse data from the first ESP32 (environment/accelerometer)."""
    global running
    buffer = ""  # Buffer to hold incomplete data chunks
    while running:
        if esp1.is_open:
            try:
                # Read and decode serial data
                data = esp1.readline().decode("utf-8").strip()
                if data:
                    buffer += data + "\n"
                    if "Temp:" in buffer:  # Ensure full data set
                        parse_and_update_esp1(buffer.strip())  # Update GUI
                        buffer = ""  # Clear buffer after parsing
            except Exception as e:
                update_status_esp1(f"Error: {e}")

def parse_and_update_esp1(raw_data):
    """Parse and display data from ESP1."""
    lines = raw_data.split("\n")
    for line in lines:
        if line.startswith("x ="):
            labels_esp1["x"].config(text=line)
        elif line.startswith("Roll ="):
            labels_esp1["roll"].config(text=line)
        elif line.startswith("Temp:"):
            labels_esp1["temp"].config(text=line)

def read_from_esp2():
    """Read and parse data from the second ESP32 (GPS module)."""
    global running
    while running:
        if esp2.is_open:
            try:
                # Read raw data from the GPS ESP32
                raw_data = esp2.readline()
                print(f"Raw GPS data: {raw_data}")  # Debugging raw data

                # Decode data, ignoring errors
                data = raw_data.decode("utf-8", errors="ignore").strip()
                if data:  # If valid data is received
                    parse_and_update_esp2(data)  # Parse and update the GUI
            except Exception as e:
                update_status_esp2(f"Error: {e}")

def parse_and_update_esp2(raw_data):
    """Parse and display GPS data."""
    print(f"Parsed GPS data: {raw_data}")  # Debugging parsed data

    if "Latitude:" in raw_data:  # Check for Latitude keyword
        labels_esp2["latitude"].config(text=raw_data)
    elif "Longitude:" in raw_data:  # Check for Longitude keyword
        labels_esp2["longitude"].config(text=raw_data)
    else:
        labels_esp2["status"].config(text="Waiting for GPS data...")

def update_status_esp1(message):
    """Update status for ESP1."""
    labels_esp1["status"].config(text=message)

def update_status_esp2(message):
    """Update status for ESP2."""
    labels_esp2["status"].config(text=message)

def on_close():
    """Handle app closure."""
    global running
    running = False
    if esp1.is_open:
        esp1.close()
    if esp2.is_open:
        esp2.close()
    root.destroy()

# Tkinter GUI
root = tk.Tk()
root.title("ESP32 Data Viewer")
root.geometry("800x600")

# ESP1 (environment/accelerometer) section
frame_esp1 = tk.LabelFrame(root, text="ESP32 Sensor Data", padx=10, pady=10)
frame_esp1.pack(fill="both", expand="yes", padx=10, pady=10)

labels_esp1["status"] = tk.Label(frame_esp1, text="Connecting to ESP32 Sensor...", font=("Arial", 12))
labels_esp1["status"].grid(row=0, column=0, columnspan=2, sticky="w")

labels_esp1["x"] = tk.Label(frame_esp1, text="x = ...", font=("Arial", 12))
labels_esp1["x"].grid(row=1, column=0, sticky="w")

labels_esp1["roll"] = tk.Label(frame_esp1, text="Roll = ...", font=("Arial", 12))
labels_esp1["roll"].grid(row=2, column=0, sticky="w")

labels_esp1["temp"] = tk.Label(frame_esp1, text="Temp: ...", font=("Arial", 12))
labels_esp1["temp"].grid(row=3, column=0, sticky="w")

# ESP2 (GPS module) section
frame_esp2 = tk.LabelFrame(root, text="ESP32 GPS Data", padx=10, pady=10)
frame_esp2.pack(fill="both", expand="yes", padx=10, pady=10)

labels_esp2["status"] = tk.Label(frame_esp2, text="Connecting to ESP32 GPS...", font=("Arial", 12))
labels_esp2["status"].grid(row=0, column=0, columnspan=2, sticky="w")

labels_esp2["latitude"] = tk.Label(frame_esp2, text="Latitude: ...", font=("Arial", 12))
labels_esp2["latitude"].grid(row=1, column=0, sticky="w")

labels_esp2["longitude"] = tk.Label(frame_esp2, text="Longitude: ...", font=("Arial", 12))
labels_esp2["longitude"].grid(row=2, column=0, sticky="w")

# Close button
close_button = tk.Button(root, text="Close", command=on_close)
close_button.pack(pady=10)

# Open serial connections
try:
    esp1 = serial.Serial(ESP1_PORT, BAUD_RATE1, timeout=1)
    update_status_esp1("Connected to ESP32 Sensor.")
except Exception as e:
    messagebox.showerror("Error", f"Failed to connect to ESP32 Sensor: {e}")
    sys.exit()

try:
    esp2 = serial.Serial(ESP2_PORT, BAUD_RATE2, timeout=1)
    update_status_esp2("Connected to ESP32 GPS.")
except Exception as e:
    messagebox.showerror("Error", f"Failed to connect to ESP32 GPS: {e}")
    sys.exit()

# Start threads for reading data
running = True
thread1 = threading.Thread(target=read_from_esp1, daemon=True)
thread2 = threading.Thread(target=read_from_esp2, daemon=True)
thread1.start()
thread2.start()

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()
