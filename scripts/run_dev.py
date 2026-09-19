import subprocess
import sys
import os

def run():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    backend_cmd = [sys.executable, "-m", "uvicorn", "backend.main:app", "--reload", "--port", "8000"]
    frontend_cmd = ["npm", "run", "dev"]
    
    print("Starting backend...")
    b_proc = subprocess.Popen(backend_cmd, cwd=root)
    
    print("Starting frontend...")
    # On Windows, npm is a .cmd file so we need shell=True
    is_windows = sys.platform.startswith('win')
    f_proc = subprocess.Popen(frontend_cmd, cwd=os.path.join(root, "frontend"), shell=is_windows)
    
    try:
        b_proc.wait()
        f_proc.wait()
    except KeyboardInterrupt:
        print("Stopping servers...")
        b_proc.terminate()
        f_proc.terminate()

if __name__ == '__main__':
    run()
