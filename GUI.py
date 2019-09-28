import tkinter as tk
import schedule


class SchedulerGui:
    def __init__(self, master):
        self.master = master
        master.title("Scheduler")

        self.label = tk.Label(master, text="Please, fill out the fields below")
        self.label.pack()

        self.year_label = tk.Label(master, text="Year:")
        self.year_label.pack()
        self.year_entry = tk.Entry(master, width=10)
        self.year_entry.pack()

        self.term_label = tk.Label(master, text="Term:")
        self.term_label.pack()
        self.term_list = tk.Listbox(master, selectmode=tk.SINGLE)
        self.term_list.insert(tk.END, "Fall")
        self.term_list.insert(tk.END, "Spring")
        self.term_list.config(width=0, height=0)
        self.term_list.pack()
        self.term_list.select_anchor(0)
        self.term_list.select_set(0)
        self.term_list.activate(0)

        self.schedule_entry = tk.Text(master, height=3)
        self.schedule_entry.pack()

        self.enter_button = tk.Button(master, text="Enter", command=self.create_schedule)
        self.enter_button.pack()

    def create_schedule(self):
        year: str = self.year_entry.get()
        if year.isdigit():
            schedule.main(int(year), self.term_list.get(self.term_list.curselection()), self.schedule_entry.get("1.0", tk.END))


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("350x200")
    root.resizable(width=False, height=False)
    my_gui = SchedulerGui(root)
    root.mainloop()
