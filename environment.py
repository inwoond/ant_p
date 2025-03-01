import numpy as np
import random

class Environment:
    """Класс для представления среды симуляции"""
    def __init__(self, width, height, initial_food=500):
        self.width = width
        self.height = height
        self.food_map = np.zeros((width, height))
        self.spawn_food(initial_food)
    
    def spawn_food(self, amount):
        """Размещение еды в среде"""
        # Равномерное распределение еды
        for _ in range(amount):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            self.food_map[x, y] += random.randint(5, 20)
        
        # Создание нескольких "островков" еды с высокой концентрацией
        food_clusters = random.randint(3, 6)
        for _ in range(food_clusters):
            center_x = random.randint(10, self.width - 10)
            center_y = random.randint(10, self.height - 10)
            cluster_radius = random.randint(3, 8)
            cluster_amount = random.randint(50, 150)
            
            for _ in range(cluster_amount):
                # Генерация точек в окружности вокруг центра
                angle = random.uniform(0, 2 * np.pi)
                radius = random.uniform(0, cluster_radius)
                x = int(center_x + radius * np.cos(angle))
                y = int(center_y + radius * np.sin(angle))
                
                # Проверка границ
                if 0 <= x < self.width and 0 <= y < self.height:
                    self.food_map[x, y] += random.randint(10, 30)
    
    def has_food(self, position):
        """Проверка наличия еды в данном месте"""
        x, y = int(position[0]), int(position[1])
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.food_map[x, y] > 0
        return False
    
    def consume_food(self, position):
        """Потребление еды муравьем"""
        x, y = int(position[0]), int(position[1])
        if 0 <= x < self.width and 0 <= y < self.height and self.food_map[x, y] > 0:
            amount = min(10, self.food_map[x, y])
            self.food_map[x, y] -= amount
            return amount
        return 0
    
    def update(self):
        """Обновление состояния среды"""
        # Случайное появление новых источников пищи
        if random.random() < 0.05:  # 5% шанс при каждом обновлении
            # Одиночные источники пищи
            self.spawn_food(random.randint(5, 15))
            
        # Редко появляются большие кластеры еды
        if random.random() < 0.01:  # 1% шанс
            center_x = random.randint(10, self.width - 10)
            center_y = random.randint(10, self.height - 10)
            cluster_radius = random.randint(5, 10)
            cluster_amount = random.randint(80, 200)
            
            for _ in range(cluster_amount):
                angle = random.uniform(0, 2 * np.pi)
                radius = random.uniform(0, cluster_radius)
                x = int(center_x + radius * np.cos(angle))
                y = int(center_y + radius * np.sin(angle))
                
                if 0 <= x < self.width and 0 <= y < self.height:
                    self.food_map[x, y] += random.randint(10, 30)