import multiprocessing
import subprocess
import time
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel

# Пути к скриптам ботов
BOT_1_SCRIPT = "int/bot_pool.py"
# BOT_2_SCRIPT = "bot2.py"

# Консоль для вывода
console = Console()


def run_bot(script_name, status_queue):
    """Запускает скрипт бота и отправляет статус в очередь."""
    try:
        status_queue.put((script_name, "Запущен"))
        process = subprocess.Popen(["python", script_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while True:
            output = process.stdout.readline()
            if output == b"" and process.poll() is not None:
                break
            if output:
                status_queue.put((script_name, output.strip().decode("utf-8")))
        status_queue.put((script_name, "Завершен"))
    except Exception as e:
        status_queue.put((script_name, f"Ошибка: {e}"))


def update_table(status_queue, table):
    """Обновляет таблицу статусов."""
    while not status_queue.empty():
        script_name, status = status_queue.get()
        if script_name == BOT_1_SCRIPT:
            table.row(0, script_name, status)
        # elif script_name == BOT_2_SCRIPT:
        #     table.row(1, script_name, status)


def status_monitor(status_queue):
    """Отображает статус работы ботов в виде таблицы."""
    table = Table(title="Статус ботов", show_header=True, header_style="bold magenta")
    table.add_column("Бот", style="cyan", width=20)
    table.add_column("Статус", style="green", width=50)
    table.add_row(BOT_1_SCRIPT, "Ожидание запуска")
    # table.add_row(BOT_2_SCRIPT, "Ожидание запуска")

    with Live(table, refresh_per_second=4) as live:
        while True:
            update_table(status_queue, table)
            live.update(table)
            time.sleep(0.25)


if __name__ == "__main__":
    # Очередь для передачи статуса
    status_queue = multiprocessing.Queue()

    # Создаем процессы для каждого бота
    process1 = multiprocessing.Process(target=run_bot, args=(BOT_1_SCRIPT, status_queue))
    # process2 = multiprocessing.Process(target=run_bot, args=(BOT_2_SCRIPT, status_queue))

    # Процесс для мониторинга статуса
    monitor_process = multiprocessing.Process(target=status_monitor, args=(status_queue,))

    # Запускаем процессы
    process1.start()
    # process2.start()
    monitor_process.start()

    # Ждем завершения процессов (если нужно)
    process1.join()
    # process2.join()
    monitor_process.join()

    console.print(Panel("Все боты завершили работу.", style="bold green"))