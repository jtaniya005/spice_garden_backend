import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from app.services.chat_service import get_chat_reply

try:
    reply = get_chat_reply([{'role': 'user', 'content': 'Hello! Can you list all the dishes you have?'}])
    with open('test_output.txt', 'w', encoding='utf-8') as f:
        f.write(str(reply))
except Exception as e:
    with open('test_output.txt', 'w', encoding='utf-8') as f:
        f.write(str(e))
