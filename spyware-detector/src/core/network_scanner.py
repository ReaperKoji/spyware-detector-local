import psutil
import os

def carregar_blacklist(caminho="ip_blacklist.txt"):
    if not os.path.exists(caminho):
        return []
    with open(caminho, "r") as f:
        return [linha.strip() for linha in f.readlines() if linha.strip()]

def ip_suspeito(ip, blacklist):
    return any(ip.startswith(bl) for bl in blacklist)

def scan_connections(log_output=False):
    mensagens = []
    mensagens.append("🌐 [*] Escaneando conexões de rede...\n")
    blacklist = carregar_blacklist()
    suspicious = []

    for conn in psutil.net_connections(kind='inet'):
        try:
            raddr = conn.raddr.ip if conn.raddr else None
            pid = conn.pid
            proc = psutil.Process(pid) if pid else None
            pname = proc.name() if proc else "Desconhecido"

            if raddr and ip_suspeito(raddr, blacklist):
                suspicious.append((raddr, pname, pid))

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if suspicious:
        mensagens.append("🚨 Conexões suspeitas encontradas:")
        for ip, pname, pid in suspicious:
            mensagens.append(f" - PID: {pid} | Processo: {pname} | IP: {ip}")
    else:
        mensagens.append("✅ Nenhuma conexão suspeita identificada.")

    if log_output:
        return mensagens
    else:
        for msg in mensagens:
            print(msg)

# 🔁 Usado pelo modo sentinela
def get_connections():
    conexoes = []
    for conn in psutil.net_connections(kind='inet'):
        try:
            conn_dict = {
                "pid": conn.pid,
                "status": conn.status,
            }

            if conn.laddr:
                conn_dict["local_ip"] = conn.laddr.ip
                conn_dict["local_port"] = conn.laddr.port

            if conn.raddr:
                conn_dict["foreign_ip"] = conn.raddr.ip
                conn_dict["foreign_port"] = conn.raddr.port

            conexoes.append(conn_dict)

        except Exception:
            continue

    return conexoes
