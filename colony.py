import random

class Colony:
    """Класс для управления колонией муравьев"""
    def __init__(self, ant_type, initial_ants, environment):
        self.ant_type = ant_type
        self.environment = environment
        self.ants = []
        self.next_id = 0
        
        # Создание начальных муравьев с рандомизированными параметрами
        for _ in range(initial_ants):
            position = (random.randint(0, environment.width - 1),
                       random.randint(0, environment.height - 1))
            self.ants.append(ant_type(self.next_ant_id(), position))
    
    def next_ant_id(self):
        """Генерация уникального ID для нового муравья"""
        ant_id = self.next_id
        self.next_id += 1
        return ant_id
    
    def update(self, creature_manager=None):
        """Обновление состояния колонии"""
        # Обновление всех муравьев
        for ant in self.ants:
            ant.update(self.environment, self, creature_manager)
        
        # Удаление мертвых муравьев
        self.ants = [ant for ant in self.ants if ant.alive]
        
        # Размножение
        processed_ants = set()
        new_ants = []
        
        for ant in self.ants:
            if ant.ant_id not in processed_ants and ant.alive and ant.food >= 70:
                mate = ant.find_mate(self)
                if mate and mate.ant_id not in processed_ants:
                    new_ant = ant.reproduce_with_partner(self, mate)
                    if new_ant:
                        new_ants.append(new_ant)
                        processed_ants.add(ant.ant_id)
                        processed_ants.add(mate.ant_id)
        
        self.ants.extend(new_ants)
    
    def move_ants(self):
        """Передвижение всех муравьев колонии"""
        for ant in self.ants:
            ant.move(self.environment)
    
    def attack_enemies(self, enemy_colony):
        """Атака вражеских муравьев"""
        for ant in self.ants:
            # Поиск врагов поблизости
            for enemy in enemy_colony.ants:
                ant.attack(enemy)
    
    def attack_predators(self, creature_manager):
        """Атака хищников"""
        for ant in self.ants:
            for predator in creature_manager.predators:
                ant.attack_predator(predator)
    
    def count(self):
        """Подсчет количества живых муравьев"""
        return len(self.ants)
    
    def get_gender_counts(self):
        """Подсчет количества муравьев каждого пола"""
        males = sum(1 for ant in self.ants if ant.gender == 'male')
        females = sum(1 for ant in self.ants if ant.gender == 'female')
        return {'male': males, 'female': females}
    
    def get_average_stats(self):
        """Получение средних показателей колонии"""
        if not self.ants:
            return {
                'health': 0,
                'damage': 0,
                'speed': 0,
                'fertility': 0,
                'awareness': 0
            }
            
        total_health = sum(ant.health for ant in self.ants)
        total_damage = sum(ant.damage for ant in self.ants)
        total_speed = sum(ant.speed for ant in self.ants)
        total_fertility = sum(ant.fertility for ant in self.ants)
        total_awareness = sum(ant.awareness for ant in self.ants)
        
        count = len(self.ants)
        return {
            'health': total_health / count,
            'damage': total_damage / count,
            'speed': total_speed / count,
            'fertility': total_fertility / count,
            'awareness': total_awareness / count
        }