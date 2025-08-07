from typing import List
from models.task import Task
from db.file_persistence import load_tasks_from_file, save_tasks_to_file

# Load existing data from file on startup
_loaded_data = load_tasks_from_file()

# In-memory "Database" for Signal tasks
# This list will hold Task objects for the "Signal" column.
# Now loads from file on startup if available.
signal_tasks_db: List[Task] = _loaded_data["signal"]

# In-memory "Database" for Noise tasks
# This list will hold Task objects for the "Noise" column.
# Now loads from file on startup if available.
noise_tasks_db: List[Task] = _loaded_data["noise"]

# A dictionary to easily access the task lists by column name
databases = {
    "signal": signal_tasks_db,
    "noise": noise_tasks_db,
}

def save_current_state():
    """Save current in-memory state to file"""
    print(f"Saving current state - Signal: {len(databases['signal'])} tasks, Noise: {len(databases['noise'])} tasks")
    result = save_tasks_to_file(databases["signal"], databases["noise"])
    if result:
        print("Successfully saved to file")
    else:
        print("Failed to save to file")
    return result

def reload_from_file():
    """Reload data from file into memory"""
    global signal_tasks_db, noise_tasks_db, databases
    loaded_data = load_tasks_from_file()
    
    # Clear and update the actual lists that databases points to
    databases["signal"].clear()
    databases["signal"].extend(loaded_data["signal"])
    databases["noise"].clear()
    databases["noise"].extend(loaded_data["noise"])
    
    print(f"Reloaded from file - Signal: {len(databases['signal'])} tasks, Noise: {len(databases['noise'])} tasks")
