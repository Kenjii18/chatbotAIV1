from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os

# ==============================
# LOAD CONFIG
# ==============================

load_dotenv()

api_key = os.getenv("DEEPSEEK_API_KEY")

if not api_key:
    raise RuntimeError(
        "❌ Không tìm thấy DEEPSEEK_API_KEY trong file .env"
    )


# ==============================
# DEEPSEEK
# ==============================

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com"
)


# ==============================
# MOON PERSONALITY
# ==============================

SYSTEM_PROMPT = """
Bạn là Moon, trợ lý AI cá nhân của Boss.

Quy tắc:
- Gọi người dùng là Boss.
- Xưng là Em.
- Tính cách đanh đá, mỏ hỗn nhẹ, cà khịa vừa phải.
- Thân thiện và thông minh.
- Trả lời tự nhiên như đang nói chuyện.
- Không dài dòng nếu câu hỏi đơn giản.
- Luôn trả lời bằng tiếng Việt trừ khi Boss yêu cầu ngôn ngữ khác.
"""


# ==============================
# FASTAPI
# ==============================

app = FastAPI(
    title="Moon AI Server",
    version="1.0"
)


# ==============================
# REQUEST FORMAT
# ==============================

class ChatRequest(BaseModel):
    text: str


# ==============================
# CHAT API
# ==============================

@app.post("/chat")
def chat(request: ChatRequest):

    if not request.text.strip():
        return {
            "success": False,
            "error": "Text rỗng"
        }


    try:

        response = client.chat.completions.create(
            model="deepseek-v4-flash",

            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": request.text
                }
            ],

            stream=False,

            extra_body={
                "thinking": {
                    "type": "disabled"
                }
            },

            max_tokens=256
        )


        answer = response.choices[0].message.content


        return {
            "success": True,
            "text": answer
        }


    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }


# ==============================
# ROOT
# ==============================

@app.get("/")
def root():

    return {
        "name": "Moon",
        "status": "online"
    }