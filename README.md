# SysMonitor
A Windows system monitor widget, Tracks CPU, RAM, ESTABLISHED CONNECTIONS and HARD DRIVERS
The Widget uses the windows registry editor to add and remove widget on start up.

# How to install
1. Download or clone repo
2. download and use pyinstaller to make it a .exe bootable application
   https://pyinstaller.org/en/stable/installation.html
   
   this command should work
   
   pyinstaller --onefile --icon CardiacMonitor_icon-icons.com_75042.ico --noconsole --name SysMonitor .\monitor.py
4. once you build it simply run it as every other .exe file

# Once Running
Once you run it the widget will edit the registy and add its self to the startup
widget is dragable across multiple screens or you can place it anywhere you like
if you want to exit it mouse over the widget and right click.
this will exist the widget and remove itself from the registry editor so no more start on startup

# How to Read
* Cores in use will turn green
* Cores using more then 90% will turn read
* Cores not used will be white
* Other information is updated and stays the same.

# Modules used 
1. Tkinter for the GUI
2. psutil to read system resources

<img width="965" height="841" alt="Screenshot 2025-11-11 085613" src="https://github.com/user-attachments/assets/55b017c5-696c-479b-ad5f-c6fecdecb373" />
