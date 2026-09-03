# 🌙 Moon - AI Voice Assistant

Moon là trợ lý AI giọng nói cá nhân, lấy cảm hứng từ XiaoZhi/JARVIS.

Project hiện đang trong quá trình phát triển. Repository này là **code base chính của Moon** để tiếp tục xây dựng và mở rộng.

---

## 🚀 Cài đặt

Clone project:

    git clone https://github.com/Kenjii18/chatbotAIV1.git
    cd chatbotAIV1

Tạo môi trường Python:

    python -m venv .venv

Kích hoạt môi trường:

    .venv\Scripts\activate

Cài đặt thư viện:

    pip install -r requirements.txt

---

## 🔑 API Key

Tạo file `.env` từ file mẫu:

    copy .env.example .env

Mở `.env` và điền DeepSeek API Key:

    DEEPSEEK_API_KEY=YOUR_DEEPSEEK_API_KEY

**Không push file `.env` lên GitHub.**

---

## ▶️ Chạy Moon Server

Moon Server là backend hiện tại của project.

Khởi động server:

    python -m uvicorn server:app --host 0.0.0.0 --port 8000

Server sẽ chạy tại:

    http://127.0.0.1:8000

---

## 🧪 Chạy Prototype Voice

Sau khi Moon Server đang chạy, mở một terminal khác:

    .venv\Scripts\activate

Sau đó chạy prototype voice:

    python moon_voice.py

`moon_voice.py` hiện tại chỉ là **prototype trong quá trình phát triển**, không phải kiến trúc cuối cùng của Moon.

---

## 📁 Cấu trúc hiện tại

    Moon/
    │
    ├── server.py
    ├── moon_voice.py
    ├── wake_test.py
    ├── test_mic.py
    ├── test_stt.py
    │
    ├── requirements.txt
    ├── .env.example
    ├── .gitignore
    └── README.md

### Các thành phần

- `server.py` — Moon Server / backend
- `moon_voice.py` — prototype voice pipeline
- `wake_test.py` — thử nghiệm Wake Word
- `test_mic.py` — kiểm tra microphone
- `test_stt.py` — kiểm tra Speech-to-Text
- `requirements.txt` — Python dependencies
- `.env.example` — mẫu cấu hình API

---

## 🧠 Kiến trúc mục tiêu

Moon sẽ được phát triển thành một trợ lý AI giọng nói độc lập:

    ESP32-S3
        ↓
    Microphone
        ↓
    Wake Word / VAD
        ↓
    Audio Streaming
        ↓
    Moon Server
        ↓
    Speech-to-Text
        ↓
    DeepSeek
        ↓
    Streaming TTS
        ↓
    Audio Streaming
        ↓
    ESP32-S3
        ↓
    Speaker

Mục tiêu cuối cùng là Moon có thể hoạt động như một thiết bị riêng, **không phụ thuộc vào PC để sử dụng hằng ngày**.

---

## 🔧 Phần cứng mục tiêu

- ESP32-S3 N16R8
- INMP441 MEMS Microphone
- MAX98357A I2S Amplifier
- Speaker
- 18650 Battery
- Boost Converter 3.7V → 5V

---

## 📌 Trạng thái

🚧 **Đang phát triển**

Các thành phần hiện tại mới là nền tảng/prototype ban đầu.

Project sẽ tiếp tục được phát triển với các thành phần như:

- Wake Word
- VAD
- ESP32-S3 Firmware
- WebSocket Audio Streaming
- Speech-to-Text
- DeepSeek LLM
- Streaming TTS
- Audio Playback
- Wi-Fi Reconnect
- OTA Update
- Conversation Memory
- Device Configuration

---

## 🎯 Mục tiêu

Xây dựng một trợ lý AI giọng nói cá nhân có tên **Moon**, có khả năng giao tiếp tự nhiên, phản hồi nhanh và hoạt động độc lập trên phần cứng ESP32-S3.

Project được phát triển từng bước từ prototype đến thiết bị hoàn chỉnh.