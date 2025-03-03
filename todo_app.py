import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TODO App")
        self.root.geometry("400x500")
        
        # Data storage
        self.tasks = []
        self.load_tasks()
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create and configure widgets
        self.task_entry = ttk.Entry(self.main_frame, width=40)
        self.task_entry.grid(row=0, column=0, padx=5, pady=5)
        
        self.add_button = ttk.Button(self.main_frame, text="Add Task", command=self.add_task)
        self.add_button.grid(row=0, column=1, padx=5, pady=5)
        
        # Task listbox
        self.task_listbox = tk.Listbox(self.main_frame, width=45, height=20)
        self.task_listbox.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
        
        # Delete button
        self.delete_button = ttk.Button(self.main_frame, text="Delete Selected", command=self.delete_task)
        self.delete_button.grid(row=2, column=0, columnspan=2, pady=5)
        
        # Populate listbox with saved tasks
        self.refresh_task_list()
        
        # Bind enter key to add task
        self.task_entry.bind('<Return>', lambda e: self.add_task())

    def add_task(self):
        task = self.task_entry.get().strip()
        if task:
            self.tasks.append(task)
            self.refresh_task_list()
            self.task_entry.delete(0, tk.END)
            self.save_tasks()
        
    def delete_task(self):
        selection = self.task_listbox.curselection()
        if selection:
            index = selection[0]
            del self.tasks[index]
            self.refresh_task_list()
            self.save_tasks()
    
    def refresh_task_list(self):
        self.task_listbox.delete(0, tk.END)
        for task in self.tasks:
            self.task_listbox.insert(tk.END, task)
    
    def save_tasks(self):
        with open('tasks.json', 'w') as f:
            json.dump(self.tasks, f)
    
    def load_tasks(self):
        try:
            if os.path.exists('tasks.json'):
                with open('tasks.json', 'r') as f:
                    self.tasks = json.load(f)
        except:
            self.tasks = []

if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()