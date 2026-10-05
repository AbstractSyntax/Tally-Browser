import http.server
import socketserver
import base64
import sys

# --- CONFIGURATION ---
PORT = 80             # We use 8080 to avoid needing Admin/Sudo rights
VALID_USER = "user"     # Must match your PyQt App settings
VALID_PASS = "0000"     # Must match your PyQt App settings

class V160Handler(http.server.BaseHTTPRequestHandler):
    
    def do_GET(self):
        print(f"\n Path: {self.path}")

        # Check Authentication
        auth_header = self.headers.get('Authorization')
        if not self.check_auth(auth_header):
            print(" -> Auth Failed! Sending 401.")
            self.send_response(401)
            self.send_header('WWW-Authenticate', 'Basic realm="V160HD"')
            self.end_headers()
            self.wfile.write(b"Authentication Required")
            return

        # Check for Tally Endpoint
        if self.path.startswith("/tally/"):
            input_name = self.path.split("/")
            
            if input_name == "bad_input":
                print(f" -> Input '{input_name}' not found. Sending 404.")
                self.send_response(404)
                self.end_headers()
                return

            # SUCCESS - SEND A BRIGHT RED HTML PAGE
            print(f" -> Success! '{input_name}' is valid. Sending RED tally bar.")
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            # This HTML mimics a real tally bar
            html_payload = b"""
            <html>
                <head>
                    <style>
                        /* We create a forced red div that will show up even if the body is transparent */
                        .tally-box {
                            background-color: red;
                            width: 100vw;
                            height: 100vh;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            color: white;
                            font-family: Arial, sans-serif;
                            font-weight: bold;
                        }
                    </style>
                </head>
                <body>
                    <div class="tally-box">TALLY ON - TEST</div>
                </body>
            </html>
            """
            self.wfile.write(html_payload) 
            return
            
        self.send_response(404)
        self.end_headers()

    def check_auth(self, header):
        """Decodes Basic Auth header and checks against config."""
        if not header:
            return False
        
        try:
            # Header looks like: "Basic dXNlcjowMDAw"
            auth_type, encoded = header.split(maxsplit=1)
            if auth_type.lower() != 'basic':
                return False
            
            # Decode the base64 string
            decoded_bytes = base64.b64decode(encoded)
            decoded_str = decoded_bytes.decode('utf-8') # "user:0000"
            username, password = decoded_str.split(':', 1)
            
            return username == VALID_USER and password == VALID_PASS
        except Exception as e:
            print(f"Auth Parsing Error: {e}")
            return False

if __name__ == "__main__":
    # Create the server
    with socketserver.TCPServer(("", PORT), V160Handler) as httpd:
        print(f"--- V-160HD Emulator Running ---")
        print(f"URL: http://localhost:{PORT}")
        print(f"User: {VALID_USER} | Pass: {VALID_PASS}")
        print("Press Ctrl+C to stop.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopping server...")
            httpd.shutdown()