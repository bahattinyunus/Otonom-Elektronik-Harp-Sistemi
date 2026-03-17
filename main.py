import subprocess
import sys
import os

def main():
    print("--------------------------------------------------")
    print("   OTONOM ELEKTRONIK HARP SISTEMI (LAUNCHER)      ")
    print("--------------------------------------------------")
    
    # Check if we are in the right directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)
    
    # Start the backend server
    print("[*] Dashboard sunucusu başlatılıyor...")
    try:
        from ui.app import socketio, app
        import threading
        from ui.app import background_thread
        
        thread = threading.Thread(target=background_thread)
        thread.daemon = True
        thread.start()
        
        print("[+] Sistem Çevrimi: AKTİF")
        print("[+] Web Arayüzü: http://localhost:5000")
        print("[!] Çıkış yapmak için Ctrl+C tuşlarına basın.")
        
        socketio.run(app, host='0.0.0.0', port=5000, debug=False)
        
    except ImportError as e:
        print(f"[!] Hata: Gerekli kütüphaneler eksik. Lütfen 'pip install -r requirements.txt' komutunu çalıştırın.")
        print(f"Detay: {e}")
    except KeyboardInterrupt:
        print("\n[*] Sistem kapatılıyor...")

if __name__ == "__main__":
    main()
