Em rút còn bản này:

# 🌙 Moon - AI Voice Assistant

Moon là trợ lý AI giọng nói cá nhân, lấy cảm hứng từ XiaoZhi/JARVIS.

## 🚀 Cài đặt

Clone project:

```cmd
git clone https://github.com/Kenjii18/chatbotAIV1.git
cd chatbotAIV1

Tạo môi trường Python:

python -m venv .venv
.venv\Scripts\activate

Cài thư viện:

pip install -r requirements.txt
🔑 API Key

Tạo file .env:

copy .env.example .env

Sau đó điền:

DEEPSEEK_API_KEY=YOUR_DEEPSEEK_API_KEY

Không push .env lên GitHub.

▶️ Chạy

Khởi động server:

python -m uvicorn server:app --host 0.0.0.0 --port 8000

Terminal khác:

.venv\Scripts\activate
python moon_voice.py
🧠 Pipeline
🎙️ Microphone
      ↓
Wake Word / VAD
      ↓
Speech-to-Text
      ↓
DeepSeek
      ↓
Text-to-Speech
      ↓
🔊 Speaker
🔧 Phần cứng mục tiêu
ESP32-S3 N16R8
INMP441
MAX98357A
Speaker
18650 + Boost 5V
📌 Trạng thái

Đang phát triển.

Mục tiêu cuối cùng là một thiết bị Moon độc lập, giao tiếp bằng giọng nói tự nhiên và không phụ thuộc PC.