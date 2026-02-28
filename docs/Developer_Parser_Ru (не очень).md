# RenParticles - Руководство разработчика по парсеру (DSL Parser)

## Введение

DSL парсер RenParticles реализован в файле `01renparticles_cds.rpy`. Он отвечает за разбор декларативного синтаксиса Ren'Py и преобразование его в внутренние структуры данных, которые затем оцениваются (evaluate) в Python-объекты системы частиц. Парсер использует встроенный лексер Ren'Py (`lexer`) для обработки ключевых слов, блоков и выражений.

**Ключевые принципы парсера:**
- **Декларативность**: DSL позволяет описывать системы частиц без прямого Python-кода, но парсер переводит это в вызовы классов behaviors, emitters и presets.
- **Иерархическая структура**: Поддерживает вложенные блоки (subblock_lexer) для `on update`, `on event`, `preset` и т.д.
- **Валидация**: Проверяет уникальность инструкций (например, только один `lifetime` или `on update`), обязательные поля и типы.
- **Расширяемость**: Легко добавить новые ключевые слова или statements через `renpy.register_statement`.
- **Ошибки**: Использует `renpy.error` для информативных сообщений об ошибках парсинга (например, "only one 'redraw' instruction allowed").

Парсер работает в два этапа:
1. **Parse**: Функции типа `renp_parse_...` разбирают лексемы и строят словарь данных.
2. **Execute**: Функции типа `renp_execute_...` оценивают данные, создают экземпляры классов и регистрируют их в глобальных структурах (например, `renparticles._fast_particles_models`).

## Структура модуля

### Классы и константы

#### _RenParserType
Определяет типы элементов DSL для внутренней классификации:
```python
class _RenParserType:
    Func = 333       # Пользовательские функции (custom)
    Shortcut = 666   # Шорткаты behaviors/emitters
    Emitter = 999    # Эмиттеры (emitter keyword)

    GeneralPreset = 1332  # Общие пресеты (preset type general)
    InnerPreset = 1665    # Внутренние пресеты (preset type inner)

    System = 8888    # Основная система
    SubSystem = 9999 # Подсистема в multiple

    PresetsTypes = (GeneralPreset, InnerPreset)
```
- Используется для различения в оценке (например, в `_renp_eval_on_block`).

#### _RenPKeywords
Внутренние ключи для словарей данных (используются в parse/execute):
```python
class _RenPKeywords:
    # ... (список ключей, таких как BEHAVIORS, FUNC, LAYER, LIFETIME и т.д.)
```
- Примеры: `ON_UPDATE` для блока обновления, `PRESETS` для списка пресетов.

#### _RenPLexerKeywords
Ключевые слова DSL, распознаваемые лексемой (lexer.keyword/match):
```python
class _RenPLexerKeywords:
    # ... (ONLAYER, ZORDER, PRESET, EMITTER, SYSTEM и т.д.)
```
- Алиасы: `redraw_asap_aliases` для "asap", "fastest" etc. → 0.0.

## Основные функции парсинга

### renp_parse_fast_particles_show(lexer)
Разбирает основной statement `rparticles` (показ системы):
- Поддерживает `model "name"` для загрузки предопределённой модели.
- Разбирает опции: `as tag`, `onlayer layer`, `zorder z`, `multiple`.
- Если multiple: парсит подсистемы (`system id "id": ...`).
- Возвращает словарь данных для execute.

### _renp_parse_common_system_content(subblock, data)
Общий парсер содержимого системы (для system/subsystem):
- Проверяет уникальность: только один `redraw`, `cache`, `sprite`, `lifetime`, `on update` etc.
- Парсит: `redraw`, `cache`, `sprite` (изображения), `lifetime` (тип/тайминги), `preset`, блоки `on ...`.
- Использует `seen` словарь для отслеживания дубликатов.

### _renp_parse_on_block(subblock)
Парсит блоки `on update/event/particle dead`:
- Поддерживает: `emitter name: ...`, `preset name: ...`, `custom Class: ...`, шорткаты (без ключевого слова).
- Возвращает список словарей для каждого элемента блока.

### _renp_parse_emitter_keyword(lexer)
Парсит `emitter name [oneshot] [system "id"]: ...`:
- Oneshot: флаг для разового выполнения.
- Target system: для cross-system спавна.
- Парсит свойства в блоке.

### _renp_parse_preset(lexer, preset_type=GeneralPreset)
Парсит `preset name [oneshot] [system "id"]: ...`:
- Различает general/inner пресеты.
- Парсит свойства и подблоки (on update etc.).

### _renp_parse_custom_keyword(lexer)
Парсит `custom Class [oneshot] [system "id"]`:
- Для прямого использования Python-классов.

### _renp_parse_shortcut(lexer)
Парсит шорткаты (например, `move: velocity [...]`):
- Ищет в static/dynamic shortcuts.
- Парсит свойства в блоке.

### _renp_parse_lifetime_keyword(lexer)
Парсит `lifetime constant 2.0` или `range random (1.0, 3.0)`.

### _renp_parse_sprites_keyword(lexer)
Парсит `sprite image; expr Solid(...)` (несколько через ;\).

## Функции оценки (execute)

### renp_execute_fast_particles_show(data)
Оценивает и показывает систему:
- Если модель: загружает из `_fast_particles_models`.
- Создаёт RenParticlesFast или RenParticleFastGroup.
- Регистрирует в `_fast_particles_entries`.
- Вызывает `renpy.show` и печатает info (для отладки).

### _renp_eval_system(system)
Оценивает систему: пресеты, behaviors, lifetimes, images.
- Мержит пресеты и блоки on ...
- Создаёт ParticlesData и RenParticlesFast.

### _renp_eval_on_block(on_block_data)
Оценивает блок: создаёт экземпляры behaviors/emitters/presets.
- Inject properties из DSL.

Другие execute: для `define`, `define preset`, `reset`, `freeze`, `unfreeze`, `clear cache`, `continue`.

## Расширенные паттерны и советы

### Добавление новых statements
Используйте `renpy.register_statement(name, parse_func, predict_func, execute_func, block=...)`.
- `parse_func`: возвращает dict данных.
- `execute_func`: создаёт/управляет объектами.

### Обработка ошибок
- `lexer.error(msg)` для синтаксиса.
- `renpy.error(msg)` для семантики (дубликаты, неизвестные шорткаты).

### Производительность парсера
- Минималистичный: использует subblock_lexer для вложенности.
- Нет рекурсии в пресетах (явно запрещено: "recursive presets are not allowed").

### Отладка
- Добавьте `print(data)` в parse/execute для инспекции.
- Используйте `system.get_info()` после показа.

Эта документация охватывает основы парсера. Для деталей изучите код: ключевые функции начинаются с `renp_parse_` / `_renp_`. Если добавляете фичи, обновляйте `_RenPLexerKeywords` и shortcuts.