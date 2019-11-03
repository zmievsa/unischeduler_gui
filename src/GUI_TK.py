import tkinter as tk
from tkinter import filedialog

import schedule
from util import ErrorHandler


class SchedulerGui:
    def __init__(self, master):
        self.master = master
        master.title("Scheduler")
        self.label_text = tk.StringVar()
        self.label_text.set("Please, paste your schedule in the field below")
        self.label = tk.Label(master, textvariable=self.label_text)
        self.label.pack()
        self.schedule_entry = tk.Text(master, height=9)
        self.schedule_entry.pack()

        self.enter_button = tk.Button(
            master, text="Enter", command=self.create_schedule)
        self.enter_button.pack(fill=tk.BOTH)
        master.bind("<Button-3>", self.right_click)

    def right_click(self, event=None):
        self.schedule_entry.delete("1.0", tk.END)
        self.schedule_entry.insert("1.0", self.master.clipboard_get())

    def create_schedule(self, event=None):
        self.enter_button.pack_forget()
        self.label_text.set('Starting...')
        self.master.update()
        with ErrorHandler(self.label_text.set):
            calendar = schedule.main(self.schedule_entry.get("1.0", tk.END))
            filename = filedialog.asksaveasfilename(
                initialdir="/", 
                title="Select file to export your schedule to",
                filetypes=(("Icalendar files", "*.ics"),)
            )
            filename += "" if filename.lower().endswith(".ics") else ".ics"
            with open(filename, "wb") as f:
                print(calendar.decode("UTF-8"))
                f.write(calendar)
        self.enter_button.pack(fill=tk.BOTH)


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("350x196")
    root.resizable(width=False, height=False)
    my_gui = SchedulerGui(root)
    root.mainloop()
