import random
import numpy as np

class Ant:
    """Базовый класс муравья"""
    
    def __init__(self, ant_id, position, health=None, damage=None, speed=None, fertility=None, awareness=None, 
                 gender=None):
        self.ant_id = ant_id
        self.position = position
        
        # Рандомизация параметров, если они не заданы
        self.health = health if health is not None else random.uniform(80, 120)
        self.damage = damage if damage is not None else random.uniform(8, 12)
        self.speed = speed if speed is not None else random.uniform(0.8, 1.2)
        self.fertility = fertility if fertility is not None else random.uniform(0.08, 0.12)
        self.awareness = awareness if awareness is not None else random.uniform(4, 6)
        self.gender = gender if gender is not None else random.choice(['male', 'female'])
        
        self.age = 0
        self.food = 100
        self.alive = True
        self.attack_cooldown = 0
        self.reproduction_cooldown = 0
        self.color = "gray"  # Default color
        self.partner = None  # Для размножения
        
    def move(self, environment):
        """Передвижение муравья по среде"""
        if not self.alive:
            return
        
        # Уменьшаем кулдауны
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.reproduction_cooldown > 0:
            self.reproduction_cooldown -= 1
        
        # Случайное направление движения
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]
        direction = random.choice(directions)
        
        new_x = self.position[0] + direction[0] * self.speed
        new_y = self.position[1] + direction[1] * self.speed
        
        # Проверка границ среды
        if 0 <= new_x < environment.width and 0 <= new_y < environment.height:
            self.position = (new_x, new_y)
            self.food -= 1  # Передвижение расходует энергию
        
        # Проверка, не закончилась ли пища
        if self.food <= 0:
            self.alive = False
    
    def attack(self, target):
        """Атака другого существа"""
        if not self.alive or not target.alive or self.attack_cooldown > 0:
            return False
        
        # Расчет расстояния до цели
        distance = np.sqrt((self.position[0] - target.position[0])**2 + 
                         (self.position[1] - target.position[1])**2)
        
        # Атака возможна только если цель в пределах внимательности
        if distance <= self.awareness:
            target.receive_damage(self.damage)
            self.attack_cooldown = 3  # Кулдаун между атаками
            return True
        return False
    
    def receive_damage(self, damage):
        """Получение урона"""
        if not self.alive:
            return
        
        self.health -= damage
        if self.health <= 0:
            self.alive = False
    
    def find_mate(self, colony):
        """Поиск партнера для размножения"""
        if not self.alive or self.food < 70 or self.reproduction_cooldown > 0:
            return None
        
        potential_mates = [
            ant for ant in colony.ants 
            if ant.alive and ant != self and ant.gender != self.gender and 
            ant.food >= 70 and ant.reproduction_cooldown <= 0
        ]
        
        for mate in potential_mates:
            # Проверяем расстояние до потенциального партнера
            distance = np.sqrt((self.position[0] - mate.position[0])**2 + 
                            (self.position[1] - mate.position[1])**2)
            
            if distance <= 2:  # Партнеры должны быть рядом
                return mate
        
        return None
    
    def reproduce_with_partner(self, colony, partner):
        """Размножение с партнером"""
        if not self.alive or not partner.alive or self.reproduction_cooldown > 0 or partner.reproduction_cooldown > 0:
            return None
            
        # Проверяем, что у обоих достаточно еды
        if self.food < 70 or partner.food < 70:
            return None
        
        # Расходуем еду
        self.food -= 50
        partner.food -= 50
        
        # Устанавливаем кулдаун размножения
        self.reproduction_cooldown = 15
        partner.reproduction_cooldown = 15
        
        # Наследование и мутация параметров от обоих родителей
        # Для каждого параметра: случайное значение между параметрами родителей с мутацией
        health = self._mutate_parameter((self.health + partner.health) / 2)
        damage = self._mutate_parameter((self.damage + partner.damage) / 2)
        speed = self._mutate_parameter((self.speed + partner.speed) / 2)
        fertility = self._mutate_parameter((self.fertility + partner.fertility) / 2)
        awareness = self._mutate_parameter((self.awareness + partner.awareness) / 2)
        
        # Определение случайного пола потомка
        gender = random.choice(['male', 'female'])
        
        # Новая позиция рядом с родителями
        new_position = (
            max(0, min(colony.environment.width - 1, 
                      (self.position[0] + partner.position[0]) / 2 + random.randint(-2, 2))),
            max(0, min(colony.environment.height - 1, 
                      (self.position[1] + partner.position[1]) / 2 + random.randint(-2, 2)))
        )
        
        # Создаем муравья того же типа, что и первый родитель (определяет колонию)
        return type(self)(colony.next_ant_id(), new_position, health, damage, speed, fertility, awareness, gender)
    
    def _mutate_parameter(self, value):
        """Мутация параметра с небольшой вероятностью"""
        mutation_chance = 0.2  # 20% шанс мутации
        mutation_range = 0.2   # ±20% от исходного значения
        
        if random.random() < mutation_chance:
            return value * random.uniform(1.0 - mutation_range, 1.0 + mutation_range)
        return value
    
    def find_food(self, environment):
        """Поиск пищи в среде"""
        if not self.alive:
            return
        
        # Если муравей находит пищу, он получает энергию
        if environment.has_food(self.position):
            food_amount = environment.consume_food(self.position)
            self.food += food_amount
    
    def find_and_eat_peaceful_creature(self, creature_manager):
        """Поиск и поедание мирных существ"""
        if not self.alive or self.attack_cooldown > 0:
            return False
            
        for creature in creature_manager.peaceful_creatures:
            if not creature.alive:
                continue
                
            distance = np.sqrt((self.position[0] - creature.position[0])**2 + 
                             (self.position[1] - creature.position[1])**2)
            
            if distance <= self.awareness:
                # Атака существа
                creature.receive_damage(self.damage)
                self.attack_cooldown = 3
                
                # Если существо умерло от этой атаки, получаем пищу
                if not creature.alive:
                    self.food += 30 * creature.size  # Получаем еду пропорционально размеру существа
                return True
        return False
    
    def attack_predator(self, predator):
        """Атака хищника"""
        if not self.alive or not predator.alive or self.attack_cooldown > 0:
            return False
            
        distance = np.sqrt((self.position[0] - predator.position[0])**2 + 
                         (self.position[1] - predator.position[1])**2)
        
        if distance <= self.awareness:
            predator.receive_damage(self.damage)
            self.attack_cooldown = 3
            return True
        return False
    
    def update(self, environment, colony, creature_manager=None):
        """Обновление состояния муравья"""
        if not self.alive:
            return
        
        self.age += 1
        self.food -= 0.5  # Существование расходует энергию
        
        # Старение влияет на здоровье
        if self.age > 100:
            self.health -= 0.5
        
        # Смерть, если закончилось здоровье или пища
        if self.health <= 0 or self.food <= 0:
            self.alive = False
            return
            
        # Поиск пищи
        self.find_food(environment)
        
        # Поиск и поедание мирных существ, если они есть
        if creature_manager:
            self.find_and_eat_peaceful_creature(creature_manager)


class RedAnt(Ant):
    """Красные муравьи - специализируются на атаке и скорости"""

    def __init__(self, ant_id, position, health=None, damage=None, speed=None, fertility=None, awareness=None, gender=None):
        base_health = random.uniform(90, 110) if health is None else health
        base_damage = random.uniform(11, 13) if damage is None else damage
        base_speed = random.uniform(1.1, 1.3) if speed is None else speed
        base_fertility = random.uniform(0.11, 0.13) if fertility is None else fertility
        base_awareness = random.uniform(3, 5) if awareness is None else awareness
        
        super().__init__(ant_id, position, base_health, base_damage, base_speed, base_fertility, base_awareness, gender)
        self.color = "red"



class BlackAnt(Ant):
    """Черные муравьи - специализируются на здоровье и внимательности"""

    def __init__(self, ant_id, position, health=None, damage=None, speed=None, fertility=None, awareness=None, gender=None):
        base_health = random.uniform(110, 130) if health is None else health
        base_damage = random.uniform(9, 11) if damage is None else damage
        base_speed = random.uniform(0.8, 1.0) if speed is None else speed
        base_fertility = random.uniform(0.09, 0.11) if fertility is None else fertility
        base_awareness = random.uniform(5, 7) if awareness is None else awareness
        
        super().__init__(ant_id, position, base_health, base_damage, base_speed, base_fertility, base_awareness, gender)
        self.color = "black"