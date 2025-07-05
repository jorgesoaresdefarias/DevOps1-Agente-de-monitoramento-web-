import time, requests, subprocess
import psycopg2
from datetime import datetime

URLS = ["https://google.com", "https://youtube.com", "https://rnp.br"]
INTERVAL = 60  

def ping(host):
    result = subprocess.run(['ping', '-c', '4', host], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output = result.stdout
    loss_line = [line for line in output.splitlines() if "packet loss" in line]
    rtt_line = [line for line in output.splitlines() if "rtt min/avg/max" in line]
    
    if loss_line:
        loss = float(loss_line[0].split("%")[0].split(" ")[-1])
    else:
        loss = None

    if rtt_line:
        avg_rtt = float(rtt_line[0].split("/")[4])
    else:
        avg_rtt = None

    return avg_rtt, loss

def check_url(url):
    try:
        start = time.time()
        resp = requests.get(url, timeout=10)
        duration = (time.time() - start) * 1000  # ms
        return duration, resp.status_code
    except Exception:
        return None, None

def insert_data(conn, table, values):
    with conn.cursor() as cur:
        cur.execute(f"INSERT INTO {table} (timestamp, target, value1, value2) VALUES (%s, %s, %s, %s)", values)
        conn.commit()
        
def wait_for_db():
    while True:
        try:
            conn = psycopg2.connect(dbname="monitor", user="monitor", password="monitor", host="db")
            print("Conectado!")
            return conn
        except psycopg2.OperationalError as e:
            print("Erro, tentando novamente")
            time.sleep(5)

def main():
    conn = wait_for_db()

    while True:
        timestamp = datetime.utcnow()
        
        for url in ["google.com", "youtube.com", "rnp.br"]:
            rtt, loss = ping(url)
            insert_data(conn, "ping_results", (timestamp, url, rtt, loss))
        
        for url in URLS:
            duration, code = check_url(url)
            insert_data(conn, "http_results", (timestamp, url, duration, code))
        
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
