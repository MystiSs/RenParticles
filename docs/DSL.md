# RenParticles DSL - Руководство пользователя

## Введение

RenParticles — это система частиц для Ren'Py с собственным DSL (предметно-ориентированным языком). Вместо написания Python-кода вы описываете поведение частиц декларативно, используя простой синтаксис.

## Быстрый старт

```renpy
rparticles as my_particles onlayer master zorder 1:
    sprite expr Solid("#ff0000", xysize=(12, 12))
    lifetime range random (1.0, 3.0)
    redraw asap
    
    preset spray:
        amount 100
    
    preset auto_expire
```

Этот код создаст 100 красных квадратных частиц со случайным временем жизни от 1 до 3 секунд.

## Основной синтаксис

### Объявление системы частиц

```renpy
rparticles [model "model_name"] [as tag] [onlayer layer_name] [zorder z] [multiple]:
    # содержимое системы
```

**Параметры:**
- `model "name"` — использовать предопределенную модель
- `as tag` — тег для управления системой (по умолчанию `rparticles_displayable`)
- `onlayer layer_name` — слой отображения (по умолчанию `master`)
- `zorder z` — порядок отрисовки (по умолчанию `0`)
- `multiple` — создать группу из нескольких подсистем

### Спрайты частиц

Определяют внешний вид частиц:

```renpy
sprite image_tag
sprite expr Solid("#ff0000", xysize=(12, 12))
sprite image1; image2; expr Solid("#00ff00", xysize=(8, 8))
```

- Обычный тег изображения: `sprite my_particle_image`
- Python-выражение: `sprite expr <expression>`
- Несколько вариантов через `;` — система выберет случайный

### Время жизни частиц

```renpy
lifetime constant 2.0
lifetime range random (1.0, 3.0)
```

- `constant <число>` — фиксированное время жизни
- `range random (<мин>, <макс>)` — случайное время в диапазоне

### Частота обновления

```renpy
redraw 0.0          # максимальная частота
redraw asap         # то же самое
redraw 0.016        # ~60 FPS
redraw None         # обновление по умолчанию
```

Меньшее значение = более плавная анимация, но выше нагрузка.

## Блоки поведения

### on update

Выполняется каждый кадр для каждой частицы:

```renpy
on update:
    move:
        velocity [0.0, 100.0]
        acceleration [0.0, 50.0]
    
    auto_expire
```

### on event

Реагирует на события мыши:

```renpy
on event:
    repulsor_event
```

### on particle dead

Выполняется когда частица умирает:

```renpy
on particle dead:
    emitter spray:
        amount 3
```

## Эмиттеры

Эмиттеры создают новые частицы.

### spray

Создает частицы единовременно:

```renpy
emitter spray oneshot:
    amount 100
    area (0, 0, 1920, 1080)
```

**Параметры:**
- `amount` — количество частиц (обязательно)
- `area` — область генерации `(x1, y1, x2, y2)` (по умолчанию весь экран)

### interval_spray

Создает частицы с интервалом:

```renpy
emitter interval_spray:
    amount 500
    interval 0.05
    per_amount 10
```

**Параметры:**
- `amount` — общее количество частиц
- `interval` — интервал между генерациями (секунды)
- `per_amount` — частиц за раз (по умолчанию 1)
- `kill_on_finish` — удалить эмиттер после завершения (по умолчанию True)

### fragmentation / interval_fragmentation_per_particle

Создает частицы в позиции существующей частицы:

```renpy
emitter interval_fragmentation_per_particle system "target_system":
    amount 1
    interval 0.1
```

**Параметры:**
- `amount` — частиц за раз
- `interval` — интервал генерации
- `system "id"` — ID целевой системы (для множественных систем)

## Поведения частиц

### auto_expire

Автоматически уменьшает время жизни и удаляет частицы:

```renpy
auto_expire
```

### move

Движение с ускорением:

```renpy
move:
    velocity [100.0, 0.0]
    velocity_range [50.0, 50.0]
    acceleration [0.0, 200.0]
    acceleration_range [10.0, 10.0]
```

**Параметры:**
- `velocity [x, y]` — начальная скорость
- `velocity_range [x, y]` — случайное отклонение скорости (±)
- `acceleration [x, y]` — ускорение
- `acceleration_range [x, y]` — случайное отклонение ускорения (±)

### oscillate

Колебательное движение:

```renpy
oscillate:
    amplitudes [100.0, 50.0]
    amplitudes_range [20.0, 10.0]
    frequencies [2.0, 1.0]
```

**Параметры:**
- `amplitudes [x, y]` — амплитуда колебаний
- `amplitudes_range [x, y]` — случайное отклонение амплитуды
- `frequencies [x, y]` — частота колебаний
- `phases [x, y]` — начальная фаза

### orbit_mouse

Частицы вращаются вокруг курсора:

```renpy
orbit_mouse:
    radius 150.0
    speed 5.0
    pull_strength 0.3
    clockwise True
    screen_bounds True
```

**Параметры:**
- `radius` — радиус орбиты (по умолчанию 100)
- `speed` — скорость вращения (по умолчанию 10)
- `speed_variance` — разброс скорости (по умолчанию 0.5)
- `pull_strength` — сила притяжения к орбите (по умолчанию 0.5)
- `clockwise` — направление вращения (по умолчанию True)
- `screen_bounds` — ограничить экраном (по умолчанию True)

### repulsor_update / repulsor_event

Отталкивание от курсора:

```renpy
on update:
    repulsor_update:
        strength 5.0
        radius 200.0

on event:
    repulsor_event
```

**Параметры:**
- `strength` — сила отталкивания (по умолчанию 3.0)
- `radius` — радиус действия (по умолчанию 150.0)
- `clamp_margin` — отступ от краев экрана (по умолчанию 2.0)

### tween

Анимация свойств Transform:

```renpy
tween:
    block "alpha":
        time 1.0
        start_value 1.0
        end_value 0.0
    
    block "zoom":
        time 0.5
        start_value 2.0
        end_value 1.0
        warper "ease"
```

**Параметры блока:**
- `time` — длительность анимации (секунды)
- `start_value` — начальное значение
- `end_value` — конечное значение
- `warper` — функция интерполяции (по умолчанию "linear")

**Доступные свойства:** alpha, zoom, xzoom, yzoom, rotate, xpos, ypos и другие свойства Transform.

## Пресеты

Пресеты — готовые комбинации поведений.

### Встроенные пресеты

```renpy
preset spray:
    amount 100

preset interval_spray:
    amount 500
    interval 0.05

preset auto_expire

preset repulsor:
    strength 5.0
    radius 200.0

preset orbit_mouse:
    speed 10.0
    pull_strength 0.5
```

### Создание собственных пресетов

```renpy
init 100:
    rparticles define preset my_preset type general:
        on update:
            move:
                velocity [0.0, 100.0]
                acceleration [0.0, 50.0]
            
            tween:
                block "alpha":
                    time 1.0
```

**Типы пресетов:**
- `type general` — используется на верхнем уровне системы
- `type inner` — используется внутри блоков on update/event/particle dead

## Множественные системы

Создание нескольких независимых систем частиц:

```renpy
rparticles multiple as particles onlayer master:
    redraw asap
    
    system id "fire":
        sprite expr Solid("#ff4400", xysize=(8, 8))
        lifetime constant 1.0
        
        preset interval_spray:
            amount 100
            interval 0.01
        
        on update:
            move:
                velocity [0.0, -100.0]
            auto_expire
    
    system id "sparks":
        sprite expr Solid("#ffff00", xysize=(4, 4))
        lifetime range random (0.5, 1.5)
        
        preset spray:
            amount 50
        
        on update:
            move:
                velocity [0.0, 0.0]
                velocity_range [200.0, 200.0]
            auto_expire
```

Взаимодействие между системами:

```renpy
on update:
    interval_fragmentation_per_particle system "sparks":
        amount 3
        interval 0.2
```

## Модели (шаблоны)

Сохранение конфигурации для повторного использования:

```renpy
init:
    rparticles define "explosion_effect":
        sprite expr Solid("#ff0000", xysize=(16, 16))
        lifetime range random (0.5, 1.5)
        redraw asap
        
        preset spray:
            amount 200
        
        on update:
            move:
                velocity [0.0, 0.0]
                velocity_range [300.0, 300.0]
                acceleration [0.0, 500.0]
            
            tween:
                block "alpha":
                    time 1.0
                block "zoom":
                    time 1.0
                    start_value 1.5
                    end_value 0.0
            
            auto_expire

label game:
    # Использование модели
    rparticles model "explosion_effect" as explosion1
```

## Управление системами

### Команды управления

```renpy
# Показать систему
rparticles model "my_model" as particles

# Сбросить систему (удалить все частицы, перезапустить эмиттеры)
rparticles reset "particles"

# Заморозить систему (остановить обновление)
rparticles freeze "particles"

# Разморозить систему
rparticles unfreeze "particles"
rparticles unfreeze "particles" noredraw

# Управление подсистемами
rparticles freeze "particles"."fire"
rparticles unfreeze "particles"."sparks" noredraw

# Скрыть систему
hide particles

# Показать снова
rparticles continue "particles" onlayer master zorder 1

# Очистить кэш
rparticles clear cache        # удалить скрытые системы
rparticles clear cache deep   # удалить все системы
```

## Продвинутые возможности

### Пользовательские функции

Вместо шорткатов можно использовать Python-функции:

```renpy
on update:
    custom my_custom_behavior oneshot
    custom my_custom_behavior system "target_system"
```

### Модификатор oneshot

Выполнить поведение один раз:

```renpy
on update:
    emitter spray oneshot:
        amount 100
```

### Динамические свойства

Для сложных конфигураций:

```renpy
tween:
    block "alpha":
        time 0.5
    block "zoom":
        time 1.0
        start_value 2.0
        end_value 0.5
        warper "easein"
```

## Примеры

### Простой дождь

```renpy
rparticles as rain onlayer master:
    sprite expr Solid("#4488ff", xysize=(2, 8))
    lifetime constant 3.0
    redraw 0.016
    
    preset interval_spray:
        amount 1000
        interval 0.01
        per_amount 5
    
    on update:
        move:
            velocity [0.0, 500.0]
        auto_expire
```

### Фейерверк

```renpy
rparticles as firework onlayer master:
    sprite expr Solid("#ff0000", xysize=(6, 6))
    lifetime range random (1.0, 2.0)
    redraw asap
    
    preset spray:
        amount 300
    
    on update:
        move:
            velocity [0.0, 0.0]
            velocity_range [400.0, 400.0]
            acceleration [0.0, 600.0]
        
        tween:
            block "alpha":
                time 1.5
        
        auto_expire
```

### Магический эффект

```renpy
rparticles as magic onlayer master:
    sprite expr Solid("#aa00ff", xysize=(12, 12))
    lifetime range random (2.0, 4.0)
    redraw asap
    
    preset interval_spray:
        amount 200
        interval 0.02
    
    on update:
        orbit_mouse:
            radius 100.0
            speed 8.0
            pull_strength 0.2
        
        tween:
            block "alpha":
                time 2.0
        
        auto_expire
```

## Советы по производительности

1. Используйте `redraw 0.016` вместо `asap` если не нужна максимальная частота
2. Ограничивайте количество одновременных частиц
3. Используйте `lifetime` для автоматического удаления частиц
4. Для статичных эффектов используйте `cache`
5. Группируйте похожие частицы в одну систему

## Отладка

Система выводит информацию о конфигурации в консоль при создании. Проверьте консоль Ren'Py для диагностики проблем.

## Ограничения

- Спрайты рисуются со смещением `размер_спрайта / 2` от указанной позиции
- Рекурсивные пресеты не поддерживаются
- Максимальная производительность зависит от количества частиц и сложности поведений
