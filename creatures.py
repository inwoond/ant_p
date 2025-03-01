import random
import numpy as np

class Creature:
    """Базовый класс для существ в симуляции"""
    
    def __init__(self, creature_id, position, health=100, damage=0, speed=1, size=1):
        self.creature_id = creature_id
        self.position = position
        self.health = health
        self.damage = damage
        self.speed = speed
        self.size = size  # Размер существа (влияет на количество еды)
        self.alive = True
        self.age = 0
    
    def move(self, environment):
        """Передвижение существа по среде"""
        if not self.alive:
            return
            
        # Случайное направление движения
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]
        direction = random.choice(directions)
        
        new_x = self.position[0] + direction[0] * self.speed
        new_y = self.position[1] + direction[1] * self.speed
        
        # Проверка границ среды
        if 0 <= new_x < environment.width and 0 <= new_y < environment.height:
            self.position = (new_x, new_y)
    
    def receive_damage(self, damage):
        """Получение урона"""
        if not self.alive:
            return
            
        self.health -= damage
        if self.health <= 0:
            self.alive = False
    
    def update(self, environment):
        """Обновление состояния существа"""
        if not self.alive:
            return
            
        self.age += 1
        
        # Естественное старение
        if self.age > 100:
            self.health -= 0.2


class PeacefulCreature(Creature):
    """Мирное существо, служащее пищей для муравьев"""
    
    def __init__(self, creature_id, position, health=50, speed=0.8, size=3):
        super().__init__(creature_id, position, health=health, damage=0, speed=speed, size=size)
        self.color = "blue"
        self.reproduction_rate = 0.02  # 2% шанс размножения при каждом обновлении
    
    def reproduce(self, environment, creature_manager):
        """Размножение мирных существ"""
        if not self.alive or self.age < 20:  # Только взрослые могут размножаться
            return None
            
        if random.random() < self.reproduction_rate:
            # Определение нового положения рядом с родителем
            new_position = (
                max(0, min(environment.width - 1, self.position[0] + random.randint(-3, 3))),
                max(0, min(environment.height - 1, self.position[1] + random.randint(-3, 3)))
            )
            
            health = self.health * random.uniform(0.9, 1.1)
            speed = self.speed * random.uniform(0.9, 1.1)
            size = self.size * random.uniform(0.9, 1.1)
            
            return PeacefulCreature(creature_manager.next_creature_id(), new_position, health, speed, size)
        return None


class Predator(Creature):
    """Хищник, который охотится на муравьев"""
    
    def __init__(self, creature_id, position, health=300, damage=50, speed=1.5, size=5):
        super().__init__(creature_id, position, health=health, damage=damage, speed=speed, size=size)
        self.color = "purple"
        self.awareness = 15  # Радиус обнаружения добычи
        self.hunt_cooldown = 0
        self.reproduction_rate = 0.01  # 1% шанс размножения
    
    def move(self, environment, red_ants=None, black_ants=None):
        """Передвижение хищника с охотой на муравьев"""
        if not self.alive:
            return
            
        if self.hunt_cooldown > 0:
            self.hunt_cooldown -= 1
        
        # Проверка наличия муравьев поблизости для охоты
        target = None
        target_distance = float('inf')
        
        # Проверяем красных муравьев
        if red_ants:
            for ant in red_ants:
                if not ant.alive:
                    continue
                dist = np.sqrt((self.position[0] - ant.position[0])**2 + (self.position[1] - ant.position[1])**2)
                if dist < self.awareness and dist < target_distance:
                    target = ant
                    target_distance = dist
        
        # Проверяем черных муравьев
        if black_ants:
            for ant in black_ants:
                if not ant.alive:
                    continue
                dist = np.sqrt((self.position[0] - ant.position[0])**2 + (self.position[1] - ant.position[1])**2)
                if dist < self.awareness and dist < target_distance:
                    target = ant
                    target_distance = dist
        
        # Если есть цель, двигаемся к ней
        if target and target.alive:
            direction_x = target.position[0] - self.position[0]
            direction_y = target.position[1] - self.position[1]
            
            # Нормализуем направление
            length = max(0.1, np.sqrt(direction_x**2 + direction_y**2))
            direction_x /= length
            direction_y /= length
            
            new_x = self.position[0] + direction_x * self.speed
            new_y = self.position[1] + direction_y * self.speed
            
            # Проверка границ среды
            new_x = max(0, min(environment.width - 1, new_x))
            new_y = max(0, min(environment.height - 1, new_y))
            
            self.position = (new_x, new_y)
            
            # Атакуем, если мы достаточно близко
            if target_distance < 1.5:
                if self.hunt_cooldown == 0:
                    target.receive_damage(self.damage)
                    self.hunt_cooldown = 5  # Кулдаун между атаками
        else:
            # Случайное движение, если нет цели
            super().move(environment)
    
    def reproduce(self, environment, creature_manager):
        """Размножение хищников"""
        if not self.alive or self.health < 200 or self.age < 50:  # Только здоровые и взрослые
            return None
            
        if random.random() < self.reproduction_rate:
            # Определение нового положения рядом с родителем
            new_position = (
                max(0, min(environment.width - 1, self.position[0] + random.randint(-3, 3))),
                max(0, min(environment.height - 1, self.position[1] + random.randint(-3, 3)))
            )
            
            health = self.health * random.uniform(0.9, 1.1)
            damage = self.damage * random.uniform(0.9, 1.1)
            speed = self.speed * random.uniform(0.9, 1.1)
            size = self.size * random.uniform(0.9, 1.1)
            
            return Predator(creature_manager.next_creature_id(), new_position, health, damage, speed, size)
        return None


class CreatureManager:
    """Класс для управления различными существами в симуляции"""
    
    def __init__(self, environment):
        self.environment = environment
        self.peaceful_creatures = []
        self.predators = []
        self.next_id = 0
    
    def next_creature_id(self):
        """Генерация уникального ID для нового существа"""
        creature_id = self.next_id
        self.next_id += 1
        return creature_id
    
    def add_peaceful_creatures(self, count):
        """Добавление мирных существ в симуляцию"""
        for _ in range(count):
            position = (random.randint(0, self.environment.width - 1),
                       random.randint(0, self.environment.height - 1))
            self.peaceful_creatures.append(PeacefulCreature(self.next_creature_id(), position))
    
    def add_predators(self, count):
        """Добавление хищников в симуляцию"""
        for _ in range(count):
            position = (random.randint(0, self.environment.width - 1),
                       random.randint(0, self.environment.height - 1))
            self.predators.append(Predator(self.next_creature_id(), position))
    
    def update(self, red_ants=None, black_ants=None):
        """Обновление всех существ"""
        # Обновление мирных существ
        for creature in self.peaceful_creatures:
            creature.update(self.environment)
            creature.move(self.environment)
        
        # Размножение мирных существ
        new_peaceful = []
        for creature in self.peaceful_creatures:
            new_creature = creature.reproduce(self.environment, self)
            if new_creature:
                new_peaceful.append(new_creature)
        
        self.peaceful_creatures.extend(new_peaceful)
        
        # Обновление хищников
        for predator in self.predators:
            predator.update(self.environment)
            predator.move(self.environment, red_ants, black_ants)
        
        # Размножение хищников
        new_predators = []
        for predator in self.predators:
            new_predator = predator.reproduce(self.environment, self)
            if new_predator:
                new_predators.append(new_predator)
        
        self.predators.extend(new_predators)
        
        # Удаление мертвых существ
        self.peaceful_creatures = [c for c in self.peaceful_creatures if c.alive]
        self.predators = [p for p in self.predators if p.alive]
    
    def count(self):
        """Подсчет количества существ каждого типа"""
        return {
            'peaceful': len(self.peaceful_creatures),
            'predators': len(self.predators)
        }