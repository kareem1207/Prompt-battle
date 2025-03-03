import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced TODO App")
        self.root.geometry("600x600")
        
        # Data storage
        self.tasks = []
        self.load_tasks()
        
        # Configure style
        style = ttk.Style()
        style.configure("Priority.High.TFrame", background="#ffe6e6")
        style.configure("Priority.Medium.TFrame", background="#fff4e6")
        style.configure("Priority.Low.TFrame", background="#e6ffe6")
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        
        # Input area frame
        input_frame = ttk.LabelFrame(self.main_frame, text="Add New Task", padding="5")
        input_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Task entry
        ttk.Label(input_frame, text="Task:").grid(row=0, column=0, padx=5, pady=5)
        self.task_entry = ttk.Entry(input_frame, width=40)
        self.task_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Priority selection
        ttk.Label(input_frame, text="Priority:").grid(row=0, column=2, padx=5, pady=5)
        self.priority_var = tk.StringVar(value="Medium")
        priority_combo = ttk.Combobox(input_frame, textvariable=self.priority_var, 
                                    values=["High", "Medium", "Low"], width=10, state="readonly")
        priority_combo.grid(row=0, column=3, padx=5, pady=5)
        
        # Add button
        self.add_button = ttk.Button(input_frame, text="Add Task", command=self.add_task)
        self.add_button.grid(row=0, column=4, padx=5, pady=5)
        
        # Task list frame
        list_frame = ttk.LabelFrame(self.main_frame, text="Tasks", padding="5")
        list_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        
        # Tasks treeview
        columns = ("task", "priority", "timestamp")
        self.task_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        self.task_tree.heading("task", text="Task")
        self.task_tree.heading("priority", text="Priority")
        self.task_tree.heading("timestamp", text="Created At")
        
        self.task_tree.column("task", width=300)
        self.task_tree.column("priority", width=100)
        self.task_tree.column("timestamp", width=150)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.task_tree.yview)
        self.task_tree.configure(yscrollcommand=scrollbar.set)
        
        self.task_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        
        # Control buttons frame
        control_frame = ttk.Frame(self.main_frame)
        control_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Delete button
        self.delete_button = ttk.Button(control_frame, text="Delete Selected", command=self.delete_task)
        self.delete_button.grid(row=0, column=0, padx=5)
        
        # Bind enter key to add task
        self.task_entry.bind('<Return>', lambda e: self.add_task())
        
        # Load existing tasks
        self.refresh_task_list()

    def add_task(self):
        task = self.task_entry.get().strip()
        if task:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            priority = self.priority_var.get()
            self.tasks.append({
                "task": task,
                "priority": priority,
                "timestamp": timestamp
            })
            self.refresh_task_list()
            self.task_entry.delete(0, tk.END)
            self.save_tasks()
        
    def delete_task(self):
        selection = self.task_tree.selection()
        if selection:
            for item in selection:
                index = self.task_tree.index(item)
                del self.tasks[index]
            self.refresh_task_list()
            self.save_tasks()
    
    def refresh_task_list(self):
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        
        for task in self.tasks:
            values = (task["task"], task["priority"], task["timestamp"])
            item = self.task_tree.insert("", tk.END, values=values)
            
            # Set tag for priority color
            if task["priority"] == "High":
                self.task_tree.tag_configure("high", background="#ffe6e6")
                self.task_tree.item(item, tags=("high",))
            elif task["priority"] == "Medium":
                self.task_tree.tag_configure("medium", background="#fff4e6")
                self.task_tree.item(item, tags=("medium",))
            else:
                self.task_tree.tag_configure("low", background="#e6ffe6")
                self.task_tree.item(item, tags=("low",))
    
    def save_tasks(self):
        with open('tasks.json', 'w') as f:
            json.dump(self.tasks, f)
    
    def load_tasks(self):
        try:
            if os.path.exists('tasks.json'):
                with open('tasks.json', 'r') as f:
                    loaded_tasks = json.load(f)
                    # Convert old format tasks to new format if necessary
                    self.tasks = []
                    for task in loaded_tasks:
                        if isinstance(task, str):
                            # Convert old format to new format
                            self.tasks.append({
                                "task": task,
                                "priority": "Medium",
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
                            })
                        else:
                            self.tasks.append(task)
            else:
                self.tasks = []
        except:
            self.tasks = []

if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()