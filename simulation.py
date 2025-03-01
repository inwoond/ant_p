class Simulation:
    """Класс для управления симуляцией"""
    def __init__(self, environment, red_colony, black_colony, creature_manager=None):
        self.environment = environment
        self.red_colony = red_colony
        self.black_colony = black_colony
        self.creature_manager = creature_manager
        self.day = 0
        self.paused = False
        self.speed = 1.0  # Множитель скорости симуляции
        
        # История популяций
        self.red_population_history = []
        self.black_population_history = []
        self.peaceful_creatures_history = []
        self.predator_history = []
        
        # История статистик
        self.red_stats_history = []
        self.black_stats_history = []
    
    def update(self):
        """Обновление симуляции на один шаг"""
        if self.paused:
            return
            
        # Обновление среды
        self.environment.update()
        
        # Передвижение муравьев
        self.red_colony.move_ants()
        self.black_colony.move_ants()
        
        # Атаки муравьев
        self.red_colony.attack_enemies(self.black_colony)
        self.black_colony.attack_enemies(self.red_colony)
        
        # Обновление существ и взаимодействие с муравьями
        if self.creature_manager:
            self.creature_manager.update(self.red_colony.ants, self.black_colony.ants)
            
            # Муравьи атакуют хищников
            self.red_colony.attack_predators(self.creature_manager)
            self.black_colony.attack_predators(self.creature_manager)
        
        # Обновление колоний (размножение, смерть и т.д.)
        self.red_colony.update(self.creature_manager)
        self.black_colony.update(self.creature_manager)
        
        # Сохранение истории популяций
        self.red_population_history.append(self.red_colony.count())
        self.black_population_history.append(self.black_colony.count())
        
        if self.creature_manager:
            creatures_count = self.creature_manager.count()
            self.peaceful_creatures_history.append(creatures_count['peaceful'])
            self.predator_history.append(creatures_count['predators'])
        
        # Сохранение истории характеристик
        self.red_stats_history.append(self.red_colony.get_average_stats())
        self.black_stats_history.append(self.black_colony.get_average_stats())
        
        self.day += 1
    
    def toggle_pause(self):
        """Переключение паузы симуляции"""
        self.paused = not self.paused
        return self.paused
    
    def set_speed(self, speed):
        """Установка скорости симуляции"""
        self.speed = max(0.1, min(10.0, speed))
        return self.speed
    
    def get_stats(self):
        """Получение текущей статистики симуляции"""
        stats = {
            'day': self.day,
            'red_ants': self.red_colony.count(),
            'black_ants': self.black_colony.count(),
            'red_stats': self.red_colony.get_average_stats(),
            'black_stats': self.black_colony.get_average_stats()
        }
        
        if self.creature_manager:
            creatures_count = self.creature_manager.count()
            stats['peaceful_creatures'] = creatures_count['peaceful']
            stats['predators'] = creatures_count['predators']
        
        return stats