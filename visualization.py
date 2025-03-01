import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.patches as mpatches

class AntVisualization:
    """Класс для визуализации симуляции муравьев"""
    
    def __init__(self, simulation):
        self.simulation = simulation
        self.environment = simulation.environment
        self.fig, self.ax = plt.subplots(figsize=(10, 8))
        self.fig.canvas.manager.set_window_title('Симуляция колонии муравьев')
        
        # Создание цветовой карты для еды
        cmap_food = LinearSegmentedColormap.from_list('food_cmap', ['white', 'forestgreen'], N=100)
        
        # Инициализация слоев для визуализации
        self.food_layer = self.ax.imshow(
            np.zeros((self.environment.width, self.environment.height)), 
            origin='lower',
            cmap=cmap_food,
            vmin=0,
            vmax=20,
            aspect='equal'
        )
        
        # Инициализация графических объектов для муравьев
        self.red_ants, = self.ax.plot([], [], 'ro', ms=4, label='Красные муравьи')
        self.black_ants, = self.ax.plot([], [], 'ko', ms=4, label='Черные муравьи')
        
        # Статистический текст
        self.stats_text = self.ax.text(
            0.02, 0.98, '', 
            transform=self.ax.transAxes, 
            verticalalignment='top',
            color='blue',
            fontweight='bold',
            bbox=dict(facecolor='white', alpha=0.7)
        )
        
        # Настройка графика
        self.ax.set_title('Симуляция колонии муравьев')
        self.ax.set_xlim(0, self.environment.width)
        self.ax.set_ylim(0, self.environment.height)
        self.ax.legend(loc='upper right')
        
        # Легенда для еды
        food_patch = mpatches.Patch(color='forestgreen', label='Еда')
        handles, labels = self.ax.get_legend_handles_labels()
        handles.append(food_patch)
        self.ax.legend(handles=handles, loc='upper right')
        
        plt.tight_layout()
    
    def init(self):
        """Инициализация анимации"""
        self.red_ants.set_data([], [])
        self.black_ants.set_data([], [])
        self.food_layer.set_array(np.zeros((self.environment.width, self.environment.height)))
        self.stats_text.set_text('')
        return self.red_ants, self.black_ants, self.food_layer, self.stats_text
    
    def update(self, frame):
        """Обновление одного кадра анимации"""
        # Обновление симуляции
        self.simulation.update()
        
        # Обновление позиций муравьев
        red_x = [ant.position[0] for ant in self.simulation.red_colony.ants]
        red_y = [ant.position[1] for ant in self.simulation.red_colony.ants]
        black_x = [ant.position[0] for ant in self.simulation.black_colony.ants]
        black_y = [ant.position[1] for ant in self.simulation.black_colony.ants]
        
        self.red_ants.set_data(red_x, red_y)
        self.black_ants.set_data(black_x, black_y)
        
        # Обновление карты еды
        self.food_layer.set_array(self.environment.food_map.T)  # Транспонируем для правильного отображения
        
        # Обновление текста статистики
        red_count = self.simulation.red_colony.count()
        black_count = self.simulation.black_colony.count()
        
        red_stats = self.simulation.red_colony.get_average_stats()
        black_stats = self.simulation.black_colony.get_average_stats()
        
        stats_text = f"День: {self.simulation.day}\n"
        stats_text += f"Красные: {red_count} | Черные: {black_count}\n"
        if red_count > 0:
            stats_text += f"Красные - Здоровье: {red_stats['health']:.1f} | Урон: {red_stats['damage']:.1f} | "
            stats_text += f"Скорость: {red_stats['speed']:.1f} | Плодов.: {red_stats['fertility']:.2f}\n"
        if black_count > 0:
            stats_text += f"Черные - Здоровье: {black_stats['health']:.1f} | Урон: {black_stats['damage']:.1f} | "
            stats_text += f"Скорость: {black_stats['speed']:.1f} | Плодов.: {black_stats['fertility']:.2f}\n"
        
        self.stats_text.set_text(stats_text)
        
        # Проверка на завершение симуляции
        if red_count == 0 or black_count == 0:
            plt.title(f"Симуляция завершена! День: {self.simulation.day}")
            return self.red_ants, self.black_ants, self.food_layer, self.stats_text
        
        return self.red_ants, self.black_ants, self.food_layer, self.stats_text
    
    def animate(self, frames=500, interval=100):
        """Запуск анимации"""
        self.animation = FuncAnimation(
            self.fig, self.update, frames=frames,
            init_func=self.init, blit=True, interval=interval,
            repeat=False
        )
        plt.show()