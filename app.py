import sys
import time
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QSlider, QLabel, QGroupBox, QGridLayout)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from environment import Environment
from ant import RedAnt, BlackAnt
from colony import Colony
from creatures import CreatureManager
from simulation import Simulation

class PopulationGraph(FigureCanvas):
    """Виджет для отображения графика численности популяций"""
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(PopulationGraph, self).__init__(self.fig)
        self.setParent(parent)
        
        self.red_pop_data = []
        self.black_pop_data = []
        self.peaceful_pop_data = []
        self.predator_pop_data = []
        self.time_data = []
        
        self.setup_plot()
        
    def setup_plot(self):
        """Настройка графика"""
        self.axes.set_title('Динамика популяций')
        self.axes.set_xlabel('Время')
        self.axes.set_ylabel('Количество')
        self.axes.grid(True)
        
        # Создаем пустые линии для данных
        self.red_line, = self.axes.plot([], [], 'r-', label='Красные муравьи')
        self.black_line, = self.axes.plot([], [], 'k-', label='Черные муравьи')
        self.peaceful_line, = self.axes.plot([], [], 'b-', label='Мирные существа')
        self.predator_line, = self.axes.plot([], [], 'm-', label='Хищники')
        
        self.axes.legend(loc='upper right')
        self.fig.tight_layout()
    
    def update_plot(self, sim):
        """Обновление данных графика"""
        max_points = 100  # Ограничим количество точек для производительности
        
        # Добавляем новые данные
        self.red_pop_data.append(len(sim.red_colony.ants))
        self.black_pop_data.append(len(sim.black_colony.ants))
        self.time_data.append(sim.day)
        
        if sim.creature_manager:
            creatures_count = sim.creature_manager.count()
            self.peaceful_pop_data.append(creatures_count['peaceful'])
            self.predator_pop_data.append(creatures_count['predators'])
        else:
            self.peaceful_pop_data.append(0)
            self.predator_pop_data.append(0)
        
        # Ограничиваем количество точек для лучшей производительности
        if len(self.time_data) > max_points:
            step = len(self.time_data) // max_points
            self.time_data = self.time_data[::step]
            self.red_pop_data = self.red_pop_data[::step]
            self.black_pop_data = self.black_pop_data[::step]
            self.peaceful_pop_data = self.peaceful_pop_data[::step]
            self.predator_pop_data = self.predator_pop_data[::step]
        
        # Обновляем данные графика
        self.red_line.set_data(self.time_data, self.red_pop_data)
        self.black_line.set_data(self.time_data, self.black_pop_data)
        self.peaceful_line.set_data(self.time_data, self.peaceful_pop_data)
        self.predator_line.set_data(self.time_data, self.predator_pop_data)
        
        # Устанавливаем диапазон осей
        if self.time_data:
            self.axes.set_xlim(min(self.time_data), max(self.time_data))
            
            all_pop_data = (self.red_pop_data + self.black_pop_data + 
                           self.peaceful_pop_data + self.predator_pop_data)
            if all_pop_data:
                y_max = max(max(all_pop_data, default=0) * 1.1, 10)
                self.axes.set_ylim(0, y_max)
                
        self.fig.canvas.draw_idle()


class SimulationCanvas(QWidget):
    """Виджет для рисования симуляции"""
    
    def __init__(self, parent=None):
        super(SimulationCanvas, self).__init__(parent)
        self.simulation = None
        self.scale_factor = 5  # Масштаб отображения
        
    def set_simulation(self, simulation):
        """Установка симуляции для отображения"""
        self.simulation = simulation
        self.update()
        
    def paintEvent(self, event):
        if not self.simulation:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Отрисовка еды
        for x in range(self.simulation.environment.width):
            for y in range(self.simulation.environment.height):
                food_amount = self.simulation.environment.food_map[x, y]
                if food_amount > 0:
                    # Интенсивность цвета зависит от количества еды
                    color_intensity = min(255, int(food_amount * 10))
                    painter.setBrush(QBrush(QColor(0, color_intensity, 0)))
                    painter.setPen(Qt.NoPen)
                    painter.drawRect(x * self.scale_factor, y * self.scale_factor, 
                                    self.scale_factor, self.scale_factor)
        
        # Отрисовка мирных существ (синий цвет)
        if self.simulation.creature_manager:
            painter.setBrush(QBrush(QColor(0, 0, 255)))
            for creature in self.simulation.creature_manager.peaceful_creatures:
                if creature.alive:
                    painter.drawEllipse(int(creature.position[0] * self.scale_factor),
                                      int(creature.position[1] * self.scale_factor),
                                      int(creature.size * self.scale_factor * 0.8),
                                      int(creature.size * self.scale_factor * 0.8))
            
            # Отрисовка хищников (фиолетовый цвет)
            painter.setBrush(QBrush(QColor(150, 0, 150)))
            for predator in self.simulation.creature_manager.predators:
                if predator.alive:
                    painter.drawEllipse(int(predator.position[0] * self.scale_factor),
                                      int(predator.position[1] * self.scale_factor),
                                      int(predator.size * self.scale_factor),
                                      int(predator.size * self.scale_factor))
        
        # Отрисовка муравьев
        # Красные муравьи
        painter.setBrush(QBrush(QColor(255, 0, 0)))
        for ant in self.simulation.red_colony.ants:
            if ant.alive:
                size = self.scale_factor * 0.8
                painter.drawEllipse(int(ant.position[0] * self.scale_factor),
                                  int(ant.position[1] * self.scale_factor),
                                  int(size), int(size))
        
        # Черные муравьи
        painter.setBrush(QBrush(QColor(0, 0, 0)))
        for ant in self.simulation.black_colony.ants:
            if ant.alive:
                size = self.scale_factor * 0.8
                painter.drawEllipse(int(ant.position[0] * self.scale_factor),
                                  int(ant.position[1] * self.scale_factor),
                                  int(size), int(size))


class StatsPanel(QWidget):
    """Панель для отображения статистики"""
    
    def __init__(self, parent=None):
        super(StatsPanel, self).__init__(parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.day_label = QLabel("День: 0")
        self.red_ants_label = QLabel("Красные муравьи: 0")
        self.black_ants_label = QLabel("Черные муравьи: 0")
        self.peaceful_label = QLabel("Мирные существа: 0")
        self.predator_label = QLabel("Хищники: 0")
        
        self.red_stats_label = QLabel("Красные - статистика")
        self.black_stats_label = QLabel("Черные - статистика")
        
        self.layout.addWidget(self.day_label)
        self.layout.addWidget(self.red_ants_label)
        self.layout.addWidget(self.black_ants_label)
        self.layout.addWidget(self.peaceful_label)
        self.layout.addWidget(self.predator_label)
        self.layout.addWidget(QLabel(""))  # Разделитель
        self.layout.addWidget(self.red_stats_label)
        self.layout.addWidget(self.black_stats_label)
        
        self.layout.addStretch()
    
    def update_stats(self, simulation):
        """Обновление статистики"""
        stats = simulation.get_stats()
        
        self.day_label.setText(f"День: {stats['day']}")
        self.red_ants_label.setText(f"Красные муравьи: {stats['red_ants']}")
        self.black_ants_label.setText(f"Черные муравьи: {stats['black_ants']}")
        
        if 'peaceful_creatures' in stats and 'predators' in stats:
            self.peaceful_label.setText(f"Мирные существа: {stats['peaceful_creatures']}")
            self.predator_label.setText(f"Хищники: {stats['predators']}")
        
        # Форматирование статистики красных муравьев
        red_stats = stats['red_stats']
        red_stats_text = "Красные - статистика:\n"
        red_stats_text += f"Здоровье: {red_stats['health']:.1f}, "
        red_stats_text += f"Урон: {red_stats['damage']:.1f}, "
        red_stats_text += f"Скорость: {red_stats['speed']:.1f}, "
        red_stats_text += f"Плодовитость: {red_stats['fertility']:.3f}, "
        red_stats_text += f"Внимательность: {red_stats['awareness']:.1f}"
        self.red_stats_label.setText(red_stats_text)
        
        # Форматирование статистики черных муравьев
        black_stats = stats['black_stats']
        black_stats_text = "Черные - статистика:\n"
        black_stats_text += f"Здоровье: {black_stats['health']:.1f}, "
        black_stats_text += f"Урон: {black_stats['damage']:.1f}, "
        black_stats_text += f"Скорость: {black_stats['speed']:.1f}, "
        black_stats_text += f"Плодовитость: {black_stats['fertility']:.3f}, "
        black_stats_text += f"Внимательность: {black_stats['awareness']:.1f}"
        self.black_stats_label.setText(black_stats_text)


class SimulationApp(QMainWindow):
    """Главное окно приложения"""

    def __init__(self):
        super(SimulationApp, self).__init__()
        self.setWindowTitle("Симуляция колонии муравьев")
        self.resize(1200, 800)

        # Создаем центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Левая панель управления
        control_panel_widget = QWidget()
        control_panel = QVBoxLayout(control_panel_widget)

        # Кнопки управления
        self.start_button = QPushButton("Старт")
        self.pause_button = QPushButton("Пауза")
        self.restart_button = QPushButton("Перезапустить")
        self.exit_button = QPushButton("Выход")

        # Подключаем кнопки
        self.start_button.clicked.connect(self.start_simulation)
        self.pause_button.clicked.connect(self.toggle_pause)
        self.restart_button.clicked.connect(self.restart_simulation)
        self.exit_button.clicked.connect(self.close)

        # Добавляем кнопки на панель
        control_panel.addWidget(self.start_button)
        control_panel.addWidget(self.pause_button)
        control_panel.addWidget(self.restart_button)
        control_panel.addWidget(QLabel(""))  # Разделитель

        # Ползунок скорости
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("Скорость:"))
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(1)
        self.speed_slider.setMaximum(20)
        self.speed_slider.setValue(10)
        self.speed_slider.valueChanged.connect(self.set_speed)
        self.speed_label = QLabel("1.0x")
        speed_layout.addWidget(self.speed_slider)
        speed_layout.addWidget(self.speed_label)

        # Добавляем ползунок скорости
        control_panel.addLayout(speed_layout)
        control_panel.addWidget(QLabel(""))  # Разделитель

        # Статистика
        self.stats_panel = StatsPanel()
        control_panel.addWidget(self.stats_panel)

        # Инициализация графика
        self.stats_graph = PopulationGraph()  # Инициализируем график
        control_panel.addWidget(self.stats_graph)  # Добавляем график на панель

        # Кнопка выхода в нижней части панели
        control_panel.addStretch()
        control_panel.addWidget(self.exit_button)

        # Правая панель для симуляции и графика
        simulation_panel_widget = QWidget()
        simulation_layout = QVBoxLayout(simulation_panel_widget)

        # Канвас для симуляции
        self.simulation_canvas = SimulationCanvas()
        self.simulation_canvas.setMinimumSize(600, 400)
        simulation_layout.addWidget(self.simulation_canvas)

        # Добавляем панель симуляции на основное окно
        main_layout.addWidget(control_panel_widget)
        main_layout.addWidget(simulation_panel_widget)

    def start_simulation(self):
        """Запуск симуляции"""
        self.simulation_canvas.start()
        self.stats_graph.start()

    def toggle_pause(self):
        """Пауза/возобновление симуляции"""
        if self.simulation_canvas.is_running():
            self.simulation_canvas.pause()
            self.stats_graph.pause()
        else:
            self.simulation_canvas.resume()
            self.stats_graph.resume()

    def restart_simulation(self):
        """Перезапуск симуляции"""
        self.simulation_canvas.restart()
        self.stats_graph.restart()

    def set_speed(self, value):
        """Изменение скорости симуляции"""
        speed = value / 10.0  # Преобразуем значение ползунка в скорость
        self.speed_label.setText(f"{speed:.1f}x")
        self.simulation_canvas.set_speed(speed)
        self.stats_graph.set_speed(speed)
