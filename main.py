import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ARCHIVODB = "tareas.json"

# --- MANEJO DE ARCHIVOS ---
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
# ---------------------------

class Tarea(BaseModel):
    id: int
    tarea: str
    completada: bool

@app.get("/tareas")
def obtener_tareas():
    return leer_tareas()

@app.post("/tareas")
def crear_tarea(nueva_tarea: Tarea):
    tareas = leer_tareas()
    tarea_dict = nueva_tarea.model_dump()
    tareas.append(tarea_dict)
    guardar_tareas(tareas)
    return {"mensaje": "¡Tarea guardada!", "tarea": tarea_dict}

# 3. Endpoint PUT: Actualizar el estado de una tarea (Completada o no)
@app.put("/tareas/{tarea_id}")
def actualizar_tarea(tarea_id: int):
    tareas = leer_tareas()
    
    # Buscamos la tarea por su ID
    for t in tareas:
        if t["id"] == tarea_id:
            # Volteamos el valor booleano: si era False pasa a True, y viceversa
            t["completada"] = not t["completada"]
            guardar_tareas(tareas)
            return {"mensaje": "Tarea actualizada", "tarea": t}
            
    # Manejo de Errores Profesional: Si el bucle termina y no encontró el ID, lanzamos un 404
    raise HTTPException(status_code=404, detail="No se encontró la tarea especificada")

@app.delete("/tareas/{tarea_id}")
def eliminar_tarea(tarea_id: int):
    tareas = leer_tareas()
    tareas_filtradas = [t for t in tareas if t["id"] != tarea_id]
    
    if len(tareas) == len(tareas_filtradas):
        raise HTTPException(status_code=404, detail="No se encontró la tarea para eliminar")
        
    guardar_tareas(tareas_filtradas)
    return {"mensaje": "Tarea eliminada exitosamente"}