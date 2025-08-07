# Focus on the Signal

This is a lightweight task management tool based on the signal-to-noise productivity principle, embraced by Steve Jobs. The app helps you categorize tasks into "Signal" (important) and "Noise" (less important) columns, with a visual progress bar showing the ratio of signal to noise tasks.

## Prerequisites

Before running the application, make sure you have the following installed:

- **Python 3.13+**: Required for running the FastAPI application
- **uv**: Python package manager and virtual environment tool
  - Install via: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **Docker** (optional): For containerized deployment
  - Download from: https://www.docker.com/products/docker-desktop/

## Installation & Usage

### Local Development

```bash
# Install dependencies and run the application
make run

# Or manually:
uv sync                    # Install dependencies
uv run uvicorn main:app --host 127.0.0.1 --port 8000    # Start server
```

The application will be available at http://127.0.0.1:8000

### Docker Deployment

```bash
# Build Docker image and run container
make build

# Or manually:
docker build -t signal-vs-noise .
docker run -d -p 8000:8000 --name signal-vs-noise-container signal-vs-noise
```

## Make Targets

| Target | Description |
|--------|-------------|
| `make init` | Install dependencies using uv |
| `make run` | Install dependencies and start the development server |
| `make stop` | Stop any process running on port 8000 |
| `make build` | Build Docker image, run container, and open the UI |
| `make destroy` | Stop Docker container and delete the Docker image |

## Features

- **Dual-column task management**: Organize tasks into Signal (important) and Noise (less important)
- **Visual progress tracking**: Color-coded progress bar (red when noise > 20%, green when signal ≥ 80%)
- **Task operations**: Add, edit, delete, and mark tasks as complete
- **Dual persistence**: Data saved to both browser localStorage and server-side JSON file
- **Real-time updates**: Progress bar updates automatically as you manage tasks
- **Responsive design**: Works on desktop and mobile devices

## Usage

1. **Adding tasks**: Type in the input field and press Enter, or click the Add button
2. **Editing tasks**: Click the "Edit" button on any task
3. **Completing tasks**: Check the checkbox to mark tasks as done
4. **Deleting tasks**: Click the "Delete" button to remove tasks
5. **Data management**: Use "Clear All Data" to reset everything or "Reload from Disk" to sync with saved data
6. **Export**: Click "Download" to export your tasks as a Markdown file

## Architecture

- **Backend**: FastAPI with Python 3.13+
- **Frontend**: Vanilla JavaScript with modern async/await patterns
- **Data**: In-memory storage with JSON file persistence
- **Styling**: CSS with a clean, professional design inspired by Claude.ai

## API Endpoints

- `GET /` - Serve the main HTML interface
- `GET /tasks/{column}` - Get tasks for signal/noise columns
- `POST /tasks/{column}` - Add new task
- `PUT /tasks/{column}/{task_id}` - Edit task text
- `PUT /tasks/{column}/{task_id}/complete` - Toggle task completion
- `DELETE /tasks/{column}/{task_id}` - Delete task
- `GET /tasks/stats` - Get task statistics for progress bar
