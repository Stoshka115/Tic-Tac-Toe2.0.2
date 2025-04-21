# SINGLE FILE FOR LAUNCHING THE GAME "Tic Tac Toe 2.0"
# ----------------------------------------------
# Includes: Database, Registration, Login, Play vs AI, Music, Menu

import tkinter as tk
from tkinter import messagebox
import sqlite3
import random
import os
import sys # Added to terminate the application via sys.exit
from pygame import mixer

# ==============================
# DATABASE
# ==============================
def create_database():
    conn = sqlite3.connect("game.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS players (
        nickname TEXT PRIMARY KEY,
        age INTEGER,
        reputation INTEGER DEFAULT 100,
        password TEXT,
        score INTEGER DEFAULT 0
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        id INTEGER PRIMARY KEY,
        volume INTEGER DEFAULT 50
    )
    """)
    cursor.execute("INSERT OR IGNORE INTO settings (id, volume) VALUES (1, 50)")
    conn.commit()
    conn.close()

def add_demo_accounts():
    conn = sqlite3.connect("game.db")
    cursor = conn.cursor()
    accounts = [
        ("Stoshka", 18, "Stoshka", 50),
        ("Charli", 21, "Charli21", 115),
        ("Lucius", 19, "Lucius19", 66),
        ("Lecron", 25, "Lecron25", 125)
    ]
    for nickname, age, password, score in accounts:
        cursor.execute("""
        INSERT OR REPLACE INTO players (nickname, age, password, score)
        VALUES (?, ?, ?, ?)
        """, (nickname, age, password, score))
    conn.commit()
    conn.close()

def get_score(nickname):
    conn = sqlite3.connect("game.db")
    cur = conn.cursor()
    cur.execute("SELECT score FROM players WHERE nickname=?", (nickname,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else 0

def get_volume():
    conn = sqlite3.connect("game.db")
    cursor = conn.cursor()
    cursor.execute("SELECT volume FROM settings WHERE id = 1")
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else 50

def save_volume_to_db(value):
    conn = sqlite3.connect("game.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE settings SET volume = ? WHERE id = 1", (int(value),))
    conn.commit()
    conn.close()

def get_user_data(nickname):
    conn = sqlite3.connect("game.db")
    cursor = conn.cursor()
    cursor.execute("SELECT nickname, password FROM players WHERE nickname=?", (nickname,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"nickname": row[0], "password": row[1]}
    return {"nickname": "", "password": ""}

# ==============================
# AI FOR TIC-TAC-TOE
# ==============================
def best_move(board):
    combos = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6]
    ]
    for c in combos:
        x, y, z = c
        if board[x] == board[y] == "O" and board[z] == "": return z
        if board[x] == board[z] == "O" and board[y] == "": return y
        if board[y] == board[z] == "O" and board[x] == "": return x
    for c in combos:
        x, y, z = c
        if board[x] == board[y] == "X" and board[z] == "": return z
        if board[x] == board[z] == "X" and board[y] == "": return y
        if board[y] == board[z] == "X" and board[x] == "": return x
    available = [i for i, v in enumerate(board) if v == ""]
    if 4 in available and random.random() < 0.7: return 4
    corners = [i for i in [0, 2, 6, 8] if i in available]
    if corners and random.random() < 0.5: return random.choice(corners)
    return random.choice(available) if available else None

# ==============================
# STARTING THE GAME (tic tac toe)
# ==============================
def update_score(nick, points):
    conn = sqlite3.connect("game.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE players SET score = score + ? WHERE nickname = ?", (points, nick))
    conn.commit()
    conn.close()

def tic_tac_toe(nick):
    def check():
        for c in [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]]:
            if board[c[0]] == board[c[1]] == board[c[2]] != "": return board[c[0]]
        return "Draw" if "" not in board else None

    def click(i):
        if board[i] == "" and not game_over[0]:
            board[i] = "X"
            btns[i].config(text="X", fg="red")
            res = check()
            if res: end(res)
            else: ai()

    def ai():
        i = best_move(board)
        if i is not None:
            board[i] = "O"
            btns[i].config(text="O", fg="blue")
            res = check()
            if res: end(res)

    def end(w):
        game_over[0] = True
        if w == "X": messagebox.showinfo("Result", "You won!"); update_score(nick, 1)
        elif w == "O": messagebox.showinfo("Result", "AI won!")
        else: messagebox.showinfo("Result", "Draw!")

    def restart(): root.destroy(); tic_tac_toe(nick)
    def back(): root.destroy(); menu2(nick)

    root = tk.Tk()
    root.title("Tic Tac Toe")
    root.attributes("-fullscreen", True)
    board, game_over, btns = [""] * 9, [False], []

    frame = tk.Frame(root); frame.pack(pady=20)
    for i in range(9):
        b = tk.Button(frame, text="", font=("Arial", 40), width=5, height=2, command=lambda i=i: click(i))
        b.grid(row=i//3, column=i%3, padx=5, pady=5)
        btns.append(b)

    ctrl = tk.Frame(root); ctrl.pack(pady=20)
    tk.Button(ctrl, text="Play again", font=("Arial", 16), command=restart).pack(side=tk.LEFT, padx=20)
    tk.Button(ctrl, text="Back", font=("Arial", 16), command=back).pack(side=tk.LEFT, padx=20)
    root.mainloop()

# ==============================
# TOP PLAYERS
# ==============================
def show_top_players():
    top_window = tk.Toplevel()
    top_window.title("Top players")
    top_window.attributes('-fullscreen', True)

    def back_to_menu():
        top_window.destroy()

    conn = sqlite3.connect("game.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM players")
    total_players = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(score) FROM players")
    avg_score = cursor.fetchone()[0] or 0

    cursor.execute("SELECT MAX(score) FROM players")
    max_score = cursor.fetchone()[0] or 0

    cursor.execute("SELECT AVG(age) FROM players")
    avg_age = cursor.fetchone()[0] or 0

    cursor.execute("SELECT MAX(age) FROM players")
    max_age = cursor.fetchone()[0] or 0

    cursor.execute("SELECT nickname, score FROM players ORDER BY score DESC LIMIT 10")
    top_score = cursor.fetchall()

    cursor.execute("SELECT nickname, age FROM players ORDER BY age DESC LIMIT 10")
    top_age = cursor.fetchall()

    conn.close()

    header_text = (
        "General statistics\n"
        f"Total players: {total_players}\n"
        f"Average score: {avg_score:.2f}\n"
        f"Maximum score: {max_score}\n"
        f"Middle age: {avg_age:.2f}\n"
        f"Maximum age: {max_age}"
    )
    tk.Label(top_window, text=header_text, font=("Arial", 18)).pack(pady=10)

    frame = tk.Frame(top_window)
    frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    score_frame = tk.Frame(frame)
    score_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
    tk.Label(score_frame, text="Top by points", font=("Arial", 20)).pack(pady=10)

    if top_score:
        for idx, (nickname, score) in enumerate(top_score, start=1):
            tk.Label(score_frame, text=f"{idx}. {nickname} - {score} points", font=("Arial", 16)).pack(pady=5)
    else:
        tk.Label(score_frame, text="No data to display", font=("Arial", 16)).pack(pady=20)

    age_frame = tk.Frame(frame)
    age_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)
    tk.Label(age_frame, text="Top by age", font=("Arial", 20)).pack(pady=10)

    if top_age:
        for idx, (nickname, age) in enumerate(top_age, start=1):
            tk.Label(age_frame, text=f"{idx}. {nickname} - {age} age", font=("Arial", 16)).pack(pady=5)
    else:
        tk.Label(age_frame, text="No data to display", font=("Arial", 16)).pack(pady=20)

    tk.Button(top_window, text="Back", font=("Arial", 16), command=back_to_menu).pack(pady=20)

# ==============================
# PROFILE
# ==============================

def show_profile(nickname):
    profile_data = get_user_data(nickname)
    profile_window = tk.Toplevel()
    profile_window.title("Profile")
    profile_window.attributes('-fullscreen', True)

    def back_to_menu():
        profile_window.destroy()

    def delete_account():
        confirm = messagebox.askyesno("Confirmation", "Are you sure you want to delete your account?")
        if confirm:
            conn = sqlite3.connect("game.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM players WHERE nickname=?", (nickname,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Deleted", "Your account has been successfully deleted!")
            profile_window.destroy()
            os._exit(0)  # <-- Completing the entire application

    tk.Label(profile_window, text=f"Your nickname: {profile_data['nickname']}", font=("Arial", 16)).pack(pady=10)
    tk.Label(profile_window, text=f"Your password: {profile_data['password']}", font=("Arial", 16)).pack(pady=10)
    tk.Button(profile_window, text="Delete account", font=("Arial", 16), command=delete_account).pack(pady=10)
    tk.Button(profile_window, text="Back", font=("Arial", 16), command=back_to_menu).pack(pady=20)

def show_statistics(nickname):
    score = get_score(nickname)
    messagebox.showinfo("Statistics", f"Your score: {score}")

def settings_screen():
    window = tk.Toplevel()
    window.title("Settings")
    window.attributes('-fullscreen', True)

    def save_volume(value):
        volume_label.config(text=f"Volume: {value}%")
        mixer.music.set_volume(int(value) / 100)
        save_volume_to_db(value)

    def back():
        window.destroy()

    tk.Label(window, text="Music volume", font=("Arial", 20)).pack(pady=20)
    current_volume = get_volume()
    volume_slider = tk.Scale(window, from_=0, to=100, orient=tk.HORIZONTAL, command=save_volume)
    volume_slider.set(current_volume)
    volume_slider.pack(pady=10)

    volume_label = tk.Label(window, text=f"Volume: {current_volume}%", font=("Arial", 14))
    volume_label.pack(pady=10)

    tk.Button(window, text="Back", font=("Arial", 16), command=back).pack(pady=20)

def menu2(nickname):
    root = tk.Tk()
    root.title("Menu 2")
    root.attributes('-fullscreen', True)
    root.bind('<Escape>', lambda e: root.attributes('-fullscreen', False))

    def start_music():
        if os.path.exists("background.mp3"):
            mixer.music.load("background.mp3")
            mixer.music.set_volume(get_volume() / 100)
            mixer.music.play(-1)

    start_music()

    tk.Label(root, text=f"Welcome, {nickname}!", font=("Arial", 24)).pack(pady=20)

    tk.Button(root, text="Play", font=("Arial", 16),
              command=lambda: [root.destroy(), tic_tac_toe(nickname)]).pack(pady=10)

    tk.Button(root, text="Profile", font=("Arial", 16),
              command=lambda: show_profile(nickname)).pack(pady=10)

    tk.Button(root, text="Statistics", font=("Arial", 16),
              command=lambda: show_statistics(nickname)).pack(pady=10)

    tk.Button(root, text="Top Players", font=("Arial", 16),
              command=show_top_players).pack(pady=10)

    tk.Button(root, text="Settings", font=("Arial", 16),
              command=settings_screen).pack(pady=10)

    tk.Button(root, text="Exit", font=("Arial", 16), command=root.destroy).pack(pady=10)

    root.mainloop()

# ==============================
# START AT STARTUP
# ==============================
if __name__ == "__main__":
    mixer.init()
    create_database()
    add_demo_accounts()

    def register_screen():
        global root
        root.destroy()
        win = tk.Tk()
        win.attributes('-fullscreen', True)
        win.title("Register")

        tk.Label(win, text="Nickname").pack()
        nick = tk.Entry(win); nick.pack()
        tk.Label(win, text="Age").pack()
        age = tk.Entry(win); age.pack()
        tk.Label(win, text="Password").pack()
        pwd = tk.Entry(win, show='*'); pwd.pack()

        def submit():
            if not nick.get() or not age.get() or not pwd.get():
                messagebox.showerror("Error", "Fill in all fields!"); return
            try:
                con = sqlite3.connect("game.db")
                cur = con.cursor()
                cur.execute("INSERT INTO players (nickname, age, password) VALUES (?, ?, ?)", (nick.get(), age.get(), pwd.get()))
                con.commit(); con.close()
                messagebox.showinfo("Success", "Registered!"); win.destroy(); main_menu()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Nickname exists")

        tk.Button(win, text="Register", command=submit).pack()
        tk.Button(win, text="Back", command=lambda: (win.destroy(), main_menu())).pack()
        win.mainloop()

    def login_screen():
        global root
        root.destroy()
        win = tk.Tk()
        win.title("Login")
        win.attributes('-fullscreen', True)

        tk.Label(win, text="Nickname").pack()
        nick = tk.Entry(win); nick.pack()
        tk.Label(win, text="Password").pack()
        pwd = tk.Entry(win, show='*'); pwd.pack()

        def try_login():
            nickname_value = nick.get()
            password_value = pwd.get()

            con = sqlite3.connect("game.db")
            cur = con.cursor()
            cur.execute("SELECT nickname FROM players WHERE nickname=? AND password=?", (nickname_value, password_value))
            result = cur.fetchone()
            con.close()
            if result:
                win.destroy()
                menu2(nickname_value)
            else:
                messagebox.showerror("Error", "Wrong data")

        tk.Button(win, text="Login", command=try_login).pack()
        tk.Button(win, text="Back", command=lambda: (win.destroy(), main_menu())).pack()
        win.mainloop()

    def main_menu():
        global root
        root = tk.Tk()
        root.title("Main Menu")
        root.attributes('-fullscreen', True)
        root.bind('<Escape>', lambda e: root.attributes('-fullscreen', False))

        tk.Label(root, text="Welcome to Tic Tac Toe!", font=("Arial", 24)).pack(pady=20)
        tk.Button(root, text="Register", font=("Arial", 16), command=register_screen).pack(pady=10)
        tk.Button(root, text="Login", font=("Arial", 16), command=login_screen).pack(pady=10)
        tk.Button(root, text="Exit", font=("Arial", 16), command=root.destroy).pack(pady=10)
        root.mainloop()

    main_menu()
