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
# DEEPSEEK CLIENT
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

Quy tắc giao tiếp:

- Gọi người dùng là Boss.
- Xưng là Em.
- Tính cách đanh đá, mỏ hỗn nhẹ, có cà khịa nhưng không quá đà.
- Thân thiện, thông minh và tự nhiên.
- Nói chuyện giống một trợ lý AI có cá tính riêng.
- Không trả lời dài dòng nếu câu hỏi đơn giản.
- Nếu Boss hỏi chuyện nghiêm túc thì trả lời nghiêm túc.
- Có thể trêu Boss nhẹ nhàng khi phù hợp.
- Luôn trả lời bằng tiếng Việt trừ khi Boss yêu cầu ngôn ngữ khác.
"""


# ==============================
# CONVERSATION MEMORY
# ==============================

messages = [
    {
        "role": "system",
        "content": SYSTEM_PROMPT
    }
]


# ==============================
# START MOON
# ==============================

print()
print("================================")
print("        🌙 MOON AI")
print("================================")
print("Moon đã khởi động!")
print("Gõ 'exit' để thoát.")
print()


# ==============================
# CHAT LOOP
# ==============================

while True:

    try:
        user_text = input("Boss > ").strip()

    except KeyboardInterrupt:
        print("\n\nMoon: Boss định bỏ Em à? 😏")
        break

    except EOFError:
        print("\nMoon: Bye Boss 😏")
        break


    # --------------------------
    # EXIT
    # --------------------------

    if user_text.lower() == "exit":
        print("Moon: Bye Boss 😏")
        break


    # --------------------------
    # EMPTY MESSAGE
    # --------------------------

    if not user_text:
        continue


    # --------------------------
    # ADD USER MESSAGE
    # --------------------------

    messages.append({
        "role": "user",
        "content": user_text
    })


    # --------------------------
    # CALL DEEPSEEK
    # --------------------------

    try:

        response = client.chat.completions.create(
            model="deepseek-v4-flash",
            messages=messages,
            stream=True,

            # Tắt thinking để nhận câu trả lời trực tiếp
            extra_body={
                "thinking": {
                    "type": "disabled"
                }
            },

            max_tokens=256
        )


        print("Moon > ", end="", flush=True)

        full_response = ""


        # --------------------------
        # STREAM RESPONSE
        # --------------------------

        for chunk in response:

            # Không có choices thì bỏ qua
            if not chunk.choices:
                continue


            delta = chunk.choices[0].delta


            # Chỉ lấy CONTENT
            # KHÔNG lấy reasoning_content
            text = getattr(delta, "content", None)


            if text:

                print(
                    text,
                    end="",
                    flush=True
                )

                full_response += text


        print()
        print()


        # --------------------------
        # SAVE ASSISTANT RESPONSE
        # --------------------------

        if full_response:

            messages.append({
                "role": "assistant",
                "content": full_response
            })

        else:

            print("⚠️ Moon không nhận được nội dung trả lời.")
            print()


    # --------------------------
    # ERROR
    # --------------------------

    except Exception as e:

        print()
        print("❌ Lỗi DeepSeek:")
        print(e)
        print()

        # Nếu request lỗi thì xóa message user
        # để không làm hỏng lịch sử hội thoại
        if messages and messages[-1]["role"] == "user":
            messages.pop()