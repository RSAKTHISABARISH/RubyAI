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

def kill_process_on_port(port):
    try:
        import psutil
        for proc in psutil.process_iter(['pid', 'name']):
            for conn in proc.connections(kind='inet'):
                if conn.laddr.port == port:
                    print(f"      - Stopping existing process {proc.info['name']} (PID: {proc.info['pid']}) on port {port}...")
                    proc.kill()
    except Exception:
        # Fallback for Windows if psutil is not available
        try:
            output = subprocess.check_output(f'netstat -ano | findstr :{port}', shell=True).decode()
            for line in output.strip().split('\n'):
                pid = line.strip().split()[-1]
                if pid != '0':
                    subprocess.run(f'taskkill /F /PID {pid}', shell=True, capture_output=True)
        except:
            pass

def start_services():
    print("="*50)
    print("      RUBY REMOTE ACCESS STARTUP")
    print("="*50)
    
    port = 5001
    
    # Pre-check: Close processes using the port
    print(f"\n[0/3] Cleaning up port {port}...")
    kill_process_on_port(port)
    time.sleep(1)

    # 1. Start Web Server
    print("\n[1/3] Starting Ruby Dashboard...")
    server_proc = subprocess.Popen([sys.executable, "frontend/web_server.py"], 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.STDOUT,
                                    text=True)
    
    time.sleep(3)
    local_ip = get_local_ip()
    print(f"      - Local Access: http://localhost:{port}")
    print(f"      - Wifi Access:  http://{local_ip}:{port}")
    
    # 2. Start Tunnel (Try LocalTunnel first, then Ngrok)
    print("\n[2/3] Starting Public Tunnel...")
    
    # Method A: LocalTunnel
    tunnel_proc = subprocess.Popen(["lt", "--port", str(port)], 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.STDOUT,
                                    text=True,
                                    shell=True)
    
    time.sleep(2)
    
    print("\n[3/3] Ready! Scan or copy the link below:")
    print("-" * 50)
    
    try:
        # Wait a bit for LT to provide URL
        timeout = 10
        found_url = False
        start_time = time.time()
        
        print("Checking for LocalTunnel URL...")
        while time.time() - start_time < timeout:
            line = tunnel_proc.stdout.readline()
            if "url is:" in line.lower():
                url = line.split("is:")[-1].strip()
                print(f"\n      PUBLIC URL: {url}")
                found_url = True
                break
            time.sleep(0.1)

        if not found_url:
            print("\nLocalTunnel slow... Try starting Ngrok as fallback?")
            print("Running: ngrok http 5001")
            # If LT fails, you can manually run 'ngrok http 5001' in another terminal.
        
        print("\nRuby is running. Press Ctrl+C to stop everything.")
        
        while True:
            # Keep reading server output
            server_line = server_proc.stdout.readline()
            if server_line:
                print(f"[REB] {server_line.strip()}")
            time.sleep(0.01)
            
    except KeyboardInterrupt:
        print("\n\nStopping services...")
        server_proc.terminate()
        tunnel_proc.terminate()
        print("Goodbye!")

if __name__ == "__main__":
    start_services()
