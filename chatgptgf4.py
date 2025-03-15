import tkinter as tk
from tkinter import scrolledtext
from g4f.client import Client
import time
import threading

client = Client()
messages = [{"role": "user", "content": "Привет"}]  # Инициализируем историю переписки

def create_window():
    """Создает окно с полем для ввода запроса и областью для вывода ответа."""

    window = tk.Tk()
    window.title("Окно запроса/ответа")

    # --- Поле для ввода ---

    input_label = tk.Label(window, text="Введите ваш запрос:")
    input_label.pack(pady=5)  # Добавляем небольшой отступ
    input_entry = tk.Entry(window, width=50)  # Настройте ширину по необходимости
    input_entry.pack(pady=5)

    # --- Область для ответа ---

    response_label = tk.Label(window, text="Ответ:")
    response_label.pack(pady=5)
    response_text = scrolledtext.ScrolledText(window, width=60, height=10, wrap=tk.WORD)  # Настройте ширину/высоту
    response_text.pack(pady=5)
    response_text.config(state=tk.DISABLED)  # Делаем ее доступной только для чтения

    # --- Кнопка для запуска действия ---
    def process_request(): #Запуск события
        
        request = input_entry.get()
        messages.append({"role": "user", "content": request}) # Добавляем запрос пользователя в историю *ДО* запроса к боту

        #-------------------------------------------#

        # Выводим сообщение о загрузке
        input_entry.delete(0, tk.END) # Очищаем поле ввода
        response_text.config(state=tk.NORMAL)
        response_text.delete("1.0", tk.END)
        response_text.insert(tk.END, "Думаю...")
        response_text.config(state=tk.DISABLED)

        #-------------------------------------------#

        # Запускаем запрос к боту
        threading.Thread(target=get_bot_response, args=(request,)).start()

    def get_bot_response(request):
        """Получает ответ от бота и отображает его."""

        #----------------------------------------------#

        # При работоспасобности бота

        try:
            # Настройки модели ChatGPT
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                web_search=False,
                )
            # Ответ бота
            bot_response = response.choices[0].message.content
            messages.append({"role": "assistant", "content": bot_response})  # Добавляем ответ бота в историю
            window.after(0, update_response_text, bot_response)  #  Отображаем ответ в текстовой области

        #----------------------------------------------#
        
        # При неработоспасобности бота

        except Exception as e:
            error_message = f"Произошла ошибка: {e}"
            window.after(0, update_response_text, error_message)  # Используем window.after для безопасного обновления UI из потока
            time.sleep(5)  # Пробуем снова через 5 секунд, на случай если API временно недоступен

        #----------------------------------------------#

    #----------------------------------------------#

    # Обновления текстового окна с ответом бота

    def update_response_text(response):
        """Обновляет текстовую область с ответом."""
        response_text.config(state=tk.NORMAL)
        response_text.delete("1.0", tk.END)
        response_text.insert(tk.END, response)
        response_text.config(state=tk.DISABLED)

    #----------------------------------------------#

    # Создаём кнопку и привязывает Enter для отправки вопросы боту
        
    process_button = tk.Button(window, text="Отправить", command=process_request)
    process_button.pack(pady=10)
    input_entry.bind('<Return>', lambda event: process_request())  # Привязываем нажатие Enter к функции отправки запроса
    input_entry.focus() # Устанавливаем фокус на поле ввода, чтобы пользователь мог сразу начать ввод

    #----------------------------------------------#
    
    # Делаем бесконечный цикл для того чтобы вопросы можно была задавать без остоновки
    window.mainloop()

if __name__ == "__main__":
    create_window()
