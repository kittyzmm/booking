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
        listbox.insert(tk.END, f'Столик {r[0]} ({r[1]} чел.) — {r[2]}')

def open_book_window():
    book_win = tk.Toplevel(root)
    book_win.title('Забронировать столик')
    book_win.geometry('300x150')
    book_win.resizable(False, False)

    tk.Label(book_win, text='Номер столика:').grid(row=0, column=0, padx=10, pady=10, sticky='w')
    e_id = tk.Entry(book_win, width=10)
    e_id.grid(row=0, column=1, padx=5)

    tk.Label(book_win, text='Количество гостей:').grid(row=1, column=0, padx=10, pady=10, sticky='w')
    e_guest = tk.Entry(book_win, width=10)
    e_guest.grid(row=1, column=1, padx=5)

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
            book_win.destroy()

    tk.Button(book_win, text='Забронировать', command=book).grid(row=2, column=0, columnspan=2, pady=10)

def open_release_window():
    release_win = tk.Toplevel(root)
    release_win.title('Освободить столик')
    release_win.geometry('300x120')
    release_win.resizable(False, False)

    tk.Label(release_win, text='Номер столика:').grid(row=0, column=0, padx=10, pady=10, sticky='w')
    e_id = tk.Entry(release_win, width=10)
    e_id.grid(row=0, column=1, padx=5)

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
            release_win.destroy()

    tk.Button(release_win, text='Освободить', command=release).grid(row=1, column=0, columnspan=2, pady=10)

def open_add_window():
    add_win = tk.Toplevel(root)
    add_win.title('Добавить столик')
    add_win.geometry('300x120')
    add_win.resizable(False, False)

    tk.Label(add_win, text='Вместимость столика:').grid(row=0, column=0, padx=10, pady=10, sticky='w')
    e_capacity = tk.Entry(add_win, width=10)
    e_capacity.grid(row=0, column=1, padx=5)

    def add_table():
        try:
            cap = int(e_capacity.get())
            if cap <= 0:
                messagebox.showerror('Ошибка', 'Вместимость должна быть положительной!')
                return
        except:
            messagebox.showerror('Ошибка', 'Введите число для вместимости!')
            return

        c.execute('INSERT INTO tables (capacity, status) VALUES (?, "свободен")', (cap,))
        conn.commit()
        update_list()
        messagebox.showinfo('Успех', f'Добавлен столик на {cap} человек!')
        add_win.destroy()

    tk.Button(add_win, text='Добавить', command=add_table).grid(row=1, column=0, columnspan=2, pady=10)

def open_delete_window():
    delete_win = tk.Toplevel(root)
    delete_win.title('Удалить столик')
    delete_win.geometry('300x120')
    delete_win.resizable(False, False)

    tk.Label(delete_win, text='Номер столика:').grid(row=0, column=0, padx=10, pady=10, sticky='w')
    e_delete_id = tk.Entry(delete_win, width=10)
    e_delete_id.grid(row=0, column=1, padx=5)

    def delete_table():
        try:
            t = int(e_delete_id.get())
        except:
            messagebox.showerror('Ошибка', 'Введите номер столика!')
            return
        res = c.execute('SELECT id FROM tables WHERE id=?', (t,)).fetchone()
        if not res:
            messagebox.showerror('Ошибка', 'Столик не найден!')
            return
        c.execute('DELETE FROM tables WHERE id=?', (t,))

        remaining_tables = c.execute('SELECT capacity, status FROM tables ORDER BY id').fetchall()
        c.execute('DELETE FROM tables')
        for i, (cap, stat) in enumerate(remaining_tables, start=1):
            c.execute('INSERT INTO tables (id, capacity, status) VALUES (?, ?, ?)', (i, cap, stat))
        
        conn.commit()
        update_list()
        messagebox.showinfo('Успех', f'Столик {t} удалён!')
        delete_win.destroy()

    tk.Button(delete_win, text='Удалить', command=delete_table).grid(row=1, column=0, columnspan=2, pady=10)

root = tk.Tk()
root.title('Бронирование столиков')
root.geometry('500x600')
root.configure(padx=10, pady=10)

tk.Label(root, text='Бронирование столиков', font=('Arial', 14, 'bold')).pack(pady=(0, 10))
listbox = tk.Listbox(root, width=60, height=10)
listbox.pack(pady=5, fill=tk.BOTH, expand=True)
update_list()


button_frame = tk.Frame(root)
button_frame.pack(pady=20)

tk.Button(
    button_frame,
    text='Забронировать',
    command=open_book_window,
    width=15,
    bg='#4CAF50',
    activebackground="#009900"
).pack(side=tk.LEFT, padx=10)

tk.Button(
    button_frame,
    text='Освободить столик',
    command=open_release_window,
    width=15
).pack(side=tk.LEFT, padx=10)

tk.Button(
    button_frame,
    text='Добавить столик',
    command=open_add_window,
    width=15
).pack(side=tk.LEFT, padx=10)

tk.Button(
    button_frame,
    text='Удалить',
    command=open_delete_window,
    width=15,
    bg='#f44336',
    activebackground="#ed1b0c"
).pack(side=tk.LEFT, padx=10)

root.mainloop()
conn.close()