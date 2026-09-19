import os
import requests
import csv
import random

def run():
    labels_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend', 'labels')
    os.makedirs(labels_dir, exist_ok=True)
    
    url = "https://raw.githubusercontent.com/scamsniffer/scam-database/main/blacklist/address.json"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except Exception:
        url = "https://raw.githubusercontent.com/scamsniffer/scam-database/master/blacklist/address.json"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        
    data = resp.json()
    
    all_csv = os.path.join(labels_dir, 'scam_all.csv')
    signal_csv = os.path.join(labels_dir, 'scam_signal.csv')
    test_csv = os.path.join(labels_dir, 'scam_test.csv')
    
    addresses = list(set([a.lower() for a in data]))
    random.seed(42)
    random.shuffle(addresses)
    
    mid = len(addresses) // 2
    signal_addrs = addresses[:mid]
    test_addrs = addresses[mid:]
    
    def write_csv(path, addrs):
        with open(path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['address', 'label', 'source'])
            for a in addrs:
                writer.writerow([a, 'scam', 'scamsniffer'])
                
    write_csv(all_csv, addresses)
    write_csv(signal_csv, signal_addrs)
    write_csv(test_csv, test_addrs)
    print(f"Total: {len(addresses)}, Signal: {len(signal_addrs)}, Test: {len(test_addrs)}")

if __name__ == '__main__':
    run()
