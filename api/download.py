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

      # 1. إعداد الطلب لسيرفر Cobalt مع إضافة User-Agent لمنع خطأ 403 Forbidden
      api_url = 'https://api.cobalt.tools/api/json'
      headers = {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'User-Agent': (
              'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
              ' (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
          ),
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

      # 2. الحصول على رابط التحميل أو إرجاع فيديو المقطع
      download_link = res_data.get('url')

      if download_link:
        self.send_response(302)
        self.send_header('Location', download_link)
        self.end_headers()
      else:
        self.send_response(400)
        self.end_headers()
        self.wfile.write(
            b'Could not fetch video. Please check the URL or try another link.'
        )

    except Exception as e:
      self.send_response(500)
      self.end_headers()
      self.wfile.write(f'Error: {str(e)}'.encode('utf-8'))
