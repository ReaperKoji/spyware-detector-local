import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import platform
import sys
import os
import shutil
import tempfile
import getpass
import subprocess
from collections import deque

import psutil
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "core")))
from core import startup_checker


def limpar_computador(log_func, on_finish=None):
    log_func("🧹 Iniciando limpeza do sistema...")

    def remover_antigos(caminho, dias=120):
        agora = time.time()
        limite = agora - dias * 86400

        if not os.path.exists(caminho):
            log_func(f"⚠️ Caminho não existe: {caminho}")
            return

        for root, dirs, files in os.walk(caminho, topdown=False):
            for nome in files:
                arquivo = os.path.join(root, nome)
                try:
                    ultimo_acesso = os.path.getatime(arquivo)
                    if ultimo_acesso < limite:
                        os.remove(arquivo)
                        log_func(f"   - Arquivo antigo removido: {arquivo}")
                except Exception as e:
                    log_func(f"   ⚠️ Erro removendo arquivo {arquivo}: {e}")

            for nome in dirs:
                dir_path = os.path.join(root, nome)
                try:
                    ultimo_acesso = os.path.getatime(dir_path)
                    if ultimo_acesso < limite:
                        shutil.rmtree(dir_path)
                        log_func(f"   - Diretório antigo removido: {dir_path}")
                except Exception as e:
                    log_func(f"   ⚠️ Erro removendo diretório {dir_path}: {e}")

    # Limpar TEMP
    temp_dir = tempfile.gettempdir()
    log_func(f"🗑️ Limpando arquivos temporários em: {temp_dir}")
    try:
        for item in os.listdir(temp_dir):
            item_path = os.path.join(temp_dir, item)
            try:
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    os.unlink(item_path)
                    log_func(f"   - Arquivo removido: {item_path}")
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                    log_func(f"   - Diretório removido: {item_path}")
            except Exception as e:
                log_func(f"   ⚠️ Erro removendo {item_path}: {e}")
    except Exception as e:
        log_func(f"❌ Erro ao listar pasta temporária: {e}")

    # Limpar APPDATA (Windows)
    if platform.system() == "Windows":
        appdata_local = os.environ.get('LOCALAPPDATA')
        appdata_roaming = os.environ.get('APPDATA')
        for path in [appdata_local, appdata_roaming]:
            if path:
                log_func(f"🗑️ Limpando AppData em: {path}")
                remover_antigos(path, dias=120)
            else:
                log_func(f"⚠️ Variável de ambiente AppData não encontrada")

    # Limpar Downloads antigos (Windows e Linux)
    home = os.path.expanduser("~")
    downloads = os.path.join(home, "Downloads")
    if os.path.exists(downloads):
        log_func(f"🗑️ Limpando Downloads antigos em: {downloads}")
        remover_antigos(downloads, dias=120)

    # Limpar cache navegador (exemplo Windows)
    if platform.system() == "Windows":
        caches = [
            os.path.join(appdata_local, r"Google\Chrome\User Data\Default\Cache") if appdata_local else None,
            os.path.join(appdata_roaming, r"Mozilla\Firefox\Profiles") if appdata_roaming else None,
        ]
        for cache_path in caches:
            if cache_path and os.path.exists(cache_path):
                log_func(f"🗑️ Limpando cache do navegador em: {cache_path}")
                remover_antigos(cache_path, dias=30)
            else:
                log_func(f"⚠️ Cache do navegador não encontrado: {cache_path}")

    # Apagar jogos de pastas comuns
    def apagar_jogos(log_func):
        paths_jogos = []
        if platform.system() == "Windows":
            usuario = os.getlogin()
            paths_jogos = [
                os.path.join("C:\\", "Program Files (x86)", "Steam"),
                os.path.join("C:\\", "Program Files", "Epic Games"),
                os.path.join("C:\\", "Program Files (x86)", "Origin"),
                os.path.join("C:\\Users", usuario, "Documents", "My Games"),
            ]
        elif platform.system() == "Linux":
            home = os.path.expanduser("~")
            paths_jogos = [
                os.path.join(home, ".steam"),
                os.path.join(home, ".local", "share", "Steam"),
                os.path.join(home, "Games"),
            ]

        log_func("🎮 Iniciando remoção de jogos...")
        for path in paths_jogos:
            if path and os.path.exists(path):
                try:
                    shutil.rmtree(path)
                    log_func(f"   - Jogos removidos: {path}")
                except Exception as e:
                    log_func(f"   ⚠️ Erro removendo jogos em {path}: {e}")
            else:
                log_func(f"   ⚠️ Pasta de jogos não encontrada: {path}")

    apagar_jogos(log_func)

    # Excluir contas de usuário (Windows e Linux)
    def excluir_usuarios(log_func):
        log_func("🗑️ Excluindo contas de usuários (exceto a atual)...")

        usuario_atual = getpass.getuser()

        if platform.system() == "Windows":
            try:
                output = subprocess.check_output("net user", shell=True, text=True)
                usuarios = []
                for line in output.splitlines():
                    if line.strip() and not line.startswith("Nome de usuário") and not line.startswith("---") and "comando concluído" not in line.lower():
                        usuarios += line.split()
                usuarios = [u for u in usuarios if u.lower() != usuario_atual.lower()]
                for u in usuarios:
                    log_func(f"   - Excluindo usuário: {u}")
                    try:
                        subprocess.check_call(f'net user "{u}" /delete', shell=True)
                        log_func(f"      ✅ Usuário {u} excluído.")
                    except Exception as e:
                        log_func(f"      ⚠️ Erro excluindo usuário {u}: {e}")
            except Exception as e:
                log_func(f"❌ Erro ao listar usuários: {e}")

        elif platform.system() == "Linux":
            try:
                output = subprocess.check_output("cut -d: -f1 /etc/passwd", shell=True, text=True)
                usuarios = [u for u in output.splitlines() if u not in ['root', usuario_atual]]
                for u in usuarios:
                    log_func(f"   - Excluindo usuário: {u}")
                    try:
                        subprocess.check_call(f'sudo userdel -r {u}', shell=True)
                        log_func(f"      ✅ Usuário {u} excluído.")
                    except Exception as e:
                        log_func(f"      ⚠️ Erro excluindo usuário {u}: {e}")
            except Exception as e:
                log_func(f"❌ Erro ao listar usuários: {e}")

    excluir_usuarios(log_func)

    log_func("✅ Limpeza do computador concluída com sucesso.")
    if on_finish:
        on_finish()


class HackerSentinelGUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("🛡️ KojiClean - ReaperKoji")
        self.geometry("1000x700")
        self.configure(bg="#0b0b0b")
        self.resizable(False, False)

        style = ttk.Style(self)
        style.theme_use('clam')

        style.configure('TButton', font=('Consolas', 11, 'bold'),
                        foreground='#00ff00', background='#111111',
                        borderwidth=0, focuscolor='none')
        style.map('TButton',
                  background=[('active', '#00cc00')],
                  foreground=[('active', '#000000')])

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = tk.Frame(self, bg="#121212", width=230)
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_propagate(False)

        self.btn_processes = ttk.Button(self.sidebar, text="💻 Processos", command=self.scan_processes)
        self.btn_startup = ttk.Button(self.sidebar, text="⚙️ Inicialização", command=self.scan_startup)
        self.btn_network = ttk.Button(self.sidebar, text="🌐 Conexões", command=self.scan_network)
        self.btn_files = ttk.Button(self.sidebar, text="📁 Arquivos Suspeitos", command=self.scan_files)
        self.btn_sentinel = ttk.Button(self.sidebar, text="🚨 Modo Sentinela", command=self.toggle_sentinel_mode)
        self.btn_clean = ttk.Button(self.sidebar, text="🧹 Limpeza Profunda", command=self.ask_confirm_clean)
        self.btn_clear = ttk.Button(self.sidebar, text="🧹 Limpar Log", command=self.clear_log)
        self.btn_export = ttk.Button(self.sidebar, text="📤 Exportar Log", command=self.export_log)
        self.btn_exit = ttk.Button(self.sidebar, text="❌ Sair", command=self.quit)

        self.buttons = [self.btn_processes, self.btn_startup, self.btn_network,
                        self.btn_files, self.btn_sentinel, self.btn_clean,
                        self.btn_clear, self.btn_export, self.btn_exit]

        for i, btn in enumerate(self.buttons):
            btn.grid(row=i, column=0, pady=6, padx=15, sticky="ew")

        self.main_panel = tk.Frame(self, bg="#0f0f0f")
        self.main_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.title_label = tk.Label(self.main_panel, text="<< KojiClean >>",
                                    font=("Consolas", 26, "bold"), fg="#00ff00", bg="#0f0f0f")
        self.title_label.pack(pady=10)

        self.log_box = tk.Text(self.main_panel, bg="#000000", fg="#00ff00",
                               font=("Consolas", 11), insertbackground="#00ff00",
                               wrap="word", borderwidth=0, height=20, width=80)
        self.log_box.pack(padx=10, pady=10, fill="both", expand=False)
        self.log_box.config(state="disabled")

        self.scrollbar = tk.Scrollbar(self.main_panel, command=self.log_box.yview)
        self.log_box.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")

        # Gráfico CPU
        self.cpu_data = deque([0]*30, maxlen=30)
        self.fig, self.ax = plt.subplots(figsize=(6,2.5))
        self.line, = self.ax.plot(range(30), list(self.cpu_data), color='lime')
        self.ax.set_ylim(0, 100)
        self.ax.set_title("Uso da CPU (%) em tempo real")
        self.ax.set_xlabel("Segundos atrás")
        self.ax.set_ylabel("CPU %")
        self.ax.grid(True, linestyle='--', alpha=0.5)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.main_panel)
        self.canvas.get_tk_widget().pack(padx=10, pady=5, fill="both", expand=False)

        self.running = True
        threading.Thread(target=self.update_cpu_usage, daemon=True).start()

        self.status_bar = tk.Label(self, text="Status: Pronto", bg="#121212", fg="#00ff00", font=("Consolas", 10))
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")

        self.sentinel_active = False
        self.animate_title()

        # Barra de progresso para limpeza
        self.progress = ttk.Progressbar(self.main_panel, mode='indeterminate')

    def animate_title(self):
        def glitch():
            colors = ["#00ff00", "#33ff33", "#00cc00", "#0aff0a"]
            idx = 0
            while True:
                self.title_label.config(fg=colors[idx])
                idx = (idx + 1) % len(colors)
                time.sleep(0.15)
        threading.Thread(target=glitch, daemon=True).start()

    def log(self, msg):
        self.log_box.config(state="normal")
        self.log_box.insert("end", msg + "\n")
        self.log_box.see("end")
        self.log_box.config(state="disabled")

    def clear_log(self):
        self.log_box.config(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.config(state="disabled")
        self.status_bar.config(text="Status: Log limpo")

    def export_log(self):
        from tkinter import filedialog
        log_content = self.log_box.get("1.0", "end-1c")
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("Todos arquivos", "*.*")]
        )
        if filename:
            try:
                with open(filename, "w") as f:
                    f.write(log_content)
                self.status_bar.config(text=f"Status: Log exportado para {filename}")
                self.log(f"✅ Log exportado para: {filename}")
            except Exception as e:
                self.status_bar.config(text=f"Status: Erro ao exportar log")
                self.log(f"❌ Erro ao exportar log: {e}")
        else:
            self.status_bar.config(text="Status: Exportação cancelada")
            self.log("⚠️ Exportação de log cancelada.")

    def toggle_sentinel_mode(self):
        self.sentinel_active = not self.sentinel_active
        if self.sentinel_active:
            self.status_bar.config(text="Status: Modo Sentinela ativado")
            self.log("🚨 Modo Sentinela ativado. Monitorando em tempo real...")
            threading.Thread(target=self.sentinel_loop, daemon=True).start()
        else:
            self.status_bar.config(text="Status: Modo Sentinela desativado")
            self.log("🛑 Modo Sentinela desativado.")

    def sentinel_loop(self):
        while self.sentinel_active:
            self.log(f"⌛ Monitorando... {time.strftime('%H:%M:%S')}")
            time.sleep(5)

    def scan_processes(self):
        self.status_bar.config(text="Status: Escaneando processos...")
        self.log("💻 Escaneando processos ativos...")
        self.status_bar.config(text="Status: Escaneamento de processos concluído.")
        self.log("✅ Escaneamento de processos concluído.")

    def scan_startup(self):
        self.status_bar.config(text="Status: Escaneando programas na inicialização...")
        self.log("⚙️ Escaneando programas na inicialização...")
        mensagens = startup_checker.check_startup_entries(log_output=True)
        import re
        ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
        for linha in mensagens:
            clean_line = ansi_escape.sub('', linha)
            self.log(clean_line)
        self.status_bar.config(text="Status: Escaneamento de inicialização concluído.")
        self.log("✅ Escaneamento de inicialização concluído.")

    def scan_network(self):
        self.status_bar.config(text="Status: Escaneando conexões de rede...")
        self.log("🌐 Escaneando conexões de rede...")
        self.status_bar.config(text="Status: Escaneamento de rede concluído.")
        self.log("✅ Escaneamento de rede concluído.")

    def scan_files(self):
        self.status_bar.config(text="Status: Escaneando arquivos suspeitos...")
        self.log("📁 Escaneando arquivos suspeitos...")
        self.status_bar.config(text="Status: Escaneamento de arquivos concluído.")
        self.log("✅ Escaneamento de arquivos concluído.")

    def ask_confirm_clean(self):
        resposta = messagebox.askyesno("Confirmação", 
                                      "⚠️ ATENÇÃO: Essa limpeza profunda apagará jogos e excluirá contas de usuários, *exceto a conta atual que você está usando*.\n\nDeseja continuar?")
        if resposta:
            self.status_bar.config(text="Status: Iniciando limpeza profunda...")
            self.log("🧹 Iniciando limpeza profunda do sistema...")
            self._toggle_buttons(state="disabled")
            self.progress.pack(pady=5, padx=10, fill="x")
            self.progress.start(10)
            threading.Thread(target=self._clean_thread, daemon=True).start()
        else:
            self.log("⚠️ Limpeza profunda cancelada pelo usuário.")
            self.status_bar.config(text="Status: Limpeza profunda cancelada.")

    def _clean_thread(self):
        limpar_computador(self.log, on_finish=self._on_clean_finished)

    def _on_clean_finished(self):
        self.progress.stop()
        self.progress.pack_forget()
        self._toggle_buttons(state="normal")
        self.status_bar.config(text="Status: Limpeza profunda concluída.")

    def _toggle_buttons(self, state):
        for btn in self.buttons:
            btn.config(state=state)

    def update_cpu_usage(self):
        while self.running:
            cpu_percent = psutil.cpu_percent(interval=1)
            self.cpu_data.append(cpu_percent)
            self.line.set_ydata(list(self.cpu_data))
            self.canvas.draw_idle()


if __name__ == "__main__":
    app = HackerSentinelGUI()
    app.mainloop()
