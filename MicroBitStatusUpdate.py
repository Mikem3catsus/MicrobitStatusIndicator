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

        master.title("Call Status")
        self.root=master
        self.port_names = self.get_port_names()
        self.port = self.port_names[-1]
        self.update_methods = {"Manual":self.update_manual, "Powershell Lync2013":self.update_powershell_lync2013}
        self.create_buttons()
        self.update()

    def get_port_names(self):
        return [port.device for port in port_list.comports()]

    def create_buttons(self):
        full_sticky = tk.W + tk.E + tk.N + tk.S

        # we make the title label wide so that the window title bar is wide enough to grab for moving.
        title_label = tk.Label(self.root, text="                  Micro:Bit Call Status Indicator                   ")
        title_label.grid(column=0, row=1, columnspan=2)
        self.status_label = tk.Label(self.root, text="Status = Unknown")
        self.status_label.grid(column=0, row=2, columnspan=2)
        self.error_label = tk.Label(self.root, text="Running fine...")
        self.error_label.grid(column=0, row=3, columnspan=2)
        busy_button = tk.Button(self.root, text="Busy", command=self.send_busy)
        busy_button.grid(column=0, row=4, sticky=full_sticky)
        free_button = tk.Button(self.root, text="Free", command=self.send_clear)
        free_button.grid(column=1, row=4, sticky=full_sticky)

        tk.Label(self.root, text="Update Method:").grid(column=0, row=5)
        self.update_select = ttk.Combobox(self.root, values=list(self.update_methods.keys()))
        self.update_select.grid(column=1, row=5, sticky= full_sticky)
        self.update_select.set("Manual")

        tk.Label(self.root, text="Port for MicroBit:").grid(column=0, row=6)
        self.comport_select = ttk.Combobox(self.root, values=self.port_names)
        self.comport_select.grid(column=1, row=6, sticky=full_sticky)
        self.comport_select.set(self.port)

        self.set_grid_weights()

    def set_grid_weights(self):
        (column_count, row_count) = self.root.grid_size()
        for column in range(column_count):
            self.root.grid_columnconfigure(column, weight=1)
        for row in range(row_count):
            self.root.grid_rowconfigure(row, weight=1)

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
        self.update_methods[update_method]()
        self.root.after(1000*30, self.update)

    def update_manual(self):
        self.error_label["text"] = "Running fine..."

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
