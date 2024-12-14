from datetime import datetime, timedelta
import pandas as pd
from tabulate import tabulate


def create_weekly_bus_schedule(start_time, end_time, peak_intervals, off_peak_intervals, peak_hours, num_buses,
                               road_time):
    """
    Создает расписание автобусов на неделю с учетом времени работы, интервалов и часов пик.

    :param start_time: Время начала работы (в формате "HH:MM")
    :param end_time: Время окончания работы (в формате "HH:MM")
    :param peak_intervals: Интервал движения в час пик (в минутах)
    :param off_peak_intervals: Интервал движения в остальное время (в минутах)
    :param peak_hours: Список часов пик (например, [(7, 9), (17, 19)])
    :param num_buses: Количество автобусов
    :param road_time: Время в пути для каждого автобуса (в минутах)
    :return: Словарь с расписанием для каждого дня недели
    """
    weekly_schedule = {}

    for day in range(7):  # 0 - понедельник, 6 - воскресенье
        is_weekend = day in [5, 6]  # Суббота и воскресенье
        # print(day)
        daily_schedule = create_bus_schedule(
            start_time,
            end_time,
            peak_intervals if not is_weekend else off_peak_intervals,
            off_peak_intervals,
            [] if is_weekend else peak_hours,
            num_buses,
            road_time
        )
        weekly_schedule[day] = daily_schedule

    return weekly_schedule


def create_bus_schedule(start_time, end_time, peak_intervals, off_peak_intervals, peak_hours, num_buses, road_time):
    """
    Создает расписание автобусов с учетом времени работы, интервалов и часов пик.

    :param start_time: Время начала работы (в формате "HH:MM")
    :param end_time: Время окончания работы (в формате "HH:MM")
    :param peak_intervals: Интервал движения в час пик (в минутах)
    :param off_peak_intervals: Интервал движения в остальное время (в минутах)
    :param peak_hours: Список часов пик (например, [(7, 9), (17, 19)])
    :param num_buses: Количество автобусов
    :param road_time: Время в пути для каждого автобуса (в минутах)
    :return: Список расписаний для каждого автобуса
    """
    # Преобразуем входные данные в объекты времени
    start = datetime.strptime(start_time, "%H:%M")
    end = datetime.strptime(end_time, "%H:%M")
    if end < start:
        end += timedelta(days=1)  # Если конец работы после полуночи

    # Расписание для каждого автобуса
    bus_schedules = [[] for _ in range(num_buses)]
    current_time = start

    def is_bus_available(bid, time, road_time):
        if not bus_schedules[bid]:
            return True
        last_dep = bus_schedules[bid][-1]
        return time > last_dep + timedelta(minutes=road_time)

    while current_time < end:
        # Определяем текущий интервал (в зависимости от часа пик)
        current_hour = current_time.hour
        is_peak = any(start_hour <= current_hour < end_hour for start_hour, end_hour in peak_hours)
        interval = peak_intervals if is_peak else off_peak_intervals

        # Распределяем рейсы по автобусам
        for bus in range(num_buses):
            if current_time >= end:
                break
            if not is_bus_available(bus, current_time, road_time):
                continue
            departure = current_time
            bus_schedules[bus].append(departure)
            # print(bus)
            break
        current_time += timedelta(minutes=interval)

    return bus_schedules


# Параметры расписания
start_time = "06:00"  # Начало работы
end_time = "03:00"  # Конец работы (следующего дня)
peak_intervals = 10  # Интервал в час пик (в минутах)
off_peak_intervals = 20  # Интервал вне часа пик (в минутах)
peak_hours = [(7, 9), (17, 19)]  # Часы пик (7:00-9:00 и 17:00-19:00)
num_buses = 8  # Количество автобусов
road_time = 60  # Время в пути

# Генерация расписания на неделю
weekly_schedule = create_weekly_bus_schedule(
    start_time,
    end_time,
    peak_intervals,
    off_peak_intervals,
    peak_hours,
    num_buses,
    road_time
)

last_hours = []
days_sorted = []
days = []

# Форматированный вывод расписания на неделю
for day, schedule in weekly_schedule.items():
    day_name = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"][day]
    # print(day_name)
    time_bus = []
    for i, bus_schedule in enumerate(schedule):
        for departure in bus_schedule:
            time_bus.append(
                [departure, departure + timedelta(minutes=road_time), i])

    days.append((day, time_bus))
    # print([i for i in time_bus if i[0].hour<6])
    last_hours_1 = [i for i in time_bus if i[0].hour < 6]

    time_bus = [i for i in time_bus if i not in last_hours_1]
    time_bus.extend(last_hours)

    a = sorted(time_bus, key=lambda x: x[0].strftime("%H:%M"), reverse=False)

    last_hours = last_hours_1

    df = pd.DataFrame(a, columns=['Отправление', 'Прибытие', f'Номер автобуса {day}'])
    days_sorted.append((day_name, df))

for i in range(7):
    days[i] = (i, sorted(days[i][1], key=lambda x: x[0]))

monday = days_sorted[0][1]

time_bus = monday.values.tolist()
time_bus.extend(last_hours)

a = sorted(time_bus, key=lambda x: x[0].strftime("%H:%M"), reverse=False)
days_sorted[0] = (days_sorted[0][0], pd.DataFrame(a, columns=['Отправление', 'Прибытие', 'Номер автобуса 0']))

df = pd.merge(days_sorted[0][1], days_sorted[1][1], on=['Отправление', 'Прибытие'], how='left')

for i in range(2, 7):
    df = pd.merge(df, days_sorted[i][1], on=['Отправление', 'Прибытие'], how='left')

print(tabulate(df, headers='keys', tablefmt='psql'))

# Константы
DRIVER_TYPES = {
    "A": {"work_min": 8 * 60, "work_max": 9 * 60, "break_duration": 60},  # Тип A: 8-9 часов работы, 1 час перерыв
    "B": {"work_min": 11 * 60, "work_max": 12 * 60, "break_duration": 0},  # Тип B: 11-12 часов работы, без перерыва
}


class Driver:
    def __init__(self, driver_id, driver_type):
        self.id = driver_id
        self.type = driver_type
        self.work_min = DRIVER_TYPES[driver_type]["work_min"]
        self.work_max = DRIVER_TYPES[driver_type]["work_max"]
        self.break_duration = DRIVER_TYPES[driver_type]["break_duration"]
        self.routes = []  # Список маршрутов (день, автобус, начало, конец)
        self.total_minutes_worked = 0
        self.daily_minutes_worked = {}  # Сколько минут отработано в каждый день

    def can_take_route(self, day, start_time, end_time):
        """
        Проверяет, может ли водитель взять маршрут.
        """
        route_minutes = (end_time - start_time).total_seconds() / 60

        # print(self.type == 'A' and 7<= start_time.hour<=18)
        if self.type == 'A' and (((6 > start_time.hour or 8 <= start_time.hour) and self.daily_minutes_worked.get(day,
                                                                                                                  0) == 0) or end_time.hour > 18 or end_time.hour < 1):
            return False

        # print(self.routes[-1][0])
        # print(day)
        if self.type == 'B' and self.routes is not [] and self.routes[-1][0] != day and self.routes[-1][0] + 2 > day:
            # print(self.routes[-1][0])
            # print(day)
            return False

        # Проверяем дневную норму работы
        daily_worked = self.daily_minutes_worked.get(day, 0)
        if daily_worked + route_minutes > self.work_max:
            return False

        # Проверяем пересечение с уже назначенными маршрутами
        for assigned_day, _, assigned_start, assigned_end in self.routes:
            if assigned_day == day and not (end_time < assigned_start or start_time > assigned_end):
                return False

        return True

    def assign_route(self, day, bus_id, start_time, end_time):
        """
        Назначает маршрут водителю.
        """

        if self.routes != []:
            last_tr = (self.routes[-1][-1] if self.routes[-1][0] == day else start_time)
        else:
            last_tr = start_time

        # route_minutes = (end_time - start_time).total_seconds() / 60

        # Добавляем маршрут
        self.routes.append((day, bus_id, start_time, end_time))
        self.total_minutes_worked += (end_time - last_tr).total_seconds() / 60
        self.daily_minutes_worked[day] = self.daily_minutes_worked.get(day, 0) + (
                end_time - last_tr).total_seconds() / 60


def assign_drivers_to_schedule(bus_schedule):
    drivers_a = []  # Водители типа A
    drivers_b = []  # Водители типа B
    next_driver_a_id = 1
    next_driver_b_id = 1

    for day, routes in bus_schedule:
        for route in routes:
            start_time = route[0]
            end_time = route[1]
            bus_id = route[2]

            # Назначаем водителя типа A (понедельник-пятница)
            if day in range(0, 5):  # Понедельник (0) -> Пятница (4)
                assigned = False
                for driver in drivers_a:
                    if driver.can_take_route(day, start_time, end_time):
                        driver.assign_route(day, bus_id, start_time, end_time)
                        assigned = True
                        break

                if not assigned:
                    new_driver = Driver(next_driver_a_id, "A")

                    if new_driver.can_take_route(day, start_time, end_time):
                        new_driver.assign_route(day, bus_id, start_time, end_time)
                        assigned = True
                        next_driver_a_id += 1
                        drivers_a.append(new_driver)

                if not assigned:
                    for driver in drivers_b:
                        if driver.can_take_route(day, start_time, end_time):
                            driver.assign_route(day, bus_id, start_time, end_time)
                            assigned = True
                            break

                    if not assigned:
                        new_driver = Driver(next_driver_b_id, "B")
                        next_driver_b_id += 1
                        new_driver.assign_route(day, bus_id, start_time, end_time)
                        drivers_b.append(new_driver)

            # Назначаем водителя типа B (раз в три дня)
            elif day in range(5, 7):  # Суббота (5) -> Воскресенье (6)
                assigned = False
                for driver in drivers_b:
                    if driver.can_take_route(day, start_time, end_time):
                        driver.assign_route(day, bus_id, start_time, end_time)
                        assigned = True
                        break

                if not assigned:
                    new_driver = Driver(next_driver_b_id, "B")
                    next_driver_b_id += 1
                    new_driver.assign_route(day, bus_id, start_time, end_time)
                    drivers_b.append(new_driver)

    return drivers_a + drivers_b


# Распределяем водителей по расписанию
drivers = assign_drivers_to_schedule(days)

# Вывод результатов
for driver in drivers:
    print(f"Водитель {driver.id} (Тип {driver.type}):")
    for day, bus_id, start_time, end_time in driver.routes:
        print(f"  День {day}, Автобус {bus_id}: {start_time.time()} - {end_time.time()}")
    print(f"  Всего отработано минут за неделю: {driver.total_minutes_worked}")
    print()

# Сортировка маршрутов по времени отправления внутри каждого дня
sorted_routes = {}
for driver in drivers:
    for route in driver.routes:
        day, bus, start_time, end_time = route
        if day not in sorted_routes:
            sorted_routes[day] = []
        sorted_routes[day].append((start_time, end_time, bus, f'{driver.id} {driver.type}'))

last_hours = []

for day in range(7):
    last_hours_1 = [i for i in sorted_routes[day] if i[0].hour < 6]
    sorted_routes[day] = [i for i in sorted_routes[day] if i not in last_hours_1]
    sorted_routes[day].extend(last_hours)
    last_hours = last_hours_1

# # Сортируем маршруты для каждого дня по времени отправления
for day in range(7):
    sorted_routes[day] = sorted(sorted_routes[day], key=lambda x: x[0].strftime("%H:%M"))

# Подготовка таблиц для каждого дня
daily_tables = {}
for day in sorted_routes:
    daily_table = []
    for start_time, end_time, bus, driver_id in sorted_routes[day]:
        daily_table.append([start_time, end_time, bus, driver_id])
    daily_tables[day] = pd.DataFrame(daily_table,
                                     columns=['Отправление', 'Прибытие', f'А {day}', f'В {day}'])

df = pd.merge(daily_tables[0], daily_tables[1], on=['Отправление', 'Прибытие'], how='right')

for i in range(2, 7):
    df = pd.merge(df, daily_tables[i], on=['Отправление', 'Прибытие'], how='left')

df['Отправление'] = [i.strftime("%H:%M") for i in df['Отправление']]
df['Прибытие'] = [i.strftime("%H:%M") for i in df['Прибытие']]
# Вывод таблицы
print(tabulate(df, headers='keys',tablefmt="grid"))
