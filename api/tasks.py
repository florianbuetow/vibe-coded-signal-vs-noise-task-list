from fastapi import APIRouter, HTTPException, status
from models.task import Task, TaskCreate, TaskUpdate, TaskComplete, TaskIgnore, TaskList, TaskMove, TasksState
import db.in_memory_db
from db.file_persistence import clear_file_data
import uuid

router = APIRouter()


# Define the /stats endpoint first to ensure it's matched before the dynamic /{column} path
@router.get("/stats")
async def get_stats_api():
    """
    Returns the task counts for the progress bar calculation.
    Only counts non-ignored tasks for the ratio.
    This endpoint is accessed via /tasks/stats due to the router prefix.
    """
    print("FastAPI: /tasks/stats endpoint hit!")  # Added for debugging
    
    # Count only non-ignored tasks (handle backward compatibility)
    signal_count = len([task for task in db.in_memory_db.databases["signal"] if not getattr(task, 'ignored', False)])
    noise_count = len([task for task in db.in_memory_db.databases["noise"] if not getattr(task, 'ignored', False)])
    
    return {
        "signal_count": signal_count,
        "noise_count": noise_count,
    }


@router.post("/save")
async def save_to_file_api():
    """
    Saves current in-memory tasks to local file.
    Returns success status.
    """
    success = db.in_memory_db.save_current_state()
    if success:
        return {"message": "Tasks saved to file successfully"}
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save tasks to file")


@router.post("/load")
async def load_from_file_api():
    """
    Loads tasks from local file into memory.
    Returns the loaded tasks.
    """
    print("Load from file API called")
    try:
        print("Calling reload_from_file()...")
        db.in_memory_db.reload_from_file()
        print(f"After reload - Signal: {len(db.in_memory_db.databases['signal'])}, Noise: {len(db.in_memory_db.databases['noise'])}")
        result = {
            "message": "Tasks loaded from file successfully",
            "tasks": {
                "signal": [task.dict() for task in db.in_memory_db.databases["signal"]],
                "noise": [task.dict() for task in db.in_memory_db.databases["noise"]]
            }
        }
        print(f"Returning: {len(result['tasks']['signal'])} signal tasks, {len(result['tasks']['noise'])} noise tasks")
        return result
    except Exception as e:
        print(f"Error in load_from_file_api: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to load tasks from file: {str(e)}")


@router.post("/clear")
async def clear_all_data_api():
    """
    Clears all data from both memory and file.
    Returns success status.
    """
    try:
        # Clear in-memory data
        db.in_memory_db.databases["signal"].clear()
        db.in_memory_db.databases["noise"].clear()
        
        # Clear file data
        success = clear_file_data()
        
        if success:
            return {"message": "All data cleared successfully"}
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to clear file data")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to clear data: {str(e)}")


@router.get("/column/{column}", response_model=TaskList)
async def get_tasks_api(column: str):
    """
    Retrieves all tasks for a given column (signal or noise).
    Raises a 404 error if the column is invalid.
    """
    if column not in db.in_memory_db.databases:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid column")
    # Return tasks sorted by order
    sorted_tasks = sorted(db.in_memory_db.databases[column], key=lambda x: x.order)
    return {"tasks": sorted_tasks}


@router.post("/column/{column}", response_model=Task, status_code=status.HTTP_201_CREATED)
async def add_task_api(column: str, task_create: TaskCreate):
    """
    Adds a new task to a specific column.
    Expects a JSON body with a 'text' field.
    Returns the newly created task.
    """
    if column not in db.in_memory_db.databases:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid column")

    # Calculate the next order number (highest order + 1)
    max_order = max([task.order for task in db.in_memory_db.databases[column]], default=-1)
    new_task = Task(id=str(uuid.uuid4()), text=task_create.text, order=max_order + 1)

    db.in_memory_db.databases[column].append(new_task)
    
    # Auto-save to file
    db.in_memory_db.save_current_state()

    return new_task


# CRITICAL: Specific routes with suffixes must come BEFORE the general route
# FastAPI matches routes in order, so /column/{column}/{task_id}/complete and /ignore
# must be defined before /column/{column}/{task_id} to avoid conflicts

@router.put("/column/{column}/{task_id}/complete", response_model=Task)
async def toggle_complete_api(column: str, task_id: str, task_complete: TaskComplete):
    """
    Toggles the 'completed' status of a task in a specific column.
    Expects a JSON body with a 'completed' boolean field.
    Returns the updated task.
    """
    if column not in db.in_memory_db.databases:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid column")

    for i, task in enumerate(db.in_memory_db.databases[column]):
        if task.id == task_id:
            db.in_memory_db.databases[column][i].completed = task_complete.completed
            # Auto-save to file
            db.in_memory_db.save_current_state()
            return db.in_memory_db.databases[column][i]

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")


@router.put("/column/{column}/{task_id}/ignore", response_model=Task)
async def toggle_ignore_api(column: str, task_id: str, task_ignore: TaskIgnore):
    """
    Toggles the 'ignored' status of a task in a specific column.
    Ignored tasks are greyed out and don't count towards the ratio.
    Expects a JSON body with an 'ignored' boolean field.
    Returns the updated task.
    """
    print(f"Ignore API called for task {task_id} in column {column}, ignored={task_ignore.ignored}")
    
    if column not in db.in_memory_db.databases:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid column")

    for i, task in enumerate(db.in_memory_db.databases[column]):
        if task.id == task_id:
            print(f"Found task: {task.text}, current ignored status: {getattr(task, 'ignored', 'NOT_SET')}")
            
            # Ensure task has ignored field (for backward compatibility)
            if not hasattr(task, 'ignored'):
                task.ignored = False
                print("Added missing ignored field to task")
            
            db.in_memory_db.databases[column][i].ignored = task_ignore.ignored
            print(f"Updated task ignored status to: {task_ignore.ignored}")
            
            # Auto-save to file
            result = db.in_memory_db.save_current_state()
            print(f"Save result: {result}")
            return db.in_memory_db.databases[column][i]

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")


# General edit route - MUST come after specific routes with suffixes
@router.put("/column/{column}/{task_id}", response_model=Task)
async def edit_task_api(column: str, task_id: str, task_update: TaskUpdate):
    """
    Updates the text of an existing task in a specific column.
    Expects a JSON body with a 'text' field.
    Returns the updated task.
    """
    if column not in db.in_memory_db.databases:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid column")

    for i, task in enumerate(db.in_memory_db.databases[column]):
        if task.id == task_id:
            db.in_memory_db.databases[column][i].text = task_update.text
            # Auto-save to file
            db.in_memory_db.save_current_state()
            return db.in_memory_db.databases[column][i]

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")


@router.delete("/column/{column}/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task_api(column: str, task_id: str):
    """
    Deletes a task from a specific column.
    Returns a 204 No Content status on successful deletion.
    """
    print(f"Delete API called for task {task_id} in column {column}")
    
    if column not in db.in_memory_db.databases:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid column")

    initial_len = len(db.in_memory_db.databases[column])
    print(f"Before delete: {column} has {initial_len} tasks")
    
    db.in_memory_db.databases[column] = [task for task in db.in_memory_db.databases[column] if task.id != task_id]
    
    final_len = len(db.in_memory_db.databases[column])
    print(f"After delete: {column} has {final_len} tasks")

    if final_len == initial_len:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    # Auto-save to file
    print("Calling save_current_state()...")
    save_result = db.in_memory_db.save_current_state()
    print(f"Save result: {save_result}")

    return


@router.put("/bulk-update", response_model=dict)
async def bulk_update_tasks_api(tasks_state: TasksState):
    """
    Updates the complete state of both columns with reordered task IDs.
    Frontend sends the complete ordered list of task IDs for both columns.
    Backend persists the new order without any reordering logic.
    """
    print(f"Bulk update request - Signal: {tasks_state.signal}, Noise: {tasks_state.noise}")
    
    # Create a map of all existing tasks by ID for quick lookup
    all_tasks = {}
    for column_name, tasks in db.in_memory_db.databases.items():
        for task in tasks:
            all_tasks[task.id] = task
    
    # Validate that all task IDs exist
    all_provided_ids = set(tasks_state.signal + tasks_state.noise)
    all_existing_ids = set(all_tasks.keys())
    
    if all_provided_ids != all_existing_ids:
        missing_ids = all_existing_ids - all_provided_ids
        extra_ids = all_provided_ids - all_existing_ids
        error_msg = f"Task ID mismatch. Missing: {missing_ids}, Extra: {extra_ids}"
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)
    
    # Clear existing columns
    db.in_memory_db.databases["signal"].clear()
    db.in_memory_db.databases["noise"].clear()
    
    # Rebuild signal column with correct order
    for i, task_id in enumerate(tasks_state.signal):
        task = all_tasks[task_id]
        task.order = i
        db.in_memory_db.databases["signal"].append(task)
    
    # Rebuild noise column with correct order
    for i, task_id in enumerate(tasks_state.noise):
        task = all_tasks[task_id]
        task.order = i
        db.in_memory_db.databases["noise"].append(task)
    
    print(f"Bulk update completed - Signal: {len(tasks_state.signal)} tasks, Noise: {len(tasks_state.noise)} tasks")
    
    # Auto-save to file
    db.in_memory_db.save_current_state()
    
    return {
        "message": "Bulk update completed successfully",
        "signal_count": len(tasks_state.signal),
        "noise_count": len(tasks_state.noise)
    }
