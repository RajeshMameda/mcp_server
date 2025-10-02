import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from datetime import datetime


app = FastAPI(title="Async Task API", 
              description="A simple async API example with FastAPI and asyncio",
              version="1.0.0")


class Task(BaseModel):
    id: int
    title: str
    description: str
    completed: bool = False
    created_at: Optional[datetime] = None

# In-memory storage for demonstration
tasks_db = []

# Simulate async database operation
async def simulate_db_operation(delay: float = 0.5):
    """Simulate a database operation with a delay"""
    await asyncio.sleep(delay)

# Create a new task
@app.post("/tasks/", response_model=Task, status_code=201)
async def create_task(task: Task):
    """Create a new task"""
    task.created_at = datetime.utcnow()
    tasks_db.append(task.dict())
    await simulate_db_operation()  # Simulate async DB operation
    return task

# Get all tasks
@app.get("/tasks/", response_model=List[Task])
async def read_tasks():
    """Get all tasks"""
    await simulate_db_operation(0.2)  # Simulate async DB operation
    return tasks_db

# Get a specific task by ID
@app.get("/tasks/{task_id}", response_model=Task)
async def read_task(task_id: int):
    """Get a specific task by ID"""
    await simulate_db_operation(0.2)
    for task in tasks_db:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail="Task not found")

# Update a task
@app.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: int, updated_task: Task):
    """Update a task by ID"""
    await simulate_db_operation(0.3)
    for idx, task in enumerate(tasks_db):
        if task["id"] == task_id:
            updated_task_data = updated_task.dict()
            updated_task_data["created_at"] = task["created_at"]  # Preserve creation time
            tasks_db[idx] = updated_task_data
            return tasks_db[idx]
    raise HTTPException(status_code=404, detail="Task not found")

# Delete a task
@app.delete("/tasks/{task_id}", status_code=204)
async def delete_task(task_id: int):
    """Delete a task by ID"""
    await simulate_db_operation(0.2)
    for idx, task in enumerate(tasks_db):
        if task["id"] == task_id:
            tasks_db.pop(idx)
            return
    raise HTTPException(status_code=404, detail="Task not found")

# Run the server
if __name__ == "__main__":
    uvicorn.run("data:app", host="0.0.0.0", port=8000, reload=True)
    