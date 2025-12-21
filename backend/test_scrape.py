import urllib.request
import sys
import json

def test_scrape():
    url = "http://localhost:8001/api/scrape?topic=motivation"
    print(f"Connecting to {url}...")
    try:
        with urllib.request.urlopen(url) as response:
            print("Connected. Reading stream...")
            for line in response:
                if line:
                    decoded = line.decode('utf-8').strip()
                    if not decoded:
                        continue
                    print(f"Received: {decoded}")
                    
                    if "error" in decoded.lower() and "stream interrupted" not in decoded.lower():
                         print("Error in stream response!")
                         sys.exit(1)
                    if "text" in decoded or "total" in decoded:
                        print("Success! Data received.")
                        sys.exit(0)
    except Exception as e:
        print(f"Request failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_scrape()
