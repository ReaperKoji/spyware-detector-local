import os
import winreg

def check_startup_entries(log_output=False):
    mensagens = []
    mensagens.append("⚙️ [*] Verificando entradas de inicialização...\n")

    suspicious = []

    startup_keys = [
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run")
    ]

    for hive, path in startup_keys:
        try:
            reg_key = winreg.OpenKey(hive, path)
            i = 0
            while True:
                try:
                    name, value, _ = winreg.EnumValue(reg_key, i)
                    i += 1

                    if not os.path.exists(value):
                        suspicious.append((name, value, "❗ Caminho inválido"))
                    elif any(term in value.lower() for term in ['temp', 'appdata', 'unknown', 'sus']):
                        suspicious.append((name, value, "⚠️ Local potencialmente suspeito"))
                except OSError:
                    break
        except Exception as e:
            mensagens.append(f"❌ Erro ao acessar registro: {e}")

    if suspicious:
        mensagens.append("⚠️ Entradas de inicialização suspeitas:\n")
        for name, path, detail in suspicious:
            mensagens.append(f"   → Nome: {name} | Caminho: {path} | Detalhe: {detail}")
    else:
        mensagens.append("✅ Nenhuma entrada suspeita encontrada.\n")

    if log_output:
        return mensagens
    else:
        for msg in mensagens:
            print(msg)
