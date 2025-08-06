import platform
from core import process_scanner, network_scanner, startup_checker

def main():
    print("="*50)
    print("🔍 DETECTOR DE SPYWARE LOCAL".center(50))
    print("="*50)
    print(f"Sistema detectado: {platform.system()} {platform.release()}\n")

    process_scanner.scan_processes()
    network_scanner.scan_connections()
    startup_checker.check_startup_entries()

if __name__ == "__main__":
    main()
