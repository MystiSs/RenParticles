# RenParticles - Руководство разработчика

---

## Архитектура системы

RenParticles построен на трех уровнях:

1. **DSL Parser** (`01renparticles_cds.rpy`) — парсит декларативный синтаксис
2. **Core Engine** (`renparticles_fast.rpy`) — управляет частицами и рендерингом
3. **Behaviors & Emitters** — расширяемые компоненты поведения

---

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

---

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

---

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

---

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

>Вы можете хранить данные о частице как вам угодно. Например, в самом классе частиц. Но стандарт – particles_properties. Таким образом, если вам понадобится изменение свойств группы частиц при обновлении для одной частицы, вы сможете обратиться к particles_properties и выполнить итерацию по доступным частицам.

---

## Создание эмиттеров

Эмиттеры отвечают за генерацию новых частиц в системе. В RenParticles существует два архитектурных подхода к созданию эмиттеров в зависимости от требуемой логики.

### 1. Стандартный эмиттер (Класс `Emitter`)

Предназначен для массовой генерации частиц независимо от состояния других объектов.

```python
class MyEmitter(Emitter):
    # Обязательные поля (вызовут ошибку при отсутствии в DSL)
    amount = _RequiredField() 
    
    # Значения по умолчанию
    spawn_area = (0, 0, 1920, 1080)
    
    def __call__(self, context):
        system = context.system
        images = system.particles_data.images
        
        for i in range(self.amount):
            # Создание спрайта на основе случайного изображения системы
            sprite = system.create(random.choice(images))
            
            # Определение начальных координат
            sprite.x = random.randint(self.spawn_area[0], self.spawn_area[2])
            sprite.y = random.randint(self.spawn_area[1], self.spawn_area[3])
            
            # Установка технических свойств спрайта (RenSprite)
            sprite.zorder = i
        
        return UpdateState.Pass

```

**Особенности архитектуры:**

* **Изоляция**: При инициализации системы эмиттеры отделяются от общего блока `on update` и помещаются в специальный приоритетный список.
* **Оптимизация**: Они вызываются **вне** цикла итерации по живым частицам.
* **Контекст**: Атрибут `context.particle` всегда равен `None`. Это сделано для исключения избыточных проверок и повышения FPS при генерации больших групп объектов.

### 2. Потоковый эмиттер (Класс `_Behavior`)

Используется, когда создание новых частиц должно зависеть от состояния «родительской» частицы (например, создание следа/trails или фрагментация при взрыве).

**Механика работы:**

* Наследуется напрямую от `_Behavior` (или `_UpdateBehavior`).
* В DSL объявляется **без** ключевого слова `emitter`.
* Вызывается внутри цикла обновления частиц, поэтому имеет доступ к `context.particle`.

> **Пример реализации:** Класс `EmitterIntervalRemoteSpawn` использует этот подход, чтобы считывать координаты текущей частицы и передавать их в качестве точки рождения для частиц в другой системе.

**Другой пример:**

```python
class MyEmitterPerParticle(_Behavior): # Потоковый эмиттер
    # Обязательные поля (вызовут ошибку при отсутствии в DSL)
    amount = _RequiredField() 
    
    # Значения по умолчанию
    spawn_area = (0, 0, 1920, 1080)
    
    def __call__(self, context):
        system = context.system
        images = system.particles_data.images
        particle = context.particle # Контекст гарантированно имеет ссылку на текущую частицу
        ...
```

### Сравнение типов эмиттеров

| Характеристика | Стандартный (`Emitter`) | Потоковый (`_Behavior`) |
| --- | --- | --- |
| **DSL ключевое слово** | `emitter <name>` | `<name>` |
| **Место в цикле** | Вне цикла частиц (отдельный список) | Внутри цикла частиц |
| **Доступ к `context.particle`** | **Нет** (`None`) | **Да** (текущая частица) |
| **Основное назначение** | Глобальный спавн, дожди, взрывы | Следы, искры от частиц, деление |
| **Влияние на CPU** | Минимальное (вызов раз в кадр) | Зависит от количества частиц (N вызовов) |

---

## Создание пресетов (Presets)

**Пресеты** в RenParticles — это высокоуровневые обертки, которые группируют несколько поведений (`Behaviors`) и эмиттеров, предоставляя удобный интерфейс для настройки через DSL.

### 1. Базовая архитектура пресета

Класс пресета наследуется от `_RFBehaviorPreset`. Его основная задача — инициализировать список классов поведений и распределить параметры из DSL между этими экземплярами.

**Жизненный цикл пресета:**

1. **Инициализация**: Парсер DSL создает экземпляр пресета и записывает в него параметры.
2. **`.build()`**: Вызывается движком автоматически.
3. **`.instanciate_behaviors()`**: Превращает списки классов в работающие экземпляры.
4. **`.distribute_properties()`**: (Вы переопределяете это) Передает значения из пресета в конкретные поведения через `inject_properties`.

### 2. Пример создания пресета (`RepulsorPreset`)

Рассмотрим пресет, который объединяет логику обновления частиц и обработку событий мыши.

```python
class RepulsorPreset(_RFBehaviorPreset):
    # 1. Определяем набор поведений
    behaviors = {
        "on_update": [RepulsorUpdate], # Класс логики отталкивания
        "on_event": [RepulsorEvent],   # Класс записи координат мыши
        "on_particle_dead": None
    }

    # 2. Объявляем параметры, которые будут доступны в DSL
    repulsor_pos = None
    strength = 3.0
    radius = 150.0
    clamp_margin = 2.0

    # 3. Распределяем данные
    def distribute_properties(self):
        # Всегда вызываем super для проверки _RequiredField()
        super(RepulsorPreset, self).distribute_properties()

        # Получаем экземпляр первого поведения из списка on_update
        update_logic = self.behaviors["on_update"][0]
        
        # Передаем свойства внутрь поведения
        update_logic.inject_properties(
            repulsor_pos=self.repulsor_pos, 
            strength=self.strength, 
            radius=self.radius, 
            clamp_margin=self.clamp_margin
        )

```

### 3. Специальные типы пресетов

| Тип | Класс-родитель | Описание |
| --- | --- | --- |
| **Простой пресет** | `_RFBehaviorPreset` | Жестко заданная структура поведений на Python. |
| **Динамический** | `_RFDynamicBehaviorPreset` | Используется парсером для создания пресетов «на лету» через DSL команду `rparticles define preset`. |

### 4. Полезные методы `_RFBehaviorPreset`

При написании сложной логики распределения свойств вам могут пригодиться встроенные методы:

* **`self.is_one_block()`**: Возвращает `True`, если пресет содержит только одно поведение во всех категориях. Полезно для упрощенной инъекции свойств.
* **`self.get_one()`**: Возвращает первое найденное поведение.
* **`self.check_initialised()`**: Автоматически проверяет, были ли заполнены все поля, помеченные как `_RequiredField()`. Вызывается внутри `super(_RFBehaviorPreset, self).distribute_properties()`.

### 5. Рекомендации по реализации

* **Копирование словаря**: В конструкторе `__init__` базовый класс делает `self.behaviors.copy()`. Это критически важно: если этого не делать, изменение списка поведений в одном экземпляре пресета изменит его для всех будущих систем.
* **Порядок в списках**: Если в `on_update` указано несколько поведений, обращайтесь к ним по индексам в `distribute_properties`, либо используйте циклы для массовой настройки.
* **Oneshot-пресеты**: Если установить флаг `m_oneshot = True`, пресет будет выполнен один раз (полезно для мгновенных импульсов или разовых выбросов частиц).

---

## Регистрация компонентов

Чтобы ваши кастомные поведения, эмиттеры или пресеты стали доступны для использования внутри DSL (например, `on update: my_behavior`), их необходимо зарегистрировать в системе шорткатов.

Система разделяет регистрацию на два типа: **статическую** (ядро) и **динамическую** (пользовательские расширения).

### 1. Статические шорткаты

Статические шорткаты определены в файле `fast_particles.rpy` внутри словаря `static_shortcuts`.

> **Важно:** Крайне не рекомендуется изменять этот словарь напрямую в исходных файлах движка.

Если вам необходимо вручную добавить статический шорткат, вы можете сделать это из своего файла, обратившись к пространству имен `renparticles`:

```python
init 1 python:
    # Пример ручного добавления в статический словарь
    renparticles.static_shortcuts["behaviors"]["global_wind"] = MyWindBehavior

```

### 2. Динамическая регистрация (Рекомендуется)

Для добавления пользовательских компонентов используйте встроенные функции регистрации. Они автоматически проверяют корректность типов и предотвращают случайную перезапись существующих тегов.

```python
init python in renparticles:
    # Регистрация поведения (должно наследоваться от _Behavior)
    # Тег: "fire_logic", Класс: FireUpdate
    add_shortcut("fire_logic", FireUpdate, is_emitter=False)
    
    # Регистрация эмиттера (должно наследоваться от Emitter или _Behavior)
    add_shortcut("spark_emitter", SparkEmitter, is_emitter=True)
    
    # Регистрация пресета (должно наследоваться от _RFDynamicBehaviorPreset или от _RFBehaviorPreset)
    # preset_type может быть "general" или "inner"
    add_preset("magic_circle", MagicPreset, preset_type="general")

```

### 3. Технические нюансы регистрации

* **Валидация типов**: Функции `add_shortcut` и `add_preset` выбрасывают `TypeError`, если регистрируемый класс не является наследником соответствующих базовых классов (`_Behavior`, `_RFDynamicBehaviorPreset` или `_RFBehaviorPreset`).
* **Предотвращение конфликтов**: Если вы попытаетесь зарегистрировать тег, который уже существует в `dynamic_shortcuts`, система выдаст критическую ошибку `renpy.error`, чтобы избежать непредсказуемого поведения системы частиц.
* **Приоритеты**: При поиске компонента парсер DSL сначала проверяет статические шорткаты, а затем динамические. Таким образом системные поведения всегда в приоритете.

### 4. Порядок инициализации (Приоритеты)

Для корректной работы регистрации используйте следующие уровни `init`:

* **Ядро системы**: `init -1337` (определяет функции регистрации).
* **Статические шорткаты**: `init -555` (базовый набор движка).
* **Пользовательские компоненты**: Рекомендуется использовать `init` без индекса или выше `-555`, чтобы гарантировать, что словари шорткатов уже созданы.

---

## Работа с частицами

### RenSprite

`RenSprite` — это расширенный класс стандартного `Sprite` из движка Ren'Py. Он поддерживает отложенное применение трансформаций.

```python
class RenSprite(Sprite):
    lifetime = 0.0          # Текущее оставшееся время жизни
    lifetime_max = 0.0      # Начальное время жизни (устанавливается движком)
    _base_image = None      # Исходное изображение без трансформаций
    
    def queue_transform(self, **properties):
        """Заменяет свойства в очереди на новые."""
        self.queued_transforms.update(properties)
    
    def queue_transform_additive(self, **properties):
        """Складывает новые свойства с уже стоящими в очереди."""
        # Поддерживает числа (int/float) и векторы (list/tuple)

```

**Доступные свойства:**

* **`x, y`** (целое или вещественное число): Координаты центра частицы на экране.
* **`zorder`** (целое число): Порядок отрисовки (чем выше, тем ближе к игроку).
* **`live`** (логическое значение): Статус частицы. Если `False`, система удалит её в следующем кадре.
* **`lifetime`** (целое или вещественное число): Оставшееся время жизни в секундах.
* **`lifetime_max`** (целое или вещественное число): Оставшееся время жизни в секундах. Базовые обработчики не изменяют этот атрибут. Не рекомендуется его изменять в принципе.
* **`events`** (логическое значение): Флаг, разрешающий частице реагировать на события (по умолчанию `False` для оптимизации).

---

### Управление визуализацией

Система использует **отложенную отрисовку** (Lazy Rendering). Вместо того чтобы перерисовывать `Transform` при каждом изменении `alpha` или `zoom`, `RenSprite` накапливает изменения.

#### Методы трансформации:

1. **`.queue_transform(**props)`**: Используется для установки абсолютных значений. Если два поведения пытаются установить `alpha`, победит последнее.
2. **`.queue_transform_additive(**props)`**: Складывает значения. Позволяет нескольким независимым поведениям одновременно влиять на одно свойство (например, два разных обработчика трансформаций, влияющих на `zoom`. Но эти самые обработчики должны в своей реализации использовать `.queue_transform_additive(**props)`. Например, `tween` обработчик использует `.queue_transform(**props)`, а значит два `tween` обработчика будут соревноваться за изменение одного и того же свойства (побеждает последний добавленный в блок обработки)).

> **Важно:** Система автоматически вызывает `apply_transforms()` в конце цикла обновления. Она берет `_base_image` (копию оригинального спрайта) и один раз применяет к нему все накопленные свойства через `Transform`.

### Практический пример: Создание и настройка

Внутри метода `__call__` вашего поведения или эмиттера вы взаимодействуете с частицами через объект системы:

```python
def __call__(self, context):
    system = context.system
    
    # 1. Создание частицы из пула доступных изображений
    # system.create возвращает экземпляр RenSprite
    sprite = system.create(random.choice(system.particles_data.images))
    
    # 2. Прямое управление позицией и состоянием
    sprite.x = 960
    sprite.y = 540
    sprite.zorder = 10
    sprite.lifetime = 2.0  # Установка времени жизни вручную
    
    # 3. Работа с визуальными эффектами
    # Устанавливаем начальный масштаб и прозрачность
    sprite.queue_transform(alpha=0.0, zoom=0.5)
    
    # 4. Удаление частицы
    # Вызов destroy() не удаляет объект мгновенно, а помечает его
    # как 'live = False' для безопасной очистки движком
    if some_condition:
        sprite.destroy()
        
    return UpdateState.Pass

```

### Нюанс с `set_child`

Если вы динамически меняете изображение частицы через `set_child(d)`, поле `_base_image` автоматически сбрасывается в `None`. Это заставляет систему захватить новое изображение как базовое при следующем вызове трансформации.

---

## Система частиц: Ядро

### 1. RenParticlesFast

Это основной управляющий класс, унаследованный от `SpriteManager`. Он координирует жизненный цикл всех частиц, вызывает поведения и управляет рендерингом.

**Ключевые механизмы:**

* **Очередь создания**: Метод `create()` не добавляет спрайт в общий список немедленно, а помещает его в `particles_queue`. Это гарантирует стабильность цикла итерации во время обновления.
* **Автоматический Redraw**: Если установлен параметр `redraw`, система сама запрашивает перерисовку через `renpy.redraw`.
* **Управление временем**: Через `delta` (разница между текущим и прошлым кадром) обеспечивается независимость скорости частиц от FPS.

**Основные методы:**

* `reset()`: Полная очистка системы. Удаляет все частицы и очищает их свойства в `particles_properties`, возвращая систему в исходное состояние. При этом она сбрасывает все обработчики и эмиттеры. Обработчики, которые находились в `oneshotted_...` списках снова попадут в списки блоков обработки.
* `freeze() / unfreeze()`: Позволяет временно остановить обновление логики (пауза), сохраняя текущее состояние частиц на экране.

### 2. ParticlesData

Объект-контейнер, который хранит настройки и состояние конкретной системы.

```python
class ParticlesData:
    particles_properties = {}   # Dictionary: {particle_instance: {custom_data}}
    images = []                 # Список Displayables для спавна
    lifetime_type = None        # "constant" или "range-random"
    lifetime_timings = None     # Значение или [min, max]

```

**Важно для разработчика:**
Используйте словарь `particles_properties` для хранения любых специфических данных частицы (например, её текущий вектор скорости или фазу анимации). При смерти частицы система автоматически очищает этот словарь, предотвращая утечки памяти.

---

## Множественные системы

### 1. RenParticleFastGroup

Этот класс позволяет объединять несколько независимых систем частиц в один `Displayable`. Это необходимо для создания сложных эффектов, где разные слои частиц (например, дым, огонь и искры) должны взаимодействовать или управляться как единое целое.

**Архитектурные особенности:**

* **ID-адресация**: Каждая система в группе может иметь уникальный `system_id` для быстрого доступа.
* **Сквозные контексты**: При инициализации группа пробрасывает ссылки на все соседние системы в контекст (`RenpFContext`), что позволяет поведениям "видеть" другие системы.
* **Blit-рендеринг**: Группа собирает рендеры всех подсистем и отрисовывает их через `subpixel_blit`.

### 2. Взаимодействие между системами

Благодаря миксину `_TryGetOtherSystemMixin`, любое поведение может получить доступ к другой системе в группе через её ID.

**Пример сценария: Fragmentation (Дробление)**
Когда частица в "Системе А" умирает или достигает определенного условия, она может дать команду "Системе Б" создать новую частицу в своих координатах.

```python
class RemoteSpawnBehavior(_UpdateBehavior):
    target_id = "sparks" # ID системы, где создадим частицу
    
    def __call__(self, context):
        # 1. Получаем доступ к соседней системе через контекст
        target_system = self.get_system(context, self.target_id)
        
        if target_system:
            # 2. Создаем частицу в целевой системе
            new_spark = target_system.create(random.choice(target_system.particles_data.images))
            
            # 3. Передаем координаты от текущей частицы
            new_spark.x = context.particle.x
            new_spark.y = context.particle.y
            
        return UpdateState.Pass

```

**Содержит методы `.freeze_one(id)` и `.unfreeze_one(id, redraw=True)`**: Замораживает одну из подсистем по переданному `id`. Если подсистема с `id` не найдена, то ничего не делает.
> **Важное примечание**: Вы можете заморозить одну из подсистем. Но будьте внимательны. Если другая подсистема создаёт частицы в замороженной подсистеме, то список `.particles_queue` накапливается и при разморозке подсистемы может произойти статтер, если частиц накопилось много.

## Техническая справка: Контексты выполнения

В RenParticles используется иерархия контекстов для передачи данных в методы `__call__`:

1. **`RenpFContext`**: Базовый (система, время, дельта, список всех систем).
2. **`UpdateEmitterContext`**: Используется эмиттерами (нет текущей частицы).
3. **`EventContext`**: Содержит данные о событии (`event`, координаты `x, y`).
4. **`ParticleDeadContext`**: Передается в обработчик `on_particle_dead`.

---

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
    
    mode = "absolute"      # Режим вычисления времени
    from_end = False       # Режим анимации

```

**Доступные warpers:**
- `linear`, `ease`, `easein`, `easeout`, `easeinout`
- `pause`, `bounce`, `spring`
- И другие из `renpy.atl.warpers`

---

## Производительность

### Оптимизация рендеринга (стандартный код RenPy из `SpriteManager.render(...)`)

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

3. **Удаляйте мертвые частицы (если не используете `auto_expire` пресет/обработчик):**
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

---

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

---

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

---

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
