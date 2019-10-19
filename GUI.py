import tkinter as tk
import schedule
import traceback


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
        self.enter_button.pack()

    def create_schedule(self):
        self.enter_button.pack_forget()
        self.label_text.set('Starting...')
        self.master.update()
        try:
            schedule.main(self.schedule_entry.get("1.0", tk.END))
        except Exception as e:
            with open('log', 'a') as f:
                self.label_text.set('ERROR OCCURRED. CHECK LOG FILE')
                f.write(str(e))
                f.write(traceback.format_exc())
        else:
            self.label_text.set('Finished!')
            self.enter_button.pack()
            


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("350x200")
    root.resizable(width=False, height=False)
    my_gui = SchedulerGui(root)
    root.mainloop()
