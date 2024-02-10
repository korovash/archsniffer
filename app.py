import os
import gzip
import re
import tkinter as tk
from tkinter import filedialog, scrolledtext

def search_in_directory(directory, pattern):
    results.delete('1.0', tk.END)  # Очистим предыдущие результаты
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)

            if file.endswith('.gz'):
                with gzip.open(file_path, 'rt', encoding='utf-8', errors='ignore') as archive:
                    search_in_file(archive, pattern)

            elif file.endswith('.log'):
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as log_file:
                    search_in_file(log_file, pattern)

def search_in_file(file, pattern):
    try:
        for line in file:
            if re.search(pattern, line):
                results.insert(tk.END, line.strip() + '\n')
    except UnicodeDecodeError as e:
        print(f"Ошибка декодирования: {e}")

def browse_directory():
    directory_path = filedialog.askdirectory()
    directory_entry.delete(0, tk.END)
    directory_entry.insert(tk.END, directory_path)

def perform_search():
    directory = directory_entry.get()
    pattern = pattern_entry.get()

    if directory and pattern:
        search_in_directory(directory, pattern)
    else:
        results.delete('1.0', tk.END)
        results.insert(tk.END, "Заполните все поля.")

# Создание главного окна
root = tk.Tk()
root.title("Поиск в архивах")

# Создание и настройка элементов управления
directory_label = tk.Label(root, text="Выберите директорию:")
directory_label.pack(pady=10)

directory_entry = tk.Entry(root, width=50)
directory_entry.pack(pady=10)

browse_button = tk.Button(root, text="Обзор", command=browse_directory)
browse_button.pack(pady=10)

pattern_label = tk.Label(root, text="Введите регулярное выражение:")
pattern_label.pack(pady=10)

pattern_entry = tk.Entry(root, width=50)
pattern_entry.pack(pady=10)

search_button = tk.Button(root, text="Выполнить поиск", command=perform_search)
search_button.pack(pady=20)

results_label = tk.Label(root, text="Результаты поиска:")
results_label.pack(pady=10)

results = scrolledtext.ScrolledText(root, width=80, height=20)
results.pack(pady=10)

# Запуск главного цикла
root.mainloop()