from typing import List, Optional
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, status
from sqlmodel import SQLModel, Field, Session, create_engine, select

# --- 1. Database Model (Table Structure) ---
class Memory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: str
    category: str = "General"
    created_at: datetime = Field(default_factory=datetime.now)

# --- 2. Database Connection ---
sqlite_url = "sqlite:///lumina_vault.db"
engine = create_engine(sqlite_url)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(title="Lumina AI Vault", version="1.0.0", lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 3. RESTful Endpoints ---

# CREATE: Nayi memory save karna
@app.post("/memories", response_model=Memory, status_code=status.HTTP_201_CREATED)
async def create_memory(memory: Memory):
    with Session(engine) as session:
        session.add(memory)
        session.commit()
        session.refresh(memory)
        return memory

# READ ALL: Saari memories dekhna
@app.get("/memories", response_model=List[Memory])
async def read_memories():
    with Session(engine) as session:
        memories = session.exec(select(Memory)).all()
        return memories

# READ ONE: Kisi ek specific memory ko ID se dhoondna
@app.get("/memories/{memory_id}", response_model=Memory)
async def read_memory(memory_id: int):
    with Session(engine) as session:
        memory = session.get(Memory, memory_id)
        if not memory:
            raise HTTPException(status_code=404, detail="Memory not found")
        return memory

# UPDATE: Purani memory ko edit karna
@app.put("/memories/{memory_id}", response_model=Memory)
async def update_memory(memory_id: int, updated_data: Memory):
    with Session(engine) as session:
        db_memory = session.get(Memory, memory_id)
        if not db_memory:
            raise HTTPException(status_code=404, detail="Memory not found")
        
        # Data update kar rahe hain
        db_memory.title = updated_data.title
        db_memory.content = updated_data.content
        db_memory.category = updated_data.category
        
        session.add(db_memory)
        session.commit()
        session.refresh(db_memory)
        return db_memory

# DELETE: Memory mita dena
@app.delete("/memories/{memory_id}")
async def delete_memory(memory_id: int):
    with Session(engine) as session:
        memory = session.get(Memory, memory_id)
        if not memory:
            raise HTTPException(status_code=404, detail="Memory not found")
        
        session.delete(memory)
        session.commit()
        return {"message": f"Memory {memory_id} deleted successfully"}