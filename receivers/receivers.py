import requests


from receivers.models import Message


class TelegramReceiver:
    def __init__(self, receiver):
        self.receiver = receiver
        self.base = f"https://api.telegram.org/bot{receiver.token}/sendMessage"

    def send_message(self, text):
        params = {"chat_id": self.receiver.channel, "text": text}
        response = requests.post(self.base, params)
        sent = False
        error = ""
        if response.status_code == 200:
            sent = True
        else:
            error = response.json()
        return sent, error
