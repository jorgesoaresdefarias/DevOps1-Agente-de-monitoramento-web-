import time
import requests
import psycopg2
from datetime import datetime

API_URL = "https://viaipe.rnp.br/api/norte"
INTERVAL = 300  # 5 minutos

def fetch_viaipe_data():
    try:
        response = requests.get(API_URL, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print("Erro ao acessar API ViaIpe:", response.status_code)
    except Exception as e:
        print("Erro na requisição ViaIpe:", e)
    return []

def process_viaipe_data(data):
    stats = []
    timestamp = datetime.utcnow()

    for cliente in data:
        nome = cliente.get("name", "desconhecido")

        smoke = cliente.get("data", {}).get("smoke", {})
        avg_loss = smoke.get("avg_loss", 0.0)
        latencia = smoke.get("avg_val", 0.0)

        interfaces = cliente.get("data", {}).get("interfaces", [])
        if interfaces:
            avg_out = interfaces[0].get("avg_out", 0.0)
        else:
            avg_out = 0.0

        disponibilidade = 100.0 - avg_loss
        banda = avg_out
        qualidade = 100.0 - latencia  # ou outra fórmula

        stats.append((timestamp, nome, disponibilidade, banda, qualidade))
    
    return stats


def insert_viaipe_stats(conn, stats):
    with conn.cursor() as cur:
        for row in stats:
            cur.execute("""
                INSERT INTO viaipe_stats (timestamp, cliente, disponibilidade, banda_consumo, qualidade)
                VALUES (%s, %s, %s, %s, %s)
            """, row)
        conn.commit()

def wait_for_db():
    while True:
        try:
            conn = psycopg2.connect(dbname="monitor", user="monitor", password="monitor", host="db")
            print("Conectado ao banco de dados!")
            return conn
        except psycopg2.OperationalError:
            print("Aguardando banco de dados...")
            time.sleep(5)

def main():
    conn = wait_for_db()

    while True:
        data = fetch_viaipe_data()
        if data:
            stats = process_viaipe_data(data)
            insert_viaipe_stats(conn, stats)
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
