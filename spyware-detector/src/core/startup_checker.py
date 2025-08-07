import os
import sys
import platform
import time
import re

# Cores ANSI - funciona na maioria dos terminais modernos
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
WHITE = "\033[97m"
MAGENTA = "\033[95m"
RESET = "\033[0m"
BOLD = "\033[1m"

# Regex para limpar códigos ANSI (útil pra GUI, logs limpos etc)
ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

def remove_ansi(text: str) -> str:
    """
    Remove sequências ANSI de cor/estilo de uma string.
    Ideal para limpar logs para GUIs ou arquivos.
    """
    return ansi_escape.sub('', text)


# Platform detection e import dinâmico do winreg para Windows
if sys.platform == "win32":
    import winreg
else:
    winreg = None  # placeholder para Linux/macOS


def banner():
    """
    Exibe banner estilizado no terminal,
    mostrando info do SO e identidade do script.
    """
    print(f"{MAGENTA}{BOLD}")
    print("╔══════════════════════════════════════════════════════╗")
    print("║             🔍 Startup Recon by ReaperKoji           ║")
    print("╠══════════════════════════════════════════════════════╣")
    print(f"║ Plataforma: {platform.system()} {platform.release()}".ljust(51) + "║")
    print("╚══════════════════════════════════════════════════════╝")
    print(RESET)
    time.sleep(0.5)


def check_startup_entries(log_output=False):
    """
    Varre entradas de inicialização suspeitas
    tanto no Windows (registry Run keys)
    quanto no Linux (~/.config/autostart e crontab @reboot).
    
    Se log_output=True, retorna lista de strings com mensagens formatadas ANSI.
    Caso contrário, imprime no terminal.
    """
    mensagens = []
    mensagens.append(f"{CYAN}[•] Scaneando entradas de inicialização...\n{RESET}")
    suspicious = []

    # === Windows Registry Run Keys ===
    if winreg:
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
                            suspicious.append((name, value, f"{RED}❗ Caminho inválido{RESET}"))
                        elif any(term in value.lower() for term in ['temp', 'appdata', 'unknown', 'sus']):
                            suspicious.append((name, value, f"{YELLOW}⚠️ Local suspeito{RESET}"))
                    except OSError:
                        break
            except Exception as e:
                mensagens.append(f"{RED}❌ Erro ao acessar registro: {e}{RESET}")

    # === Linux autostart e crontab @reboot ===
    else:
        autostart_dir = os.path.expanduser("~/.config/autostart/")
        if os.path.isdir(autostart_dir):
            for f in os.listdir(autostart_dir):
                if f.endswith(".desktop"):
                    path = os.path.join(autostart_dir, f)
                    suspicious.append((f, path, f"{YELLOW}⚠️ Autostart detectado{RESET}"))

        try:
            import subprocess
            result = subprocess.run(["crontab", "-l"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
            for line in result.stdout.splitlines():
                if "@reboot" in line:
                    suspicious.append(("crontab", line.strip(), f"{YELLOW}⚠️ Crontab '@reboot' detectado{RESET}"))
        except Exception as e:
            mensagens.append(f"{RED}❌ Erro ao verificar crontab: {e}{RESET}")

    # === Resultados formatados ===
    if suspicious:
        mensagens.append(f"\n{YELLOW}[!] Entradas suspeitas encontradas:{RESET}")
        for name, path, detail in suspicious:
            mensagens.append(f"   → {BOLD}Nome:{RESET} {name} | {BOLD}Caminho:{RESET} {path} | {BOLD}Status:{RESET} {detail}")
    else:
        mensagens.append(f"{GREEN}✅ Nenhuma entrada suspeita encontrada.{RESET}\n")

    if log_output:
        return mensagens
    else:
        for msg in mensagens:
            print(msg)


# TESTE DIRETO
if __name__ == "__main__":
    banner()
    check_startup_entries()
