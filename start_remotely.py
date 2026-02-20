import os
import subprocess
import time
import socket
import sys

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def start_services():
    print("="*50)
    print("      RUBY REMOTE ACCESS STARTUP")
    print("="*50)
    
    # 1. Start Web Server
    print("\n[1/3] Starting Ruby Dashboard...")
    server_proc = subprocess.Popen([sys.executable, "frontend/web_server.py"], 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.STDOUT,
                                    text=True)
    
    time.sleep(3)
    
    local_ip = get_local_ip()
    port = 5001
    
    print(f"      - Local Access: http://localhost:{port}")
    print(f"      - Wifi Access:  http://{local_ip}:{port}")
    
    # 2. Start Tunnel
    print("\n[2/3] Starting Public Tunnel (LocalTunnel)...")
    tunnel_proc = subprocess.Popen(["lt", "--port", str(port)], 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.STDOUT,
                                    text=True)
    
    print("\n[3/3] Ready! Scan or copy the link below:")
    print("-" * 50)
    
    try:
        # Try to find the URL from the tunnel output
        for line in tunnel_proc.stdout:
            if "url is:" in line.lower():
                url = line.split("is:")[-1].strip()
                print(f"\n      PUBLIC URL: {url}")
                print("\n      Open this on your phone!")
                print("-" * 50)
                break
        
        print("\nRuby is running. Press Ctrl+C to stop everything.")
        
        while True:
            # Keep reading server output to prevent buffer fill
            server_line = server_proc.stdout.readline()
            if server_line:
                print(f"[REB] {server_line.strip()}")
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n\nStopping services...")
        server_proc.terminate()
        tunnel_proc.terminate()
        print("Goodbye!")

if __name__ == "__main__":
    start_services()
