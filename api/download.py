import json
import os
import subprocess
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs


class handler(BaseHTTPRequestHandler):

  def do_POST(self):
    try:
      content_length = int(self.headers.get('Content-Length', 0))
      post_data = self.rfile.read(content_length).decode('utf-8')
      params = parse_qs(post_data)

      video_url = params.get('video_url', [''])[0]
      remove_music = params.get('remove_music', ['true'])[0] == 'true'

      if not video_url:
        self.send_response(400)
        self.end_headers()
        self.wfile.write(b'URL is required')
        return

      # 1. تنزيل الفيديو بأعلى جودة وبدون حقوق/علامة مائية
      input_path = '/tmp/input_video.mp4'
      dl_cmd = f'yt-dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" --no-watermark -o "{input_path}" "{video_url}"'
      subprocess.run(dl_cmd, shell=True, check=True)

      final_output = input_path

      # 2. عزل الصوت والموسيقى بدقة عالية عند اختيار الخيار
      if remove_music:
        output_dir = '/tmp/out'
        subprocess.run(
            f'demucs --two-stems=vocals {input_path} -o {output_dir}',
            shell=True,
            check=True,
        )

        clean_audio = f'{output_dir}/htdemucs/input_video/vocals.wav'
        clean_video_path = '/tmp/clean_video.mp4'

        # دمج الصوت المنقى مع الفيديو الأصلي بسرعة عبر FFmpeg
        merge_cmd = f'ffmpeg -y -i {input_path} -i {clean_audio} -c:v copy -map 0:v:0 -map 1:a:0 {clean_video_path}'
        subprocess.run(merge_cmd, shell=True, check=True)
        final_output = clean_video_path

      # 3. إرسال الملف النهائي للمستخدم للتحميل مباشرة
      self.send_response(200)
      self.send_header('Content-Type', 'video/mp4')
      self.send_header(
          'Content-Disposition', 'attachment; filename="Clean_Video.mp4"'
      )
      self.end_headers()

      with open(final_output, 'rb') as f:
        self.wfile.write(f.read())

    except Exception as e:
      self.send_response(500)
      self.end_headers()
      self.wfile.write(f'Error processing video: {str(e)}'.encode('utf-8'))
