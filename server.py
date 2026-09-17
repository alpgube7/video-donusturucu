"""
Video Dönüştürücü - Yerel Sunucu
SharedArrayBuffer + çoklu çekirdek desteği için COOP/COEP başlıkları ekler.
@ffmpeg/core-mt (multi-threaded) kullanarak tam CPU gücünü sağlar.

Kullanim:
  python server.py
  Veya:
  python server.py 8080

Tarayicida: http://localhost:8080
"""
import http.server
import socketserver
import sys
import os
import urllib.request

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
CORE_MT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'core-mt')
CORE_MT_URL = 'https://cdn.jsdelivr.net/npm/@ffmpeg/core-mt@0.12.6/dist/esm'

def download_core_mt():
    """core-mt dosyalarini indir (ilk calistirmada)."""
    if os.path.exists(os.path.join(CORE_MT_DIR, 'ffmpeg-core.wasm')):
        return  # zaten indirilmis

    os.makedirs(CORE_MT_DIR, exist_ok=True)
    files = ['ffmpeg-core.js', 'ffmpeg-core.wasm', 'ffmpeg-core.worker.js']
    print("core-mt dosyalari indiriliyor (ilk sefer ~35MB)...")
    for f in files:
        url = f'{CORE_MT_URL}/{f}'
        dest = os.path.join(CORE_MT_DIR, f)
        print(f"  {f}...")
        urllib.request.urlretrieve(url, dest)
        size_mb = os.path.getsize(dest) / (1024*1024)
        print(f"    {size_mb:.1f} MB")
    print("core-mt hazir!\n")

class COOPCOEPHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cross-Origin-Opener-Policy', 'same-origin')
        self.send_header('Cross-Origin-Embedder-Policy', 'require-corp')
        self.send_header('Cache-Control', 'no-cache')
        super().end_headers()

    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {format % args}")

# core-mt dosyalarini indir
download_core_mt()

with socketserver.TCPServer(("", PORT), COOPCOEPHandler) as httpd:
    print(f"Video Dönüştürücü sunucusu baslatildi!")
    print(f"  http://localhost:{PORT}")
    print(f"  COOP/COEP basliklari aktif — coklu cekirdek destegi")
    print(f"  Durdurmak icin: Ctrl+C")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nSunucu kapatildi.")
