# RenParticles - Руководство разработчика

## Архитектура системы

RenParticles построен на трех уровнях:

1. **DSL Parser** (`01renparticles_cds.rpy`) — парсит декларативный синтаксис
2. **Core Engine** (`renparticles_fast.rpy`) — управляет частицами и рендерингом
3. **Behaviors & Emitters** — расширяемые компоненты поведения

## Структура модулей

```
00RenParticles/
├── renparticles_base.rpy          # Базовые классы и миксины
├── renparticles_fast.rpy          # Основной движок частиц
├── renparticles_static.rpy        # Утилиты и регистрация шорткатов
├── 01renparticles_cds.rpy         # DSL парсер
└── Particles Implementation/
    └── Fast Particles/
        ├── Emitters/              # Эмиттеры частиц
        ├── Presets/               # Готовые пресеты
        ├── move_behaviors.rpy     # Поведения движения
        ├── tween.rpy              # Анимация свойств
        ├── mouse_orbiting.rpy     # Взаимодействие с курсором
        └── ...
```

## Базовые классы

### _Behavior

Базовый класс для всех поведений частиц:

```python
class _Behavior(_InjectPropertiesMixin, _CheckInitialisedMixin, _TryGetOtherSystemMixin):
    def __call__(self, context):
        raise NotImplementedError()
```

**Миксины:**
- `_InjectPropertiesMixin` — внедрение свойств через `inject_properties(**props)`
- `_CheckInitialisedMixin` — проверка обязательных полей через `_RequiredField()`
- `_TryGetOtherSystemMixin` — доступ к другим системам через `get_system(context, id)`

### Типы поведений

```python
class _UpdateBehavior(_Behavior):
    """Выполняется каждый кадр для каждой частицы"""
    pass

class _EventBehavior(_Behavior):
    """Обрабатывает события мыши"""
    pass

class _OnDeadBehavior(_Behavior):
    """Выполняется при смерти частицы"""
    pass

class Emitter(_Behavior):
    """Создает новые частицы"""
    pass
```

## Контексты выполнения

### RenpFContext

Базовый контекст, передаваемый в поведения:

```python
class RenpFContext:
    system = None      # Текущая система частиц
    st = None          # Время показа (show time)
    delta = None       # Время с последнего кадра
    particle = None    # Текущая частица (если есть)
    systems = None     # Словарь всех систем по ID
```

### EventContext

Расширенный контекст для событий:

```python
class EventContext(RenpFContext):
    x = None           # X координата события
    y = None           # Y координата события
    event = None       # Объект события Ren'Py
```

## Создание собственного поведения

### Простое поведение

```python
init -1000 python in renparticles:
    class MyCustomBehavior(_UpdateBehavior):
        # Обязательные поля
        speed = _RequiredField()
        
        # Опциональные поля с значениями по умолчанию
        direction = [1.0, 0.0]
        
        def __call__(self, context):
            particle = context.particle
            delta = context.delta
            
            # Ваша логика
            particle.x += self.direction[0] * self.speed * delta
            particle.y += self.direction[1] * self.speed * delta
            
            return UpdateState.Pass
```

**Возвращаемые значения:**
- `UpdateState.Pass` — продолжить выполнение
- `UpdateState.Repeat` — повторить (не используется)
- `UpdateState.Kill` — удалить это поведение из системы

### Поведение с состоянием на частицу

Для хранения данных на каждую частицу используйте `particles_properties`:

```python
class MyStatefulBehavior(_UpdateBehavior):
    _MY_DATA_KEY = "_my_behavior_data"
    _COUNTER = 0
    
    def __init__(self):
        # Уникальный ключ для каждого экземпляра
        self._MY_DATA_KEY = f"{self._MY_DATA_KEY}_{self._COUNTER}"
        self._COUNTER += 1
    
    def __call__(self, context):
        particle = context.particle
        particles_props = context.system.particles_data.particles_properties
        
        # Получить или создать данные частицы
        particle_data = particles_props.setdefault(particle, {})
        
        if self._MY_DATA_KEY not in particle_data:
            # Инициализация при первом вызове
            particle_data[self._MY_DATA_KEY] = {
                "counter": 0,
                "velocity": [random.uniform(-100, 100), random.uniform(-100, 100)]
            }
        
        data = particle_data[self._MY_DATA_KEY]
        data["counter"] += 1
        
        # Использование данных
        particle.x += data["velocity"][0] * context.delta
        particle.y += data["velocity"][1] * context.delta
        
        return UpdateState.Pass
```

### Эмиттер

```python
class MyEmitter(Emitter):
    amount = _RequiredField()
    spawn_area = (0, 0, 1920, 1080)
    
    def __call__(self, context):
        system = context.system
        images = system.particles_data.images
        
        for i in range(self.amount):
            sprite = system.create(random.choice(images))
            sprite.x = random.randint(self.spawn_area[0], self.spawn_area[2])
            sprite.y = random.randint(self.spawn_area[1], self.spawn_area[3])
            
            # Можно установить дополнительные свойства
            sprite.zorder = i
        
        return UpdateState.Pass
```

## Создание пресетов

### Простой пресет

```python
class MyPreset(_RFBehaviorPreset):
    behaviors = {
        "on_update": [Move, LifetimeDeltaDecreaser],
        "on_event": None,
        "on_particle_dead": None
    }
    
    # Параметры пресета
    velocity = _RequiredField()
    acceleration = [0.0, 0.0]
    
    def distribute_properties(self):
        # Вызвать базовую проверку
        super(MyPreset, self).distribute_properties()
        
        # Распределить свойства по поведениям
        move_behavior = self.behaviors["on_update"][0]
        move_behavior.inject_properties(
            velocity=self.velocity,
            acceleration=self.acceleration
        )
        
        expire_behavior = self.behaviors["on_update"][1]
        expire_behavior.inject_properties()
```

### Динамический пресет (для DSL)

```python
class MyDynamicPreset(_RFDynamicBehaviorPreset):
    # Определяется через DSL, не требует реализации
    pass
```

## Регистрация компонентов

### Статические шорткаты

В `fast_particles.rpy`:

```python
static_shortcuts = {
    "behaviors": {
        "my_behavior": MyCustomBehavior,
    },
    "emitters": {
        "my_emitter": MyEmitter,
    },
    "presets": {
        "general": {
            "my_preset": MyPreset,
        },
        "inner": {}
    }
}
```

### Динамическая регистрация

```python
init python in renparticles:
    # Регистрация поведения
    add_shortcut("my_behavior", MyCustomBehavior, is_emitter=False)
    
    # Регистрация эмиттера
    add_shortcut("my_emitter", MyEmitter, is_emitter=True)
    
    # Регистрация пресета
    add_preset("my_preset", MyPreset, preset_type="general")
```

## Работа с частицами

### RenSprite

Расширенный класс Ren'Py Sprite:

```python
class RenSprite(Sprite):
    lifetime = 0.0              # Время жизни
    _base_image = None          # Базовое изображение
    queued_transforms = {}      # Очередь трансформаций
    
    def queue_transform(self, **properties):
        """Добавить трансформацию (применится в следующем кадре)"""
        self.queued_transforms.update(properties)
    
    def apply_transforms(self):
        """Применить накопленные трансформации"""
        # Вызывается автоматически системой
```

**Доступные свойства:**
- `x, y` — позиция
- `zorder` — порядок отрисовки
- `live` — жив ли спрайт
- `lifetime` — оставшееся время жизни
- `events` — обрабатывать ли события

**Методы:**
- `destroy()` — пометить для удаления
- `queue_transform(**props)` — добавить трансформацию

### Создание частиц

```python
def __call__(self, context):
    system = context.system
    images = system.particles_data.images
    
    # Создать частицу
    sprite = system.create(random.choice(images))
    
    # Установить свойства
    sprite.x = 100
    sprite.y = 200
    sprite.zorder = 5
    
    # Добавить трансформацию
    sprite.queue_transform(alpha=0.5, zoom=2.0)
    
    return UpdateState.Pass
```

## Система частиц

### RenParticlesFast

Основной класс системы частиц:

```python
class RenParticlesFast(SpriteManager):
    def __init__(self, on_update=None, on_event=None, on_particle_dead=None, 
                 particles_data=None, ignore_time=False, redraw=None, layer=None):
        # ...
    
    def create(self, displayable):
        """Создать новую частицу"""
        
    def reset(self):
        """Сбросить систему"""
        
    def freeze(self):
        """Заморозить обновления"""
        
    def unfreeze(self, redraw=True):
        """Разморозить обновления"""
```

### ParticlesData

Хранилище данных системы:

```python
class ParticlesData:
    particles_properties = {}   # Данные частиц
    images = []                 # Доступные изображения
    lifetime_type = None        # Тип времени жизни
    lifetime_timings = None     # Параметры времени жизни
    
    def get(self, key):
        return getattr(self, key, None)
```

## Множественные системы

### RenParticleFastGroup

Контейнер для нескольких систем:

```python
class RenParticleFastGroup(renpy.Displayable):
    def __init__(self, systems=None, redraw=None, layer=None):
        self.systems = systems or []
        self.systems_by_id = {}  # Доступ по ID
    
    def freeze_one(self, id):
        """Заморозить одну подсистему"""
        
    def unfreeze_one(self, id, redraw=True):
        """Разморозить одну подсистему"""
```

### Взаимодействие между системами

```python
class CrossSystemBehavior(_UpdateBehavior):
    target_system_id = None
    
    def __call__(self, context):
        # Получить целевую систему
        target = self.get_system(context, self.target_system_id)
        
        if target:
            # Создать частицу в другой системе
            sprite = target.create(target.particles_data.images[0])
            sprite.x = context.particle.x
            sprite.y = context.particle.y
        
        return UpdateState.Pass
```

## Трансформации частиц

### PropertyTween

Анимация свойств Transform:

```python
class PropertyTween(_Behavior):
    property = None         # Имя свойства
    time = 1.0             # Длительность
    start_value = 0.0      # Начальное значение
    end_value = 1.0        # Конечное значение
    warper = "linear"      # Функция интерполяции
    dynamic = None         # Словарь блоков
```

**Доступные warpers:**
- `linear`, `ease`, `easein`, `easeout`, `easeinout`
- `pause`, `bounce`, `spring`
- И другие из `renpy.atl.warpers`

### Использование в коде

```python
class MyTweenBehavior(_UpdateBehavior):
    def __call__(self, context):
        particle = context.particle
        
        # Добавить трансформацию
        particle.queue_transform(
            alpha=0.5,
            zoom=2.0,
            rotate=45
        )
        
        return UpdateState.Pass
```

## Производительность

### Оптимизация рендеринга

```python
# Быстрый путь рендеринга (без сложных эффектов)
cache.fast = (
    (r.forward is None) and
    (not r.mesh) and
    (not r.uniforms) and
    (not r.shaders) and
    (not r.properties) and
    (not r.xclipping) and
    (not r.yclipping)
)
```

### Советы по оптимизации

1. **Используйте oneshot для эмиттеров:**
```python
emitter spray oneshot:
    amount 100
```

2. **Ограничивайте частоту обновления:**
```python
redraw 0.016  # 60 FPS вместо максимальной
```

3. **Удаляйте мертвые частицы:**
```python
class MyBehavior(_UpdateBehavior):
    def __call__(self, context):
        if context.particle.lifetime <= 0:
            context.particle.destroy()
        return UpdateState.Pass
```

4. **Используйте кэширование:**
```python
rparticles as particles:
    cache  # Кэшировать рендеры
```

## Отладка

### Вывод информации о системе

```python
system = renparticles._fast_particles_entries.get("my_particles")
if system:
    print(system.get_info())
```

Выведет:
```
========================================
PARTICLES DATA:
----------------------------------------
redraw: 0.0
images: [...]
lifetime_type: range-random
lifetime_timings: (1.0, 3.0)
----------------------------------------
ON UPDATE:
  • <Move object>
    velocity = [0.0, 100.0]
    acceleration = [0.0, 50.0]
----------------------------------------
...
```

### Проверка состояния частиц

```python
class DebugBehavior(_UpdateBehavior):
    def __call__(self, context):
        particle = context.particle
        print(f"Particle at ({particle.x}, {particle.y}), lifetime: {particle.lifetime}")
        
        # Проверить данные частицы
        props = context.system.particles_data.particles_properties.get(particle, {})
        print(f"Particle data: {props}")
        
        return UpdateState.Pass
```

## Расширенные паттерны

### Пул частиц

```python
class ParticlePool:
    def __init__(self, system, size=100):
        self.system = system
        self.pool = []
        self.active = []
        
        # Предсоздать частицы
        for i in range(size):
            sprite = system.create(system.particles_data.images[0])
            sprite.live = False
            self.pool.append(sprite)
    
    def acquire(self):
        if self.pool:
            sprite = self.pool.pop()
            sprite.live = True
            self.active.append(sprite)
            return sprite
        return None
    
    def release(self, sprite):
        sprite.live = False
        self.active.remove(sprite)
        self.pool.append(sprite)
```

### Цепочки поведений

```python
class BehaviorChain(_UpdateBehavior):
    behaviors = _RequiredField()  # Список поведений
    
    def __call__(self, context):
        for behavior in self.behaviors:
            result = behavior(context)
            if result == UpdateState.Kill:
                return UpdateState.Kill
        return UpdateState.Pass
```

### Условные поведения

```python
class ConditionalBehavior(_UpdateBehavior):
    condition = _RequiredField()  # Функция условия
    true_behavior = _RequiredField()
    false_behavior = None
    
    def __call__(self, context):
        if self.condition(context):
            return self.true_behavior(context)
        elif self.false_behavior:
            return self.false_behavior(context)
        return UpdateState.Pass
```

## API Reference

### Основные константы

```python
class UpdateState:
    Pass = 1000      # Продолжить
    Repeat = 2000    # Повторить (не используется)
    Kill = 3000      # Удалить поведение

class BehaviorType:
    Function = 1500
    Emitter = 2500
```

### Утилиты

```python
def _renp_lerp(start, end, t):
    """Линейная интерполяция"""
    return start + (end - start) * t

def _renp_clamp(value, min_value, max_value):
    """Ограничить значение диапазоном"""
    return max(min_value, min(max_value, value))
```

### Доступ к системам

```python
# Получить систему по тегу
system = renparticles._fast_particles_entries.get("my_tag")

# Получить модель
model = renparticles._fast_particles_models.get("my_model")

# Получить шорткат
behavior_class = renparticles.static_shortcuts["behaviors"]["move"]
```

## Соглашения о коде

1. **Именование:**
   - Классы: `PascalCase`
   - Функции/методы: `snake_case`
   - Константы: `UPPER_CASE`
   - Приватные поля: `_prefix`

2. **Инициализация приоритетов:**
   - Базовые классы: `init -2448`
   - Движок: `init -1337`
   - Поведения: `init -1115`
   - Шорткаты: `init -555`

3. **Обязательные поля:**
```python
required_field = _RequiredField()
```

4. **Уникальные ключи данных:**
```python
_MY_KEY = "_my_key"
_COUNTER = 0

def __init__(self):
    self._MY_KEY = f"{self._MY_KEY}_{self._COUNTER}"
    self._COUNTER += 1
```

## Примеры реализации

### Гравитация

```python
init -1000 python in renparticles:
    class Gravity(_UpdateBehavior):
        strength = 500.0
        direction = [0.0, 1.0]  # Вниз
        
        _VELOCITY_KEY = "_gravity_vel"
        _COUNTER = 0
        
        def __init__(self):
            self._VELOCITY_KEY = f"{self._VELOCITY_KEY}_{self._COUNTER}"
            self._COUNTER += 1
        
        def __call__(self, context):
            particle = context.particle
            delta = context.delta
            props = context.system.particles_data.particles_properties
            
            particle_data = props.setdefault(particle, {})
            if self._VELOCITY_KEY not in particle_data:
                particle_data[self._VELOCITY_KEY] = [0.0, 0.0]
            
            vel = particle_data[self._VELOCITY_KEY]
            vel[0] += self.direction[0] * self.strength * delta
            vel[1] += self.direction[1] * self.strength * delta
            
            particle.x += vel[0] * delta
            particle.y += vel[1] * delta
            
            return UpdateState.Pass
```

### Столкновения с границами

```python
class BoundsCollision(_UpdateBehavior):
    bounce_factor = 0.8
    
    _VELOCITY_KEY = "_bounds_vel"
    
    def __call__(self, context):
        particle = context.particle
        system = context.system
        props = context.system.particles_data.particles_properties
        
        particle_data = props.get(particle, {})
        vel = particle_data.get(self._VELOCITY_KEY, [0.0, 0.0])
        
        # Проверка границ
        if particle.x < 0:
            particle.x = 0
            vel[0] = abs(vel[0]) * self.bounce_factor
        elif particle.x > system.width:
            particle.x = system.width
            vel[0] = -abs(vel[0]) * self.bounce_factor
        
        if particle.y < 0:
            particle.y = 0
            vel[1] = abs(vel[1]) * self.bounce_factor
        elif particle.y > system.height:
            particle.y = system.height
            vel[1] = -abs(vel[1]) * self.bounce_factor
        
        return UpdateState.Pass
```

### Следование за целью

```python
class FollowTarget(_UpdateBehavior):
    target_pos = _RequiredField()  # [x, y] или функция
    speed = 100.0
    
    def __call__(self, context):
        particle = context.particle
        delta = context.delta
        
        # Получить позицию цели
        if callable(self.target_pos):
            tx, ty = self.target_pos()
        else:
            tx, ty = self.target_pos
        
        # Направление к цели
        dx = tx - particle.x
        dy = ty - particle.y
        dist = math.hypot(dx, dy)
        
        if dist > 0:
            # Нормализовать и применить скорость
            nx = dx / dist
            ny = dy / dist
            
            particle.x += nx * self.speed * delta
            particle.y += ny * self.speed * delta
        
        return UpdateState.Pass
```

Эта документация покрывает основы расширения RenParticles. Для более сложных случаев изучите исходный код существующих поведений в директории `Particles Implementation`.
