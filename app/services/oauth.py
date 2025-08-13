import os, threading, webbrowser, http.server, socketserver, urllib.parse, json, time, requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL").rstrip("/")
SUPABASE_ANON = os.getenv("SUPABASE_ANON_KEY")

LOCAL_PORT = 8910
REDIRECT_URI = f"http://127.0.0.1:{LOCAL_PORT}/callback"

def start_google_oauth():
    params = {
        "provider": "google",
        "redirect_to": REDIRECT_URI,
        "scopes": "email profile"
    }
    url = f"{SUPABASE_URL}/auth/v1/authorize?{urllib.parse.urlencode(params)}"

    code_holder = {"code": None, "error": None}

    class Handler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            parsed = urllib.parse.urlparse(self.path)
            if parsed.path == "/callback":
                qs = urllib.parse.parse_qs(parsed.query)
                code_holder["code"] = (qs.get("code") or [None])[0]
                code_holder["error"] = (qs.get("error_description") or [None])[0]
                self.send_response(200)
                self.send_header("Content-Type","text/html")
                self.end_headers()
                self.wfile.write(b"<h2>You may close this tab and return to ExpenseMaster.</h2>")
            else:
                self.send_response(404); self.end_headers()

    httpd = socketserver.TCPServer(("", LOCAL_PORT), Handler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()

    webbrowser.open(url)

    for _ in range(240):
        if code_holder["code"] or code_holder["error"]:
            break
        time.sleep(0.5)

    httpd.shutdown()

    if code_holder["error"]:
        raise RuntimeError(code_holder["error"] or "OAuth error")

    if not code_holder["code"]:
        raise RuntimeError("Timed out waiting for Google Sign-In.")

    token_url = f"{SUPABASE_URL}/auth/v1/token?grant_type=authorization_code"
    headers = {
        "apikey": SUPABASE_ANON,
        "Content-Type": "application/json"
    }
    payload = {
        "code": code_holder["code"],
        "redirect_uri": REDIRECT_URI
    }
    r = requests.post(token_url, headers=headers, json=payload, timeout=20)
    r.raise_for_status()
    return r.json()
