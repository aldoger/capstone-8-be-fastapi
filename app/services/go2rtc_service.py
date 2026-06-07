import os
import requests
import yt_dlp

YOUTUBE_HOSTS = ("youtube.com", "youtu.be")


class Go2RtcService:
    """Registers external sources with go2rtc and hands back playback URLs."""

    def __init__(self):
        self.api_url = os.getenv("GO2RTC_API_URL", "http://localhost:1984")
        self.rtsp_host = os.getenv("GO2RTC_RTSP_HOST", "localhost:8554")

    def _resolve_youtube_url(self, source_url: str) -> str:
        """Resolve a YouTube page URL to a direct playable media URL.

        ffmpeg/go2rtc can't read the YouTube HTML page directly, so the
        actual stream URL has to be extracted via yt-dlp first.
        """
        ydl_opts = {"quiet": True, "noplaylist": True, "format": "best"}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(source_url, download=False)
            return info["url"]

    def add_stream(self, stream_id: str, source_url: str) -> str:
        if any(host in source_url for host in YOUTUBE_HOSTS):
            source_url = self._resolve_youtube_url(source_url)

        response = requests.put(
            f"{self.api_url}/api/streams",
            params={
                "name": stream_id,
                "src": f"ffmpeg:{source_url}#video=h264",
            },
            timeout=10,
        )

        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            raise RuntimeError(
                f"go2rtc error ({response.status_code}): {response.text}"
            ) from e

        return f"rtsp://{self.rtsp_host}/{stream_id}"


go2rtc_service = Go2RtcService()
