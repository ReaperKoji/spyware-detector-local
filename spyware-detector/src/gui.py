import tkinter as tk
from tkinter import scrolledtext
import threading
import os
import time
from core import process_scanner, network_scanner, startup_checker, file_scanner
from core.quarantine_manager import quarantine_file

class SpywareDetectorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🛡️ Spyware Local Detector")
        self.root.geometry("850x600")
        self.root.configure(bg="#0f111a")

        # Título com animação
        self.title_label = tk.Label(
            root, text="🧐 DETECTOR DE SPYWARE LOCAL",
            font=("Consolas", 18, "bold"), bg="#0f111a", fg="#00ffcc"
        )
        self.title_label.pack(pady=15)
        self.pulse_text_color(self.title_label, ["#00ffcc", "#33ffff"])

        # Botões
        button_frame = tk.Frame(root, bg="#0f111a")
        button_frame.pack()

        self.buttons = []
        self.scan_all_btn = self.create_button(button_frame, "🔍 Escanear Tudo", self.start_full_scan, 0, "#1a1a2e", "#0f3460")
        self.proc_btn = self.create_button(button_frame, "💻 Processos", self.start_process_scan, 1, "#16213e", "#1f4068")
        self.net_btn = self.create_button(button_frame, "🌐 Conexões", self.start_network_scan, 2, "#16213e", "#00818a")
        self.startup_btn = self.create_button(button_frame, "⚙️ Inicialização", self.start_startup_scan, 3, "#16213e", "#2e8b57")
        self.files_btn = self.create_button(button_frame, "📁 Arquivos", self.start_file_scan, 4, "#16213e", "#8a2be2")
        self.sentinel_btn = self.create_button(button_frame, "👁‍☈️ Iniciar Modo Sentinela", self.toggle_sentinel_mode, 5, "#2e2e2e", "#440000")

        self.output_text = scrolledtext.ScrolledText(
            root, width=100, height=24, bg="#0d0d0d", fg="#00ffcc",
            font=("Consolas", 10), insertbackground="#00ffcc"
        )
        self.output_text.pack(padx=10, pady=(15, 5))

        self.actions_frame = tk.Frame(root, bg="#0f111a")
        self.actions_frame.pack()

    def create_button(self, parent, text, command, column, color1, color2):
        btn = tk.Button(
            parent, text=text, command=command,
            bg=color1, fg="white", font=("Consolas", 11), padx=12, pady=6
        )
        btn.grid(row=0, column=column, padx=5)
        self.pulse_color(btn, [color1, color2])
        self.buttons.append(btn)
        return btn

    def pulse_color(self, widget, colors, index=0, delay=700):
        widget.configure(bg=colors[index])
        next_index = (index + 1) % len(colors)
        widget.after(delay, self.pulse_color, widget, colors, next_index, delay)

    def pulse_text_color(self, widget, colors, index=0, delay=800):
        widget.configure(fg=colors[index])
        next_index = (index + 1) % len(colors)
        widget.after(delay, self.pulse_text_color, widget, colors, next_index, delay)

    def log(self, message):
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)

    def clear_output(self):
        self.output_text.delete(1.0, tk.END)
        for widget in self.actions_frame.winfo_children():
            widget.destroy()

    def scan_processes(self):
        self.log("💻 [Processos Ativos]\n" + "-"*60)
        mensagens = process_scanner.scan_processes(log_output=True)
        for msg in mensagens:
            self.log(msg)
        self.log("-"*60 + "\n")

    def scan_network(self):
        self.log("🌐 [Conexões de Rede]\n" + "-"*60)
        mensagens = network_scanner.scan_connections(log_output=True)
        for msg in mensagens:
            self.log(msg)
        self.log("-"*60 + "\n")

    def scan_startup(self):
        self.log("⚙️ [Programas na Inicialização]\n" + "-"*60)
        mensagens = startup_checker.check_startup_entries(log_output=True)
        for msg in mensagens:
            self.log(msg)
        self.log("-"*60 + "\n")

    def scan_files(self):
        self.log("📁 [Arquivos Suspeitos]\n" + "-"*60)
        arquivos = file_scanner.scan_files(log_output=False)

        if not arquivos:
            self.log("[✔] Nenhum arquivo suspeito encontrado.")
            return

        for path in arquivos:
            self.log(f"[!] {path}")
            btn_frame = tk.Frame(self.actions_frame, bg="#0f111a")
            btn_frame.pack(pady=2)

            lbl = tk.Label(btn_frame, text=path, bg="#0f111a", fg="#cccccc", font=("Consolas", 9), anchor="w", width=70)
            lbl.pack(side=tk.LEFT)

            tk.Button(btn_frame, text="🗑 Excluir", bg="#ff3333", fg="white",
                      command=lambda p=path: self.delete_file(p)).pack(side=tk.LEFT, padx=4)
            tk.Button(btn_frame, text="📅 Quarentena", bg="#ffcc00", fg="black",
                      command=lambda p=path: self.quarantine_file(p)).pack(side=tk.LEFT)

        self.log("-"*60 + "\n")

    def delete_file(self, path):
        try:
            os.remove(path)
            self.log(f"[✔] Arquivo excluído: {path}")
        except Exception as e:
            self.log(f"[X] Erro ao excluir {path}: {str(e)}")

    def quarantine_file(self, path):
        try:
            resultado = quarantine_file(path)
            self.log(resultado)
        except Exception as e:
            self.log(f"[X] Erro ao mover para quarentena: {str(e)}")

    def start_full_scan(self):
        self.clear_output()
        threading.Thread(target=self.full_scan_thread).start()

    def full_scan_thread(self):
        self.scan_processes()
        self.scan_network()
        self.scan_startup()
        self.scan_files()

    def start_process_scan(self):
        self.clear_output()
        threading.Thread(target=self.scan_processes).start()

    def start_network_scan(self):
        self.clear_output()
        threading.Thread(target=self.scan_network).start()

    def start_startup_scan(self):
        self.clear_output()
        threading.Thread(target=self.scan_startup).start()

    def start_file_scan(self):
        self.clear_output()
        threading.Thread(target=self.scan_files).start()

    def toggle_sentinel_mode(self):
        if hasattr(self, "sentinel_running") and self.sentinel_running:
            self.sentinel_running = False
            self.log("🛡️ Modo Sentinela desativado.")
            self.sentinel_btn.config(text="👁‍☈️ Iniciar Modo Sentinela", bg="#2e2e2e")
        else:
            self.sentinel_running = True
            self.log("🟢 Modo Sentinela ativado. Monitorando em tempo real...")
            self.sentinel_btn.config(text="🔚 Parar Modo Sentinela", bg="#440000")
            threading.Thread(target=self.sentinel_loop, daemon=True).start()

    def sentinel_loop(self):
        processos_anteriores = set()
        conexoes_anteriores = set()

        while self.sentinel_running:
            time.sleep(5)

            # Processos novos
            processos_atuais = set(
                p['name'].lower() for p in process_scanner.get_processes() if p['name']
            )
            novos_procs = processos_atuais - processos_anteriores
            if novos_procs:
                for nome in novos_procs:
                    if any(s in nome for s in ["keylogger", "hack", "stealer", "rat", "spy"]):
                        self.log(f"⚠️ Processo suspeito detectado: {nome}")
                    else:
                        self.log(f"🆕 Novo processo iniciado: {nome}")
            processos_anteriores = processos_atuais

            # Conexões novas
            mensagens_conexoes = network_scanner.scan_connections(log_output=True)
            conexoes_atuais = set(mensagens_conexoes)
            novas_conexoes = conexoes_atuais - conexoes_anteriores
            if novas_conexoes:
                for msg in novas_conexoes:
                    if "PID:" in msg and "IP:" in msg:
                        self.log(f"🌐 Nova conexão suspeita: {msg}")
            conexoes_anteriores = conexoes_atuais


if __name__ == "__main__":
    root = tk.Tk()
    app = SpywareDetectorGUI(root)
    root.mainloop()
