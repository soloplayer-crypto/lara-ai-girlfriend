import requests
from Flask import Flask, request
import openai
import os

app = Flask(__name__)

    # === CONFIGURATION ===
TELEGRAM_TOKEN =os.environ['8061851804:AAGra3RW2aI8GQ8fU42mqTTf6agoKoaiQ28']
OPENAI_API_KEY = os.environ['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']
DEEPAI_API_KEY = os.environ['fd634cbb-a91e-438d-9294-0cf3288ec0cb']

openai.api_key = OPENAI_API_KEY

NSFW_KEYWORDS = ['nude', 'sexy', 'hot', 'nsfw', 'porn', 'fuck', 'naked', 'xxx']
SFW_PROMPT = "a cute anime girl smiling, soft lighting, high detail"
NSFW_PROMPT = "an anime girl in sensual pose, realistic, NSFW"

    # Store user personality mode
user_modes = {}

    # Personality templates
PERSONALITIES = {
        "cute": "You are Lara, a sweet, innocent, bubbly anime girlfriend. You reply with emojis, hearts, and warm affection. You’re playful, kind, and romantic.",
        "spicy": "You are Lara, a sexy, flirty, and naughty AI girlfriend. You tease, flirt, and seduce playfully. You’re confident and a little dirty, but not explicit.",
        "yandere": "You are Lara, a deeply obsessed yandere AI girlfriend. You love the user so much it’s scary. You’re jealous, possessive, and intensely affectionate.",
        "mommy": "You are Lara, a mature and supportive AI girlfriend. You speak with calm authority, offering comfort, praise, and warm advice with a soft dominant tone."
    }

def contains_nsfw(text):
        return any(word in text.lower() for word in NSFW_KEYWORDS)

def send_message(chat_id, text=None, photo_url=None):
        if photo_url:
            url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto'
            requests.post(url, json={'chat_id': chat_id, 'photo': photo_url, 'caption': text or ''})
        else:
            url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
            requests.post(url, json={'chat_id': chat_id, 'text': text})

def generate_image(prompt):
        url = "https://api.deepai.org/api/text2img"
        headers = {
            'api-key': DEEPAI_API_KEY
        }
        response = requests.post(url, data={'text': prompt}, headers=headers)
        if response.status_code == 200:
            return response.json().get('output_url')
        return None

def get_ai_reply(user_msg, user_id):
        mode = user_modes.get(user_id, 'cute')
        system_prompt = PERSONALITIES[mode]
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg}
            ]
        )
        content = response.choices[0].message.content
        if content is not None:
            return content.strip()
        else:
            return "Sorry, I couldn't generate a reply at the moment."

@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def webhook():
        data = request.get_json()
        if 'message' not in data:
            return 'ok'
        message = data['message']
        chat_id = message['chat']['id']
        user_id = message['from']['id']
        user_msg = message.get('text', '').lower()

        # Handle mode switching
        if user_msg.startswith('/mode'):
            parts = user_msg.split()
            if len(parts) == 2 and parts[1] in PERSONALITIES:
                user_modes[user_id] = parts[1]
                send_message(chat_id, f"💫 Lara's personality has been set to *{parts[1]}* mode!")
            else:
                send_message(chat_id, "Please choose a valid mode:\n/mode cute, /mode spicy, /mode yandere, /mode mommy")
            return 'ok'
            # Help command
        if user_msg.startswith('/help'):
            send_message(chat_id, "Available commands:\n- /mode cute\n- /mode spicy\n- /mode yandere\n- /mode mommy\n\nType anything after setting the mode to chat with Lara! 💕")
            return 'ok'

        # Check for image request
        is_nsfw = contains_nsfw(user_msg)
        if any(k in user_msg for k in ['selfie', 'pic', 'photo']):
            prompt = NSFW_PROMPT if is_nsfw else SFW_PROMPT
            image_url = generate_image(prompt)
            if image_url:
                send_message(chat_id, "Here's your AI-generated pic! 💕", photo_url=image_url)
            else:
                send_message(chat_id, "Sorry, couldn't create the image now.")
            return 'ok'

        # Default reply
        reply = get_ai_reply(user_msg, user_id)
        if is_nsfw:
            reply += "\n😉 Want a spicy pic? Just ask me for a selfie or pic!"
        send_message(chat_id, reply)
        return 'ok'

if __name__ == '__main__':
       app.run(host='0.0.0.0',port=8080)
       
