import tkinter as tk
from tkinter import messagebox, simpledialog
import datetime
import os
import threading
import time
import webbrowser
import pandas as pd
import socket

class TwitchChatGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Twitch Chat Monitor")

        self.streamer_name = tk.StringVar()
        self.logged_in_user = None
        self.oauth_token = None
        self.chat_monitor = None 

        self.create_widgets()
        self.root.protocol("WM_DELETE_WINDOW", self.close_application)
        self.root.mainloop()

    def create_widgets(self):
        tk.Label(self.root, text="Streamer Name:").grid(row=0, column=0, padx=10, pady=10)
        tk.Entry(self.root, textvariable=self.streamer_name).grid(row=0, column=1, padx=10, pady=10)
        
        self.logged_in_as_label = tk.Label(self.root, text="")
        self.logged_in_as_label.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        self.login_button = tk.Button(self.root, text="Log In", command=self.login)
        self.login_button.grid(row=2, column=0, padx=10, pady=10, sticky='ew')

        self.logout_button = tk.Button(self.root, text="Log Out", command=self.logout, state=tk.DISABLED)
        self.logout_button.grid(row=2, column=1, padx=10, pady=10, sticky='ew')

        self.start_service_button = tk.Button(self.root, text="Start Service", command=self.start_service)
        self.start_service_button.grid(row=3, column=0, padx=10, pady=10, sticky='ew')

        self.stop_service_button = tk.Button(self.root, text="Stop Service", command=self.stop_service, state=tk.DISABLED)
        self.stop_service_button.grid(row=3, column=1, padx=10, pady=10, sticky='ew')

    def login(self):
        self.logged_in_user = simpledialog.askstring("Log In", "Enter your Twitch username:")
        if self.logged_in_user:
            webbrowser.open("https://twitchapps.com/tmi/")
            self.oauth_token = simpledialog.askstring("OAuth Token", "Enter your Twitch OAuth token:")
            if self.oauth_token:
                self.update_login_status()
        
    def logout(self):
        self.logged_in_user = None
        self.oauth_token = None
        self.update_login_status()

    def start_service(self):
        streamer = self.streamer_name.get()
        if streamer and self.logged_in_user and self.oauth_token:
            self.chat_monitor = TwitchChatMonitor(streamer, self.logged_in_user, self.oauth_token)
            self.chat_monitor.start()
            self.start_service_button.config(state=tk.DISABLED)
            self.stop_service_button.config(state=tk.NORMAL)
        else:
            messagebox.showwarning("Missing Information", "Please log in and enter a streamer name to start the service.")
        
    def stop_service(self):
        if self.chat_monitor:
            self.chat_monitor.stop()
            self.start_service_button.config(state=tk.NORMAL)
            self.stop_service_button.config(state=tk.DISABLED)

    def update_login_status(self):
        if self.logged_in_user:
            self.logged_in_as_label.config(text=f"Logged in as {self.logged_in_user}")
            self.login_button.config(state=tk.DISABLED)
            self.logout_button.config(state=tk.NORMAL)
        else:
            self.logged_in_as_label.config(text="")
            self.login_button.config(state=tk.NORMAL)
            self.logout_button.config(state=tk.DISABLED)

    def close_application(self):
        if self.chat_monitor and self.chat_monitor.running:
            self.stop_service()  
        self.root.quit()

class TwitchChatMonitor:
    def __init__(self, streamer, username, token):
        self.server = 'irc.chat.twitch.tv'
        self.port = 6667
        self.nickname = username
        self.token = token  
        self.channel = f'#{streamer}'
        self.streamer = streamer
        self.running = False
        self.sock = None

    def start(self):
        self.running = True
        threading.Thread(target=self.connect_and_monitor_chat).start()

    def stop(self):
        self.running = False
        if self.sock:
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
                self.sock.close()
            except Exception as e:
                print(f"Error closing socket: {e}")

    def connect_and_monitor_chat(self):
        try:
            self.sock = socket.socket()
            self.sock.connect((self.server, self.port))
            self.sock.send(f"PASS {self.token}\n".encode('utf-8'))
            self.sock.send(f"NICK {self.nickname}\n".encode('utf-8'))
            self.sock.send(f"JOIN {self.channel}\n".encode('utf-8'))

            while self.running:
                try:
                    response = self.sock.recv(2048).decode('utf-8')
                    if response.startswith('PING'):
                        self.sock.send("PONG\n".encode('utf-8'))
                    elif 'PRIVMSG' in response:
                        self.parse_message(response)
                except socket.error as e:
                    print(f"Socket error: {e}")
                    self.stop()
                time.sleep(1)
        except Exception as e:
            print(f"Connection error: {e}")
        finally:
            if self.sock:
                try:
                    self.sock.close()
                except Exception as e:
                    print(f"Error closing socket in finally block: {e}")

    def parse_message(self, response):
        parts = response.split(':', 2)
        if len(parts) < 3:
            return  
        username = parts[1].split('!')[0]
        message = parts[2].strip()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_chat_message(self.streamer, username, timestamp, message)

def create_twitch_chats_folder():
    documents_path = os.path.expanduser("~/Documents")
    twitch_chats_folder = os.path.join(documents_path, "Twitch_Chats")
    if not os.path.exists(twitch_chats_folder):
        os.makedirs(twitch_chats_folder)

def save_chat_message(streamer, username, timestamp, message):
    create_twitch_chats_folder()
    filename = f"{streamer}.csv"
    filepath = os.path.join(os.path.expanduser("~/Documents/Twitch_Chats"), filename)

    if os.path.exists(filepath):
        df = pd.read_csv(filepath)
    else:
        df = pd.DataFrame(columns=["Username", "Time", "Message"])

    new_row = pd.DataFrame({"Username": [username], "Time": [timestamp], "Message": [message]})
    df = pd.concat([df, new_row], ignore_index=True)

    df.to_csv(filepath, index=False)

if __name__ == "__main__":
    TwitchChatGUI()
