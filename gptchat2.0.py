import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox
from g4f.client import Client
import threading
import pyodbc

# Настройки подключения к MSSQL
DB_CONFIG = {
    'server': 'BASESRV\sqlexpress',
    'database': 'basa27',
    'username': 'basa27',
    'password': 'basa27'
}

client = Client()
current_language = "ru"  # Текущий язык (ru/en)

class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GPT Чат-бот")
        self.messages = []
        
        # Инициализация интерфейса
        self.setup_ui()
        
        # Загрузка истории при старте
        self.load_history()
    
    def create_connection(self):
        """Автоматическое подключение к MSSQL с подбором драйвера"""
        drivers = [
            "{ODBC Driver 17 for SQL Server}",
            "{ODBC Driver 13 for SQL Server}",
            "{SQL Server Native Client 11.0}",
            "{SQL Server}",
            ""  # Попытка подключения без указания драйвера
        ]
        
        for driver in drivers:
            try:
                conn_str = f"DRIVER={driver};SERVER={DB_CONFIG['server']};DATABASE={DB_CONFIG['database']};UID={DB_CONFIG['username']};PWD={DB_CONFIG['password']}"
                return pyodbc.connect(conn_str, timeout=5)
            except Exception as e:
                last_error = e
                continue
        
        messagebox.showerror(
            "Ошибка подключения",
            f"Не удалось подключиться к базе данных.\n\n"
            f"Проверьте:\n"
            f"1. Доступность сервера\n"
            f"2. Правильность логина/пароля\n"
            f"3. Наличие ODBC драйверов\n\n"
            f"Ошибка: {last_error}"
        )
        return None
    
    def load_history(self):
        """Загружает историю сообщений из MSSQL"""
        conn = self.create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT TOP 100 [User], [Bot] FROM [gptchat_saves] ORDER BY [Id] DESC")
                for row in reversed(cursor.fetchall()):
                    if row[0]:  # Сообщение пользователя
                        self.messages.append({"role": "user", "content": row[0]})
                    if row[1]:  # Ответ бота
                        self.messages.append({"role": "assistant", "content": row[1]})
                
                if not self.messages:
                    self.messages.append({"role": "user", "content": "Привет"})
                
                self.update_chat_display()
            except Exception as e:
                messagebox.showwarning("Предупреждение", f"Не удалось загрузить историю: {e}")
            finally:
                conn.close()
    
    def save_message(self, user_msg, bot_msg):
        """Сохраняет сообщение в MSSQL"""
        conn = self.create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO [gptchat_saves] ([User], [Bot]) VALUES (?, ?)", user_msg, bot_msg)
                conn.commit()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить сообщение: {e}")
            finally:
                conn.close()
    
    def setup_ui(self):
        """Настраивает пользовательский интерфейс"""
        # Стилизация
        style = ttk.Style()
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabel", background="#f0f0f0", font=("Arial", 10))
        style.configure("TButton", font=("Arial", 10), padding=5)
        
        # Главный контейнер
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Вкладки
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True)
        
        # Вкладка чата
        self.setup_chat_tab()
        
        # Вкладка настроек
        self.setup_settings_tab()
        
        # Вкладка "О нас"
        self.setup_about_tab()
        
    #Семёнов Юрий и Слепцов Евгений
    def setup_chat_tab(self):
        """Настраивает вкладку чата"""
        chat_tab = ttk.Frame(self.notebook)
        self.notebook.add(chat_tab, text="Чат")
        #Слепцов Евгений
        # История сообщений
        self.chat_history = scrolledtext.ScrolledText(
            chat_tab,
            wrap=tk.WORD,
            width=80,
            height=20,
            font=("Arial", 10),
            state=tk.DISABLED
        )
        self.chat_history.pack(fill="both", expand=True, padx=5, pady=5)
        #Семёнов Юрий
        # Поле ввода
        input_frame = ttk.Frame(chat_tab)
        input_frame.pack(fill="x", padx=5, pady=5)
        
        self.user_input = ttk.Entry(input_frame, font=("Arial", 10))
        self.user_input.pack(side="left", fill="x", expand=True)
        self.user_input.bind("<Return>", lambda e: self.process_message())
        
        send_btn = ttk.Button(
            input_frame,
            text="Отправить",
            command=self.process_message
        )
        send_btn.pack(side="right", padx=(5, 0))
    
    def setup_settings_tab(self):
        """Настраивает вкладку настроек"""
        settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(settings_tab, text="Настройки")
        
        # Настройка языка
        lang_frame = ttk.LabelFrame(settings_tab, text="Язык интерфейса")
        lang_frame.pack(fill="x", padx=10, pady=10)
        
        self.lang_var = tk.StringVar(value=current_language)
        ttk.Radiobutton(
            lang_frame,
            text="Русский",
            variable=self.lang_var,
            value="ru"
        ).pack(anchor="w", padx=5, pady=2)
        
        ttk.Radiobutton(
            lang_frame,
            text="English",
            variable=self.lang_var,
            value="en"
        ).pack(anchor="w", padx=5, pady=2)
        
        # Кнопка применения
        ttk.Button(
            settings_tab,
            text="Применить настройки",
            command=self.apply_settings
        ).pack(pady=10)
    
    def setup_about_tab(self):
        """Настраивает вкладку 'О нас'"""
        about_tab = ttk.Frame(self.notebook)
        self.notebook.add(about_tab, text="О нас")
        
        title = ttk.Label(
            about_tab,
            text="Разработчики:",
            font=("Arial", 12, "bold")
        )
        title.pack(pady=10)
        
        developers = [
            "Степанов Руслан КИСП-9-22 (2)",
            "Слепцов Евгений КИСП-9-22 (2)",
            "Цвикальский Артём КИСП-9-22 (2)",
            "Лаптев Никита КИСП-9-22 (2)",
            "Семёнов Юрий КИСП-9-22 (2)"
        ]
        
        for dev in developers:
            ttk.Label(about_tab, text=dev).pack(pady=2)
    
    def process_message(self):
        """Обрабатывает отправку сообщения"""
        message = self.user_input.get().strip()
        if not message:
            return
        
        # Добавляем сообщение пользователя
        self.messages.append({"role": "user", "content": message})
        self.update_chat_display()
        self.user_input.delete(0, tk.END)
        
        # Получаем ответ от ИИ
        threading.Thread(target=self.get_ai_response, args=(message,), daemon=True).start()
    
    #Лаптев Никита
    def get_ai_response(self, user_message):
        """Получает ответ от ИИ и сохраняет в MSSQL"""
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=self.messages,
            )
            
            bot_response = response.choices[0].message.content
            self.messages.append({"role": "assistant", "content": bot_response})
            
            # Сохраняем в MSSQL
            self.save_message(user_message, bot_response)
            
            # Обновляем интерфейс
            self.root.after(0, self.update_chat_display)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror(
                "Ошибка",
                f"Не удалось получить ответ: {str(e)}"
            ))
    
    def update_chat_display(self):
        """Обновляет отображение чата"""
        self.chat_history.config(state=tk.NORMAL)
        self.chat_history.delete("1.0", tk.END)
        
        for msg in self.messages:
            if msg["role"] == "user":
                self.chat_history.insert(tk.END, "Вы: ", "user")
                self.chat_history.insert(tk.END, f"{msg['content']}\n\n")
            else:
                self.chat_history.insert(tk.END, "Бот: ", "bot")
                self.chat_history.insert(tk.END, f"{msg['content']}\n\n")
        
        self.chat_history.tag_config("user", foreground="blue", font=("Arial", 10, "bold"))
        self.chat_history.tag_config("bot", foreground="green", font=("Arial", 10, "bold"))
        self.chat_history.config(state=tk.DISABLED)
        self.chat_history.see(tk.END)
    
    def apply_settings(self):
        """Применяет настройки языка"""
        global current_language
        new_lang = self.lang_var.get()
        
        if new_lang != current_language:
            current_language = new_lang
            self.update_ui_language()
            messagebox.showinfo(
                "Уведомление",
                "Язык изменен. Перезапустите приложение для полного применения."
                if current_language == "ru" else 
                "Language changed. Restart the application for full effect."
            )
    
    def update_ui_language(self):
        """Обновляет язык интерфейса"""
        # Обновляем вкладки
        self.notebook.tab(0, text="Чат" if current_language == "ru" else "Chat")
        self.notebook.tab(1, text="Настройки" if current_language == "ru" else "Settings")
        self.notebook.tab(2, text="О нас" if current_language == "ru" else "About")
        
        # Обновляем кнопки
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Button):
                if widget["text"] == "Отправить":
                    widget.config(text="Send" if current_language == "en" else "Отправить")
                elif widget["text"] == "Применить настройки":
                    widget.config(text="Apply settings" if current_language == "en" else "Применить настройки")

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()
