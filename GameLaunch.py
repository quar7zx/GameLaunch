import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import subprocess
import time
from datetime import datetime, timedelta
import threading
import sys
import math
import winreg
import webbrowser


class UltraSmoothLaunchGame:
    def __init__(self, root):
        self.root = root
        self.root.title("LaunchGame")
        self.root.geometry("1300x850")
        self.root.minsize(1100, 700)

        # Настройка плавной анимации окна
        self.root.withdraw()  # Скрываем окно до полной загрузки

        # Современные цвета с плавными градиентами
        self.setup_smooth_colors()

        # Инициализация
        self.data_file = "games.json"
        self.games = []
        self.running_games = {}
        self.selected_game_id = None

        # Steam
        self.steam_path = self.find_steam_path()
        self.steam_apps = {}

        # Загрузка данных
        self.load_games_data()
        self.load_steam_library()

        # Создание интерфейса
        self.create_ultra_smooth_interface()

        # Плавное появление окна
        self.root.after(100, self.animate_window_appear)

        # Запуск анимаций
        self.start_animations()
        self.update_timer()

    def find_steam_path(self):
        """Найти путь к Steam"""
        steam_paths = []

        common_paths = [
            os.path.join(os.environ.get('ProgramFiles(x86)', ''), 'Steam'),
            os.path.join(os.environ.get('ProgramFiles', ''), 'Steam'),
            os.path.expanduser('~\\Steam'),
            'C:\\Steam'
        ]

        for path in common_paths:
            if os.path.exists(path):
                steam_paths.append(path)

        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                 r"Software\Valve\Steam")
            reg_path = winreg.QueryValueEx(key, "SteamPath")[0]
            if os.path.exists(reg_path):
                steam_paths.append(reg_path)
        except:
            pass

        return steam_paths[0] if steam_paths else None

    def load_steam_library(self):
        """Загрузить библиотеку Steam игр"""
        if not self.steam_path:
            return

        library_file = os.path.join(self.steam_path, 'steamapps', 'libraryfolders.vdf')

        if os.path.exists(library_file):
            try:
                with open(library_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    import re
                    paths = re.findall(r'"path"\s+"([^"]+)"', content)

                    for path in paths:
                        path = path.replace('\\\\', '\\')
                        apps_path = os.path.join(path, 'steamapps')

                        if os.path.exists(apps_path):
                            for file in os.listdir(apps_path):
                                if file.endswith('.acf'):
                                    acf_path = os.path.join(apps_path, file)
                                    try:
                                        with open(acf_path, 'r', encoding='utf-8') as acf:
                                            acf_content = acf.read()
                                            name_match = re.search(r'"name"\s+"([^"]+)"', acf_content)
                                            appid_match = re.search(r'"appid"\s+"(\d+)"', acf_content)
                                            installdir_match = re.search(r'"installdir"\s+"([^"]+)"', acf_content)

                                            if name_match and appid_match and installdir_match:
                                                app_id = appid_match.group(1)
                                                game_name = name_match.group(1)
                                                install_dir = installdir_match.group(1)
                                                game_path = os.path.join(path, 'steamapps', 'common', install_dir)

                                                if os.path.exists(game_path):
                                                    exe_files = []
                                                    for root, dirs, files in os.walk(game_path):
                                                        for file in files:
                                                            if file.lower().endswith('.exe'):
                                                                if not any(x in file.lower() for x in
                                                                           ['uninstall', 'install', 'setup',
                                                                            'launcher']):
                                                                    exe_path = os.path.join(root, file)
                                                                    exe_files.append(exe_path)

                                                    if exe_files:
                                                        self.steam_apps[app_id] = {
                                                            'name': game_name,
                                                            'exe_path': exe_files[0],
                                                            'steam_id': app_id,
                                                            'game_path': game_path,
                                                            'is_steam': True
                                                        }
                                    except:
                                        continue
            except:
                pass

    def setup_smooth_colors(self):
        """Настройка красивой цветовой палитры"""
        self.colors = {
            # Основные цвета фона с градиентом
            'bg_dark': '#0f0f1a',
            'bg_darker': '#0a0a14',
            'bg_darkest': '#05050a',
            'bg_card': '#1a1a2e',
            'bg_card_hover': '#22223b',
            'bg_card_selected': '#2d2d44',

            # Акцентные цвета (современная пастель)
            'primary': '#6d72c3',  # Мягкий фиолетовый
            'primary_light': '#8d92e3',
            'primary_dark': '#5a5faa',
            'secondary': '#54c6c1',  # Бирюзовый
            'secondary_light': '#74e6e1',
            'accent': '#ff8ba7',  # Нежно-розовый
            'accent_light': '#ffabbd',
            'success': '#50c878',  # Изумрудный
            'warning': '#ffb347',  # Персиковый
            'danger': '#ff6b6b',  # Коралловый
            'info': '#6495ed',  # Васильковый

            # Текст
            'text': '#f5f5f7',
            'text_secondary': '#c7c7d1',
            'text_muted': '#8a8a9a',
            'text_dark': '#3a3a4a',

            # Градиенты
            'gradient_start': '#1a1a2e',
            'gradient_end': '#16213e',

            # Специальные
            'steam_color': '#1b2838',
            'steam_light': '#2a3f5f',
        }

        # Устанавливаем цвет фона
        self.root.configure(bg=self.colors['bg_dark'])

    def create_ultra_smooth_interface(self):
        """Создание ультра-плавного интерфейса"""
        # Главный контейнер с градиентом
        self.main_container = tk.Frame(self.root, bg=self.colors['bg_dark'])
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Верхняя панель с градиентом
        self.create_gradient_header()

        # Основное содержимое
        self.create_main_content()

        # Нижний статус бар
        self.create_status_bar()

    def create_gradient_header(self):
        """Создание верхней панели с градиентом"""
        header = tk.Frame(self.main_container, bg=self.colors['bg_dark'], height=140)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        # Градиентный фон
        gradient_canvas = tk.Canvas(header, bg=self.colors['bg_dark'],
                                    highlightthickness=0, height=140)
        gradient_canvas.pack(fill=tk.BOTH, expand=True)

        # Заполняем canvas градиентом
        width = self.root.winfo_screenwidth()
        gradient_canvas.create_rectangle(0, 0, width, 140,
                                         fill=self.colors['primary_dark'], outline='')

        # Логотип и название
        logo_frame = tk.Frame(gradient_canvas, bg=self.colors['primary_dark'])
        logo_frame.place(relx=0.05, rely=0.5, anchor='w')

        self.logo_label = tk.Label(logo_frame, text="🚀",
                                   font=("Arial", 48, "bold"),
                                   bg=self.colors['primary_dark'],
                                   fg=self.colors['primary_light'])
        self.logo_label.pack(side=tk.LEFT)

        name_frame = tk.Frame(logo_frame, bg=self.colors['primary_dark'])
        name_frame.pack(side=tk.LEFT, padx=(15, 0))

        # Исправлено: теперь "LaunchGame"
        tk.Label(name_frame, text="LaunchGame",
                 font=("Segoe UI", 32, "bold"),
                 bg=self.colors['primary_dark'],
                 fg=self.colors['text']).pack(anchor='w')

        # Статистика в заголовке
        self.header_stats = tk.Label(gradient_canvas,
                                     text="🕹️ 0 игр | ⏱️ 0ч | 🔥 0 активных",
                                     font=("Segoe UI", 11, "bold"),
                                     bg=self.colors['primary_dark'],
                                     fg=self.colors['text'],
                                     padx=20, pady=10)
        self.header_stats.place(relx=0.95, rely=0.5, anchor='e')

        # Кнопки действий
        self.create_header_buttons(gradient_canvas)

    def create_header_buttons(self, canvas):
        """Создание плавных кнопок в заголовке"""
        btn_frame = tk.Frame(canvas, bg=self.colors['primary_dark'])
        btn_frame.place(relx=0.5, rely=0.8, anchor='center')

        buttons = [
            ("➕ Добавить игру", self.add_game_dialog, self.colors['primary']),
            ("🎮 Steam игры", self.find_steam_games, self.colors['steam_color']),
            ("⚡ Быстрый запуск", self.quick_launch, self.colors['accent']),
            ("⚙️ Настройки", self.show_settings, self.colors['secondary']),
        ]

        for text, command, color in buttons:
            btn = tk.Button(btn_frame, text=text, command=command,
                            font=('Segoe UI', 10, 'bold'),
                            relief='flat',
                            padx=20, pady=10,
                            cursor='hand2',
                            bd=0,
                            highlightthickness=0)

            # Плавные цвета кнопок
            btn.config(bg=color, fg='white',
                       activebackground=self.lighten_color(color, 20),
                       activeforeground='white')

            btn.pack(side=tk.LEFT, padx=8)

            # Эффект при наведении
            btn.bind("<Enter>", lambda e, b=btn, c=color:
            self.animate_button_hover(b, c, True))
            btn.bind("<Leave>", lambda e, b=btn, c=color:
            self.animate_button_hover(b, c, False))

    def create_main_content(self):
        """Создание основного контента с плавными вкладками"""
        content_frame = tk.Frame(self.main_container, bg=self.colors['bg_dark'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Кастомные вкладки
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Стилизация вкладок
        style = ttk.Style()
        style.theme_use('clam')

        style.configure('TNotebook', background=self.colors['bg_dark'], borderwidth=0)
        style.configure('TNotebook.Tab',
                        background=self.colors['bg_card'],
                        foreground=self.colors['text_secondary'],
                        padding=[20, 10],
                        font=('Segoe UI', 11))
        style.map('TNotebook.Tab',
                  background=[('selected', self.colors['primary'])],
                  foreground=[('selected', 'white')])

        # Создаем вкладки
        self.games_frame = self.create_games_tab()
        self.notebook.add(self.games_frame, text="    🎮  МОИ ИГРЫ    ")

        self.stats_frame = self.create_stats_tab()
        self.notebook.add(self.stats_frame, text="    📊  СТАТИСТИКА    ")

        self.steam_frame = self.create_steam_tab()
        self.notebook.add(self.steam_frame, text="    ⚙️  STEAM    ")

        self.load_games_ui()

    def create_games_tab(self):
        """Создание вкладки с играми"""
        frame = tk.Frame(self.notebook, bg=self.colors['bg_darker'])

        # Двухпанельный интерфейс
        paned = tk.PanedWindow(frame, orient=tk.HORIZONTAL,
                               bg=self.colors['bg_darker'],
                               sashwidth=3, sashrelief='flat')
        paned.pack(fill=tk.BOTH, expand=True)

        # Левая панель - список игр
        left_panel = tk.Frame(paned, bg=self.colors['bg_darker'])

        # Поиск с иконкой
        search_frame = tk.Frame(left_panel, bg=self.colors['bg_darker'],
                                padx=15, pady=15)
        search_frame.pack(fill=tk.X)

        search_container = tk.Frame(search_frame, bg=self.colors['bg_card'],
                                    relief='flat', borderwidth=0)
        search_container.pack(fill=tk.X, padx=5, pady=5)

        search_icon = tk.Label(search_container, text="🔍",
                               font=('Segoe UI', 14),
                               bg=self.colors['bg_card'],
                               fg=self.colors['primary'],
                               padx=15)
        search_icon.pack(side=tk.LEFT)

        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_container,
                                     textvariable=self.search_var,
                                     font=('Segoe UI', 11),
                                     bg=self.colors['bg_card'],
                                     fg=self.colors['text'],
                                     insertbackground=self.colors['primary'],
                                     relief='flat',
                                     bd=0)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True,
                               padx=(0, 15), pady=15, ipady=4)
        self.search_entry.insert(0, "Поиск игр...")
        self.search_entry.bind('<FocusIn>', self.on_search_focus_in)
        self.search_entry.bind('<FocusOut>', self.on_search_focus_out)
        self.search_entry.bind('<KeyRelease>', self.filter_games)

        # Прокручиваемый список игр
        list_container = tk.Frame(left_panel, bg=self.colors['bg_darker'])
        list_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

        self.games_canvas = tk.Canvas(list_container,
                                      bg=self.colors['bg_darker'],
                                      highlightthickness=0)

        self.scrollable_frame = tk.Frame(self.games_canvas,
                                         bg=self.colors['bg_darker'])

        scrollbar = ttk.Scrollbar(list_container, orient="vertical",
                                  command=self.games_canvas.yview)
        self.games_canvas.configure(yscrollcommand=scrollbar.set)

        self.games_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.games_canvas.create_window((0, 0), window=self.scrollable_frame,
                                        anchor="nw", width=self.games_canvas.winfo_reqwidth())

        self.scrollable_frame.bind("<Configure>",
                                   lambda e: self.games_canvas.configure(
                                       scrollregion=self.games_canvas.bbox("all")
                                   ))

        paned.add(left_panel, minsize=400)

        # Правая панель - детали игры
        right_panel = tk.Frame(paned, bg=self.colors['bg_darker'])
        self.setup_game_info_panel(right_panel)
        paned.add(right_panel, minsize=400)

        return frame

    def setup_game_info_panel(self, parent):
        """Настройка панели информации об игре"""
        main_card = tk.Frame(parent, bg=self.colors['bg_card'],
                             relief='flat', padx=0, pady=0)
        main_card.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Верхняя часть с градиентом
        header_gradient = tk.Frame(main_card, bg=self.colors['primary'],
                                   height=80)
        header_gradient.pack(fill=tk.X)

        tk.Label(header_gradient,
                 text="🎯 ВЫБРАННАЯ ИГРА",
                 font=('Segoe UI', 16, 'bold'),
                 bg=self.colors['primary'],
                 fg='white').pack(expand=True)

        # Контент
        content = tk.Frame(main_card, bg=self.colors['bg_card'],
                           padx=25, pady=25)
        content.pack(fill=tk.BOTH, expand=True)

        # Иконка игры (анимированная)
        self.game_icon_frame = tk.Frame(content, bg=self.colors['bg_card'])
        self.game_icon_frame.pack(pady=(0, 20))

        self.game_icon = tk.Label(self.game_icon_frame, text="🕹️",
                                  font=('Segoe UI', 72),
                                  bg=self.colors['bg_card'],
                                  fg=self.colors['primary_light'])
        self.game_icon.pack()

        # Название
        self.game_name_label = tk.Label(content,
                                        text="Выберите игру",
                                        font=('Segoe UI', 22, 'bold'),
                                        bg=self.colors['bg_card'],
                                        fg=self.colors['text'],
                                        wraplength=320,
                                        justify='center')
        self.game_name_label.pack(pady=(0, 30))

        # Информация в карточках
        self.game_info_labels = {}
        info_items = [
            ("⏱️", "Время игры:", "time", "0 часов", self.colors['secondary']),
            ("📊", "Сессий:", "sessions", "0", self.colors['primary']),
            ("📅", "Последний запуск:", "last_played", "Никогда", self.colors['accent']),
            ("🎮", "Тип:", "game_type", "Неизвестно", self.colors['warning'])
        ]

        for icon, title, key, default, color in info_items:
            card = self.create_info_card(content, icon, title, default, color)
            card.pack(fill=tk.X, pady=8)
            self.game_info_labels[key] = card.winfo_children()[-1].winfo_children()[-1]

        # Кнопки действий
        btn_container = tk.Frame(content, bg=self.colors['bg_card'])
        btn_container.pack(fill=tk.X, pady=(20, 0))

        self.launch_btn = self.create_action_button(btn_container,
                                                    "🚀 ЗАПУСТИТЬ",
                                                    self.colors['success'],
                                                    tk.DISABLED)
        self.launch_btn.pack(fill=tk.X, pady=(0, 10))

        self.remove_btn = self.create_action_button(btn_container,
                                                    "🗑️ УДАЛИТЬ",
                                                    self.colors['danger'],
                                                    tk.DISABLED)
        self.remove_btn.pack(fill=tk.X)

    def create_info_card(self, parent, icon, title, value, color):
        """Создание карточки информации"""
        card = tk.Frame(parent, bg=self.colors['bg_card_hover'],
                        relief='flat', padx=15, pady=15)

        # Левая часть с иконкой
        left_frame = tk.Frame(card, bg=self.colors['bg_card_hover'])
        left_frame.pack(side=tk.LEFT)

        icon_label = tk.Label(left_frame, text=icon,
                              font=('Segoe UI', 20),
                              bg=self.colors['bg_card_hover'],
                              fg=color)
        icon_label.pack()

        # Правая часть с текстом
        right_frame = tk.Frame(card, bg=self.colors['bg_card_hover'])
        right_frame.pack(side=tk.LEFT, padx=(15, 0), fill=tk.X, expand=True)

        title_label = tk.Label(right_frame, text=title,
                               font=('Segoe UI', 10, 'bold'),
                               bg=self.colors['bg_card_hover'],
                               fg=self.colors['text_muted'])
        title_label.pack(anchor='w')

        value_label = tk.Label(right_frame, text=value,
                               font=('Segoe UI', 12),
                               bg=self.colors['bg_card_hover'],
                               fg=self.colors['text'])
        value_label.pack(anchor='w', pady=(2, 0))

        return card

    def create_action_button(self, parent, text, color, state=tk.NORMAL, command=None):
        """Создание кнопки действия с плавной анимацией"""
        btn = tk.Button(parent, text=text,
                        font=('Segoe UI', 12, 'bold'),
                        bg=color,
                        fg='white',
                        relief='flat',
                        padx=20,
                        pady=12,
                        cursor='hand2',
                        bd=0,
                        state=state,
                        highlightthickness=0,
                        command=command if command else lambda: None)

        btn.config(activebackground=self.lighten_color(color, 20),
                   activeforeground='white')

        btn.bind("<Enter>", lambda e, b=btn, c=color:
        self.animate_button_hover(b, c, True))
        btn.bind("<Leave>", lambda e, b=btn, c=color:
        self.animate_button_hover(b, c, False))

        return btn

    def create_stats_tab(self):
        """Создание вкладки статистики"""
        frame = tk.Frame(self.notebook, bg=self.colors['bg_darker'])

        container = tk.Frame(frame, bg=self.colors['bg_darker'],
                             padx=20, pady=20)
        container.pack(fill=tk.BOTH, expand=True)

        # Статистика в виде карточек
        stats_frame = tk.Frame(container, bg=self.colors['bg_darker'])
        stats_frame.pack(fill=tk.BOTH, expand=True)

        # Первый ряд
        row1 = tk.Frame(stats_frame, bg=self.colors['bg_darker'])
        row1.pack(fill=tk.X, pady=(0, 15))

        stats_data = [
            ("🎮", "Всего игр", "total_games", "0", self.colors['primary']),
            ("⏱️", "Общее время", "total_time", "0ч", self.colors['secondary']),
            ("🔥", "Самая играемая", "most_played", "Нет", self.colors['accent']),
        ]

        self.stats_labels = {}
        for i, (icon, title, key, default, color) in enumerate(stats_data):
            card = self.create_stat_card(row1, icon, title, default, color)
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
            self.stats_labels[key] = card.winfo_children()[-1]

        # Второй ряд
        row2 = tk.Frame(stats_frame, bg=self.colors['bg_darker'])
        row2.pack(fill=tk.X, pady=(0, 15))

        stats_data2 = [
            ("⚡", "Сессий всего", "total_sessions", "0", self.colors['warning']),
            ("📅", "Последняя активность", "last_activity", "Не было", self.colors['info']),
            ("🏆", "Рекорд времени", "record_time", "0ч", self.colors['success']),
        ]

        for i, (icon, title, key, default, color) in enumerate(stats_data2):
            card = self.create_stat_card(row2, icon, title, default, color)
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
            self.stats_labels[key] = card.winfo_children()[-1]

        # График активности (симуляция)
        activity_frame = tk.Frame(container, bg=self.colors['bg_card'],
                                  padx=20, pady=20)
        activity_frame.pack(fill=tk.BOTH, expand=True, pady=(15, 0))

        tk.Label(activity_frame, text="📈 АКТИВНОСТЬ ЗА НЕДЕЛЮ",
                 font=('Segoe UI', 14, 'bold'),
                 bg=self.colors['bg_card'],
                 fg=self.colors['text']).pack(anchor='w', pady=(0, 15))

        # Создаем простой график
        graph_canvas = tk.Canvas(activity_frame, bg=self.colors['bg_card'],
                                 height=150, highlightthickness=0)
        graph_canvas.pack(fill=tk.X)

        # Рисуем график активности
        self.draw_activity_graph(graph_canvas)

        return frame

    def create_stat_card(self, parent, icon, title, value, color):
        """Создание карточки статистики"""
        card = tk.Frame(parent, bg=self.colors['bg_card'],
                        relief='flat', padx=20, pady=25)

        # Иконка
        tk.Label(card, text=icon, font=('Segoe UI', 28),
                 bg=self.colors['bg_card'], fg=color).pack(anchor='w')

        # Заголовок
        tk.Label(card, text=title, font=('Segoe UI', 11),
                 bg=self.colors['bg_card'],
                 fg=self.colors['text_muted']).pack(anchor='w', pady=(10, 5))

        # Значение
        value_label = tk.Label(card, text=value, font=('Segoe UI', 24, 'bold'),
                               bg=self.colors['bg_card'], fg=self.colors['text'])
        value_label.pack(anchor='w')

        return card

    def create_steam_tab(self):
        """Создание вкладки Steam"""
        frame = tk.Frame(self.notebook, bg=self.colors['bg_darker'])

        container = tk.Frame(frame, bg=self.colors['bg_darker'],
                             padx=20, pady=20)
        container.pack(fill=tk.BOTH, expand=True)

        if self.steam_path:
            steam_card = tk.Frame(container, bg=self.colors['bg_card'],
                                  padx=25, pady=25)
            steam_card.pack(fill=tk.BOTH, expand=True)

            tk.Label(steam_card, text="🟦 STEAM ИНТЕГРАЦИЯ",
                     font=('Segoe UI', 18, 'bold'),
                     bg=self.colors['bg_card'],
                     fg=self.colors['text']).pack(anchor='w', pady=(0, 25))

            # Информация
            info_items = [
                ("📁", "Путь к Steam:", self.steam_path),
                ("🎮", "Найдено игр:", str(len(self.steam_apps))),
                ("⚡", "Статус:", "Подключено" if self.steam_path else "Не найдено"),
            ]

            for icon, label, value in info_items:
                item_frame = tk.Frame(steam_card, bg=self.colors['bg_card'])
                item_frame.pack(fill=tk.X, pady=12)

                tk.Label(item_frame, text=icon, font=('Segoe UI', 16),
                         bg=self.colors['bg_card'],
                         fg=self.colors['primary']).pack(side=tk.LEFT, padx=(0, 15))

                tk.Label(item_frame, text=label, font=('Segoe UI', 11),
                         bg=self.colors['bg_card'],
                         fg=self.colors['text_muted']).pack(side=tk.LEFT)

                tk.Label(item_frame, text=value, font=('Segoe UI', 11, 'bold'),
                         bg=self.colors['bg_card'],
                         fg=self.colors['text']).pack(side=tk.RIGHT)

            # Кнопки действий
            btn_frame = tk.Frame(steam_card, bg=self.colors['bg_card'])
            btn_frame.pack(fill=tk.X, pady=(30, 0))

            import_btn = self.create_action_button(btn_frame,
                                                   "📥 ИМПОРТИРОВАТЬ ВСЕ ИГРЫ",
                                                   self.colors['steam_color'],
                                                   command=self.import_all_steam_games)
            import_btn.pack(fill=tk.X, pady=(0, 10))

            scan_btn = self.create_action_button(btn_frame,
                                                 "🔍 ОБНОВИТЬ БИБЛИОТЕКУ",
                                                 self.colors['primary'],
                                                 command=self.load_steam_library)
            scan_btn.pack(fill=tk.X)

        else:
            # Steam не найден
            not_found_card = tk.Frame(container, bg=self.colors['bg_card'],
                                      padx=25, pady=25)
            not_found_card.pack(fill=tk.BOTH, expand=True)

            tk.Label(not_found_card, text="❌ STEAM НЕ НАЙДЕН",
                     font=('Segoe UI', 20, 'bold'),
                     bg=self.colors['bg_card'],
                     fg=self.colors['danger']).pack(pady=(20, 15))

            tk.Label(not_found_card,
                     text="Установите Steam или проверьте путь установки",
                     font=('Segoe UI', 12),
                     bg=self.colors['bg_card'],
                     fg=self.colors['text_muted']).pack(pady=(0, 25))

            manual_btn = self.create_action_button(not_found_card,
                                                   "🔧 УКАЗАТЬ ПУТЬ ВРУЧНУЮ",
                                                   self.colors['warning'],
                                                   command=self.manual_steam_path)
            manual_btn.pack(fill=tk.X)

        return frame

    def manual_steam_path(self):
        """Ручной выбор пути к Steam"""
        path = filedialog.askdirectory(title="Выберите папку Steam")
        if path:
            self.steam_path = path
            self.load_steam_library()
            messagebox.showinfo("Успех", f"Путь к Steam установлен: {path}")

    def create_status_bar(self):
        """Создание нижнего статус бара"""
        status_bar = tk.Frame(self.main_container, bg=self.colors['bg_darkest'],
                              height=40)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        status_bar.pack_propagate(False)

        left_frame = tk.Frame(status_bar, bg=self.colors['bg_darkest'])
        left_frame.pack(side=tk.LEFT, padx=20)

        self.status_label = tk.Label(left_frame,
                                     text="Готов к работе",
                                     font=('Segoe UI', 10),
                                     bg=self.colors['bg_darkest'],
                                     fg=self.colors['text_secondary'])
        self.status_label.pack(side=tk.LEFT)

        right_frame = tk.Frame(status_bar, bg=self.colors['bg_darkest'])
        right_frame.pack(side=tk.RIGHT, padx=20)

        self.time_label = tk.Label(right_frame,
                                   text=datetime.now().strftime("%H:%M"),
                                   font=('Segoe UI', 10),
                                   bg=self.colors['bg_darkest'],
                                   fg=self.colors['text_secondary'])
        self.time_label.pack(side=tk.RIGHT)

    def draw_activity_graph(self, canvas):
        """Рисование графика активности"""
        width = canvas.winfo_reqwidth()
        height = 150

        # Очищаем canvas
        canvas.delete("all")

        # Фон графика
        canvas.create_rectangle(0, 0, width, height,
                                fill=self.colors['bg_card'], outline='')

        # Сетка
        for i in range(1, 6):
            y = height - (i * height / 5)
            canvas.create_line(0, y, width, y,
                               fill=self.colors['bg_card_hover'], width=1)

        # Данные активности (примерные)
        days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
        activity = [30, 45, 60, 75, 50, 85, 40]  # В процентах

        bar_width = (width - 100) / 7

        for i, (day, act) in enumerate(zip(days, activity)):
            x = 50 + i * bar_width + bar_width / 2
            bar_height = (act / 100) * (height - 50)
            y = height - 25 - bar_height

            # Столбик
            canvas.create_rectangle(x - bar_width / 2 + 5, y,
                                    x + bar_width / 2 - 5, height - 25,
                                    fill=self.colors['primary_light'],
                                    outline='')

            # Подпись дня
            canvas.create_text(x, height - 10,
                               text=day,
                               font=('Segoe UI', 9),
                               fill=self.colors['text_secondary'])

    def animate_window_appear(self):
        """Плавное появление окна"""
        self.root.deiconify()

        # Анимация увеличения прозрачности
        for alpha in range(0, 101, 5):
            self.root.attributes('-alpha', alpha / 100)
            self.root.update()
            time.sleep(0.01)

        # Центрирование после появления
        self.center_window()

    def center_window(self):
        """Центрирование окна с анимацией"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Начальная позиция (центр)
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        # Плавное движение к центру
        for i in range(0, 21):
            current_x = int(x * (i / 20))
            current_y = int(y * (i / 20))
            self.root.geometry(f'{width}x{height}+{current_x}+{current_y}')
            self.root.update()
            time.sleep(0.01)

    def start_animations(self):
        """Запуск всех анимаций"""
        self.animate_logo()
        self.update_clock()

    def animate_logo(self):
        """Анимация логотипа"""

        def pulse(step=0):
            if hasattr(self, 'logo_label') and self.logo_label.winfo_exists():
                # Плавное изменение размера
                scale = 1 + math.sin(step * 0.05) * 0.1
                font_size = int(48 * scale)
                self.logo_label.config(font=("Segoe UI", font_size, "bold"))

                # Плавное изменение цвета
                color_shift = int(math.sin(step * 0.03) * 30)
                color = self.lighten_color(self.colors['primary_light'], color_shift)
                self.logo_label.config(fg=color)

                self.root.after(50, lambda: pulse(step + 1))

        pulse()

    def update_clock(self):
        """Обновление времени в статус баре"""
        current_time = datetime.now().strftime("%H:%M:%S")
        if hasattr(self, 'time_label'):
            self.time_label.config(text=current_time)
        self.root.after(1000, self.update_clock)

    def hex_to_rgb(self, hex_color):
        """Конвертация HEX цвета в RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

    def lighten_color(self, color, amount=20):
        """Осветлить цвет"""
        r, g, b = self.hex_to_rgb(color)
        r = min(255, r + amount)
        g = min(255, g + amount)
        b = min(255, b + amount)
        return f'#{r:02x}{g:02x}{b:02x}'

    def animate_button_hover(self, button, base_color, hover):
        """Анимация при наведении на кнопку"""
        if hover:
            button.config(bg=self.lighten_color(base_color, 20))
        else:
            button.config(bg=base_color)

    # Методы из оригинального кода
    def load_games_data(self):
        """Загрузить игры из файла"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.games = json.load(f)
            except:
                self.games = []
        else:
            self.games = []

    def save_games(self):
        """Сохранить игры в файл"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.games, f, ensure_ascii=False, indent=2)

    def load_games_ui(self):
        """Загрузить игры в интерфейс"""
        self.load_games_data()
        self.check_running_games()

        if hasattr(self, 'scrollable_frame'):
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()

        self.game_widgets = []
        for game in self.games:
            self.add_smooth_game_card(game)

        self.update_stats()
        self.update_header_stats()

    def add_smooth_game_card(self, game):
        """Добавить плавную карточку игры"""
        is_running = any(info["game_id"] == game["id"]
                         for info in self.running_games.values())
        is_steam = game.get('is_steam', False)
        is_selected = self.selected_game_id == game["id"]

        # Создаем карточку
        card = tk.Frame(self.scrollable_frame,
                        bg=self.colors['bg_card_selected'] if is_selected else self.colors['bg_card'],
                        relief='flat',
                        padx=20, pady=15)
        card.pack(fill=tk.X, pady=5, padx=5)
        card.game_id = game["id"]

        # Эффект при наведении
        if not is_selected:
            def on_enter(e):
                card.config(bg=self.colors['bg_card_hover'])

            def on_leave(e):
                card.config(bg=self.colors['bg_card'])

            card.bind("<Enter>", on_enter)
            card.bind("<Leave>", on_leave)

        # Содержимое карточки
        content_frame = tk.Frame(card,
                                 bg=self.colors['bg_card_selected'] if is_selected else self.colors['bg_card'])
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Левая часть: иконка
        icon_frame = tk.Frame(content_frame,
                              bg=self.colors['steam_color'] if is_steam else self.colors['primary'],
                              width=60, height=60)
        icon_frame.pack_propagate(False)
        icon_frame.pack(side=tk.LEFT, padx=(0, 15))

        icon_text = "🟦" if is_steam else "🎮"
        icon = tk.Label(icon_frame, text=icon_text,
                        font=('Segoe UI', 24),
                        bg=self.colors['steam_color'] if is_steam else self.colors['primary'],
                        fg='white')
        icon.pack(expand=True)

        # Центральная часть: информация
        info_frame = tk.Frame(content_frame,
                              bg=self.colors['bg_card_selected'] if is_selected else self.colors['bg_card'])
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Название
        name_label = tk.Label(info_frame, text=game["name"],
                              font=('Segoe UI', 14, 'bold'),
                              bg=self.colors['bg_card_selected'] if is_selected else self.colors['bg_card'],
                              fg=self.colors['text'],
                              anchor='w',
                              wraplength=300,
                              justify='left')
        name_label.pack(anchor='w')

        # Детали
        details_frame = tk.Frame(info_frame,
                                 bg=self.colors['bg_card_selected'] if is_selected else self.colors['bg_card'])
        details_frame.pack(anchor='w', pady=(8, 0))

        # Время игры
        time_label = tk.Label(details_frame,
                              text=f"⏱️ {self.format_time(game.get('total_time', 0))}",
                              font=('Segoe UI', 9),
                              bg=self.colors['bg_card_selected'] if is_selected else self.colors['bg_card'],
                              fg=self.colors['text_secondary'])
        time_label.pack(side=tk.LEFT, padx=(0, 10))

        # Steam бейдж
        if is_steam:
            steam_badge = tk.Label(details_frame, text="STEAM",
                                   font=('Segoe UI', 9, 'bold'),
                                   bg=self.colors['steam_light'],
                                   fg='white',
                                   padx=8, pady=2)
            steam_badge.pack(side=tk.LEFT)

        # Статус запуска
        if is_running:
            status_badge = tk.Label(details_frame, text="▶ ЗАПУЩЕНА",
                                    font=('Segoe UI', 9, 'bold'),
                                    bg=self.colors['success'],
                                    fg='white',
                                    padx=8, pady=2)
            status_badge.pack(side=tk.LEFT, padx=(10, 0))

        # Правая часть: кнопка запуска
        btn_frame = tk.Frame(content_frame,
                             bg=self.colors['bg_card_selected'] if is_selected else self.colors['bg_card'])
        btn_frame.pack(side=tk.RIGHT)

        # Круглая кнопка запуска
        btn_bg = self.colors['success'] if not is_running else self.colors['warning']
        btn_text = "▶" if not is_running else "⏸"

        launch_btn = tk.Button(btn_frame, text=btn_text,
                               font=('Segoe UI', 16, 'bold'),
                               bg=btn_bg,
                               fg='white',
                               relief='flat',
                               width=3,
                               height=1,
                               cursor='hand2',
                               bd=0,
                               command=lambda: self.start_game(game["id"]))
        launch_btn.pack()

        # Эффект при наведении на кнопку
        launch_btn.bind("<Enter>",
                        lambda e, b=launch_btn:
                        b.config(bg=self.lighten_color(btn_bg, 20)))
        launch_btn.bind("<Leave>",
                        lambda e, b=launch_btn:
                        b.config(bg=btn_bg))

        # Привязываем выбор игры
        for widget in [card, icon_frame, icon, name_label, time_label]:
            widget.bind("<Button-1>", lambda e, g=game: self.select_game(g))

        if hasattr(self, 'game_widgets'):
            self.game_widgets.append(card)

    def select_game(self, game):
        """Выбрать игру"""
        self.selected_game_id = game["id"]

        # Обновляем панель информации
        self.selected_game = game
        self.game_name_label.config(text=game["name"])

        # Обновляем иконку в зависимости от типа игры
        icon_text = "🟦" if game.get('is_steam', False) else "🎮"
        self.game_icon.config(text=icon_text)

        self.game_info_labels['time'].config(
            text=self.format_time(game.get('total_time', 0))
        )
        self.game_info_labels['sessions'].config(
            text=str(len(game.get('sessions', [])))
        )

        last_played = game.get('last_played', 'Никогда')
        if last_played != 'Никогда':
            try:
                last_played = datetime.fromisoformat(last_played).strftime("%d.%m.%Y %H:%M")
            except:
                pass
        self.game_info_labels['last_played'].config(text=last_played)

        # Тип игры
        game_type = "Steam игра" if game.get('is_steam', False) else "Локальная игра"
        self.game_info_labels['game_type'].config(text=game_type)

        self.launch_btn.config(state=tk.NORMAL,
                               command=lambda: self.start_game(game["id"]))
        self.remove_btn.config(state=tk.NORMAL,
                               command=lambda: self.remove_selected_game(game))

        # Обновляем отображение всех карточек
        if hasattr(self, 'game_widgets'):
            for card in self.game_widgets:
                if hasattr(card, 'game_id'):
                    is_selected = card.game_id == game["id"]
                    new_bg = self.colors['bg_card_selected'] if is_selected else self.colors['bg_card']
                    card.config(bg=new_bg)

                    # Обновляем цвет всех внутренних фреймов
                    for widget in card.winfo_children():
                        if isinstance(widget, tk.Frame):
                            widget.config(bg=new_bg)
                            for child in widget.winfo_children():
                                if isinstance(child, tk.Frame):
                                    child.config(bg=new_bg)
                                    for grandchild in child.winfo_children():
                                        if isinstance(grandchild, tk.Frame):
                                            grandchild.config(bg=new_bg)
                                        elif isinstance(grandchild, tk.Label):
                                            grandchild.config(bg=new_bg)

    def format_time(self, seconds):
        """Форматировать время в красивый вид"""
        if seconds < 60:
            return f"{int(seconds)} сек"
        elif seconds < 3600:
            minutes = seconds // 60
            seconds_remain = int(seconds % 60)
            if seconds_remain > 0:
                return f"{int(minutes)} мин {seconds_remain} сек"
            else:
                return f"{int(minutes)} мин"
        elif seconds < 86400:
            hours = seconds // 3600
            minutes = int((seconds % 3600) // 60)
            if minutes > 0:
                return f"{int(hours)} ч {minutes} мин"
            else:
                return f"{int(hours)} ч"
        else:
            days = seconds // 86400
            hours = int((seconds % 86400) // 3600)
            if hours > 0:
                return f"{int(days)} д {hours} ч"
            else:
                return f"{int(days)} д"

    def update_stats(self):
        """Обновить статистику"""
        total_time = sum(game.get("total_time", 0) for game in self.games)
        total_games = len(self.games)
        total_sessions = sum(len(game.get("sessions", [])) for game in self.games)

        most_played = None
        max_time = 0
        record_time = 0
        for game in self.games:
            game_time = game.get("total_time", 0)
            if game_time > max_time:
                max_time = game_time
                most_played = game["name"]

            # Находим рекорд времени за сессию
            for session in game.get("sessions", []):
                if "duration" in session:
                    record_time = max(record_time, session["duration"])

        last_activity = "Не было"
        for game in self.games:
            last_played = game.get('last_played')
            if last_played:
                try:
                    last_date = datetime.fromisoformat(last_played)
                    if last_activity == "Не было" or last_date > datetime.fromisoformat(last_activity):
                        last_activity = last_played
                except:
                    pass

        if last_activity != "Не было":
            last_activity = datetime.fromisoformat(last_activity).strftime("%d.%m.%Y")

        if hasattr(self, 'stats_labels'):
            for key, label in self.stats_labels.items():
                if key == 'total_games':
                    label.config(text=str(total_games))
                elif key == 'total_time':
                    label.config(text=self.format_time(total_time))
                elif key == 'most_played':
                    label.config(text=most_played[:15] + "..." if most_played and len(
                        most_played) > 15 else most_played or "Нет")
                elif key == 'last_activity':
                    label.config(text=last_activity)
                elif key == 'total_sessions':
                    label.config(text=str(total_sessions))
                elif key == 'record_time':
                    label.config(text=self.format_time(record_time))

    def update_header_stats(self):
        """Обновить статистику в заголовке"""
        total_games = len(self.games)
        total_time = sum(game.get("total_time", 0) for game in self.games)

        if total_time < 60:
            time_str = f"{int(total_time)} сек"
        elif total_time < 3600:
            time_str = f"{int(total_time // 60)} мин"
        else:
            hours = total_time // 3600
            time_str = f"{int(hours)} ч"

        running_games = len(self.running_games)

        if hasattr(self, 'header_stats'):
            self.header_stats.config(
                text=f"🕹️ {total_games} игр | ⏱️ {time_str} | 🔥 {running_games} активных"
            )

    def filter_games(self, event=None):
        """Фильтрация игр"""
        search_text = self.search_var.get().lower()

        if search_text == "Поиск игр...":
            search_text = ""

        if hasattr(self, 'scrollable_frame'):
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()

        if hasattr(self, 'game_widgets'):
            self.game_widgets = []

        for game in self.games:
            if not search_text or search_text in game["name"].lower():
                self.add_smooth_game_card(game)

    def quick_launch(self):
        """Быстрый запуск последней игры"""
        if self.games:
            last_game = None
            last_date = None
            for game in self.games:
                last_played = game.get('last_played')
                if last_played:
                    try:
                        game_date = datetime.fromisoformat(last_played)
                        if last_date is None or game_date > last_date:
                            last_date = game_date
                            last_game = game
                    except:
                        pass

            if last_game:
                self.start_game(last_game["id"])
            else:
                self.start_game(self.games[0]["id"])

    def start_game(self, game_id):
        """Запустить игру"""
        game = next((g for g in self.games if g["id"] == game_id), None)
        if not game:
            self.show_notification("Игра не найдена", "error")
            return False

        exe_path = game['exe_path']
        is_steam = game.get('is_steam', False)
        steam_id = game.get('steam_id')

        try:
            def run_game():
                try:
                    if is_steam and steam_id and self.steam_path:
                        steam_exe = os.path.join(self.steam_path, 'steam.exe')

                        if os.path.exists(steam_exe):
                            webbrowser.open(f'steam://rungameid/{steam_id}')
                            process = None
                        else:
                            if os.path.exists(exe_path):
                                process = subprocess.Popen(exe_path, shell=True,
                                                           creationflags=subprocess.CREATE_NO_WINDOW)
                            else:
                                raise FileNotFoundError(f"Файл не найден: {exe_path}")
                    else:
                        if os.path.exists(exe_path):
                            process = subprocess.Popen(exe_path, shell=True,
                                                       creationflags=subprocess.CREATE_NO_WINDOW)
                        else:
                            raise FileNotFoundError(f"Файл не найден: {exe_path}")

                    session = {
                        "start_time": datetime.now().isoformat(),
                        "process_id": process.pid if process else 0
                    }

                    if "sessions" not in game:
                        game["sessions"] = []
                    game["sessions"].append(session)

                    if process:
                        self.running_games[process.pid] = {
                            "game_id": game_id,
                            "start_time": datetime.now(),
                            "process": process
                        }

                    game["last_played"] = datetime.now().isoformat()
                    self.save_games()
                    self.load_games_ui()

                    if process:
                        process.wait()

                        if process.pid in self.running_games:
                            session_info = self.running_games[process.pid]
                            end_time = datetime.now()
                            play_time = (end_time - session_info["start_time"]).total_seconds()

                            game["total_time"] = game.get("total_time", 0) + play_time

                            for s in game["sessions"]:
                                if s.get("process_id") == process.pid:
                                    s["end_time"] = end_time.isoformat()
                                    s["duration"] = play_time
                                    break

                            del self.running_games[process.pid]
                            self.save_games()
                            self.load_games_ui()

                except Exception as e:
                    print(f"Ошибка при запуске игры: {e}")
                    self.root.after(0, lambda: messagebox.showerror(
                        "Ошибка запуска",
                        f"Не удалось запустить игру:\n{str(e)}\n\n"
                        f"Попробуйте:\n"
                        f"1. Запустить Steam вручную\n"
                        f"2. Проверить путь к игре\n"
                        f"3. Запустить игру от имени администратора"
                    ))

            thread = threading.Thread(target=run_game, daemon=True)
            thread.start()

            self.show_notification(f"Запускается {game['name']}", "info")
            return True

        except Exception as e:
            self.show_notification(f"Ошибка: {str(e)}", "error")
            return False

    def check_running_games(self):
        """Проверить запущенные игры"""
        completed = []

        for pid, info in list(self.running_games.items()):
            process = info["process"]
            if process.poll() is not None:
                game = next((g for g in self.games if g["id"] == info["game_id"]), None)

                if game:
                    end_time = datetime.now()
                    play_time = (end_time - info["start_time"]).total_seconds()
                    game["total_time"] = game.get("total_time", 0) + play_time

                    for s in game["sessions"]:
                        if s.get("process_id") == pid:
                            s["end_time"] = end_time.isoformat()
                            s["duration"] = play_time
                            break

                    completed.append(pid)

        for pid in completed:
            if pid in self.running_games:
                del self.running_games[pid]

        if completed:
            self.save_games()

    def update_timer(self):
        """Таймер обновления"""
        self.check_running_games()
        self.root.after(1000, self.update_timer)

    def on_search_focus_in(self, event):
        if self.search_entry.get() == "Поиск игр...":
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(fg=self.colors['text'])

    def on_search_focus_out(self, event):
        if not self.search_entry.get():
            self.search_entry.insert(0, "Поиск игр...")
            self.search_entry.config(fg=self.colors['text_muted'])

    def show_notification(self, message, type_="info"):
        """Показать красивое уведомление"""
        colors = {
            "success": self.colors['success'],
            "error": self.colors['danger'],
            "info": self.colors['primary'],
            "warning": self.colors['warning']
        }

        notification = tk.Toplevel(self.root)
        notification.overrideredirect(True)
        notification.configure(bg=colors[type_], padx=0, pady=0)

        # Анимация появления
        notification.attributes('-alpha', 0)

        frame = tk.Frame(notification, bg=colors[type_], padx=20, pady=15)
        frame.pack()

        icon = {
            "success": "✅",
            "error": "❌",
            "info": "ℹ️",
            "warning": "⚠️"
        }.get(type_, "ℹ️")

        tk.Label(frame, text=f"{icon} {message}",
                 font=('Segoe UI', 11, 'bold'),
                 bg=colors[type_], fg='white').pack()

        notification.update_idletasks()
        x = self.root.winfo_rootx() + self.root.winfo_width() - notification.winfo_width() - 20
        y = self.root.winfo_rooty() + 80

        notification.geometry(f"+{x}+{y}")

        # Анимация появления
        for alpha in range(0, 101, 20):
            notification.attributes('-alpha', alpha / 100)
            notification.update()
            time.sleep(0.01)

        # Анимация исчезновения
        notification.after(2000, lambda: self.fade_out(notification))

    def fade_out(self, window):
        """Плавное исчезновение окна"""
        for alpha in range(100, -1, -20):
            window.attributes('-alpha', alpha / 100)
            window.update()
            time.sleep(0.01)
        window.destroy()

    def show_settings(self):
        """Показать настройки"""
        messagebox.showinfo("Настройки",
                            "Настройки будут доступны в следующей версии!\n\n"
                            "Планируемые функции:\n"
                            "• Настройка цветовой темы\n"
                            "• Автозапуск при старте системы\n"
                            "• Уведомления о достижениях\n"
                            "• Экспорт статистики",
                            parent=self.root)

    def add_game_dialog(self):
        """Диалог добавления игры"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить игру")
        dialog.geometry("500x400")
        dialog.configure(bg=self.colors['bg_dark'])
        dialog.transient(self.root)
        dialog.grab_set()

        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (500 // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (400 // 2)
        dialog.geometry(f"+{x}+{y}")

        header = tk.Frame(dialog, bg=self.colors['primary'], height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(header, text="🎮 ДОБАВИТЬ ИГРУ",
                 font=('Segoe UI', 16, 'bold'),
                 bg=self.colors['primary'], fg='white').pack(expand=True)

        content = tk.Frame(dialog, bg=self.colors['bg_card'], padx=30, pady=25)
        content.pack(fill=tk.BOTH, expand=True)

        tk.Label(content, text="Название игры:", font=('Segoe UI', 11),
                 bg=self.colors['bg_card'],
                 fg=self.colors['text_muted']).pack(anchor='w', pady=(0, 5))

        name_var = tk.StringVar()
        name_entry = tk.Entry(content, textvariable=name_var,
                              font=('Segoe UI', 12),
                              bg=self.colors['bg_darker'],
                              fg=self.colors['text'],
                              insertbackground=self.colors['primary'],
                              relief='flat')
        name_entry.pack(fill=tk.X, pady=(0, 15))

        tk.Label(content, text="Путь к игре:", font=('Segoe UI', 11),
                 bg=self.colors['bg_card'],
                 fg=self.colors['text_muted']).pack(anchor='w', pady=(0, 5))

        path_frame = tk.Frame(content, bg=self.colors['bg_card'])
        path_frame.pack(fill=tk.X, pady=(0, 5))

        path_var = tk.StringVar()
        path_entry = tk.Entry(path_frame, textvariable=path_var,
                              font=('Segoe UI', 11),
                              bg=self.colors['bg_darker'],
                              fg=self.colors['text'],
                              insertbackground=self.colors['primary'],
                              relief='flat')
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        browse_btn = tk.Button(path_frame, text="Обзор",
                               bg=self.colors['primary'],
                               fg='white',
                               font=('Segoe UI', 10, 'bold'),
                               relief='flat', padx=15,
                               command=lambda: self.browse_file_dialog(path_var, name_var))
        browse_btn.pack(side=tk.RIGHT)

        steam_var = tk.BooleanVar(value=False)
        steam_check = tk.Checkbutton(content, text="Это Steam игра",
                                     variable=steam_var,
                                     font=('Segoe UI', 10),
                                     bg=self.colors['bg_card'],
                                     fg=self.colors['text'],
                                     selectcolor=self.colors['primary'])
        steam_check.pack(anchor='w', pady=15)

        steam_id_frame = tk.Frame(content, bg=self.colors['bg_card'])
        steam_id_frame.pack(fill=tk.X, pady=(5, 0))

        tk.Label(steam_id_frame, text="Steam App ID (опционально):",
                 font=('Segoe UI', 10),
                 bg=self.colors['bg_card'],
                 fg=self.colors['text_muted']).pack(side=tk.LEFT)

        steam_id_var = tk.StringVar()
        steam_id_entry = tk.Entry(steam_id_frame, textvariable=steam_id_var,
                                  font=('Segoe UI', 10),
                                  bg=self.colors['bg_darker'],
                                  fg=self.colors['text'],
                                  width=15)
        steam_id_entry.pack(side=tk.RIGHT)

        btn_frame = tk.Frame(content, bg=self.colors['bg_card'])
        btn_frame.pack(fill=tk.X, pady=(25, 0))

        def add_game():
            name = name_var.get().strip()
            path = path_var.get().strip()
            is_steam = steam_var.get()
            steam_id = steam_id_var.get().strip()

            if not name or not path:
                messagebox.showerror("Ошибка", "Заполните все поля!", parent=dialog)
                return

            if not os.path.exists(path) and not is_steam:
                messagebox.showerror("Ошибка", "Файл не существует!", parent=dialog)
                return

            game_id = len(self.games) + 1
            game = {
                "id": game_id,
                "name": name,
                "exe_path": path,
                "total_time": 0,
                "sessions": [],
                "last_played": None,
                "added_date": datetime.now().isoformat(),
                "is_steam": is_steam
            }

            if is_steam and steam_id:
                game["steam_id"] = steam_id

            self.games.append(game)
            self.save_games()
            self.load_games_ui()
            dialog.destroy()

            self.show_notification(f"Игра '{name}' добавлена!", "success")

        tk.Button(btn_frame, text="ДОБАВИТЬ", command=add_game,
                  bg=self.colors['success'], fg='white',
                  font=('Segoe UI', 12, 'bold'),
                  relief='flat', padx=30, pady=12).pack(side=tk.RIGHT, padx=(10, 0))

        tk.Button(btn_frame, text="ОТМЕНА", command=dialog.destroy,
                  bg=self.colors['danger'], fg='white',
                  font=('Segoe UI', 11),
                  relief='flat', padx=30, pady=12).pack(side=tk.RIGHT)

    def browse_file_dialog(self, path_var, name_var):
        """Открыть диалог выбора файла"""
        filename = filedialog.askopenfilename(
            title="Выберите файл игры",
            filetypes=[("Исполняемые файлы", "*.exe"), ("Все файлы", "*.*")]
        )
        if filename:
            path_var.set(filename)
            if not name_var.get():
                name = os.path.splitext(os.path.basename(filename))[0]
                name_var.set(name)

    def find_steam_games(self):
        """Найти Steam игры"""
        if not self.steam_path:
            messagebox.showinfo("Steam не найден",
                                "Не удалось найти установленный Steam на вашем компьютере.",
                                parent=self.root)
            return

        if not self.steam_apps:
            messagebox.showinfo("Библиотека Steam",
                                "Игры Steam не найдены в библиотеке.",
                                parent=self.root)
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Игры Steam")
        dialog.geometry("600x500")
        dialog.configure(bg=self.colors['bg_dark'])
        dialog.transient(self.root)
        dialog.grab_set()

        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (600 // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (500 // 2)
        dialog.geometry(f"+{x}+{y}")

        header = tk.Frame(dialog, bg=self.colors['primary'], height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(header, text="🟦 ИГРЫ STEAM",
                 font=('Segoe UI', 16, 'bold'),
                 bg=self.colors['primary'], fg='white').pack(expand=True)

        list_frame = tk.Frame(dialog, bg=self.colors['bg_card'], padx=20, pady=20)
        list_frame.pack(fill=tk.BOTH, expand=True)

        tree = ttk.Treeview(list_frame, columns=("Игра", "App ID"), show="headings", height=15)
        tree.heading("Игра", text="Игра")
        tree.heading("App ID", text="App ID")
        tree.column("Игра", width=400)
        tree.column("App ID", width=100)

        for app_id, game_info in self.steam_apps.items():
            tree.insert("", tk.END, values=(game_info['name'], app_id), tags=(app_id,))

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        btn_frame = tk.Frame(dialog, bg=self.colors['bg_dark'], pady=20)
        btn_frame.pack(fill=tk.X)

        def import_selected():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Внимание", "Выберите игры для импорта", parent=dialog)
                return

            imported = 0
            for item in selected:
                values = tree.item(item)['values']
                game_name = values[0]
                app_id = values[1]

                if not any(g.get('steam_id') == app_id for g in self.games):
                    game_id = len(self.games) + 1
                    game_info = self.steam_apps[app_id]

                    game = {
                        "id": game_id,
                        "name": game_name,
                        "exe_path": game_info['exe_path'],
                        "total_time": 0,
                        "sessions": [],
                        "last_played": None,
                        "added_date": datetime.now().isoformat(),
                        "is_steam": True,
                        "steam_id": app_id
                    }

                    self.games.append(game)
                    imported += 1

            if imported > 0:
                self.save_games()
                self.load_games_ui()
                dialog.destroy()
                self.show_notification(f"Импортировано {imported} игр", "success")

        tk.Button(btn_frame, text="ИМПОРТИРОВАТЬ ВЫБРАННЫЕ", command=import_selected,
                  bg=self.colors['success'], fg='white',
                  font=('Segoe UI', 11, 'bold'),
                  relief='flat', padx=20, pady=10).pack(side=tk.LEFT, padx=20)

        tk.Button(btn_frame, text="ОТМЕНА", command=dialog.destroy,
                  bg=self.colors['danger'], fg='white',
                  font=('Segoe UI', 11),
                  relief='flat', padx=20, pady=10).pack(side=tk.RIGHT, padx=20)

    def import_all_steam_games(self):
        """Импортировать все Steam игры"""
        if not self.steam_apps:
            messagebox.showinfo("Нет игр", "Игры Steam не найдены", parent=self.root)
            return

        imported = 0
        for app_id, game_info in self.steam_apps.items():
            if not any(g.get('steam_id') == app_id for g in self.games):
                game_id = len(self.games) + 1

                game = {
                    "id": game_id,
                    "name": game_info['name'],
                    "exe_path": game_info['exe_path'],
                    "total_time": 0,
                    "sessions": [],
                    "last_played": None,
                    "added_date": datetime.now().isoformat(),
                    "is_steam": True,
                    "steam_id": app_id
                }

                self.games.append(game)
                imported += 1

        if imported > 0:
            self.save_games()
            self.load_games_ui()
            self.show_notification(f"Импортировано {imported} игр из Steam", "success")
        else:
            messagebox.showinfo("Импорт", "Все игры Steam уже добавлены", parent=self.root)

    def remove_selected_game(self, game):
        """Удалить игру"""
        if not messagebox.askyesno("Подтверждение",
                                   f"Удалить игру '{game['name']}'?"):
            return

        self.games = [g for g in self.games if g["id"] != game["id"]]
        self.save_games()
        self.load_games_ui()

        if hasattr(self, 'game_name_label'):
            self.game_name_label.config(text="Выберите игру")

        if hasattr(self, 'game_info_labels'):
            for label in self.game_info_labels.values():
                label.config(text="")

        if hasattr(self, 'launch_btn'):
            self.launch_btn.config(state=tk.DISABLED)

        if hasattr(self, 'remove_btn'):
            self.remove_btn.config(state=tk.DISABLED)

        self.selected_game_id = None

        self.show_notification(f"Игра '{game['name']}' удалена", "info")


def main():
    root = tk.Tk()

    # Устанавливаем иконку приложения
    try:
        root.iconbitmap(default='icon.ico')
    except:
        pass

    app = UltraSmoothLaunchGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()