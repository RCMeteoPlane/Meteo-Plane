import tkinter as tk
from tkinter import messagebox
import serial
import threading
import sys
import folium
import os
from cefpython3 import cefpython as cef

# Replace these with your actual serial ports
ESP1_PORT = "/dev/cu.usbserial-14310"  # Replace with the port for the first ESP32
ESP2_PORT = "/dev/cu.usbserial-14320"  # Replace with the port for the second ESP32
BAUD_RATE1 = 115200  # Baud rate for ESP1
BAUD_RATE2 = 115200  # Baud rate for ESP2 (GPS module)

# Global dictionaries to store label references for both ESP32s
labels_esp1 = {}
labels_esp2 = {}
latitude, longitude = 0.0, 0.0  # Default GPS coordinates
map_file_path = "gps_map.html"

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
    global running, latitude, longitude
    while running:
        if esp2.is_open:
            try:
                # Read raw data from the GPS ESP32
                raw_data = esp2.readline()
                data = raw_data.decode("utf-8", errors="ignore").strip()
                if data:  # If valid data is received
                    parse_and_update_esp2(data)  # Parse and update the GUI
            except Exception as e:
                update_status_esp2(f"Error: {e}")

def parse_and_update_esp2(raw_data):
    """Parse and display GPS data."""
    global latitude, longitude
    if "Latitude:" in raw_data:  # Check for Latitude keyword
        latitude = float(raw_data.split(":")[1].strip())
        labels_esp2["latitude"].config(text=f"Latitude: {latitude}")
    elif "Longitude:" in raw_data:  # Check for Longitude keyword
        longitude = float(raw_data.split(":")[1].strip())
        labels_esp2["longitude"].config(text=f"Longitude: {longitude}")

def update_status_esp1(message):
    """Update status for ESP1."""
    labels_esp1["status"].config(text=message)

def update_status_esp2(message):
    """Update status for ESP2."""
    labels_esp2["status"].config(text=message)

def create_map():
    """Create and display a live map inside the application window using CEF."""
    global latitude, longitude

    if latitude == 0.0 and longitude == 0.0:
        messagebox.showinfo("Map", "No valid GPS data available yet.")
        return

    try:
        # Create the map
        m = folium.Map(location=[latitude, longitude], zoom_start=15)
        folium.Marker([latitude, longitude], tooltip="Current Location").add_to(m)

        # Save the map to a file
        m.save(map_file_path)
        print(f"Map file saved as {map_file_path}")

        # Embed the map using CEF
        file_url = f"file://{os.path.abspath(map_file_path)}"

        def cef_thread():
            settings = {
                "windowless_rendering_enabled": False,
            }
            cef.Initialize(settings)
            cef.CreateBrowserSync(url=file_url, window_title="Live Map")
            cef.MessageLoop()
            cef.Shutdown()

        threading.Thread(target=cef_thread, daemon=True).start()

    except Exception as e:
        print(f"Error creating map: {e}")
        messagebox.showerror("Error", f"Failed to create map: {e}")

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
root.title("ESP32 Data Viewer with Live Map")
root.geometry("1000x800")

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

# Map button
map_button = tk.Button(root, text="Show Live Map", command=create_map)
map_button.pack(pady=10)

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
