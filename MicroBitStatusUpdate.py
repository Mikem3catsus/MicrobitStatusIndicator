import subprocess
import serial
import serial.tools.list_ports as port_list
import tkinter as tk
from tkinter import ttk


def launch_gui():
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.root=master
        self.port_names = self.get_port_names()
        self.port = self.port_names[-1]
        self.create_buttons()
        self.update()

    def get_port_names(self):
        return [port.device for port in port_list.comports()]

    def create_buttons(self):
        # we make the title label wide so that the window title bar is wide enough to grab for moving.
        self.title_label = tk.Label(self, text="                  Micro:Bit Call Status Indicator                   ")
        self.title_label.pack(side="top")
        self.status_label = tk.Label(self, text="Status = Unknown")
        self.status_label.pack(side="top")
        self.error_label = tk.Label(self, text="Running fine...")
        self.error_label.pack(side="top")
        busy_button = tk.Button(self, text="Busy", command=self.send_busy)
        busy_button.pack(side="left", expand=1, fill="both")
        free_button = tk.Button(self, text="Free", command=self.send_clear)
        free_button.pack(side="left", expand=1, fill="both")

        self.update_select = ttk.Combobox(values=["Manual", "Powershell_Lync2013"])
        self.update_select.pack(side="bottom", expand=1, fill="both")
        self.update_select.set("Manual")

        self.comport_select = ttk.Combobox(values=self.port_names)
        self.comport_select.pack(side="bottom", expand=1, fill="both")
        self.comport_select.set(self.port)

    def send_busy(self):
        self.status_label["text"] = "Status = Busy"
        self.safe_send_com(b"1\n")

    def send_clear(self):
        self.status_label["text"] = "Status = Free"
        self.safe_send_com(b"0\n")

    def safe_send_com(self, binary_string):
        try:
            self.port = self.comport_select.get()
            ser = serial.Serial(port=self.port, baudrate=115200)
            ser.write(binary_string)
        except Exception as e:
            self.error_label = str(e)
            pass

    def update(self):
        update_method = self.update_select.get()
        if update_method == "Manual":
            self.error_label["text"] = "Running fine..."
        elif update_method == "Powershell_Lync2013":
            self.update_powershell_lync2013()
        self.root.after(1000*30, self.update)

    def update_powershell_lync2013(self):
        """
        This update method relies on Powershell and the Lync 2013 API to attach to either Lync or the
        newer "Skype for Business" API to get the current status.

        Installing the Lync2013 API can be complicated as most people don't have that version of Lync
        installed, so the API .msi must be extracted from the installer and installed manually as
        described in several places on the web:

         * https://blog.jongallant.com/2016/08/solution-lync-2013-not-found/
         * https://stackoverflow.com/questions/56286156/lync-model-reference-for-skype-for-business-2016-online-status?noredirect=1&lq=1

        :return: None
        """
        cmd_string = 'Import-Module "C:\Program Files (x86)\Microsoft Office 2013\LyncSDK\Assemblies\Desktop\Microsoft.Lync.Model.dll";' + \
        '[Microsoft.Lync.Model.LyncClient]::GetClient().Self.Contact.GetContactInformation([Microsoft.Lync.Model.ContactInformationType]::ActivityID)\n'

        self.ps_shell = subprocess.Popen(["powershell.exe", cmd_string], stdout=subprocess.PIPE,
                                         universal_newlines=True)
        result = self.ps_shell.communicate()[0].strip()
        self.error_label["text"] = f"Running fine, skype status is {result}"
        if result in ["on-the-phone", "in-a-conference", "presenting", "DoNotDisturb"]:
            self.send_busy()
        else:
            self.send_clear()

if __name__ == "__main__":
    launch_gui()
