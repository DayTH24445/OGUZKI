import tkinter as tk
from tkinter import scrolledtext
from g4f.client import Client
import time
import threading

client = Client()
messages = [{"role": "user", "content": "Привет"}]  # Инициализируем историю переписки
system_prompt = "" # Инициализируем системный промт

def create_window():
    """Создает окно с полем для ввода запроса и областью для вывода ответа."""

    window = tk.Tk()
    window.title("Окно запроса/ответа")

    # --- Поле для системного промта ---
    system_prompt_label = tk.Label(window, text="Системный промт (описание роли GPT):")
    system_prompt_label.pack(pady=5)

    system_prompt_entry = tk.Entry(window, width=50)
    system_prompt_entry.pack(pady=5)

    def set_system_prompt():
        """Устанавливает системный промт."""
        global system_prompt
        system_prompt = system_prompt_entry.get()
        messages.clear()  # Очищаем историю, чтобы начать с новым промтом
        messages.append({"role": "system", "content": system_prompt}) # Устанавливаем системный промт в истории
        messages.append({"role": "user", "content": "Привет"}) # Добавляем приветствие после промта
    system_prompt_button = tk.Button(window, text="Установить промт", command=set_system_prompt)
    system_prompt_button.pack(pady=10)

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
    def process_request():
        """Получает запрос из поля ввода, выполняет запрос и отображает ответ."""
        request = input_entry.get()

        # Добавляем запрос пользователя в историю *ДО* запроса к боту
        messages.append({"role": "user", "content": request})

        # Очищаем поле ввода
        input_entry.delete(0, tk.END)

        # Выводим сообщение о загрузке
        response_text.config(state=tk.NORMAL)
        response_text.delete("1.0", tk.END)
        response_text.insert(tk.END, "Думаю...")
        response_text.config(state=tk.DISABLED)

        # Запускаем запрос к боту в отдельном потоке
        threading.Thread(target=get_bot_response, args=(request,)).start()

    def get_bot_response(request):
        """Получает ответ от бота и отображает его."""
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                web_search=False,  # Явно отключаем веб-поиск
            )

            bot_response = response.choices[0].message.content
            messages.append({"role": "assistant", "content": bot_response})  # Добавляем ответ бота в историю

            # Отображаем ответ в текстовой области
            window.after(0, update_response_text, bot_response) # Используем window.after для безопасного обновления UI из потока

        except Exception as e:
            error_message = f"Произошла ошибка: {e}"
            window.after(0, update_response_text, error_message) # Используем window.after для безопасного обновления UI из потока
            time.sleep(5)  # Пробуем снова через 5 секунд, на случай если API временно недоступен

    def update_response_text(response):
        """Обновляет текстовую область с ответом."""
        response_text.config(state=tk.NORMAL)
        response_text.delete("1.0", tk.END)
        response_text.insert(tk.END, response)
        response_text.config(state=tk.DISABLED)


    process_button = tk.Button(window, text="Отправить", command=process_request)
    process_button.pack(pady=10)


    window.mainloop()  # Запускаем цикл обработки событий

if __name__ == "__main__":
    create_window()