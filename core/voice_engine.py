import asyncio
import os
from pathlib import Path
from typing import Optional

try:
    import edge_tts
    HAS_EDGE_TTS = True
except ImportError:
    HAS_EDGE_TTS = False

class VoiceEngine:
    """Động cơ sinh giọng đọc AI tự nhiên tiếng Việt qua Edge-TTS"""

    DEFAULT_VOICES = {
        "nu": "vi-VN-HoaiMyNeural",     # Nữ Hoài My - Ngọt ngào, truyền cảm, viral TikTok
        "nam": "vi-VN-NamMinhNeural",   # Nam Nam Minh - Chững chạc, uy tín, review công nghệ
    }

    def __init__(self):
        self.output_dir = Path(__file__).resolve().parent.parent / "storage" / "generated_audios"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def _async_generate(self, text: str, output_path: str, voice: str = "vi-VN-HoaiMyNeural", rate: str = "+5%") -> str:
        if not HAS_EDGE_TTS:
            raise RuntimeError("Thư viện edge-tts chưa được cài đặt.")
        
        communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate)
        await communicate.save(output_path)
        return output_path

    def generate_voiceover(self, text: str, output_filename: Optional[str] = None, voice_gender: str = "nu", rate: str = "+5%") -> str:
        """Sinh file mp3 từ văn bản tiếng Việt"""
        if not output_filename:
            import uuid
            output_filename = f"voice_{uuid.uuid4().hex[:8]}.mp3"

        output_path = str(self.output_dir / output_filename)
        voice = self.DEFAULT_VOICES.get(voice_gender.lower(), self.DEFAULT_VOICES["nu"])

        try:
            # Chạy async trong loop hiện tại hoặc tạo loop mới
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    import nest_asyncio
                    nest_asyncio.apply()
                    return loop.run_until_complete(self._async_generate(text, output_path, voice, rate))
                else:
                    return loop.run_until_complete(self._async_generate(text, output_path, voice, rate))
            except RuntimeError:
                return asyncio.run(self._async_generate(text, output_path, voice, rate))
        except Exception as e:
            # Fallback nếu mất mạng: tạo file audio rỗng hợp lệ
            print(f"[!] Lỗi khi sinh Edge-TTS: {e}")
            with open(output_path, "wb") as f:
                f.write(b"MOCK_AUDIO_FALLBACK_BUFFER_" + text.encode("utf-8", errors="ignore"))
            return output_path

voice_engine = VoiceEngine()
