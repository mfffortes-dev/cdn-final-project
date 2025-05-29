from google.cloud import storage
import requests
import os

# 🔐 Caminho da chave de serviço
GCS_KEY_PATH = "gcs-key.json"

# 🪣 Nome do seu bucket
BUCKET_NAME = "cdn-gcs-bucket1"  # Substitua se o nome for diferente

# 📁 Pasta com vídeos locais
VIDEO_FOLDER = "videos"

# 🌐 IP fixo do Master (substitua pelo IP interno se estiver testando no GCP)
MASTER_IP = "http://10.10.0.68:8000"  # Substitua se necessário

def upload_video(filename):
    client = storage.Client.from_service_account_json(GCS_KEY_PATH)
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)

    file_path = os.path.join(VIDEO_FOLDER, filename)
    blob.upload_from_filename(file_path)
    print(f"✅ Upload para GCS: {filename}")

    # Notificar o Master
    response = requests.post(f"{MASTER_IP}/new_video_notification", json={"filename": filename})
    if response.status_code == 200:
        print(f"📣 Notificação enviada ao Master: {filename}")
    else:
        print(f"⚠️ Erro ao notificar Master: {response.status_code}")

def delete_video(filename):
    client = storage.Client.from_service_account_json(GCS_KEY_PATH)
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)

    if blob.exists():
        blob.delete()
        print(f"🗑️ Vídeo removido do GCS: {filename}")
        
        # Notificar o Master
        response = requests.post(f"{MASTER_IP}/remove", json={"filename": filename})
        if response.status_code == 200:
            print(f"📣 Notificação de remoção enviada ao Master: {filename}")
        else:
            print(f"⚠️ Erro ao notificar Master: {response.status_code}")
    else:
        print("⚠️ Arquivo não existe no bucket.")

# Exemplo de uso direto
if __name__ == "__main__":
    upload_video("video1_30mb.mp4")
    # delete_video("video1.mp4")
