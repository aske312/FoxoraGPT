import multiprocessing
import subprocess
import time
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel

# Консоль для вывода
console = Console()


def run_script(script_name, status_queue):
    """Запускает скрипт и отправляет статус в очередь."""
    try:
        status_queue.put((script_name, "[yellow]Запуск[/yellow]"))
        process = subprocess.Popen(["python", script_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        status_queue.put((script_name, "[green]Работает[/green]"))
        while True:
            output = process.stdout.readline()
            if output == b"" and process.poll() is not None:
                break
            if output:
                status_queue.put((script_name, f"[blue]{output.strip().decode('utf-8')}[/blue]"))
        status_queue.put((script_name, "[red]Завершен[/red]"))
    except Exception as e:
        status_queue.put((script_name, f"[red]Ошибка: {e}[/red]"))


def status_monitor(status_queue, scripts):
    """Отображает статус работы скриптов в виде таблицы."""
    # Словарь для хранения статусов
    status_dict = {script: "[yellow]Ожидание запуска[/yellow]" for script in scripts}

    def generate_table():
        """Генерирует таблицу на основе текущих статусов."""
        table = Table(title="Статус скриптов", show_header=True, header_style="bold magenta")
        table.add_column("Скрипт", style="cyan", width=30)
        table.add_column("Статус", style="green", width=50)
        for script, status in status_dict.items():
            table.add_row(script, status)
        return table

    with Live(generate_table(), refresh_per_second=4) as live:
        while True:
            # Обновляем статусы
            while not status_queue.empty():
                script_name, status = status_queue.get()
                status_dict[script_name] = status

            # Обновляем таблицу
            live.update(generate_table())
            time.sleep(0.25)


if __name__ == "__main__":
    # Список скриптов для запуска
    scripts = [
        "int/bot_pool.py",  # Пример бота
        "other_script.py",  # Другой скрипт
        "another_script.py"  # Еще один скрипт
    ]

    # Очередь для передачи статуса
    status_queue = multiprocessing.Queue()

    # Создаем процессы для каждого скрипта
    processes = []
    for script in scripts:
        process = multiprocessing.Process(target=run_script, args=(script, status_queue))
        processes.append(process)

    # Процесс для мониторинга статуса
    monitor_process = multiprocessing.Process(target=status_monitor, args=(status_queue, scripts))

    # Запускаем процессы
    for process in processes:
        process.start()
    monitor_process.start()

    # Ждем завершения процессов (если нужно)
    for process in processes:
        process.join()
    monitor_process.join()

    console.print(Panel("Все скрипты завершили работу.", style="bold green"))