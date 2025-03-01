import time
from environment import Environment
from ant import RedAnt, BlackAnt
from colony import Colony
from simulation import Simulation
from visualization import AntVisualization
import matplotlib.pyplot as plt

def run_with_visualization():
    # Параметры симуляции
    width, height = 100, 100
    initial_red_ants = 30
    initial_black_ants = 30
    
    # Создаем среду
    environment = Environment(width, height, initial_food=800)
    
    # Создаем колонии муравьев
    red_colony = Colony(RedAnt, initial_red_ants, environment)
    black_colony = Colony(BlackAnt, initial_black_ants, environment)
    
    # Создаем симуляцию
    simulation = Simulation(environment, red_colony, black_colony)
    
    # Создаем и запускаем визуализацию
    print("Запуск визуализации симуляции муравьев...")
    viz = AntVisualization(simulation)
    viz.animate(frames=500, interval=100)  # 500 дней, обновление каждые 100 мс

def run_without_visualization():
    # Параметры симуляции
    width, height = 100, 100
    initial_red_ants = 50
    initial_black_ants = 50
    days_to_simulate = 200
    
    # Создаем среду
    environment = Environment(width, height, initial_food=1000)
    
    # Создаем колонии муравьев
    red_colony = Colony(RedAnt, initial_red_ants, environment)
    black_colony = Colony(BlackAnt, initial_black_ants, environment)
    
    # Создаем симуляцию
    simulation = Simulation(environment, red_colony, black_colony)
    
    # Запускаем симуляцию
    print(f"Запуск симуляции на {days_to_simulate} дней...")
    start_time = time.time()
    
    simulation.run(days_to_simulate)
    
    end_time = time.time()
    print(f"Симуляция завершена за {end_time - start_time:.2f} секунд.")
    
    # Вывод финальной статистики
    print("\nРезультаты симуляции:")
    print(f"Выжившие красные муравьи: {red_colony.count()}")
    print(f"Выжившие черные муравьи: {black_colony.count()}")
    
    # Анализ эволюции параметров
    if red_colony.count() > 0:
        print("\nФинальные параметры красных муравьев:")
        red_stats = red_colony.get_average_stats()
        for key, value in red_stats.items():
            print(f"Средний {key}: {value:.2f}")
            
    if black_colony.count() > 0:
        print("\nФинальные параметры черных муравьев:")
        black_stats = black_colony.get_average_stats()
        for key, value in black_stats.items():
            print(f"Средний {key}: {value:.2f}")
    
    # Визуализация результатов
    simulation.visualize_population_history()
    simulation.visualize_attributes_evolution()
    simulation.visualize_current_state()
    
    # Определение победителя
    if red_colony.count() > black_colony.count():
        print("\nПобедили красные муравьи!")
    elif black_colony.count() > red_colony.count():
        print("\nПобедили черные муравьи!")
    else:
        print("\nНичья!")

def main():
    visualization_mode = input("Запустить с визуализацией в реальном времени? (y/n): ").lower().strip()
    
    if visualization_mode == 'y':
        run_with_visualization()
    else:
        run_without_visualization()

if __name__ == "__main__":
    main()