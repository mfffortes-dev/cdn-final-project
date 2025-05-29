from fastapi import FastAPI, Request
from pydantic import BaseModel
import requests
import time

app = FastAPI()

# 🎬 Catálogo de vídeos
video_catalog = set()

# 🌍 Registro de edges: {ip: {"region": str, "last_seen": timestamp}}
edge_registry = {}

class VideoNotification(BaseModel):
    filename: str

@app.get("/")
def index():
    if not video_catalog:
        return {"message": "📂 Nenhum conteúdo disponível no momento"}
    return {
        "message": "📂 Catálogo de vídeos disponível no GCS",
        "videos": list(video_catalog)
    }

@app.post("/new_video_notification")
def new_video(notification: VideoNotification):
    filename = notification.filename
    print(f"\n🔔 Nova notificação recebida!")
    print(f"📥 Conteúdo adicionado ao GCS: {filename}")

    video_catalog.add(filename)

    # Notifica todos os edges registrados
    for edge_ip in edge_registry:
        try:
            response = requests.post(f"{edge_ip}/fetch", json={"filename": filename}, timeout=5)
            print(f"📣 Notificado edge: {edge_ip} → {response.status_code}")
        except Exception as e:
            print(f"⚠️ Falha ao notificar {edge_ip}: {e}")

    return {"message": f"{filename} registrado com sucesso"}

@app.post("/remove")
def remove_video(notification: VideoNotification):
    filename = notification.filename
    print(f"\n🔔 Notificação de remoção recebida!")
    print(f"🗑️ Conteúdo removido do GCS: {filename}")
    video_catalog.discard(filename)
    return {"message": f"{filename} removido"}

@app.post("/register_edge")
async def register_edge(request: Request):
    data = await request.json()
    edge_ip = data.get("ip")
    region = data.get("region")

    if not edge_ip or not region:
        return {"error": "ip e region são obrigatórios."}

    edge_registry[edge_ip] = {
        "region": region,
        "last_seen": time.time()
    }

    print(f"\n✅ Edge registrado: {edge_ip} ({region})")
    return {
        "message": "Edge registrado com sucesso",
        "conteudos": list(video_catalog)
    }

@app.get("/status")
def get_status():
    return {
        "catalogo": list(video_catalog),
        "edges": edge_registry
    }
