import os
import shutil
import tempfile
import time
import platform
import getpass

def limpar_computador(log_func):
    log_func("🧹 Iniciando limpeza do sistema...")

    def remover_antigos(caminho, dias=120):
        """Remove arquivos e pastas que não são acessados/modificados há mais de 'dias' dias."""
        agora = time.time()
        limite = agora - dias * 86400  # segundos em 'dias'

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

    # 1. Limpar TEMP (todas as plataformas)
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

    # 2. Limpar APPDATA no Windows (Local e Roaming)
    if platform.system() == "Windows":
        appdata_local = os.environ.get('LOCALAPPDATA')
        appdata_roaming = os.environ.get('APPDATA')

        for path in [appdata_local, appdata_roaming]:
            if path:
                log_func(f"🗑️ Limpando AppData em: {path}")
                remover_antigos(path, dias=120)
            else:
                log_func(f"⚠️ Variável de ambiente AppData não encontrada")

    # 3. Limpar Downloads antigos (Linux e Windows)
    home = os.path.expanduser("~")
    downloads = os.path.join(home, "Downloads")
    if os.path.exists(downloads):
        log_func(f"🗑️ Limpando Downloads antigos em: {downloads}")
        remover_antigos(downloads, dias=120)

    # 4. Limpar cache do navegador (Chrome, Firefox) - só no Windows para exemplo
    if platform.system() == "Windows":
        caches = [
            os.path.join(appdata_local, r"Google\Chrome\User Data\Default\Cache") if appdata_local else None,
            os.path.join(appdata_roaming, r"Mozilla\Firefox\Profiles") if appdata_roaming else None,
        ]
        for cache_path in caches:
            if cache_path and os.path.exists(cache_path):
                log_func(f"🗑️ Limpando cache do navegador em: {cache_path}")
                remover_antigos(cache_path, dias=30)  # cache recente só 30 dias
            else:
                log_func(f"⚠️ Cache do navegador não encontrado: {cache_path}")

    # 5. Apagar pastas de usuários que NÃO são o usuário atual
    def apagar_usuarios_externos():
        log_func("🗑️ Iniciando limpeza das contas de usuários não vinculadas...")

        usuario_atual = getpass.getuser()
        sistema = platform.system()
        
        if sistema == "Windows":
            base_path = os.path.join(os.environ.get('SystemDrive', 'C:'), "Users")
        else:
            base_path = "/home"

        if not os.path.exists(base_path):
            log_func(f"⚠️ Diretório base de usuários não encontrado: {base_path}")
            return

        for usuario_pasta in os.listdir(base_path):
            if usuario_pasta.lower() != usuario_atual.lower():
                usuario_path = os.path.join(base_path, usuario_pasta)
                try:
                    # Evitar apagar pastas críticas do sistema
                    if usuario_pasta.lower() in ["public", "default", "default user", "all users"]:
                        log_func(f"   ⚠️ Ignorando pasta do sistema: {usuario_pasta}")
                        continue

                    if os.path.isdir(usuario_path):
                        shutil.rmtree(usuario_path)
                        log_func(f"   - Pasta do usuário removida: {usuario_path}")
                except Exception as e:
                    log_func(f"   ⚠️ Erro removendo pasta {usuario_path}: {e}")

        log_func("✅ Limpeza das contas de usuários concluída.")

    apagar_usuarios_externos()

    log_func("✅ Limpeza concluída.")
