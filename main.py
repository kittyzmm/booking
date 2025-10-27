import tkinter as tk
from tkinter import messagebox
import sqlite3

conn = sqlite3.connect('restaurant.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS tables 
          (id INTEGER PRIMARY KEY, capacity INT, status TEXT)''')

if not c.execute('SELECT 1 FROM tables').fetchone():
    c.executescript('''INSERT INTO tables VALUES
    (1,2,'свободен'),(2,4,'занят'),(3,6,'свободен'),
    (4,2,'свободен'),(5,4,'занят')''')
    conn.commit()

def update_list():
    listbox.delete(0, tk.END)
    for r in c.execute('SELECT * FROM tables'):
        listbox.insert(tk.END, f'№{r[0]} ({r[1]} чел.) — {r[2]}')

def book():
    try:
        t, g = int(e_id.get()), int(e_guest.get())
    except:
        messagebox.showerror('Ошибка', 'Введите числа!')
        return
    
    res = c.execute('SELECT capacity,status FROM tables WHERE id=?', (t,)).fetchone()
    if not res:
        messagebox.showerror('Ошибка', 'Столик не найден!')
        return
    cap, stat = res
    
    if stat == 'занят':
        messagebox.showerror('Ошибка', 'Столик занят!')
    elif g > cap:
        messagebox.showerror('Ошибка', f'Максимум {cap} гостей!')
    else:
        c.execute('UPDATE tables SET status="занят" WHERE id=?', (t,))
        conn.commit()
        update_list()
        messagebox.showinfo('Успех', f'Столик {t} забронирован!')

def release():
    try:
        t = int(e_id.get())
    except:
        messagebox.showerror('Ошибка', 'Введите номер столика!')
        return
    
    stat = c.execute('SELECT status FROM tables WHERE id=?', (t,)).fetchone()
    if not stat:
        messagebox.showerror('Ошибка', 'Столик не найден!')
    elif stat[0] == 'свободен':
        messagebox.showerror('Ошибка', 'Столик уже свободен!')
    else:
        c.execute('UPDATE tables SET status="свободен" WHERE id=?', (t,))
        conn.commit()
        update_list()
        messagebox.showinfo('Успех', f'Столик {t} освобождён!')

root = tk.Tk()
root.title('Бронирование столиков')
root.geometry('500x450')

tk.Label(root, text='Бронирование столиков', font=('Arial', 14, 'bold')).pack(pady=10)
listbox = tk.Listbox(root, width=60, height=10)
listbox.pack(pady=10)
update_list()

tk.Label(root, text='Номер столика:').pack()
e_id = tk.Entry(root)
e_id.pack(pady=5)

tk.Label(root, text='Количество гостей:').pack()
e_guest = tk.Entry(root)
e_guest.pack(pady=5)

tk.Button(root, text='Забронировать', command=book).pack(pady=5)
tk.Button(root, text='Освободить столик', command=release).pack(pady=5)

root.mainloop()
conn.close()