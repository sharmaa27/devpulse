from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="DevPulse")

# in-memory store (fine for now; we'll discuss why it's bad later)
tasks: dict[int, dict] = {}
next_id = 1


class TaskIn(BaseModel):
    title: str
    done: bool = False


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/tasks", status_code=201)
def create_task(task: TaskIn):
    global next_id
    task_id = next_id
    tasks[task_id] = {"id": task_id, **task.model_dump()}
    next_id += 1
    return tasks[task_id]


@app.get("/tasks")
def list_tasks():
    return list(tasks.values())


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="not found")
    return tasks[task_id]


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="not found")
    del tasks[task_id]


@app.get("/stats")
def stats():
    total = len(tasks)
    done = sum(1 for t in tasks.values() if t["done"])
    return {"total": total, "done": done, "pending": total - done}
