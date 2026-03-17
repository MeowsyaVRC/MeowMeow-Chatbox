import customtkinter as ctk
import tkinter as tk
from pythonosc.udp_client import SimpleUDPClient
import threading
import time
import sys
import ctypes
import os
import locale
import re
from tkinter import messagebox

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
SEND_INTERVAL = 1.5
APP_VERSION = "v1.1"

client = SimpleUDPClient(OSC_IP, OSC_PORT)
running = False
typing_enabled = True
typing_timer = None
send_timer = None
last_sent_text = ""
last_sent_time = 0.0
last_typing_time = 0.0
sending_active = False 
loop_job = None
typing_loop_job = None
typing_timeout_job = None

LANGUAGES = {
    "ESP": {
        "write_msg": "Escribe tu mensaje:",
        "clear": "Vaciar Chat",
        "send_once": "Enviar Mensaje",
        "resend": "Reenviar (F10)",
        "stop": "Detenerse (F10)",
        "typing_on": "Detectar escritura: Sí",
        "typing_off": "Detectar escritura: No",
        "interval": "Intervalo en segundos",
        "osc_settings": "Ajustes OSC",
        "language": "🌐 Idioma",
        "save": "Guardar",
        "invalid_ip": "La IP no es válida. Debe tener formato x.x.x.x y cada octeto entre 0 y 255",
        "invalid_port": "El puerto no es válido. Debe ser un número entre 1 y 65535"
    },

    "ENG": {
        "write_msg": "Type your message:",
        "clear": "Clear Chat",
        "send_once": "Send Message",
        "resend": "Loop send (F10)",
        "stop": "Stop Loop (F10)",
        "typing_on": "Detect Typing: Yes",
        "typing_off": "Detect Typing: No",
        "interval": "Interval (seconds)",
        "osc_settings": "OSC Settings",
        "language": "🌐 Language",
        "save": "Save",
        "invalid_ip": "Invalid IP. Must be in format x.x.x.x and each octet between 0 and 255",
        "invalid_port": "Invalid port. Must be a number between 1 and 65535"
    },
    
    "DEU": {
        "write_msg": "Nachricht eingeben:",
        "clear": "Chat leeren",
        "send_once": "Nachricht senden",
        "resend": "Erneut senden (F10)",
        "stop": "Stoppen (F10)",
        "typing_on": "Tipperkennung: Ja",
        "typing_off": "Tipperkennung: Nein",
        "interval": "Intervall (Sekunden)",
        "osc_settings": "OSC Einstellungen",
        "language": "🌐 Sprache",
        "save": "Speichern",
        "invalid_ip": "Ungültige IP. Muss im Format x.x.x.x sein und jedes Oktett zwischen 0 und 255",
        "invalid_port": "Ungültiger Port. Muss eine Zahl zwischen 1 und 65535 sein"
    },

    "FRA": {
        "write_msg": "Écrivez votre message :",
        "clear": "Vider le chat",
        "send_once": "Envoyer le message",
        "resend": "Renvoyer (F10)",
        "stop": "Arrêter (F10)",
        "typing_on": "Détection de frappe : Oui",
        "typing_off": "Détection de frappe : Non",
        "interval": "Intervalle (secondes)",
        "osc_settings": "Paramètres OSC",
        "language": "🌐 Langue",
        "save": "Enregistrer",
        "invalid_ip": "IP invalide. Doit être au format x.x.x.x et chaque octet entre 0 et 255",
        "invalid_port": "Port invalide. Doit être un nombre entre 1 et 65535"
    },

    "РУС": {
         "write_msg": "Введите сообщение:",
         "clear": "Очистить чат",
          "send_once": "Отправить сообщение",
         "resend": "Отправлять постоянно (F10)",
         "stop": "Остановить отправку (F10)",
         "typing_on": "Автообнаружение: Да",
         "typing_off": "Автообнаружение: Нет",
         "interval": "Интервал (секунды)",
         "osc_settings": "Настройки OSC",
        "language": "🌐 Язык",
        "save": "Сохранить",
        "invalid_ip": "Неверный IP. Формат должен быть x.x.x.x и каждый октет должен быть от 0 до 255",
        "invalid_port": "Неверный порт. Должно быть число от 1 до 65535"
    },

    "日本語": {
        "write_msg": "メッセージを書く:",
        "clear": "チャットを消す",
        "send_once": "送信",
        "resend": "再送信 (F10)",
        "stop": "停止 (F10)",
        "typing_on": "入力検出: はい",
        "typing_off": "入力検出: いいえ",
         "interval": "送信間隔（秒）",
         "osc_settings": "OSC 設定",
        "language": "🌐 言語",
        "save": "保存",
        "invalid_ip": "無効なIPアドレスです。形式は x.x.x.x で、各オクテットは0～255である必要があります",
        "invalid_port": "無効なポートです。1から65535の数字である必要があります"
    },

    "简体中文": {
        "write_msg": "输入你的消息：",
        "clear": "清空聊天",
        "send_once": "发送消息",
        "resend": "重复发送 (F10)",
        "stop": "停止 (F10)",
        "typing_on": "输入检测：是",
        "typing_off": "输入检测：否",
        "interval": "发送间隔（秒）",
        "osc_settings": "OSC 设置",
        "language": "🌐 语言",
        "save": "保存",
        "invalid_ip": "无效的IP。格式必须为 x.x.x.x，每个八位字节必须在0到255之间",
        "invalid_port": "无效的端口。必须是1到65535之间的数字"
    },

    "한국어": {
        "write_msg": "메시지를 입력하세요:",
        "clear": "채팅 지우기",
        "send_once": "메시지 보내기",
        "resend": "반복 전송 (F10)",
        "stop": "중지 (F10)",
        "typing_on": "입력 감지: 예",
        "typing_off": "입력 감지: 아니요",
        "interval": "전송 간격(초)",
        "osc_settings": "OSC 설정",
        "language": "🌐 언어",
        "save": "저장",
        "invalid_ip": "유효하지 않은 IP입니다. 형식은 x.x.x.x 이어야 하며 각 옥텟은 0~255 사이여야 합니다",
        "invalid_port": "유효하지 않은 포트입니다. 1에서 65535 사이의 숫자여야 합니다"
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
    osc_button.configure(text=tr("osc_settings"))
    lang_label.configure(text=tr("language"))
    osc_button.configure(text=tr("osc_settings"))
        
def send_message(msg):
    client.send_message("/chatbox/input", [msg, True, False])

def send_once(event=None):
    msg = message_box.get()
    send_message(msg)

def clear_text():
    global last_sent_text, sending_active, typing_loop_job, typing_timeout_job

    sending_active = False
    if typing_loop_job:
        app.after_cancel(typing_loop_job)
        typing_loop_job = None
    if typing_timeout_job:
        app.after_cancel(typing_timeout_job)
        typing_timeout_job = None

    message_box.delete(0, "end")
    update_counter()

def clear_text():
    global last_sent_text, sending_active

    message_box.delete(0, "end")
    update_counter()

    sending_active = False

    def send_empty():
        try:
            client.send_message("/chatbox/input", ["", True, False])
        except Exception:
            pass

    for i, delay in enumerate([100, 400]):
        app.after(delay, send_empty)

    last_sent_text = ""

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
    global last_typing_time, sending_active, last_sent_time
    global typing_loop_job, typing_timeout_job

    if not typing_enabled:
        return

    current_time = time.time()

    if (current_time - last_typing_time) >= TYPING_INTERVAL:
        try:
            client.send_message("/chatbox/typing", True)
        except Exception:
            pass
        last_typing_time = current_time

    sending_active = True

    def send_loop():
        global last_sent_text, last_sent_time, typing_loop_job
        if not sending_active:
            typing_loop_job = None
            return

        try:
            msg = message_box.get()
            now = time.time()
            if msg != last_sent_text and (now - last_sent_time) >= SEND_INTERVAL:
                send_message(msg)
                last_sent_text = msg
                last_sent_time = now
        except tk.TclError:
            typing_loop_job = None
            return

        typing_loop_job = app.after(100, send_loop)

    if typing_loop_job:
        app.after_cancel(typing_loop_job)

    typing_loop_job = app.after(0, send_loop)

    if typing_timeout_job:
        app.after_cancel(typing_timeout_job)

    typing_timeout_job = app.after(int(TYPING_TIMEOUT*1000), stop_typing)


def stop_typing():
    global sending_active, last_sent_text, last_sent_time
    global typing_loop_job, typing_timeout_job

    sending_active = False

    if typing_loop_job:
        app.after_cancel(typing_loop_job)
        typing_loop_job = None
    if typing_timeout_job:
        app.after_cancel(typing_timeout_job)
        typing_timeout_job = None

    try:
        client.send_message("/chatbox/typing", False)
        msg = message_box.get()
        now = time.time()
        if typing_enabled and msg != last_sent_text and (now - last_sent_time) >= SEND_INTERVAL:
            send_message(msg)
            last_sent_text = msg
            last_sent_time = now
    except tk.TclError:
        pass

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

def open_osc_settings():
    global OSC_IP, OSC_PORT, client

    settings = ctk.CTkToplevel(app)
    settings.title(tr("osc_settings"))
    settings.geometry("250x220")
    settings.grab_set()
    settings.after(200, lambda: set_window_icon(settings, resource_path("MewLogoMulti.ico")))
    settings.bind("<Escape>", lambda e: settings.destroy())

    ctk_frame = ctk.CTkFrame(settings, fg_color="transparent")
    ctk_frame.pack(fill="both", expand=True, padx=10, pady=10)

    ip_label = ctk.CTkLabel(ctk_frame, text="OSC IP")
    ip_label.pack(pady=(10,0))

    ip_entry = ctk.CTkEntry(ctk_frame)
    ip_entry.insert(0, OSC_IP)
    ip_entry.pack(pady=5)

    port_label = ctk.CTkLabel(ctk_frame, text="OSC Port")
    port_label.pack()

    port_entry = ctk.CTkEntry(ctk_frame)
    port_entry.insert(0, str(OSC_PORT))
    port_entry.pack(pady=5)

    def save_settings():
        global OSC_IP, OSC_PORT, client
        ip = ip_entry.get().strip()
        port = port_entry.get().strip()

        ip_pattern = r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
        if not re.match(ip_pattern, ip):
            messagebox.showerror(tr("osc_settings"), tr("invalid_ip"))
            return

        octets = ip.split(".")
        if any(int(o) < 0 or int(o) > 255 for o in octets):
            messagebox.showerror(tr("osc_settings"), tr("invalid_ip"))
            return

        try:
            port_int = int(port)
            if not (0 < port_int < 65536):
                raise ValueError
        except ValueError:
            messagebox.showerror(tr("osc_settings"), tr("invalid_port"))
            return

        OSC_IP = ip
        OSC_PORT = port_int
        client = SimpleUDPClient(OSC_IP, OSC_PORT)
        settings.destroy()

    save_button = ctk.CTkButton(ctk_frame, text=tr("save"), command=save_settings)
    save_button.pack(pady=10)

ctk.set_appearance_mode("dark")
app = ctk.CTk()
app.title("MeowMeow Chatbox")
set_window_icon(app, resource_path("MewLogoMulti.ico"))
app.geometry("530x275")

app.focus_force()

top_bar = ctk.CTkFrame(app, fg_color="transparent")
top_bar.pack(fill="x", padx=10, pady=(6,0))

language_box = ctk.CTkComboBox(
    top_bar,
    values=list(LANGUAGES.keys()),
    width=110,
    command=apply_language
)

language_box.set(current_lang)
language_box.pack(side="left")

lang_label = ctk.CTkLabel(top_bar, text="", text_color="gray")
lang_label.pack(side="left", padx=(6,0))

osc_button = ctk.CTkButton(
    top_bar,
    text="",
    width=120,
    command=open_osc_settings
)
osc_button.pack(side="right", padx=(0,5))

version_label = ctk.CTkLabel(
    top_bar,
    text=APP_VERSION,
    text_color="gray",
    font=("Segoe UI", 11)
)
version_label.pack(side="right", padx=(0,10))

header_label = ctk.CTkLabel(app, text="", font=("Arial", 14))
header_label.pack(pady=(10, 2))

msg_frame = ctk.CTkFrame(app, fg_color="transparent")
msg_frame.pack(pady=2)

message_box = ctk.CTkEntry(msg_frame, width=320)
message_box.pack(side="left", padx=(0,5))

def on_key_release(event=None):
    update_counter()
    start_typing()

tags = list(message_box.bindtags())
message_box.bindtags((app,) + tuple(tags))

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

def clear_text_event(event=None):
    clear_text()
    return "break"

message_box.bind("<Control-BackSpace>", clear_text_event)

def block_other_entries(event):
    if event.widget != message_box:
        return "break"

app.bind_class("CTkEntry", "<Control-BackSpace>", block_other_entries)

message_box.bind("<KeyRelease>", lambda e: [update_counter(), start_typing()])

apply_language(current_lang)
app.mainloop()