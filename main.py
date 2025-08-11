from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os

# Import the API router from api.tasks
from api.tasks import router as tasks_router

app = FastAPI()

# Create a 'static' directory if it doesn't exist
static_dir = "static"
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

# Create a custom StaticFiles class with no-cache headers
from fastapi.staticfiles import StaticFiles
from fastapi import Request
from fastapi.responses import FileResponse
import time

class NoCacheStaticFiles(StaticFiles):
    def file_response(self, *args, **kwargs) -> FileResponse:
        response = super().file_response(*args, **kwargs)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache" 
        response.headers["Expires"] = "0"
        return response

# Mount static files with no-cache headers
app.mount("/static", NoCacheStaticFiles(directory=static_dir), name="static")

# Include the tasks router
# All routes defined in tasks_router will be prefixed with "/tasks".
app.include_router(tasks_router, prefix="/tasks", tags=["tasks"])
print("FastAPI: tasks_router included with prefix '/tasks'") # Added for debugging confirmation

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """
    Serves the main HTML page.
    """
    # Construct the full path to index.html
    index_html_path = os.path.join(static_dir, "index.html")

    # Ensure index.html exists for the initial run or if it's missing
    # In a real deployment, these static files would be part of your build process.
    if not os.path.exists(index_html_path):
        # This block creates the static files if they don't exist.
        # It's primarily for convenience when running the app for the first time.
        # In a production environment, you would ensure these files are pre-built.
        print(f"Creating {index_html_path}...")
        with open(index_html_path, "w") as f:
            f.write("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Focus on the Signal</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>

    <h1 class="app-title">Focus on the Signal</h1>

    <div class="container">
        <div class="column-wrapper">
            <h2 class="column-title">Signal</h2>
            <div class="column">
                <div class="task-input-container">
                    <input type="text" class="task-input" id="signal-input" placeholder="Add a signal task... (Press Enter)">
                </div>
                <ul id="signal-list"></ul>
            </div>
        </div>

        <div class="column-wrapper">
            <h2 class="column-title">Noise</h2>
            <div class="column">
                <div class="task-input-container">
                    <input type="text" class="task-input" id="noise-input" placeholder="Add a noise task... (Press Enter)">
                </div>
                <ul id="noise-list"></ul>
            </div>
        </div>
    </div>

    <div class="progress-container">
        <div class="progress-bar-label" id="progress-label">Signal: 0% | Noise: 0%</div>
        <div class="progress-bar-wrapper">
            <div class="progress-bar-fill" id="progress-bar" style="width: 0%;"></div>
        </div>
        <div class="control-buttons">
            <button id="clear-btn" class="control-button clear-button" onclick="clearAllData()">Clear All Data</button>
            <div class="right-buttons">
                <button id="download-btn" class="control-button download-button" onclick="downloadMarkdown()">Download</button>
                <button id="reload-btn" class="control-button reload-button" onclick="reloadFromDisk()">Reload from Disk</button>
            </div>
        </div>
    </div>

    <script src="/static/script.js?v={int(time.time())}"></script>
</body>
</html>
                    """)
        # Create style.css if it doesn't exist
        style_css_path = os.path.join(static_dir, "style.css")
        print(f"Creating {style_css_path}...")
        with open(style_css_path, "w") as f:
            f.write("""
/* Claude.ai inspired design system */
:root {
    --claude-bg: #f7f7f7;
    --claude-surface: #ffffff;
    --claude-surface-hover: #f8f9fa;
    --claude-border: #e5e7eb;
    --claude-border-hover: #d1d5db;
    --claude-text-primary: #1f2937;
    --claude-text-secondary: #6b7280;
    --claude-text-muted: #9ca3af;
    --claude-accent: #d97706;
    --claude-accent-hover: #b45309;
    --claude-accent-light: #fed7aa;
    --claude-success: #059669;
    --claude-success-hover: #047857;
    --claude-success-light: #d1fae5;
    --claude-danger: #dc2626;
    --claude-danger-hover: #b91c1c;
    --claude-danger-light: #fee2e2;
    --claude-shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
    --claude-shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
    --claude-radius: 8px;
    --claude-radius-lg: 12px;
    --claude-spacing: 16px;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    background-color: var(--claude-bg);
    color: var(--claude-text-primary);
    margin: 0;
    padding: var(--claude-spacing);
    line-height: 1.6;
    font-size: 14px;
}

.app-title {
    text-align: center;
    font-size: 2.25rem;
    font-weight: 700;
    color: var(--claude-text-primary);
    margin: 0 0 2rem 0;
    letter-spacing: -0.025em;
}

.container {
    display: flex;
    gap: 1.5rem;
    max-width: 1200px;
    margin: 0 auto;
    flex-wrap: wrap;
}

.column {
    flex: 1;
    min-width: 300px;
    background-color: var(--claude-surface);
    padding: 1.5rem;
    border-radius: var(--claude-radius-lg);
    border: 1px solid var(--claude-border);
    box-shadow: var(--claude-shadow-sm);
    transition: all 0.15s ease;
}

.column:hover {
    box-shadow: var(--claude-shadow-md);
    border-color: var(--claude-border-hover);
}

.column-title {
    text-align: center;
    font-size: 1.25rem;
    font-weight: 600;
    margin: 0 0 1.5rem 0;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid var(--claude-border);
    color: var(--claude-text-primary);
}

.task-input-container {
    display: flex;
    gap: 0.75rem;
    margin-bottom: 1.25rem;
}

.task-input {
    flex: 1;
    padding: 0.75rem 1rem;
    border: 1px solid var(--claude-border);
    border-radius: var(--claude-radius);
    font-size: 0.875rem;
    color: var(--claude-text-primary);
    background-color: var(--claude-surface);
    transition: all 0.15s ease;
}

.task-input:focus {
    outline: none;
    border-color: var(--claude-accent);
    box-shadow: 0 0 0 3px var(--claude-accent-light);
}

.task-input::placeholder {
    color: var(--claude-text-muted);
}

.add-button {
    padding: 0.75rem 1.25rem;
    background-color: var(--claude-accent);
    color: white;
    border: none;
    border-radius: var(--claude-radius);
    cursor: pointer;
    font-size: 0.875rem;
    font-weight: 500;
    transition: all 0.15s ease;
    white-space: nowrap;
}

.add-button:hover {
    background-color: var(--claude-accent-hover);
    transform: translateY(-1px);
}

.add-button:active {
    transform: translateY(0);
}

ul {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.task-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.875rem;
    background-color: var(--claude-surface);
    border: 1px solid var(--claude-border);
    border-radius: var(--claude-radius);
    transition: all 0.15s ease;
    font-size: 0.875rem;
    cursor: grab;
}

.task-item:active {
    cursor: grabbing;
}

.task-item:hover {
    background-color: var(--claude-surface-hover);
    border-color: var(--claude-border-hover);
    transform: translateY(-1px);
    box-shadow: var(--claude-shadow-sm);
}

.task-item:hover .task-actions {
    opacity: 1;
    transform: translateX(0);
}

.task-item.dragging {
    opacity: 0.5;
}

.drag-handle {
    color: var(--claude-text-muted);
    font-size: 0.875rem;
    line-height: 1;
    cursor: grab;
    user-select: none;
    opacity: 0;
    transition: opacity 0.15s ease;
}

.task-item:hover .drag-handle {
    opacity: 1;
}

.task-text {
    flex: 1;
    word-break: break-word;
    color: var(--claude-text-primary);
}

.task-text.completed {
    text-decoration: line-through;
    color: var(--claude-text-muted);
}

.task-checkbox {
    width: 18px;
    height: 18px;
    cursor: pointer;
    accent-color: var(--claude-accent);
}

.task-actions {
    display: flex;
    gap: 0.5rem;
    margin-left: auto;
}

.edit-button, .delete-button {
    padding: 0.375rem 0.75rem;
    font-size: 0.75rem;
    border: none;
    border-radius: calc(var(--claude-radius) * 0.75);
    cursor: pointer;
    font-weight: 500;
    transition: all 0.15s ease;
}

.edit-button {
    background-color: var(--claude-accent-light);
    color: var(--claude-accent);
}

.edit-button:hover {
    background-color: var(--claude-accent);
    color: white;
}

.delete-button {
    background-color: var(--claude-danger-light);
    color: var(--claude-danger);
}

.delete-button:hover {
    background-color: var(--claude-danger);
    color: white;
}

.control-buttons {
    display: flex;
    justify-content: center;
    gap: 1rem;
    margin: 2rem 0;
    max-width: 1200px;
    margin-left: auto;
    margin-right: auto;
}

.control-button {
    padding: 0.75rem 1.5rem;
    font-size: 0.875rem;
    border: none;
    border-radius: var(--claude-radius);
    cursor: pointer;
    font-weight: 500;
    transition: all 0.15s ease;
    position: relative;
    overflow: hidden;
}

.control-button:hover {
    transform: translateY(-2px);
    box-shadow: var(--claude-shadow-md);
}

.control-button:active {
    transform: translateY(-1px);
}

.clear-button {
    background-color: var(--claude-danger);
    color: white;
}

.clear-button:hover {
    background-color: var(--claude-danger-hover);
}

.reload-button {
    background-color: var(--claude-success);
    color: white;
}

.reload-button:hover {
    background-color: var(--claude-success-hover);
}

.progress-container {
    margin-top: 2rem;
    text-align: center;
    max-width: 1200px;
    margin-left: auto;
    margin-right: auto;
}

.progress-bar-label {
    font-weight: 600;
    font-size: 1rem;
    margin-bottom: 0.75rem;
    color: var(--claude-text-primary);
}

.progress-bar-wrapper {
    background-color: var(--claude-border);
    border-radius: calc(var(--claude-radius) * 2);
    height: 24px;
    overflow: hidden;
    position: relative;
}

.progress-bar-fill {
    height: 100%;
    transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1), background-color 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 500;
    font-size: 0.75rem;
    background-color: var(--claude-text-secondary);
    position: relative;
}

.progress-bar-fill.green {
    background-color: var(--claude-success);
}

.progress-bar-fill.red {
    background-color: var(--claude-danger);
}

/* Responsive design */
@media (max-width: 768px) {
    .container {
        flex-direction: column;
    }
    
    .control-buttons {
        flex-direction: column;
        align-items: center;
    }
    
    .task-input-container {
        flex-direction: column;
    }
    
    .add-button {
        align-self: flex-start;
    }
}

/* Focus styles for accessibility */
.control-button:focus-visible,
.add-button:focus-visible,
.edit-button:focus-visible,
.delete-button:focus-visible {
    outline: 2px solid var(--claude-accent);
    outline-offset: 2px;
}

.task-checkbox:focus-visible {
    outline: 2px solid var(--claude-accent);
    outline-offset: 2px;
}
                    """)
        # Create script.js if it doesn't exist
        script_js_path = os.path.join(static_dir, "script.js")
        print(f"Creating {script_js_path}...")
        with open(script_js_path, "w") as f:
            f.write("""
const API_URL = window.location.origin; // Dynamically gets the base URL of your application

// Event listener to fetch and render tasks when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    fetchAndRenderTasks('signal'); // Load tasks for the 'Signal' column
    fetchAndRenderTasks('noise');  // Load tasks for the 'Noise' column
    updateProgressBar();           // Initialize the progress bar
});

/**
 * Fetches tasks for a given column from the API and renders them in the UI.
 * @param {string} column - The column name ('signal' or 'noise').
 */
async function fetchAndRenderTasks(column) {
    try {
        const response = await fetch(`${API_URL}/tasks/${column}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        const list = document.getElementById(`${column}-list`);
        list.innerHTML = ''; // Clear existing tasks to prevent duplicates on re-render

        // Append each task to the appropriate list in the DOM
        data.tasks.forEach(task => {
            list.appendChild(createTaskElement(task, column));
        });
    } catch (error) {
        console.error(`Error fetching tasks for ${column}:`, error);
        // Optionally, display an error message to the user
    }
}

/**
 * Creates an individual task list item (<li>) element.
 * @param {object} task - The task object with id, text, and completed properties.
 * @param {string} column - The column name ('signal' or 'noise').
 * @returns {HTMLElement} The created <li> element.
 */
function createTaskElement(task, column) {
    const li = document.createElement('li');
    li.className = 'task-item';
    li.dataset.id = task.id; // Store task ID in a data attribute for easy access

    // Checkbox for marking task as complete/incomplete
    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.className = 'task-checkbox';
    checkbox.checked = task.completed;
    checkbox.onchange = () => toggleTaskCompleted(task.id, column, checkbox.checked);

    // Span to display task text
    const textSpan = document.createElement('span');
    textSpan.className = 'task-text' + (task.completed ? ' completed' : '');
    textSpan.textContent = task.text;

    // Container for action buttons (Edit, Delete)
    const actionsDiv = document.createElement('div');
    actionsDiv.className = 'task-actions';

    // Edit button
    const editButton = document.createElement('button');
    editButton.className = 'edit-button';
    editButton.textContent = 'Edit';
    editButton.onclick = () => editTask(task.id, column, textSpan);

    // Delete button
    const deleteButton = document.createElement('button');
    deleteButton.className = 'delete-button';
    deleteButton.textContent = 'Delete';
    deleteButton.onclick = () => deleteTask(task.id, column);

    // Append buttons to actions container
    actionsDiv.appendChild(editButton);
    actionsDiv.appendChild(deleteButton);

    // Append all elements to the list item
    li.appendChild(checkbox);
    li.appendChild(textSpan);
    li.appendChild(actionsDiv);

    return li;
}

/**
 * Adds a new task to the specified column.
 * @param {string} column - The column name ('signal' or 'noise').
 */
async function addTask(column) {
    const input = document.getElementById(`${column}-input`);
    const text = input.value.trim(); // Get and trim the input text

    if (text) { // Only proceed if the input is not empty
        try {
            // Send a POST request with a JSON body
            const response = await fetch(`${API_URL}/tasks/${column}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: text }) // Send text as JSON
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            input.value = ''; // Clear the input field after successful addition
            await fetchAndRenderTasks(column); // Re-fetch and render to update the list
            updateProgressBar(); // Update the progress bar as task counts have changed
        } catch (error) {
            console.error(`Error adding task to ${column}:`, error);
            // Optionally, display an error message to the user
        }
    }
}

/**
 * Deletes a task from the specified column.
 * @param {string} taskId - The ID of the task to delete.
 * @param {string} column - The column name ('signal' or 'noise').
 */
async function deleteTask(taskId, column) {
    try {
        const response = await fetch(`${API_URL}/tasks/${column}/${taskId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        await fetchAndRenderTasks(column); // Re-fetch and render to update the list
        updateProgressBar(); // Update the progress bar as task counts have changed
    } catch (error) {
        console.error(`Error deleting task from ${column}:`, error);
        // Optionally, display an error message to the user
    }
}

/**
 * Edits the text of an existing task.
 * @param {string} taskId - The ID of the task to edit.
 * @param {string} column - The column name ('signal' or 'noise').
 * @param {HTMLElement} textSpan - The span element containing the task text.
 */
async function editTask(taskId, column, textSpan) {
    const newText = prompt("Edit the task:", textSpan.textContent); // Prompt user for new text

    if (newText !== null && newText.trim() !== "") { // If user entered new text and didn't cancel
        try {
            const response = await fetch(`${API_URL}/tasks/${column}/${taskId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: newText.trim() }) // Send new text as JSON
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            textSpan.textContent = newText.trim(); // Update the text directly in the DOM for immediate feedback
            // No need to re-fetch all tasks for just a text edit, but update progress bar if needed
            updateProgressBar();
        } catch (error) {
            console.error(`Error editing task in ${column}:`, error);
            // Optionally, display an error message to the user
        }
    }
}

/**
 * Toggles the completion status of a task.
 * @param {string} taskId - The ID of the task to toggle.
 * @param {string} column - The column name ('signal' or 'noise').
 * @param {boolean} isCompleted - The new completion status.
 */
async function toggleTaskCompleted(taskId, column, isCompleted) {
    try {
        const response = await fetch(`${API_URL}/tasks/${column}/${taskId}/complete`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ completed: isCompleted }) // Send completion status as JSON
        });

        if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

        // Re-fetch to apply strikethrough/un-strikethrough and keep UI consistent
        await fetchAndRenderTasks(column);
        updateProgressBar(); // Update progress bar (though completion doesn't change counts, it's good practice)
    } catch (error) {
        console.error(`Error toggling task completion in ${column}:`, error);
        // Optionally, display an error message to the user
    }
}

/**
 * Updates the progress bar based on the ratio of signal to noise tasks.
 */
async function updateProgressBar() {
    try {
        // Get current data from localStorage or fetch from API
        const localData = loadFromLocalStorage();
        if (localData && localData.signal && localData.noise) {
            updateProgressBarFromData(localData);
        } else {
            // Fallback: fetch current data from API
            const signalResponse = await fetch(`${API_URL}/tasks/column/signal`);
            const noiseResponse = await fetch(`${API_URL}/tasks/column/noise`);
            
            if (signalResponse.ok && noiseResponse.ok) {
                const signalData = await signalResponse.json();
                const noiseData = await noiseResponse.json();
                const data = {
                    signal: signalData.tasks,
                    noise: noiseData.tasks
                };
                updateProgressBarFromData(data);
            } else {
                throw new Error('Failed to fetch task data');
            }
        }
    } catch (error) {
        console.error('Error updating progress bar:', error);
        // Fallback to a neutral state if data can't be loaded
        const progressBar = document.getElementById('progress-bar');
        const progressLabel = document.getElementById('progress-label');
        progressBar.style.width = '0%';
        progressLabel.textContent = 'Error loading stats';
        progressBar.className = 'progress-bar-fill';
    }
}

                    """)

    # Open index.html and return its content
    with open(index_html_path, "r") as f:
        return HTMLResponse(content=f.read())

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
