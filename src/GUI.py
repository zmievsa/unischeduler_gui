import tkinter as tk
import schedule
import traceback
from requests import ConnectionError


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

        self.enter_button = tk.Button(master, text="Enter", command=self.create_schedule)
        self.enter_button.pack(fill=tk.X)
        master.bind("<Button-3>", self.right_click)
    
    def right_click(self, event=None):
        self.schedule_entry.delete("1.0", tk.END)
        self.schedule_entry.insert("1.0", self.master.clipboard_get())

    def create_schedule(self, event=None):
        self.enter_button.pack_forget()
        self.label_text.set('Starting...')
        self.master.update()
        try:
            calendar = schedule.main(self.schedule_entry.get("1.0", tk.END))
            with open("schedule.ics", "wb") as f:
                print(calendar.decode("UTF-8"))
                f.write(calendar)
        except Exception as e:
            with open('log.txt', 'a') as f:
                f.write(str(e))
                f.write(traceback.format_exc())
            if isinstance(e, ConnectionError):
                self.label_text.set("There's a problem with your internet connection. Please, try again.")
            else:
                self.label_text.set('UNKNOWN ERROR OCCURRED. CHECK LOG FILE')
        else:
            self.label_text.set('Finished!')
        finally:
            self.enter_button.pack()
            


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("350x196")
    root.resizable(width=False, height=False)
    my_gui = SchedulerGui(root)
    root.mainloop()
