import tkinter as tk
from tkinter import ttk
import time

# Root window
root = tk.Tk()
root.title("Multi-Threaded Weather Data Collector")
root.geometry("800x500")
root.configure(bg="#f0f4f7")

# Title
title = tk.Label(root, text="Multi-Threaded Weather Data Collector",
                 font=("Arial", 18, "bold"), bg="#f0f4f7")
title.pack(pady=10)

# Table Frame
table_frame = tk.Frame(root)
table_frame.pack(pady=10)

columns = ("City", "Temperature (°C)", "Humidity (%)", "Pressure (hPa)", "Condition")

tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=140, anchor="center")

tree.pack(side="left")

scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
scrollbar.pack(side="right", fill="y")
tree.configure(yscrollcommand=scrollbar.set)

# Status Label
status_label = tk.Label(root, text="Status: Ready",
                        font=("Arial", 11), bg="#f0f4f7")
status_label.pack(pady=10)

# Sample weather data
sample_data = [
    ("Kathmandu", 25, 60, 1012, "Clear Sky"),
    ("Pokhara", 22, 65, 1010, "Cloudy"),
    ("Biratnagar", 28, 70, 1008, "Sunny"),
    ("Nepalgunj", 30, 55, 1005, "Hot"),
    ("Dhangadhi", 27, 58, 1007, "Windy")
]

# Fetch Sequential Function
def fetch_sequential():
    tree.delete(*tree.get_children())  # clear table
    status_label.config(text="Status: Fetching sequentially...")
    root.update()
    
    for row in sample_data:
        time.sleep(1)  # simulate sequential fetching delay
        tree.insert("", "end", values=row)
    
    status_label.config(text="Status: Sequential fetch complete")

# Fetch Parallel Function
def fetch_parallel():
    tree.delete(*tree.get_children())  # clear table
    status_label.config(text="Status: Fetching in parallel...")
    root.update()
    for row in sample_data:
        tree.insert("", "end", values=row)
    
    status_label.config(text="Status: Parallel fetch complete")
# Button Frame
button_frame = tk.Frame(root, bg="#f0f4f7")
button_frame.pack(pady=10)
seq_btn = tk.Button(button_frame, text="Fetch Sequential",
                    width=20, bg="#4CAF50", fg="black", command=fetch_sequential)
seq_btn.grid(row=0, column=0, padx=10)
par_btn = tk.Button(button_frame, text="Fetch Parallel",
                    width=20, bg="#2196F3", fg="black", command=fetch_parallel)
par_btn.grid(row=0, column=1, padx=10)
root.mainloop()
