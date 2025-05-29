from fastapi import FastAPI
import requests

app = FastAPI()
MASTER_URL = "http://34.71.180.38:8000"  # Substitua pelo IP fixo do master
REGION = "us"
EDGE_IP = "http://10.10.0.74:8000"  # Use IP interno se estiver no GCP

@app.on_event("startup")
def register():
    try:
        print("📡 Registrando no Master...")
        requests.post(f"{MASTER_URL}/register_edge", json={
            "region": REGION,
            "ip": EDGE_IP
        })
        print("✅ Registro completo.")
    except Exception as e:
        print("⚠️ Falha no registro:", e)

@app.get("/")
def status():
    return {"message": f"Edge US ativo e pronto"}
