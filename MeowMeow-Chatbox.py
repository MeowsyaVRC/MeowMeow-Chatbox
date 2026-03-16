import customtkinter as ctk
from pythonosc.udp_client import SimpleUDPClient
import threading
import time
import sys
import ctypes
import os
import locale
from tkinter import Tk

ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("MewBox")

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
        

    return os.path.join(base_path, relative_path)

def set_window_icon(window, icon_file):
    window.iconbitmap(icon_file)


OSC_IP = "127.0.0.1"
OSC_PORT = 9000
CHAR_LIMIT = 144

TYPING_TIMEOUT = 4.0
TYPING_INTERVAL = 4.0
SEND_INTERVAL = 1.0

client = SimpleUDPClient(OSC_IP, OSC_PORT)
running = False
typing_enabled = True
typing_timer = None
send_timer = None
last_sent_text = ""
last_typing_time = 0.0
sending_active = False 
loop_job = None

LANGUAGES = {
    "ESP": {
        "write_msg": "Escribe tu mensaje:",
        "clear": "Vaciar Chat",
        "send_once": "Enviar Mensaje",
        "resend": "Reenviar (F10)",
        "stop": "Detenerse (F10)",
        "typing_on": "Detectar escritura: Sí",
        "typing_off": "Detectar escritura: No",
        "interval": "Intervalo en segundos"
    },

    "ENG": {
        "write_msg": "Type your message:",
        "clear": "Clear Chat",
        "send_once": "Send Message",
        "resend": "Loop send (F10)",
        "stop": "Stop Loop (F10)",
        "typing_on": "Detect Typing: Yes",
        "typing_off": "Detect Typing: No",
        "interval": "Interval (seconds)"
    },
    
    "DEU": {
        "write_msg": "Nachricht eingeben:",
        "clear": "Chat leeren",
        "send_once": "Nachricht senden",
        "resend": "Erneut senden (F10)",
        "stop": "Stoppen (F10)",
        "typing_on": "Tipperkennung: Ja",
        "typing_off": "Tipperkennung: Nein",
        "interval": "Intervall (Sekunden)"
    },

    "FRA": {
        "write_msg": "Écrivez votre message :",
        "clear": "Vider le chat",
        "send_once": "Envoyer le message",
        "resend": "Renvoyer (F10)",
        "stop": "Arrêter (F10)",
        "typing_on": "Détection de frappe : Oui",
        "typing_off": "Détection de frappe : Non",
        "interval": "Intervalle (secondes)"
    },

    "РУС": {
         "write_msg": "Введите сообщение:",
         "clear": "Очистить чат",
          "send_once": "Отправить сообщение",
         "resend": "Отправлять постоянно (F10)",
         "stop": "Остановить отправку (F10)",
         "typing_on": "Автообнаружение: Да",
         "typing_off": "Автообнаружение: Нет",
         "interval": "Интервал (секунды)"
    },

    "日本語": {
        "write_msg": "メッセージを書く:",
        "clear": "チャットを消す",
        "send_once": "送信",
        "resend": "再送信 (F10)",
        "stop": "停止 (F10)",
        "typing_on": "入力検出: はい",
        "typing_off": "入力検出: いいえ",
         "interval": "送信間隔（秒）"
    },

    "简体中文": {
        "write_msg": "输入你的消息：",
        "clear": "清空聊天",
        "send_once": "发送消息",
        "resend": "重复发送 (F10)",
        "stop": "停止 (F10)",
        "typing_on": "输入检测：是",
        "typing_off": "输入检测：否",
        "interval": "发送间隔（秒）"
    },

    "한국어": {
        "write_msg": "메시지를 입력하세요:",
        "clear": "채팅 지우기",
        "send_once": "메시지 보내기",
        "resend": "반복 전송 (F10)",
        "stop": "중지 (F10)",
        "typing_on": "입력 감지: 예",
        "typing_off": "입력 감지: 아니요",
        "interval": "전송 간격(초)"
    },

}


def detect_system_language():
    try:
        lang = locale.getlocale()[0] 
    except Exception:
        lang = None

    if not lang:
        return "ENG"

    lang = lang.lower()

    if "es" in lang:
        return "ESP"
    if "ru" in lang:
        return "РУС"
    if "ja" in lang:
        return "日本語"
    if "zh" in lang:
        return "简体中文"
    if "ko" in lang:
        return "한국어"
    if "de" in lang:
        return "DEU"
    if "fr" in lang:
        return "FRA"

    return "ENG"

current_lang = detect_system_language()

def tr(key):
    t = LANGUAGES[current_lang]
    if key == "start_button":
        return t["stop"] if running else t["resend"]
    elif key == "typing_button":
        return t["typing_on"] if typing_enabled else t["typing_off"]
    else:
        return t[key]

def apply_language(lang):
    global current_lang
    current_lang = lang

    header_label.configure(text=tr("write_msg"))
    clear_button.configure(text=tr("clear"))
    send_once_button.configure(text=tr("send_once"))
    interval_label.configure(text=tr("interval"))
    start_button.configure(text=tr("start_button"))
    typing_button.configure(text=tr("typing_button"))
        
def send_message(msg):
    client.send_message("/chatbox/input", [msg, True, False])

def send_once(event=None):
    msg = message_box.get()
    send_message(msg)

def clear_text():
    global last_sent_text, sending_active
    message_box.delete(0, "end")
    update_counter()
    stop_typing()
    send_message("")
    last_sent_text = ""
    sending_active = False

def start_stop_loop(event=None):
    global running, loop_job

    running = not running
    start_button.configure(text=tr("start_button"))

    if running:
        loop_after()
    elif loop_job:
        app.after_cancel(loop_job)
        loop_job = None

def loop_after():
    global loop_job

    if not running:
        return

    msg = message_box.get()
    send_message(msg)

    interval = int(interval_box.get()) * 1000
    loop_job = app.after(interval, loop_after)

def start_typing(event=None):
    global typing_timer, send_timer, last_typing_time, sending_active

    if not typing_enabled:
        return

    current_time = time.time()
    if (current_time - last_typing_time) >= TYPING_INTERVAL:
        client.send_message("/chatbox/typing", True)
        last_typing_time = current_time

    if typing_timer:
        typing_timer.cancel()
    typing_timer = threading.Timer(TYPING_TIMEOUT, stop_typing)
    typing_timer.start()

    if typing_enabled:
        sending_active = True
        if send_timer:
            send_timer.cancel()
        send_timer = threading.Timer(SEND_INTERVAL, send_accumulated_text)
        send_timer.start()

def send_accumulated_text():
    global last_sent_text, send_timer, sending_active
    if not typing_enabled:
        sending_active = False
        return

    msg = message_box.get()
    if msg != last_sent_text:
        send_message(msg)
        last_sent_text = msg

    if sending_active:
        send_timer = threading.Timer(SEND_INTERVAL, send_accumulated_text)
        send_timer.start()

def stop_typing():
    global last_sent_text, sending_active
    client.send_message("/chatbox/typing", False)
    if typing_enabled and sending_active:
        msg = message_box.get()
        if msg != last_sent_text:
            send_message(msg)
            last_sent_text = msg
    sending_active = False

def toggle_typing():
    global typing_enabled, typing_timer, send_timer, sending_active

    typing_enabled = not typing_enabled

    if not typing_enabled:
        sending_active = False
        if typing_timer: typing_timer.cancel(); typing_timer = None
        if send_timer: send_timer.cancel(); send_timer = None
        client.send_message("/chatbox/typing", False)

    typing_button.configure(text=tr("typing_button"))

def update_counter(event=None):
    text = message_box.get()
    count = len(text)
    counter_label.configure(text=f"{count}/{CHAR_LIMIT}")
    counter_label.configure(text_color="red" if count > CHAR_LIMIT else "gray")

ctk.set_appearance_mode("dark")
app = ctk.CTk()
app.title("MeowMeow Chatbox")
set_window_icon(app, resource_path("MewLogoMulti.ico"))
app.geometry("530x275")

app.focus_force()

language_box = ctk.CTkComboBox(
    app,
    values=list(LANGUAGES.keys()),
    width=110,
    command=apply_language
)

language_box.set(current_lang)
language_box.pack(anchor="w", padx=10, pady=(6,0))

header_label = ctk.CTkLabel(app, text="", font=("Arial", 14))
header_label.pack(pady=(10, 2))

msg_frame = ctk.CTkFrame(app, fg_color="transparent")
msg_frame.pack(pady=2)

message_box = ctk.CTkEntry(msg_frame, width=320)
message_box.pack(side="left", padx=(0,5))

def on_key_release(event=None):
    update_counter()
    start_typing()

message_box.bind("<KeyRelease>", on_key_release)

clear_button = ctk.CTkButton(msg_frame, text=tr("clear"), width=80, command=clear_text)
clear_button.pack(side="left")

counter_label = ctk.CTkLabel(app, text="0/144", text_color="gray")
counter_label.pack(pady=(2,5))

interval_label = ctk.CTkLabel(app, text=tr("interval"))
interval_label.pack()

interval_box = ctk.CTkComboBox(app, values=["2","3","5","10","15","20","30"])
interval_box.set("10")
interval_box.pack(pady=5)

btn_frame = ctk.CTkFrame(app, fg_color="transparent")
btn_frame.pack(pady=5)

send_once_button = ctk.CTkButton(btn_frame, text="", command=send_once)
send_once_button.pack(side="left", padx=(0,5))

start_button = ctk.CTkButton(btn_frame, text="", command=start_stop_loop, width=120)
start_button.pack(side="left", padx=(0,5))

typing_button = ctk.CTkButton(btn_frame, text="", command=toggle_typing, width=160)
typing_button.pack(side="left")

app.bind("<Return>", send_once)
app.bind_all("<F10>", start_stop_loop)

apply_language(current_lang)
app.mainloop()