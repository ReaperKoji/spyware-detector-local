import psutil
import os

# 🔍 Escaneia os processos ativos procurando comportamentos suspeitos
def scan_processes(log_output=False):
    mensagens = []
    mensagens.append("💻 [*] Escaneando processos ativos...\n")

    suspicious = []

    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        try:
            pid = proc.info['pid']
            name = proc.info['name'] or "Desconhecido"
            exe = proc.info['exe']

            # Critérios de suspeita:
            if not exe or not os.path.exists(exe):
                suspicious.append((pid, name, "❗ Caminho não encontrado"))
            elif any(term in name.lower() for term in ['keylogger', 'stealer', 'rat', 'spy', 'sniffer']):
                suspicious.append((pid, name, exe))
            # 👉 Adicione "notepad" na lista abaixo se quiser forçar aparecer durante testes
            # elif 'notepad' in name.lower():
            #     suspicious.append((pid, name, exe))

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if suspicious:
        mensagens.append("⚠️ Processos potencialmente suspeitos detectados:\n")
        for pid, name, detail in suspicious:
            mensagens.append(f"   → PID: {pid} | Nome: {name} | Detalhe: {detail}")
    else:
        mensagens.append("✅ Nenhum processo suspeito encontrado.\n")

    if not log_output:
        for msg in mensagens:
            print(msg)

    return mensagens

# 🔁 Função usada no modo sentinela para monitoramento em tempo real
def get_processes():
    processos = []
    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        try:
            processos.append({
                "pid": proc.info['pid'],
                "name": proc.info['name'] or "Desconhecido",
                "exe": proc.info['exe'] or "N/A"
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return processos
