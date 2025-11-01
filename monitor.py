import tkinter as tk
from tkinter import ttk
import psutil
import platform
import time
import threading



class SystemMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("System Monitor")
        self.root.geometry("430x400")
        # set the style 
        style = ttk.Style()
        style.theme_use('default')
        # root.attributes('-alpha',0.95)
        self.root.configure(bg="#232324")
        style.configure('Custom.TFrame', background="#232324", foreground='#232324')
        style.configure('Custom.TLabel', background="#232324", foreground='#ECEFF4', font=('Segoe UI', 10))
        style.configure('Header.TLabel', background='#232324', foreground="#FFFFFF", font=('Segoe UI', 18, 'bold'))
        style.configure('Value.TLabel', background='#232324', foreground="#FFFFFF", font=('Segoe UI', 10), padding=5)
        style.configure('Changed.TLabel', background="#232324", foreground="#3CFF00", font=('Segoe UI', 10), padding=5)
        style.configure('Danger.TLabel', background="#232324", foreground="#FF0000", font=('Segoe UI', 10), padding=5)

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
        header = ttk.Label(self.memory_frame, text="DISKS", style='Header.TLabel', anchor='center')
        header.grid(row=0, column=1, columnspan=2)
        self.disk_label_frame.grid(row=1, column=1, sticky="nw", columnspan=2)

        self.network_frame = ttk.Frame(self.cup_frame, style='Custom.TFrame')
        header = ttk.Label(self.network_frame, text="NETWORK CONNECTIONS", style='Header.TLabel', anchor='center')
        header.grid(row=1, column=0, columnspan=2)
        self.connections_listbox = tk.Listbox(self.network_frame, fg="#050505", font=('Segoe UI', 8), bd=0, highlightthickness=0, selectbackground="#3CFF00", selectforeground="#000000", width=70, height=8)
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
        num_cpus = psutil.cpu_count()  # Get the number of CPU cores
        if num_cpus is not None:
            # enumerate through each cpu core and create a label for it
            for i in range(num_cpus):
                cpu_label = ttk.Label(self.display_cpu_frame, text=f"{i}", style='Value.TLabel', width=7)
                cpu_label.grid(row=current_row, column=current_coloumn, sticky='nw', padx=2, pady=2)
                self.cpu_labels.append(cpu_label) # append to cpu_labels list for future updates
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
                    self.cpu_labels[i].config(text=f"Core {i}\n{cpu_percent}", style='Changed.TLabel')
                if cpu_percent >= 90.0:
                    self.cpu_labels[i].config(text=f"Core {i}\n{cpu_percent}%", style='Danger.TLabel')

            # update the Memory stats
            memory = psutil.virtual_memory()
            self.memory_percent.config(text=f"Memory: {self.format_bytes(memory.total)}", style='Value.TLabel')
            self.memory_used.config(text=f"Used: {self.format_bytes(memory.used)}", style='Value.TLabel')

            # updates the Disk
            column = 0
            row = 2
            for disk in psutil.disk_partitions():
                self.diskname_label = ttk.Label(self.disk_label_frame, text=f"{disk.device}", style='Value.TLabel', anchor='center')
                self.disk_percent_ = ttk.Label(self.disk_label_frame, text="", style='Value.TLabel')
                column += 1
                if column >= 4:
                    column = 0
                    row += 1
                self.diskname_label.grid(row=row, column=column, sticky='nesw')
                self.disk_percent_.grid(row=row + 1, column=column, sticky='nesw')
                disk_usage = psutil.disk_usage(disk.mountpoint)
                self.disk_percent_.config(text=f"Usage: {disk_usage.percent}%")
        
            # update the Network Connections
            network = psutil.net_connections(kind='tcp')
            for conn in network:
                self.connections_listbox.insert(tk.END, f"{conn.status} | LAddr: {conn.laddr} | RAddr: {conn.raddr}")
                # print(conn.status, conn.raddr, conn.laddr)
        # rest for a second before next update
        time.sleep(1)



if __name__ == "__main__":
    root = tk.Tk()
    app = SystemMonitor(root)
    root.protocol("WM_DELETE_WINDOW", )#app.on_closing)
    root.mainloop()