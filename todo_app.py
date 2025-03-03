import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
import ttkbootstrap as ttk  # Modern styling
from typing import List, Dict
import logging
from functools import lru_cache
import threading
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='todo_app.log'
)

class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced TODO App")
        self.root.geometry("800x700")
        
        # Data storage with type hints
        self.tasks: List[Dict] = []
        self.data_file = Path('tasks.json')
        
        # Configure theme and style
        self.style = ttk.Style(theme='flatly')
        self.setup_ui()
        self.load_tasks()
        
    def setup_ui(self):
        """Setup the UI components with modern styling"""
        # Create main container with padding
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header = ttk.Label(
            self.main_frame, 
            text="Task Manager", 
            font=("Helvetica", 24),
            bootstyle="primary"
        )
        header.pack(pady=10)
        
        # Input area
        input_frame = ttk.LabelFrame(self.main_frame, text="Add New Task", padding="10")
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Task entry with validation
        task_frame = ttk.Frame(input_frame)
        task_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(task_frame, text="Task:").pack(side=tk.LEFT, padx=5)
        self.task_entry = ttk.Entry(task_frame, width=50)
        self.task_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Priority selection with modern combobox
        priority_frame = ttk.Frame(input_frame)
        priority_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(priority_frame, text="Priority:").pack(side=tk.LEFT, padx=5)
        self.priority_var = tk.StringVar(value="Medium")
        priority_combo = ttk.Combobox(
            priority_frame,
            textvariable=self.priority_var,
            values=["High", "Medium", "Low"],
            width=15,
            state="readonly",
            bootstyle="primary"
        )
        priority_combo.pack(side=tk.LEFT, padx=5)
        
        # Add button with modern styling
        self.add_button = ttk.Button(
            input_frame,
            text="Add Task",
            command=self.add_task,
            bootstyle="success"
        )
        self.add_button.pack(pady=5)
        
        # Task list with modern treeview
        list_frame = ttk.LabelFrame(self.main_frame, text="Tasks", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview with sorting capability
        columns = ("task", "priority", "timestamp")
        self.task_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show="headings",
            height=15,
            bootstyle="primary"
        )
        
        # Configure columns and headings
        self.task_tree.heading("task", text="Task", command=lambda: self.sort_tasks("task"))
        self.task_tree.heading("priority", text="Priority", command=lambda: self.sort_tasks("priority"))
        self.task_tree.heading("timestamp", text="Created At", command=lambda: self.sort_tasks("timestamp"))
        
        self.task_tree.column("task", width=400, minwidth=200)
        self.task_tree.column("priority", width=100, minwidth=100)
        self.task_tree.column("timestamp", width=150, minwidth=150)
        
        # Scrollbar with modern styling
        scrollbar = ttk.Scrollbar(
            list_frame,
            orient=tk.VERTICAL,
            command=self.task_tree.yview,
            bootstyle="primary-round"
        )
        self.task_tree.configure(yscrollcommand=scrollbar.set)
        
        self.task_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Control buttons with modern styling
        control_frame = ttk.Frame(self.main_frame)
        control_frame.pack(pady=10)
        
        self.delete_button = ttk.Button(
            control_frame,
            text="Delete Selected",
            command=self.delete_task,
            bootstyle="danger"
        )
        self.delete_button.pack(side=tk.LEFT, padx=5)
        
        # Bind events
        self.task_entry.bind('<Return>', lambda e: self.add_task())
        self.task_tree.bind('<Delete>', lambda e: self.delete_task())
        
    @lru_cache(maxsize=None)
    def sort_tasks(self, column: str) -> None:
        """Sort tasks by column with caching for performance"""
        try:
            items = [(self.task_tree.set(item, column), item) for item in self.task_tree.get_children('')]
            items.sort()
            for index, (_, item) in enumerate(items):
                self.task_tree.move(item, '', index)
        except Exception as e:
            logging.error(f"Error sorting tasks: {str(e)}")
            messagebox.showerror("Error", "Failed to sort tasks")

    def add_task(self) -> None:
        """Add a new task with error handling"""
        try:
            task = self.task_entry.get().strip()
            if not task:
                messagebox.showwarning("Warning", "Please enter a task")
                return
                
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            priority = self.priority_var.get()
            
            new_task = {
                "task": task,
                "priority": priority,
                "timestamp": timestamp
            }
            
            self.tasks.append(new_task)
            self.refresh_task_list()
            self.task_entry.delete(0, tk.END)
            
            # Save in background thread
            threading.Thread(target=self.save_tasks, daemon=True).start()
            
        except Exception as e:
            logging.error(f"Error adding task: {str(e)}")
            messagebox.showerror("Error", "Failed to add task")
    
    def delete_task(self) -> None:
        """Delete selected tasks with confirmation and error handling"""
        try:
            selection = self.task_tree.selection()
            if not selection:
                messagebox.showinfo("Info", "Please select a task to delete")
                return
                
            if messagebox.askyesno("Confirm", "Are you sure you want to delete the selected task(s)?"):
                for item in selection:
                    index = self.task_tree.index(item)
                    del self.tasks[index]
                self.refresh_task_list()
                
                # Save in background thread
                threading.Thread(target=self.save_tasks, daemon=True).start()
                
        except Exception as e:
            logging.error(f"Error deleting task: {str(e)}")
            messagebox.showerror("Error", "Failed to delete task")
    
    def refresh_task_list(self) -> None:
        """Refresh the task list with error handling"""
        try:
            for item in self.task_tree.get_children():
                self.task_tree.delete(item)
            
            for task in self.tasks:
                values = (task["task"], task["priority"], task["timestamp"])
                item = self.task_tree.insert("", tk.END, values=values)
                
                # Set tag for priority color
                priority_tag = task["priority"].lower()
                self.task_tree.tag_configure(
                    priority_tag,
                    background=self.get_priority_color(task["priority"])
                )
                self.task_tree.item(item, tags=(priority_tag,))
        except Exception as e:
            logging.error(f"Error refreshing task list: {str(e)}")
            messagebox.showerror("Error", "Failed to refresh task list")
    
    @staticmethod
    def get_priority_color(priority: str) -> str:
        """Get color for priority level"""
        colors = {
            "High": "#ffe6e6",
            "Medium": "#fff4e6",
            "Low": "#e6ffe6"
        }
        return colors.get(priority, "#ffffff")
    
    def save_tasks(self) -> None:
        """Save tasks to file with error handling"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.tasks, f, indent=2)
            logging.info("Tasks saved successfully")
        except Exception as e:
            logging.error(f"Error saving tasks: {str(e)}")
            messagebox.showerror("Error", "Failed to save tasks")
    
    def load_tasks(self) -> None:
        """Load tasks from file with error handling"""
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r') as f:
                    loaded_tasks = json.load(f)
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
                self.refresh_task_list()
                logging.info("Tasks loaded successfully")
            else:
                self.tasks = []
        except Exception as e:
            logging.error(f"Error loading tasks: {str(e)}")
            messagebox.showerror("Error", "Failed to load tasks")
            self.tasks = []

def main():
    try:
        root = ttk.Window(themename="flatly")
        app = TodoApp(root)
        root.mainloop()
    except Exception as e:
        logging.critical(f"Application failed to start: {str(e)}")
        messagebox.showerror("Critical Error", "Application failed to start")

if __name__ == "__main__":
    main()