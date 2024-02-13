import os
import gzip
import re
import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk
import threading  # Добавлено для многозадачности

# Флаг для отмены поиска
cancel_search = False

def search_in_file(file_path, pattern):
    results_data = []
    try:
        if file_path.endswith('.gz'):
            with gzip.open(file_path, 'rt', encoding='utf-8', errors='ignore') as file:
                results_data = search_in_file_content(file, pattern)
        elif file_path.endswith('.log'):
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                results_data = search_in_file_content(file, pattern)
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
    return results_data

def search_in_file_content(file, pattern):
    results_data = []
    current_message = []
    inside_message = False

    try:
        lines = file.readlines()
        for line in lines:
            if cancel_search:  # Проверка на отмену поиска
                break

            if re.search(pattern, line, re.IGNORECASE):
                # Начало нового сообщения
                inside_message = True
                current_message = [line.strip()]
            elif inside_message:
                # Добавляем строки сообщения до следующей временной метки
                current_message.append(line.strip())
                if re.search(r"\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}:\d{3}", line):
                    inside_message = False
                    results_data.append('\n'.join(current_message))

    except UnicodeDecodeError as e:
        print(f"Error decoding file: {e}")
    
    return results_data

def update_progress(file_name):
    progress_bar['value'] += 1
    status_label.config(text=f"Обрабатывается файл: {file_name}")

def save_results():
    save_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if save_path:
        with open(save_path, 'w', encoding='utf-8') as save_file:
            save_file.write(results.get('1.0', tk.END))
        status_label.config(text=f"Результаты сохранены в {save_path}")

def browse_directory():
    directory_path = filedialog.askdirectory()
    directory_entry.delete(0, tk.END)
    directory_entry.insert(tk.END, directory_path)

def perform_search():
    global cancel_search  # Using a global variable for the flag
    cancel_search = False  # Reset the flag before a new search

    directory = directory_entry.get()
    pattern = pattern_entry.get()

    if directory and pattern:
        results.delete('1.0', tk.END)
        progress_bar['value'] = 0
        status_label.config(text="")
        files_to_search = [os.path.join(root, file) for root, dirs, files in os.walk(directory) for file in files]
        total_files = len(files_to_search)

        # Using a list to store the flag
        cancel_search_flag = [False]

        # Function for performing the search
        def search_in_thread():
            for file_path in files_to_search:
                results_data = search_in_file(file_path, pattern)
                update_progress(file_path)
                for result_message in results_data:
                    results.insert(tk.END, result_message + '\n')
                # Check the flag from the list
                if cancel_search_flag[0]:
                    break
            status_label.config(text="Поиск завершен")

        # Create and start the thread
        search_thread = threading.Thread(target=search_in_thread)
        search_thread.start()

        # Function to set the flag when cancel button is pressed
        def set_cancel_flag():
            cancel_search_flag[0] = True

        # Bind the set_cancel_flag function to the cancel button
        cancel_button.config(command=set_cancel_flag)
    else:
        results.delete('1.0', tk.END)
        results.insert(tk.END, "Заполните все поля.")

def cancel_search_operation():
    global cancel_search
    cancel_search = True
    status_label.config(text="Поиск отменен")

root = tk.Tk()
root.title("Поиск в архивах")
style = ttk.Style()
style.theme_use('clam')

left_frame = ttk.Frame(root)
left_frame.grid(row=0, column=0, padx=10, pady=10)

right_frame = ttk.Frame(root)
right_frame.grid(row=0, column=1, padx=10, pady=10)

directory_label = ttk.Label(left_frame, text="Выберите директорию:", font=('Arial', 10))
directory_label.grid(row=0, column=0, pady=10)

directory_entry = ttk.Entry(left_frame, width=50, font=('Arial', 10))
directory_entry.grid(row=1, column=0, pady=10)

browse_button = ttk.Button(left_frame, text="Обзор", command=browse_directory)
browse_button.grid(row=2, column=0, pady=10)

pattern_label = ttk.Label(left_frame, text="Введите регулярное выражение:", font=('Arial', 10))
pattern_label.grid(row=3, column=0, pady=10)

pattern_entry = ttk.Entry(left_frame, width=50, font=('Arial', 10))
pattern_entry.grid(row=4, column=0, pady=10)

search_button = ttk.Button(right_frame, text="Выполнить поиск", command=perform_search)
search_button.grid(row=0, column=0, pady=20)

cancel_button = ttk.Button(right_frame, text="Отменить поиск", command=cancel_search_operation)
cancel_button.grid(row=1, column=0, pady=10)

save_results_button = ttk.Button(right_frame, text="Сохранить результат", command=save_results)
save_results_button.grid(row=2, column=0, pady=10)

results_label = ttk.Label(right_frame, text="Результаты поиска:", font=('Arial', 10))
results_label.grid(row=3, column=0, pady=10)

results = scrolledtext.ScrolledText(right_frame, width=80, height=20, font=('Arial', 10))
results.grid(row=4, column=0, pady=10)

progress_bar = ttk.Progressbar(right_frame, orient=tk.HORIZONTAL, length=200)
progress_bar.grid(row=5, column=0, pady=10)

status_label = ttk.Label(right_frame, text="", font=('Arial', 10))
status_label.grid(row=6, column=0, pady=10)

root.mainloop()
