import json
import urllib.request
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs


class handler(BaseHTTPRequestHandler):

  def do_POST(self):
    try:
      content_length = int(self.headers.get('Content-Length', 0))
      post_data = self.rfile.read(content_length).decode('utf-8')
      params = parse_qs(post_data)

      video_url = params.get('video_url', [''])[0]

      if not video_url:
        self.send_response(400)
        self.end_headers()
        self.wfile.write(b'URL is required')
        return

      # 1. طلب التنزيل مباشرة عبر Cobalt API المفتوحة
      api_url = 'https://api.cobalt.tools/api/json'
      headers = {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
      }

      payload = json.dumps({
          'url': video_url,
          'videoQuality': 'max',
          'downloadMode': 'auto',
      }).encode('utf-8')

      req = urllib.request.Request(
          api_url, data=payload, headers=headers, method='POST'
      )

      with urllib.request.urlopen(req) as response:
        res_data = json.loads(response.read().decode('utf-8'))

      # 2. الحصول على رابط التحميل المباشر والتحويل إليه
      download_link = res_data.get('url')

      if download_link:
        self.send_response(302)
        self.send_header('Location', download_link)
        self.end_headers()
      else:
        self.send_response(500)
        self.end_headers()
        self.wfile.write(b'Failed to extract video URL')

    except Exception as e:
      self.send_response(500)
      self.end_headers()
      self.wfile.write(f'Error: {str(e)}'.encode('utf-8'))
