from pydantic import BaseModel
from typing import List

# Represents a single task item
class Task(BaseModel):
    id: str  # Unique identifier for the task
    text: str # The content of the task
    completed: bool = False # Whether the task is completed or not (default: False)
    ignored: bool = False # Whether the task is ignored and should not count towards ratio (default: False)
    order: int = 0 # Order position within the column (default: 0)

# Model for creating a new task (only needs the text)
class TaskCreate(BaseModel):
    text: str

# Model for updating an existing task (e.g., changing its text)
class TaskUpdate(BaseModel):
    text: str

# Model for toggling the completion status of a task
class TaskComplete(BaseModel):
    completed: bool

# Model for toggling the ignore status of a task
class TaskIgnore(BaseModel):
    ignored: bool

# Model for updating a task's position and column
class TaskMove(BaseModel):
    task_id: str
    new_column: str
    new_order: int

# Model for updating the complete state of both columns
class TasksState(BaseModel):
    signal: List[str]  # Ordered list of task IDs
    noise: List[str]   # Ordered list of task IDs

# Model for a list of tasks, used when fetching all tasks for a column
class TaskList(BaseModel):
    tasks: List[Task]
