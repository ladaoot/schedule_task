from tabulate import tabulate  # Для красивого вывода таблицы
import pandas as pd

# Параметры задачи
WORK_HOURS = 21  # Часы работы (с 6:00 до 3:00)
START_HOUR = 6   # Начало работы автобусов
END_HOUR = 3     # Конец работы автобусов (следующего дня)
DAYS_IN_WEEK = 7  # Количество дней в неделе
PEAK_HOURS = [(7, 9), (17, 19)]  # Часы пик (утро и вечер)
MAX_HOURS_A = 9  # Максимальное количество часов работы для Типа A
MAX_HOURS_B = 12  # Максимальное количество часов работы для Типа B
TRIP_DURATION = 1  # Длительность поездки в часах

# Ограничения для Типа A
TYPE_A_START = 7  # Начало работы Типа A
TYPE_A_END = 19  # Конец работы Типа A

# Интервалы отправления автобусов
INTERVAL_NORMAL = 20  # Интервал в обычное время (в минутах)
INTERVAL_PEAK = 10    # Интервал в часы пик (в минутах)

# Генерация водителей
drivers_a = [{"id": i + 1, "type": "A", "hours_worked": 0, "busy_until": -1} for i in range(5)]  # Водители Типа A
drivers_b = [{"id": i + 1, "type": "B", "hours_worked": 0, "busy_until": -1, "last_worked_day": -3} for i in range(5)]  # Водители Типа B

# Генерация автобусов
buses = [{"id": i + 1, "busy_until": -1} for i in range(8)]  # Всего 8 автобусов

# Норма часов для каждого типа водителей
DAILY_HOURS_A = MAX_HOURS_A
DAILY_HOURS_B = MAX_HOURS_B


def is_peak_hour(hour):
    """Проверяет, является ли указанный час часом пик."""
    for start, end in PEAK_HOURS:
        if start <= hour < end:
            return True
    return False


def is_type_a_available(day, hour):
    """Проверяет доступность водителей Типа A."""
    if day >= 5:  # Тип A работает только по будням (дни с 0 до 4)
        return False
    if hour < TYPE_A_START or hour >= TYPE_A_END:  # Ограничение по времени
        return False
    return True


def assign_driver_a(drivers, max_hours, hour):
    """
    Назначает водителя из списка доступных водителей типа A.
    Если нет доступных водителей, возвращает None.
    """
    for driver in drivers:
        if driver["hours_worked"] + TRIP_DURATION <= max_hours and driver["busy_until"] <= hour:
            driver["hours_worked"] += TRIP_DURATION
            driver["busy_until"] = hour + TRIP_DURATION
            return driver
    return None


def assign_driver_b(drivers, day, max_hours, hour):
    """
    Назначает водителя из списка доступных водителей типа B.
    Учитывает правило "каждый водитель работает раз в три дня".
    Если нет доступных водителей, возвращает None.
    """
    for driver in drivers:
        if (
            driver["hours_worked"] + TRIP_DURATION <= max_hours and
            driver["busy_until"] <= hour and
                (day - driver["last_worked_day"] >= 3 or day == driver["last_worked_day"])  # Проверяем правило "раз в три дня"
        ):
            driver["hours_worked"] += TRIP_DURATION
            driver["busy_until"] = hour + TRIP_DURATION
            driver["last_worked_day"] = day  # Обновляем последний рабочий день водителя
            return driver
    return None


def create_new_driver(driver_type):
    """Создает нового водителя указанного типа."""
    if driver_type == "A":
        new_id = len(drivers_a) + 1
        new_driver = {"id": new_id, "type": "A", "hours_worked": 0, "busy_until": -1}
        drivers_a.append(new_driver)
        return new_driver
    elif driver_type == "B":
        new_id = len(drivers_b) + 1
        new_driver = {"id": new_id, "type": "B", "hours_worked": 0, "busy_until": -1, "last_worked_day": -3}
        drivers_b.append(new_driver)
        return new_driver


def assign_bus(buses, hour):
    """
    Назначает автобус из списка доступных автобусов.
    Если нет доступных автобусов, возвращает None.
    """
    for bus in buses:
        if bus["busy_until"] <= hour:
            bus["busy_until"] = hour + TRIP_DURATION
            return bus
    return None

def reset_driver_hours_and_buses():
    """Сбрасывает часы работы водителей и освобождает автобусы в начале нового дня."""
    for driver in drivers_a:
        driver["hours_worked"] = 0
        driver["busy_until"] = -1
    for driver in drivers_b:
        driver["hours_worked"] = 0
        driver["busy_until"] = -1
    for bus in buses:
        bus["busy_until"] = -1

def generate_schedule():
    """
    Генерирует расписание на неделю с учётом типов водителей, их ограничений и интервалов отправления автобусов.
    Если не хватает водителей или автобусов, поездка пропускается.
    """
    schedule = []

    for day in range(DAYS_IN_WEEK):  # Проходим по каждому дню недели
        reset_driver_hours_and_buses()  # Сбрасываем часы работы водителей и освобождаем автобусы в начале каждого дня
        day_schedule = []

        for hour in range(START_HOUR, START_HOUR + WORK_HOURS):
            current_hour = hour % 24  # Преобразуем часы в формат от 0 до 23
            next_day = (hour >= 24)  # Проверяем, переходит ли время на следующий день

            interval = INTERVAL_PEAK if is_peak_hour(current_hour) and day < 5 else INTERVAL_NORMAL
            departures_in_hour = list(range(0, 60, interval))  # Время отправлений в этом часе

            for minute in departures_in_hour:
                driver_assigned = None
                bus_assigned = None

                if is_type_a_available(day if not next_day else day + 1, current_hour):
                    driver_assigned = assign_driver_a(drivers_a, DAILY_HOURS_A, current_hour)

                if driver_assigned is None:
                    driver_assigned = assign_driver_b(drivers_b, day if not next_day else day + 1,
                                                      DAILY_HOURS_B, current_hour)

                if driver_assigned is None:
                    if is_type_a_available(day if not next_day else day + 1, current_hour):
                        driver_assigned = create_new_driver("A")
                    else:
                        driver_assigned = create_new_driver("B")

                bus_assigned = assign_bus(buses, current_hour)

                if bus_assigned is not None and driver_assigned is not None:
                    day_schedule.append({
                        "hour": current_hour,
                        "minute": minute,
                        "driver_id": driver_assigned["id"],
                        "driver_type": driver_assigned["type"],
                        "bus_id": bus_assigned["id"]
                    })

        schedule.append(day_schedule)

    return schedule

def print_schedule(schedule):

    days_pd = []

    """Выводит расписание в виде таблицы."""
    for day_index, day_schedule in enumerate(schedule):
        table_data = []
        for entry in day_schedule:
            departure_time = f"{entry['hour']:02d}:{entry['minute']:02d}"
            arrival_time = f"{(entry['hour'] + TRIP_DURATION) % WORK_HOURS:02d}:{entry['minute']:02d}"
            bus_id = entry["bus_id"]
            driver_info = f"{entry['driver_id']} {entry['driver_type']}"

            table_data.append([departure_time, arrival_time, f"Bus {bus_id}", driver_info])

        headers = ["Отправление", "Прибытие", f"А {day_index}", f"В {day_index}"]

        days_pd.append(pd.DataFrame(table_data, columns=headers))

    df = pd.merge(days_pd[0], days_pd[1], on=["Отправление", "Прибытие"], how = 'left')
    for i in range(2, 7):
        df = pd.merge(df, days_pd[i], on=["Отправление", "Прибытие"], how = 'left')

    print(tabulate(df, headers='keys', tablefmt="grid"))

def main():
    schedule = generate_schedule()
    print("Сгенерированное расписание:")
    print_schedule(schedule)

if __name__ == "__main__":
    main()
