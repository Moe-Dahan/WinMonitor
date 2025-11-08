import tkinter as tk
from tkinter import ttk, messagebox
import psutil
import time
import threading
import winreg
import sys
import os
from pathlib import Path

APP_NAME = "SysMonitor"

def set_run_at_startup(app_name: str, file_path: Path):
    RUN_KEY = r"Software\\Microsoft\\Windows\\CurrentVersion\\Run" # The key path for applications to run at user login
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_WRITE)
        reg_value = str(file_path)
        # set the value to true to enable startup
        winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, reg_value)
        winreg.CloseKey(key)
        return True

    except Exception as e:
        messagebox.showerror("Error", f"Failed to set startup registration: {e}")
        return False

def remove_run_at_startup(app_name: str):
    RUN_KEY = r"Software\\Microsoft\\Windows\\CurrentVersion\\Run"
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, app_name)
        winreg.CloseKey(key)
        return True

    except FileNotFoundError:
        messagebox.showerror("Error", f"Startup entry for '{app_name}' was not found in the registry (already removed).")
        return True
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to remove startup registration: {e}")
        return False
    
class SystemMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("System Monitor")
        self.root.geometry("460x400")
        self.root.resizable(False, False)
        root.overrideredirect(True) # sets the window to be borderless
       
        # set the style 
        style = ttk.Style()
        style.theme_use('default')
        root.attributes('-alpha',0.95)
        self.root.configure(bg="#232324")
        style.configure('Custom.TFrame', background="#232324", foreground='#232324')
        style.configure('Custom.TLabel', background="#232324", foreground='#ECEFF4', font=('Segoe UI', 10))
        style.configure('Header.TLabel', background='#232324', foreground="#FFFFFF", font=('Segoe UI', 18, 'bold'))
        style.configure('Value.TLabel', background='#232324', foreground="#FFFFFF", font=('Segoe UI', 10), padding=5)
        style.configure('Changed.TLabel', background="#232324", foreground="#3CFF00", font=('Segoe UI', 10), padding=5)
        style.configure('Danger.TLabel', background="#232324", foreground="#FF0000", font=('Segoe UI', 10), padding=5)
        
        # allow for draging the frameless window
        self._offsetx = 0
        self._offsety = 0
        self.root.x = 0
        self.root.y = 0
        self.root.bind('<Button-1>',self.clickwin)
        self.root.bind('<B1-Motion>',self.dragwin)
        self.root.bind('<Button-3>', self.on_closing)

        # main frame setup
        self.cup_frame = ttk.Frame(root, style='Custom.TFrame')
        
        # CPU Section
        self.cpu_label_frame = ttk.Frame(self.cup_frame, style='Custom.TFrame')
        header = ttk.Label(self.cpu_label_frame, text="CPU", style='Header.TLabel')
        header.grid(row=0, column=0, pady=(0, 0))
        self.display_cpu_frame = ttk.Frame(self.cpu_label_frame, style='Custom.TFrame')
        self.create_cpu_section()
        self.display_cpu_frame.grid(row=1, column=0, sticky='nsew')
        self.cpu_label_frame.grid(row=0, column=0, sticky='nsew', columnspan=12)
        
        # Memory Section
        self.memory_frame = ttk.Frame(self.cup_frame, style='Custom.TFrame')
        header = ttk.Label(self.memory_frame, text="MEMORY", style='Header.TLabel')
        header.grid(row=0, column=0, pady=(0, 0))
        self.show_memory_frame = ttk.Frame(self.memory_frame, style='Custom.TFrame')
        self.create_memory_section()
        self.show_memory_frame.grid(row=1, column=0, sticky='nsew')
        self.memory_frame.grid(row=1, column=0, sticky="nw", columnspan=1)
        
        # Disk Section
        self.disk_label_frame = ttk.Frame(self.memory_frame, style='Custom.TFrame')
        self.disk_labels = {}
        header = ttk.Label(self.memory_frame, text="DISKS", style='Header.TLabel', anchor='center')
        header.grid(row=0, column=1, columnspan=2)
        self.create_disk_section()
        self.disk_label_frame.grid(row=1, column=1, sticky="nw", columnspan=2)

        self.network_frame = ttk.Frame(self.cup_frame, style='Custom.TFrame')
        header = ttk.Label(self.network_frame, text="ESTABLISHED CONNECTIONS", style='Header.TLabel', anchor='center')
        header.grid(row=1, column=0, columnspan=2)
        self.connections_listbox = tk.Listbox(self.network_frame, fg="#050505", font=('Segoe UI', 8), bd=0, highlightthickness=0, selectbackground="#3CFF00", selectforeground="#000000", width=70, height=8, background="Yellow")
        self.connections_listbox.grid(row=2, column=0, sticky='nsew', columnspan=2)

        self.network_frame.grid(row=2, column=0, sticky="nw", columnspan=12)

        self.cup_frame.pack(expand=True, fill='both', padx=20, pady=10)
        # end of main frame setup

        # start the thread to update stats
        self.running = True
        self.update_thread = threading.Thread(target=self.update_stats)
        self.update_thread.daemon = True
        self.update_thread.start()

    # cpu section creation
    def create_cpu_section(self):
        current_coloumn = 0
        current_row = 1
        self.cpu_labels = []
        num_cpus = psutil.cpu_count()
        if num_cpus is not None:
            # enumerate through each cpu core and create a label for it
            for i in range(num_cpus):
                cpu_label = ttk.Label(self.display_cpu_frame, text=f"{i}", style='Value.TLabel', width=7)
                cpu_label.grid(row=current_row, column=current_coloumn, sticky='nw', padx=2, pady=2)
                self.cpu_labels.append(cpu_label)
                # make the grid dynamic and sets max 6 columns per row
                current_coloumn += 1
                if current_coloumn >= 6:
                    current_coloumn = 0
                    current_row = 2

    # memory section creation
    def create_memory_section(self):
        self.memory_percent = ttk.Label(self.show_memory_frame, text="", style='Value.TLabel')
        self.memory_percent.grid(row=0, column=0, sticky='nsew')
        self.memory_used = ttk.Label(self.show_memory_frame, text="", style='Value.TLabel')
        self.memory_used.grid(row=1, column=0, sticky='nesw')

    def create_disk_section(self):
        column = 0
        row = 2
        partitions = psutil.disk_partitions()
        
        for disk in partitions:
            disk_key = disk.device 

            diskname_label = ttk.Label(self.disk_label_frame, text=f"{disk.device}", style='Value.TLabel', anchor='center')
            diskname_label.grid(row=row, column=column, sticky='nesw', padx=5)

            disk_percent_label = ttk.Label(self.disk_label_frame, text="Loading...", style='Value.TLabel')
            disk_percent_label.grid(row=row + 1, column=column, sticky='nesw', padx=5)

            self.disk_labels[disk_key] = {
                'name': diskname_label,
                'percent': disk_percent_label,
                'mountpoint': disk.mountpoint 
            }
            
            # Grid layout management
            column += 1
            if column >= 4:
                column = 0
                row += 2 # Increment by 2 since each disk takes 2 rows (name + percent)

    # format bytes function for the memory display
    def format_bytes(self, bytes):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes < 1024:
                return f"{bytes:.1f} {unit}"
            bytes /= 1024
        return f"{bytes:.1f} TB"
    
    # update system stats funtion
    def update_stats(self):
        last_net_io = psutil.net_io_counters()
        last_time = time.time()
        # set the while loop to keep updating stats
        while self.running:
            # update the cpu stats
            cpu_per_core = psutil.cpu_percent(interval=1, percpu=True)
            for i, cpu_percent in enumerate(cpu_per_core):
                self.cpu_labels[i].config(text=f"Core {i}\n{cpu_percent}%", style='Value.TLabel')
                if cpu_percent >= 0.1:
                    self.cpu_labels[i].config(text=f"Core {i}\n{cpu_percent}%", style='Changed.TLabel')
                if cpu_percent >= 90.0:
                    self.cpu_labels[i].config(text=f"Core {i}\n{cpu_percent}%", style='Danger.TLabel')

            # update the Memory stats
            memory = psutil.virtual_memory()
            self.memory_percent.config(text=f"Memory: {self.format_bytes(memory.total)}", style='Value.TLabel')
            self.memory_used.config(text=f"Used: {self.format_bytes(memory.used)}", style='Value.TLabel')

            # updates the Disk
            for disk_key, labels in self.disk_labels.items():
                try:
                    # Use the stored mountpoint to get the usage data
                    mountpoint = labels['mountpoint']
                    disk_usage = psutil.disk_usage(mountpoint)
                    
                    # Update ONLY the text of the existing label
                    labels['percent'].config(text=f"Usage: {disk_usage.percent}%")
                    
                    # Optional: Add color coding for disk usage
                    if disk_usage.percent >= 90.0:
                        labels['percent'].config(style='Danger.TLabel')
                    elif disk_usage.percent >= 70.0:
                        labels['percent'].config(style='Changed.TLabel')
                    else:
                        labels['percent'].config(style='Value.TLabel')
                         
                except Exception as e:
                    # Handles case where a disk is disconnected (e.g., external drive)
                    labels['percent'].config(text="N/A", style='Danger.TLabel')
                    print(f"Error accessing disk {disk_key}: {e}")
            # update the Network Connections
            network = psutil.net_connections(kind='all')
            for conn in network:
                if conn.status == 'ESTABLISHED':
                    self.connections_listbox.insert(tk.END, f"{conn.laddr} | {conn.raddr}")
        # rest for a second before next update
        time.sleep(1)

    # dragging the window functions
    def dragwin(self,event):
        deltax = event.x - self.root.x
        deltay = event.y - self.root.y
        new_x = root.winfo_x() + deltax
        new_y = root.winfo_y() + deltay
        root.geometry(f"+{new_x}+{new_y}")

    # record the position on click
    def clickwin(self,event):
        self.root.x = event.x
        self.root.y = event.y

    # remove from registry on closing
    def on_closing(self, event):
        quiter = messagebox.askyesno("Quit", "Do you want to quit?")
        if quiter:
            self.running = False # stop the update thread
            if remove_run_at_startup(APP_NAME):
                messagebox.showinfo("Info", "Application removed from startup.")
        self.root.destroy()


if __name__ == "__main__":
    if getattr(sys, 'frozen', False):
        current_exe_path = Path(sys.executable)
    else:
        current_exe_path = Path(os.path.abspath(__file__))
    if set_run_at_startup(APP_NAME, current_exe_path):
        print("Application started and registered for Windows startup.")
        
    root = tk.Tk()
    app = SystemMonitor(root)
    root.mainloop()
