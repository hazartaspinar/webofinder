import socket
import requests
import threading
import ipaddress
import os
import sys
import glob
import webbrowser

# Windows uyumluluğu için readline alternatifi
if sys.platform == "win32":
    try:
        import pyreadline3 as readline
    except ImportError:
        print("⚠️ pyreadline3 bulunamadı! Tab tamamlama çalışmayabilir.")
else:
    import readline

def print_banner():
    banner = """
 ▄  █    ▄▄▄▄▀ ▄▄▄▄▀ █ ▄▄      ▄████  ▄█    ▄   ██▄   ▄███▄   █▄▄▄▄ 
█   █ ▀▀▀ █ ▀▀▀ █    █   █     █▀   ▀ ██     █  █  █  █▀   ▀  █  ▄▀ 
██▀▀█     █     █    █▀▀▀      █▀▀    ██ ██   █ █   █ ██▄▄    █▀▀▌  
█   █    █     █     █         █      ▐█ █ █  █ █  █  █▄   ▄▀ █  █  
   █    ▀     ▀       █         █      ▐ █  █ █ ███▀  ▀███▀     █   
  ▀                    ▀         ▀       █   ██                ▀   
                 Web Service Finder (WeboFinder)
    """
    print(banner)

def check_web_service(ip, port, output_file, html_file):
    try:
        protocol = "https" if port in [443, 8443] else "http"
        url = f"{protocol}://{ip}:{port}" if port not in [80, 443] else f"{protocol}://{ip}"
        response = requests.get(url, timeout=1)
        result = f"{url} - {response.status_code} - {response.headers.get('Server', 'Unknown')}\n"
        print(result.strip())
        
        with open(output_file, "a") as f:
            f.write(result)
        
        with open(html_file, "a") as f:
            f.write(f'<a href="{url}" target="_blank">{url}</a> - {response.status_code} - {response.headers.get("Server", "Unknown")}<br>\n')
    except requests.exceptions.RequestException:
        pass

def scan_ip(ip, ports, output_file, html_file):
    for port in ports:
        check_web_service(ip, port, output_file, html_file)

def complete_path(text, state):
    return (glob.glob(text + '*') + [None])[state]

if 'readline' in sys.modules:
    readline.set_completer(complete_path)
    readline.parse_and_bind("tab: complete")

def get_ip_list():
    print("\nNasıl IP adresleri girmek istiyorsunuz?")
    print("[1] Dosyadan 📄")
    print("[2] CIDR Aralığı 🌐")
    print("[3] Tek IP 🔍")
    
    choice = input("Seçiminiz (1/2/3): ")
    
    if choice == "1":
        file_path = input("📂 Kullanmak istediğiniz dosyanın tam yolunu girin: ")
        file_path = os.path.expanduser(file_path)
        
        if not os.path.exists(file_path):
            print(f"❌ Hata: {file_path} bulunamadı! Lütfen dosyanın mevcut olduğundan emin olun.")
            exit()
        with open(file_path, "r") as f:
            return [line.strip() for line in f.readlines()]
    
    elif choice == "2":
        cidr = input("🌍 CIDR formatında subnet girin (örn: 192.168.1.0/24): ")
        return [str(ip) for ip in ipaddress.IPv4Network(cidr, strict=False)]
    
    elif choice == "3":
        ip = input("🔎 Tek bir IP adresi girin: ")
        return [ip]
    
    else:
        print("❌ Geçersiz seçim! Program sonlandırılıyor.")
        exit()

def main():
    print_banner()
    output_file = "web_services.txt"  # Sonuçları buraya kaydediyoruz
    html_file = "web_services.html"  # HTML dosyası
    
    # Daha kapsamlı tarama için genişletilmiş web portları listesi
    ports_to_scan = [
        80, 443, 8080, 8443, 8000, 8888, 8081, 8090, 9000, 5000, 7000, 9090, 10000, 10443, 
        18080, 28080, 3000, 3001, 5001, 5601, 5672, 15672, 61613, 8161, 9200, 4505, 4506, 
        8444, 9443, 16000, 18000, 27017, 28017, 3306, 5432, 5984, 6379, 7001, 7474, 8001, 
        8082, 8083, 8091, 8092, 8448, 8500, 8778, 8880, 9001, 9042, 9091, 9201, 9444, 9999
    ]
    
    # HTML dosyasını başlat
    with open(html_file, "w") as f:
        f.write("<html><body><h2>Tarama Sonuçları</h2>\n")
    
    ip_list = get_ip_list()
    
    threads = []
    for ip in ip_list:
        t = threading.Thread(target=scan_ip, args=(ip, ports_to_scan, output_file, html_file))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    # HTML dosyasını kapat
    with open(html_file, "a") as f:
        f.write("</body></html>")
    
    print("\n✅ Tarama tamamlandı! Sonuçlar 'web_services.txt' ve 'web_services.html' dosyasına kaydedildi.")
    
    # HTML dosyasını otomatik aç
    webbrowser.open(html_file)

if __name__ == "__main__":
    main()
