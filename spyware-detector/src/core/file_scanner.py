import os

# Retorna apenas os caminhos de arquivos suspeitos
def scan_files(log_output=False):
    arquivos_suspeitos = []
    caminhos_comuns = [
        os.path.expanduser("~\\AppData\\Roaming"),
        os.path.expanduser("~\\Downloads"),
        "/tmp", "/var/tmp", "/usr/local/bin"
    ]
    extensoes_suspeitas = [".exe", ".bat", ".vbs", ".scr", ".dll", ".ps1", ".sh"]

    for caminho in caminhos_comuns:
        if os.path.exists(caminho):
            for root, dirs, files in os.walk(caminho):
                for f in files:
                    if any(f.lower().endswith(ext) for ext in extensoes_suspeitas):
                        full_path = os.path.join(root, f)
                        arquivos_suspeitos.append(full_path)

    if log_output:
        if arquivos_suspeitos:
            mensagens = ["[!] Arquivos suspeitos detectados:"]
            mensagens += [f" - {path}" for path in arquivos_suspeitos]
        else:
            mensagens = ["[✔] Nenhum arquivo suspeito encontrado."]
        return mensagens
    else:
        return arquivos_suspeitos
