from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import engine, SessionLocal, Base
from models import TodoDB

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Todo API with CRUD")

# Pydantic model
class Todo(BaseModel):
    title: str
    description: str
    completed: bool

# DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------- CRUD Routes ----------------

# Create Todo
@app.post("/todos/")
def create_todo(todo: Todo, db: Session = Depends(get_db)):
    db_todo = TodoDB(title=todo.title, description=todo.description, completed=todo.completed)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return {"message": "Todo created!", "todo": {
        "id": db_todo.id,
        "title": db_todo.title,
        "description": db_todo.description,
        "completed": db_todo.completed
    }}

# Read all Todos
@app.get("/todos/")
def get_todos(db: Session = Depends(get_db)):
    todos = db.query(TodoDB).all()
    return {"todos": [{"id": t.id, "title": t.title, "description": t.description, "completed": t.completed} for t in todos]}

# Read single Todo by ID
@app.get("/todos/{todo_id}")
def get_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(TodoDB).filter(TodoDB.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"id": todo.id, "title": todo.title, "description": todo.description, "completed": todo.completed}

# Update Todo
@app.put("/todos/{todo_id}")
def update_todo(todo_id: int, updated_todo: Todo, db: Session = Depends(get_db)):
    todo = db.query(TodoDB).filter(TodoDB.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    todo.title = updated_todo.title
    todo.description = updated_todo.description
    todo.completed = updated_todo.completed
    db.commit()
    db.refresh(todo)
    return {"message": "Todo updated!", "todo": {
        "id": todo.id,
        "title": todo.title,
        "description": todo.description,
        "completed": todo.completed
    }}

# Delete Todo
@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(TodoDB).filter(TodoDB.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo)
    db.commit()
    return {"message": "Todo deleted!"}
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
