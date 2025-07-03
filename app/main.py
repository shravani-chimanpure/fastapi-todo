# app/main.py
# -----------------------------------------
# A minimal FastAPI “to‑do list” service.
# Keeps data in memory (dictionary) so it resets
# every time the server restarts. Perfect for learning!
#
# Endpoints
# ─────────
#   • GET  /                 – welcome message
#   • POST /todos            – create a new task
#   • GET  /todos            – list all tasks
#   • GET  /todos/{id}       – get one task
#   • PUT  /todos/{id}       – replace / edit a task
#   • DELETE /todos/{id}     – delete a task
#
# Run locally:
#   uvicorn app.main:app --reload
#
# Swagger UI will be at http://127.0.0.1:8000/docs
# -----------------------------------------

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
import itertools

app = FastAPI(title="Simple To‑Do API")

# ── Pydantic models ────────────────────────────────────────────────────────────
class TodoIn(BaseModel):
    title: str
    description: Optional[str] = None

class TodoOut(TodoIn):
    id: int


# ── In‑memory “database” ───────────────────────────────────────────────────────
_todos: dict[int, TodoIn] = {}
_id_counter = itertools.count(1)


# ── Routes ─────────────────────────────────────────────────────────────────────
@app.get("/")
def root() -> dict[str, str]:
    """Basic healthcheck / welcome route."""
    return {"message": "Welcome to the FastAPI To‑Do App 🎉"}


@app.post("/todos", response_model=TodoOut, status_code=status.HTTP_201_CREATED)
def create_todo(todo: TodoIn) -> TodoOut:
    """Add a new to‑do item."""
    todo_id = next(_id_counter)
    _todos[todo_id] = todo
    return TodoOut(id=todo_id, **todo.dict())


@app.get("/todos", response_model=List[TodoOut])
def list_todos() -> List[TodoOut]:
    """Return all tasks."""
    return [TodoOut(id=i, **t.dict()) for i, t in _todos.items()]


@app.get("/todos/{todo_id}", response_model=TodoOut)
def get_todo(todo_id: int) -> TodoOut:
    """Get one task by ID."""
    if todo_id not in _todos:
        raise HTTPException(status_code=404, detail="Todo not found")
    return TodoOut(id=todo_id, **_todos[todo_id].dict())


@app.put("/todos/{todo_id}", response_model=TodoOut)
def update_todo(todo_id: int, todo: TodoIn) -> TodoOut:
    """Replace an existing task entirely."""
    if todo_id not in _todos:
        raise HTTPException(status_code=404, detail="Todo not found")
    _todos[todo_id] = todo
    return TodoOut(id=todo_id, **todo.dict())


@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int) -> None:
    """Delete a task."""
    if todo_id not in _todos:
        raise HTTPException(status_code=404, detail="Todo not found")
    del _todos[todo_id]
    # Returning None lets FastAPI send an empty 204 response body.
