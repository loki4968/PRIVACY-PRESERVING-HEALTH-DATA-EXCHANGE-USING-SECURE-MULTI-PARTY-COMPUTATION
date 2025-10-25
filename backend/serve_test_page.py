import http.server
import socketserver

PORT = 8080
Handler = http.server.SimpleHTTPRequestHandler

print(f'Starting server at http://localhost:{PORT}/backend/test_fetch.html')
print('Press Ctrl+C to stop the server')

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    httpd.serve_forever()