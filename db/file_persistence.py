import json
import os
from typing import Dict, List
from models.task import Task

# Path to store the task data
DATA_FILE = "tasks_data.json"

def save_tasks_to_file(signal_tasks: List[Task], noise_tasks: List[Task]) -> bool:
    """
    Save tasks to a local JSON file.
    Returns True if successful, False otherwise.
    """
    try:
        print(f"save_tasks_to_file called with {len(signal_tasks)} signal tasks, {len(noise_tasks)} noise tasks")
        data = {
            "signal": [task.dict() for task in signal_tasks],
            "noise": [task.dict() for task in noise_tasks]
        }
        
        print(f"About to write to {DATA_FILE}")
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        
        print("Successfully wrote to file")
        return True
    except Exception as e:
        print(f"Error saving tasks to file: {e}")
        return False

def load_tasks_from_file() -> Dict[str, List[Task]]:
    """
    Load tasks from the local JSON file.
    Returns dictionary with signal and noise task lists.
    If file doesn't exist or is invalid, returns empty lists.
    """
    try:
        if not os.path.exists(DATA_FILE):
            return {"signal": [], "noise": []}
        
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
        
        signal_tasks = [Task(**task_data) for task_data in data.get("signal", [])]
        noise_tasks = [Task(**task_data) for task_data in data.get("noise", [])]
        
        return {"signal": signal_tasks, "noise": noise_tasks}
    
    except Exception as e:
        print(f"Error loading tasks from file: {e}")
        return {"signal": [], "noise": []}

def clear_file_data() -> bool:
    """
    Clear the data file by removing it.
    Returns True if successful, False otherwise.
    """
    try:
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
        return True
    except Exception as e:
        print(f"Error clearing file data: {e}")
        return False