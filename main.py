import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# --- CORS CONFIGURATION (ALLOWS MOBILE & WEB FRONTEND ACCESS) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows requests from any origin (GitHub Pages, mobile devices, etc.)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods: GET, POST, PUT, DELETE
    allow_headers=["*"],  # Allows all headers
)

ARCHIVODB = "tareas.json"

# --- FILE HANDLING (JSON DATABASE) ---
def leer_tareas():
    if not os.path.exists(ARCHIVODB):
        return []
    try:
        with open(ARCHIVODB, "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def guardar_tareas(tareas):
    with open(ARCHIVODB, "w", encoding="utf-8") as archivo:
        json.dump(tareas, archivo, indent=4, ensure_ascii=False)
# --------------------------------------------------

# --- DATA MODEL ---
class Tarea(BaseModel):
    id: int
    tarea: str
    completada: bool

# --- API ENDPOINTS / ROUTES ---

# 1. Get all tasks (GET)
@app.get("/tareas")
def obtener_tareas():
    return leer_tareas()

# 2. Create a new task (POST)
@app.post("/tareas")
def crear_tarea(nueva_tarea: Tarea):
    tareas = leer_tareas()
    tarea_dict = nueva_tarea.model_dump()
    tareas.append(tarea_dict)
    guardar_tareas(tareas)
    return {"message": "Task saved successfully!", "task": tarea_dict}

# 3. Update task completion status (PUT)
@app.put("/tareas/{tarea_id}")
def actualizar_tarea(tarea_id: str):  # Using str for flexible ID parsing from web clients
    tareas = leer_tareas()
    
    # Try converting the incoming ID to match internal storage formats
    try:
        id_buscado = int(tarea_id)
    except ValueError:
        id_buscado = tarea_id

    # Search for the task by comparing IDs strictly as strings
    for t in tareas:
        if str(t["id"]) == str(id_buscado):
            t["completada"] = not t["completada"]
            guardar_tareas(tareas)
            return {"message": "Task updated successfully", "task": t}
            
    raise HTTPException(status_code=404, detail="Specified task ID not found")

# 4. Delete a task (DELETE)
@app.delete("/tareas/{tarea_id}")
def eliminar_tarea(tarea_id: str):  # Using str here as well
    tareas = leer_tareas()
    
    try:
        id_buscado = int(tarea_id)
    except ValueError:
        id_buscado = tarea_id

    # Filter out the target task by comparing IDs as strings
    tareas_filtradas = [t for t in tareas if str(t["id"]) != str(id_buscado)]
    
    if len(tareas) == len(tareas_filtradas):
        raise HTTPException(status_code=404, detail="Task to delete not found")
        
    guardar_tareas(tareas_filtradas)
    return {"message": "Task deleted successfully"}