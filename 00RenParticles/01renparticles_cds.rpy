# RenParticles - Particle System for Ren'Py
# Copyright (c) 2026 MystiSs
# Licensed under the MIT License.


python early:
    import re


    class _RenParserType:
        Func = 333
        Shortcut = 666
        Emitter = 999

        GeneralPreset = 1332
        InnerPreset = 1665

        System = 8888
        SubSystem = 9999

        PresetsTypes = (GeneralPreset, InnerPreset)

    class _RenPKeywords:
        BEHAVIORS = "behaviors"
        FUNC = "func"
        LAYER = "layer"
        LIFETIME = "lifetime"
        MULTIPLE = "multiple"
        ON_EVENT = "on_event"
        ON_PARTICLE_DEAD = "on_particle_dead"
        ON_UPDATE = "on_update"
        ONESHOT = "oneshot"
        PRESETS = "presets"
        PROPERTIES = "properties"
        REDRAW = "redraw"
        CACHE = "cache"
        SHORTCUT = "shortcut"
        SHORTCUTS_BLOCK = "shortcuts_block"
        GENERAL_SHORTCUTS = "general"
        INNER_SHORTCUTS = "inner"

        PRESET_NAME = "preset_name"
        PRESET_TYPE = "preset_type"
        PRESET_DEFINE_DATA = "preset_define_data"

        SYSTEM_ID = "system_id"
        TARGET_SYSTEM = "renp_target_system"
        BEHAVIOR_ID = "renp_behavior_id"

        SPRITE = "sprite"
        IMAGES = "images"

        SUBSYSTEMS = "subsystems"
        TAG = "tag"
        MODEL_NAME = "model_name"
        BASE_NAME = "rparticles_displayable"
        TIMINGS = "timings"
        TYPE = "type"
        ZORDER = "zorder"

        POSSIBLE = "possible"

    class _RenPLexerKeywords:
        ONLAYER = "onlayer"
        ZORDER = "zorder"
        MULTIPLE = "multiple"

        PRESET = "preset"
        ON_UPDATE = "on update"
        ON_EVENT = "on event"
        ON_PARTICLE_DEAD = "on particle dead"

        PRESET_TYPE = "type"

        BEHAVIOR_ID = "id"

        EMITTER = "emitter"

        CUSTOM = "custom"

        RANDOM = "random"
        RANGE = "range"
        CONSTANT = "constant"

        SYSTEM = "system"
        TARGET_SYSTEM = "system"
        SUBSYSTEM_ID = "id"

        AS = "as"

        MODEL = "model"

        PROP_BLOCK = "block"

        NOREDRAW = "noredraw"
        DEEP = "deep"

    redraw_asap_aliases = {
        "asap",
        "fastest",
        "fast"
    }

    renp_renpy_reserved_words = { "move" }

    def renp_parse_fast_particles_show(lexer):
        data = {
            _RenPKeywords.TAG: None, 
            _RenPKeywords.LAYER: "master", 
            _RenPKeywords.ZORDER: "0", 
            _RenPKeywords.MULTIPLE: False, 
            _RenPKeywords.SUBSYSTEMS: [], 
            _RenPKeywords.REDRAW: "None"
        }

        if lexer.keyword(_RenPLexerKeywords.MODEL):
            data[_RenPKeywords.MODEL_NAME] = lexer.string()

            while not lexer.eol():
                if lexer.match(':'):
                    renpy.error("rparticles model show mode does not support redefining properties. Sub-block there is not allowed")
                data.update(_renp_try_parse_show_data_component(lexer))
            return data

        while not lexer.match(':'):
            show_component = _renp_parse_show_data_component(lexer)

            if show_component:
                data.update(show_component)
            elif lexer.keyword(_RenPLexerKeywords.MULTIPLE):
                data[_RenPKeywords.MULTIPLE] = True
            
            if lexer.eol():
                renpy.error("rparticles: subblock required")

        lexer.expect_eol()
        subblock = lexer.subblock_lexer()
        _renp_parse_renparticles_system_subblock(subblock, data)

        return data

    def _renp_try_parse_show_data_component(lexer):
        data = { }
        if lexer.keyword(_RenPLexerKeywords.AS):
            data[_RenPKeywords.TAG] = lexer.image_name_component()
        elif lexer.keyword(_RenPLexerKeywords.ONLAYER):
            data[_RenPKeywords.LAYER] = lexer.simple_expression()
        elif lexer.keyword(_RenPLexerKeywords.ZORDER):
            data[_RenPKeywords.ZORDER] = lexer.simple_expression()

        return data

    def _renp_parse_renparticles_system_subblock(subblock, data):
        if data[_RenPKeywords.MULTIPLE]:
            while subblock.advance():
                if subblock.keyword(_RenPKeywords.REDRAW):
                    data[_RenPKeywords.REDRAW] = _renp_parse_redraw(subblock)
                elif subblock.keyword(_RenPLexerKeywords.SYSTEM):
                    system_id = None
                    if subblock.keyword(_RenPLexerKeywords.SUBSYSTEM_ID):
                        system_id = subblock.string()

                    subblock.require(':')
                    subblock.expect_eol()
                    sub_data = _renp_get_default_system_data(_RenParserType.SubSystem)
                    sub_data[_RenPKeywords.SYSTEM_ID] = system_id
                    _renp_parse_common_system_content(subblock.subblock_lexer(), sub_data)
                    data[_RenPKeywords.SUBSYSTEMS].append(sub_data)
                else:
                    renpy.error("Multiple rparticles can only contain 'system:' blocks or 'redraw'. Got: " + subblock.rest())
                subblock.expect_eol()
        else:
            system_data = _renp_get_default_system_data(_RenParserType.System)
            if not _renp_parse_common_system_content(subblock, system_data):
                renpy.error("Unknown instruction in rparticles: " + subblock.rest())
            
            data.update(system_data)

        return data

    def _renp_get_default_system_data(system_type=_RenParserType.System):
        return {
            _RenPKeywords.PRESETS: [], 
            _RenPKeywords.ON_UPDATE: [], 
            _RenPKeywords.ON_EVENT: [], 
            _RenPKeywords.ON_PARTICLE_DEAD: [], 
            _RenPKeywords.IMAGES: [],
            _RenPKeywords.LIFETIME: None,
            _RenPKeywords.TYPE: system_type
        }

    def _renp_parse_common_system_content(subblock, data):
        seen = {
            _RenPKeywords.SPRITE: False, 
            _RenPKeywords.LIFETIME: False, 
            _RenPKeywords.ON_UPDATE: False, 
            _RenPKeywords.ON_EVENT: False, 
            _RenPKeywords.ON_PARTICLE_DEAD: False,
            _RenPKeywords.REDRAW: False,
            _RenPKeywords.CACHE: False,
        }

        while subblock.advance():
            if subblock.keyword(_RenPKeywords.REDRAW):
                if seen[_RenPKeywords.REDRAW]: 
                    subblock.error("only one 'redraw' instruction allowed")
                data[_RenPKeywords.REDRAW] = _renp_parse_redraw(subblock)
                seen[_RenPKeywords.REDRAW] = True

            elif subblock.keyword(_RenPKeywords.CACHE):
                if seen[_RenPKeywords.CACHE]: 
                    subblock.error("only one 'cache' instruction allowed")
                data[_RenPKeywords.CACHE] = "True"
                seen[_RenPKeywords.CACHE] = True
                subblock.expect_eol()

            elif subblock.keyword(_RenPKeywords.SPRITE):
                if seen[_RenPKeywords.SPRITE]: 
                    subblock.error("only one 'sprite' instruction allowed")
                data[_RenPKeywords.IMAGES] = _renp_parse_sprites_keyword(subblock)
                seen[_RenPKeywords.SPRITE] = True
            
            elif subblock.keyword(_RenPKeywords.LIFETIME):
                if seen[_RenPKeywords.LIFETIME]: 
                    subblock.error("only one 'lifetime' instruction allowed")
                data[_RenPKeywords.LIFETIME] = _renp_parse_lifetime_keyword(subblock)
                seen[_RenPKeywords.LIFETIME] = True

            elif subblock.keyword(_RenPLexerKeywords.PRESET):
                data[_RenPKeywords.PRESETS].append(_renp_parse_preset(subblock))

            elif subblock.match(_RenPLexerKeywords.ON_UPDATE):
                if seen[_RenPKeywords.ON_UPDATE]: 
                    subblock.error("only one 'on update' block allowed")
                data[_RenPKeywords.ON_UPDATE] = _renp_parse_on_block(subblock)
                seen[_RenPKeywords.ON_UPDATE] = True

            elif subblock.match(_RenPLexerKeywords.ON_EVENT):
                if seen[_RenPKeywords.ON_EVENT]: 
                    subblock.error("only one 'on event' block allowed")
                data[_RenPKeywords.ON_EVENT] = _renp_parse_on_block(subblock)
                seen[_RenPKeywords.ON_EVENT] = True

            elif subblock.match(_RenPLexerKeywords.ON_PARTICLE_DEAD):
                if seen[_RenPKeywords.ON_PARTICLE_DEAD]: 
                    subblock.error("only one 'on particle dead' block allowed")
                data[_RenPKeywords.ON_PARTICLE_DEAD] = _renp_parse_on_block(subblock)
                seen[_RenPKeywords.ON_PARTICLE_DEAD] = True
            
            else:
                return False
            
            subblock.expect_eol()
        return True

    def _renp_parse_redraw(lexer, was_redraw=False):
        if was_redraw:
            renpy.error("there can be only one 'redraw' instruction")
        
        for alias in redraw_asap_aliases:
            if lexer.keyword(alias):
                return "0.0"
        return lexer.float()

    def _renp_parse_on_block(subblock):
        block_data = [ ]

        subblock.require(':')
        on_block = subblock.subblock_lexer()

        while on_block.advance():
            if on_block.keyword(_RenPLexerKeywords.EMITTER):
                emitter_data = _renp_parse_emitter_keyword(on_block)
                block_data.append(emitter_data)

            elif on_block.keyword(_RenPLexerKeywords.PRESET):
                preset_data = _renp_parse_preset(on_block, _RenParserType.InnerPreset)
                block_data.append(preset_data)

            elif on_block.keyword(_RenPLexerKeywords.CUSTOM):
                func_data = _renp_parse_custom_keyword(on_block)
                block_data.append(func_data)

            #<Потенциальный шорткат>#
            else:
                shortcut_data = _renp_parse_shortcut(on_block)
                block_data.append(shortcut_data)

            on_block.expect_eol()
        
        #renpy.error("wih?\n{}".format(block_data))
        return block_data

    def renp_execute_fast_particles_show(data):
        is_model = _RenPKeywords.MODEL_NAME in data
        if is_model:
            model_name = data[_RenPKeywords.MODEL_NAME]
            model_data = renparticles._fast_particles_models.get(model_name, None)
            if model_data is None:
                renpy.error("the rparticles model named '{}' does not exist\n"
                            "Available static preset shortcuts: {}".format(model_name, renparticles._fast_particles_models.keys())
                            )
                return
            
            data = data.copy()
            data.update(model_data)

        tag = data.get(_RenPKeywords.TAG, None)
        layer = data[_RenPKeywords.LAYER]
        zorder = eval(data[_RenPKeywords.ZORDER])
        redraw = eval(data[_RenPKeywords.REDRAW])

        if data[_RenPKeywords.MULTIPLE]:
            subsystems = [_renp_eval_system(system) for system in data[_RenPKeywords.SUBSYSTEMS]]
            displayable = renparticles.RenParticleFastGroup(subsystems, redraw, layer)
        else:
            displayable = _renp_eval_system(data)

        print(displayable.get_info())
        
        true_tag = tag or _RenPKeywords.BASE_NAME
        renparticles._fast_particles_entries[true_tag] = displayable

        renpy.show(name=_RenPKeywords.BASE_NAME, tag=tag, what=displayable, layer=layer, zorder=zorder)

    def _renp_eval_system(system):
        on_update = [ ]
        on_event = [ ]
        images = _renp_eval_images(system[_RenPKeywords.IMAGES])

        on_update_preset = [ ]
        on_event_preset = [ ]
        on_particle_dead_preset = [ ]
        _renp_eval_high_level_presets(system[_RenPKeywords.PRESETS], on_update_preset, on_event_preset, on_particle_dead_preset)

        on_update = _renp_eval_on_block(system[_RenPKeywords.ON_UPDATE])
        on_event = _renp_eval_on_block(system[_RenPKeywords.ON_EVENT])
        on_particle_dead = _renp_eval_on_block(system[_RenPKeywords.ON_PARTICLE_DEAD])

        #<Merge lists>#
        on_update = on_update_preset + on_update
        on_event = on_event_preset + on_event
        on_particle_dead = on_particle_dead_preset + on_particle_dead

        lifetime_type = None
        lifetime_timings = None
        if system[_RenPKeywords.LIFETIME]:
            lifetime_type = system[_RenPKeywords.LIFETIME][_RenPKeywords.TYPE]
            lifetime_timings = eval(system[_RenPKeywords.LIFETIME][_RenPKeywords.TIMINGS])

        particles_data = renparticles.ParticlesData(images=images, tag=system.get(_RenPKeywords.TAG, None), lifetime_type=lifetime_type, lifetime_timings=lifetime_timings)
        system_instance = renparticles.RenParticlesFast(on_update,
                                                        on_event,
                                                        on_particle_dead,
                                                        particles_data,
                                                        eval(system.get(_RenPKeywords.CACHE, "False")),
                                                        eval(system.get(_RenPKeywords.REDRAW, "None")),
                                                        system.get(_RenPKeywords.LAYER, None)
                                                        )
        system_instance.system_id = system.get(_RenPKeywords.SYSTEM_ID, None)

        return system_instance

    def _renp_eval_images(images_data):
        images = [ ]
        for content, is_expr in images_data:
            if is_expr:
                images.append(eval(content))
            else:
                images.append(content)
        return images

    def _renp_eval_on_block(on_block_data):
        on_block = [ ]
        for content in on_block_data:
            behavior = None
            if content[_RenPKeywords.TYPE] in (_RenParserType.Func, _RenParserType.Emitter):
                behavior = eval(content[_RenPKeywords.FUNC])

            elif content[_RenPKeywords.TYPE] == _RenParserType.Shortcut:
                shortcuts_block = content[_RenPKeywords.SHORTCUTS_BLOCK]
                shortcut = content[_RenPKeywords.SHORTCUT]
                behavior = _renp_try_get_shortcut_behavior(shortcuts_block, shortcut)

            elif content[_RenPKeywords.TYPE] == _RenParserType.InnerPreset:
                behavior = _renp_try_get_preset_behavior(_RenPKeywords.INNER_SHORTCUTS, content[_RenPKeywords.SHORTCUT])
                if isinstance(behavior, renparticles._RFDynamicBehaviorPreset):
                    if not behavior.is_one_block():
                        _renp_inner_preset_multiple_blocks_error(behavior)
                    on_block.extend(_renp_eval_on_block(behavior.get_one()))
                    continue

            behavior = behavior()
            props = _renp_eval_props(content[_RenPKeywords.PROPERTIES])

            if content[_RenPKeywords.TYPE] not in _RenParserType.PresetsTypes:
                behavior.inject_properties(**props)
                behavior.check_initialised()
                on_block.append((behavior, behavior.m_properties))
            else:
                if not behavior.is_one_block():
                    _renp_inner_preset_multiple_blocks_error(behavior)
                behavior.build()
                on_block.extend(behavior.get_one())

            # on_block.append((behavior, props))
        return on_block

    def _renp_try_get_shortcut_behavior(shortcut_block, shortcut):
        shortcut_behavior = renparticles.static_shortcuts[shortcut_block].get(shortcut, None)
        
        if shortcut_behavior is None:
            shortcut_behavior = renparticles.dynamic_shortcuts[shortcut_block].get(shortcut, None)
        
        if shortcut_behavior is None:
            _renp_shortcut_error(shortcut_block, shortcut)
        
        return shortcut_behavior

    def _renp_eval_high_level_presets(presets, on_update, on_event, on_particle_dead):
        for preset in presets:
            preset_behavior = _renp_try_get_preset_behavior(_RenPKeywords.GENERAL_SHORTCUTS, preset[_RenPKeywords.SHORTCUT])

            if isinstance(preset_behavior, renparticles._RFDynamicBehaviorPreset):
                on_update.extend(_renp_eval_on_block(preset_behavior.behaviors[_RenPKeywords.ON_UPDATE]))
                on_event.extend(_renp_eval_on_block(preset_behavior.behaviors[_RenPKeywords.ON_EVENT]))
                on_particle_dead.extend(_renp_eval_on_block(preset_behavior.behaviors[_RenPKeywords.ON_PARTICLE_DEAD]))
            else:
                preset_behavior = preset_behavior()
                props = _renp_eval_props(preset[_RenPKeywords.PROPERTIES])
                preset_behavior.inject_properties(**props)
                behaviors = preset_behavior.build()
                on_update.extend([(behavior, behavior.m_properties or {}) for behavior in behaviors[_RenPKeywords.ON_UPDATE]])
                on_event.extend([(behavior, behavior.m_properties or {}) for behavior in behaviors[_RenPKeywords.ON_EVENT]])
                on_particle_dead.extend([(behavior, behavior.m_properties or {}) for behavior in behaviors[_RenPKeywords.ON_PARTICLE_DEAD]])

    def _renp_try_get_preset_behavior(preset_block, shortcut):
            preset_behavior = renparticles.static_shortcuts[_RenPKeywords.PRESETS][preset_block].get(shortcut, None)
            
            if preset_behavior is None:
                preset_behavior = renparticles.dynamic_shortcuts[_RenPKeywords.PRESETS][preset_block].get(shortcut, None)
                
            if preset_behavior is None:
                _renp_preset_error(preset_block, shortcut)
            
            return preset_behavior

    def _renp_eval_props(props_raw):        
        if isinstance(props_raw, dict):
            result = {}
            for key, value in props_raw.items():
                result[key] = _renp_eval_props(value)
            return result
        
        elif isinstance(props_raw, (list, tuple)):
            result = [_renp_eval_props(item) for item in props_raw]
            return type(props_raw)(result)
        
        elif isinstance(props_raw, basestring) and props_raw not in renp_renpy_reserved_words:
            try:
                return eval(props_raw)
            except:
                return props_raw
        
        else:
            return props_raw

    # lifetime ::= "constant" <postive number> | "range" <range behavior>
    # range behavior ::= <random range>
    # random range ::= "random" <2D positive number tuple>
    def _renp_parse_lifetime_keyword(lexer):
        data = { _RenPKeywords.TYPE: None, _RenPKeywords.TIMINGS: None }

        if lexer.keyword(_RenPLexerKeywords.RANGE):
            if lexer.keyword(_RenPLexerKeywords.RANDOM):
                data[_RenPKeywords.TYPE] = "range-random"
                data[_RenPKeywords.TIMINGS] = lexer.simple_expression()
        
        elif lexer.keyword(_RenPLexerKeywords.CONSTANT):
            data[_RenPKeywords.TYPE] = "constant"
            data[_RenPKeywords.TIMINGS] = lexer.simple_expression()
        
        else:
            lexer.error()

        return data

    # expression_jit ::= "expr" | "expession" <expression>
    # sprite_property ::= <expression_jit> | <image tag> {";" <sprite_property>}*
    def _renp_parse_sprites_keyword(lexer):
        data = [ ]
        images = [ img.strip() for img in lexer.rest().split(';') ]

        expr_pattern = re.compile(r'^(expression|expr)\s+(.*)$')
        for image in images:
            match = expr_pattern.match(image)
            if match:
                content = match.group(2)
                is_expr = True
            else:
                content = image
                is_expr = False
            
            data.append((content, is_expr))

        return data

    def _renp_parse_custom_keyword(lexer, allow_oneshot=True, allow_properties=True, allow_target_system=True, expect_eol=True):
        func = lexer.simple_expression()
        properties = { _RenPKeywords.ONESHOT: "False", _RenPKeywords.BEHAVIOR_ID: None }

        seen = { _RenPKeywords.ONESHOT: False, _RenPLexerKeywords.TARGET_SYSTEM: False, _RenPKeywords.BEHAVIOR_ID: False }
        
        was_delim = False
        while not lexer.eol():
            if allow_oneshot and lexer.keyword(_RenPKeywords.ONESHOT):
                if seen[_RenPKeywords.ONESHOT]:
                    lexer.error("only one 'oneshot' instruction allowed")

                properties[_RenPKeywords.ONESHOT] = "True"
                seen[_RenPKeywords.ONESHOT] = True

            elif allow_target_system and lexer.keyword(_RenPLexerKeywords.TARGET_SYSTEM):
                if seen[_RenPLexerKeywords.TARGET_SYSTEM]:
                    lexer.error("only one 'system' instruction allowed")

                properties[_RenPKeywords.TARGET_SYSTEM] = lexer.string()
                seen[_RenPLexerKeywords.TARGET_SYSTEM] = True
            
            elif lexer.keyword(_RenPLexerKeywords.BEHAVIOR_ID):
                if seen[_RenPKeywords.BEHAVIOR_ID]:
                    lexer.error("only one behavior 'id' instruction allowed")

                properties[_RenPKeywords.BEHAVIOR_ID] = lexer.string()
                seen[_RenPKeywords.BEHAVIOR_ID] = True

            elif lexer.match(':'):
                lexer.expect_eol()
                was_delim = True

        if allow_properties and was_delim:
            properties.update(_renp_parse_properties(lexer))

        if expect_eol:
            lexer.expect_eol()
        
        return {_RenPKeywords.FUNC: func, _RenPKeywords.PROPERTIES: properties, _RenPKeywords.TYPE: _RenParserType.Func}

    def _renp_parse_shortcut(lexer, what_block=_RenPKeywords.BEHAVIORS, allow_oneshot=True, allow_properties=True, allow_target_system=True, expect_eol=True):
        shortcut = lexer.word()
        properties = { _RenPKeywords.ONESHOT: "False", _RenPKeywords.BEHAVIOR_ID: None }

        seen = { _RenPKeywords.ONESHOT: False, _RenPLexerKeywords.TARGET_SYSTEM: False, _RenPKeywords.BEHAVIOR_ID: False }

        was_delim = False
        while not lexer.eol():
            if allow_oneshot and lexer.keyword(_RenPKeywords.ONESHOT):
                if seen[_RenPKeywords.ONESHOT]:
                    lexer.error("only one 'oneshot' instruction allowed")

                properties[_RenPKeywords.ONESHOT] = "True"
                seen[_RenPKeywords.ONESHOT] = True

            elif allow_target_system and lexer.keyword(_RenPLexerKeywords.TARGET_SYSTEM):
                if seen[_RenPLexerKeywords.TARGET_SYSTEM]:
                    lexer.error("only one 'system' instruction allowed")

                properties[_RenPKeywords.TARGET_SYSTEM] = lexer.string()
                seen[_RenPLexerKeywords.TARGET_SYSTEM] = True
            
            elif lexer.keyword(_RenPLexerKeywords.BEHAVIOR_ID):
                if seen[_RenPKeywords.BEHAVIOR_ID]:
                    lexer.error("only one behavior 'id' instruction allowed")

                properties[_RenPKeywords.BEHAVIOR_ID] = lexer.string()
                seen[_RenPKeywords.BEHAVIOR_ID] = True

            elif lexer.match(':'):
                lexer.expect_eol()
                was_delim = True

        if allow_properties and was_delim:
            properties.update(_renp_parse_properties(lexer))

        if expect_eol:
            lexer.expect_eol()

        return {_RenPKeywords.SHORTCUT: shortcut,
                _RenPKeywords.SHORTCUTS_BLOCK: what_block,
                _RenPKeywords.PROPERTIES: properties,
                _RenPKeywords.TYPE: _RenParserType.Shortcut
                }

    def _renp_parse_preset(lexer, what_type=_RenParserType.GeneralPreset):
        shortcut_data = _renp_parse_shortcut(lexer, _RenPKeywords.PRESETS, False)
        shortcut_data[_RenPKeywords.TYPE] = what_type

        return shortcut_data

    def _renp_parse_emitter_keyword(subblock):
        data = { }

        if subblock.keyword(_RenPLexerKeywords.CUSTOM):
            data = _renp_parse_custom_keyword(subblock)
        else:
            data = _renp_parse_shortcut(subblock, "emitters")
        
        return data

    def _renp_parse_properties(lexer, allow_dynamic=True):
        properties = { }
        prop_blocks = { }
        properties_block = lexer.subblock_lexer()

        while properties_block.advance():
            if allow_dynamic and properties_block.keyword(_RenPLexerKeywords.PROP_BLOCK):
                prop_name = properties_block.string()
                properties_block.require(':')
                properties_block.expect_eol()
                prop_blocks[prop_name] = _renp_parse_properties(properties_block, False)
            else:
                key = properties_block.word()
                value = properties_block.simple_expression()
                properties[key] = value
        
        if prop_blocks:
            properties["dynamic"] = prop_blocks

        return properties

    def _renp_shortcut_error(shortcuts_block, shortcut):
        renpy.error(
            "Unknown shortcut '{}' in '{}' block.\n"
            "Available static shortcuts: {}\n"
            "Available dynamic shortcuts: {}".format(shortcut, shortcuts_block,
                                                ", ".join(renparticles.static_shortcuts[shortcuts_block].keys()),
                                                ", ".join(renparticles.dynamic_shortcuts[shortcuts_block].keys())
                                                )
        )

    def _renp_preset_error(preset_block, shortcut):
        renpy.error(
            "Unknown shortcut '{}' in '{}' block.\n"
            "Available static preset shortcuts: {}\n"
            "Available dynamic preset shortcuts: {}".format(shortcut, preset_block,
                                                ", ".join(renparticles.static_shortcuts[_RenPKeywords.PRESETS][preset_block].keys()),
                                                ", ".join(renparticles.dynamic_shortcuts[_RenPKeywords.PRESETS][preset_block].keys())
                                                )
        )

    def _renp_inner_preset_multiple_blocks_error(preset_behavior):
        renpy.error(
            "Preset '{}' must have exactly one active block. "
            "Current blocks: on_update={}\non_event={}\non_particle_dead={}. "
            "Expected: exactly one block to be active (not None).".format(
                preset_behavior.__class__.__name__,
                preset_behavior.behaviors.get(_RenPKeywords.ON_UPDATE),
                preset_behavior.behaviors.get(_RenPKeywords.ON_EVENT),
                preset_behavior.behaviors.get(_RenPKeywords.ON_PARTICLE_DEAD)
            )
        )

    renpy.register_statement("rparticles", renp_parse_fast_particles_show, None, renp_execute_fast_particles_show, block=_RenPKeywords.POSSIBLE)

# -------------------------------------------------------------------------------------------------------------------------------

    def renp_parse_fast_particles_define(lexer):
        data = {
            _RenPKeywords.MODEL_NAME: None, 
            _RenPKeywords.MULTIPLE: False, 
            _RenPKeywords.SUBSYSTEMS: [], 
            _RenPKeywords.REDRAW: "None"
        }

        if lexer.keyword(_RenPLexerKeywords.MULTIPLE):
            data[_RenPKeywords.MULTIPLE] = True

        data[_RenPKeywords.MODEL_NAME] = lexer.string()

        if not lexer.match(':'):
            renpy.error("rparticles define: subblock required")

        lexer.expect_eol()
        subblock = lexer.subblock_lexer()
        _renp_parse_renparticles_system_subblock(subblock, data)

        return data

    def renp_parse_fast_particles_define_execute_init(data):
        model_name = data[_RenPKeywords.MODEL_NAME]

        if model_name in renparticles._fast_particles_models:
            renpy.error("rparticles model named '{}' already declared. Name your system differently".format(model_name))

        renparticles._fast_particles_models[model_name] = data.copy()
    
    renpy.register_statement("rparticles define", renp_parse_fast_particles_define, None, execute_init=renp_parse_fast_particles_define_execute_init, block=_RenPKeywords.POSSIBLE)

# -------------------------------------------------------------------------------------------------------------------------------

    def renp_parse_fast_particles_define_preset(lexer):
        data = {
            _RenPKeywords.PRESET_NAME: None,
            _RenPKeywords.PRESET_TYPE: "general",
            _RenPKeywords.PRESET_DEFINE_DATA: { }
        }

        data[_RenPKeywords.PRESET_NAME] = lexer.word()

        if lexer.keyword(_RenPLexerKeywords.PRESET_TYPE):
            data[_RenPKeywords.PRESET_TYPE] = lexer.word()
        
        lexer.require(':')
        lexer.expect_eol()
        _renp_parse_fast_particles_preset_block(lexer.subblock_lexer(), data[_RenPKeywords.PRESET_DEFINE_DATA])

        return data

    def _renp_parse_fast_particles_preset_block(subblock, data):
        seen = {
                _RenPKeywords.ON_UPDATE: False, 
                _RenPKeywords.ON_EVENT: False, 
                _RenPKeywords.ON_PARTICLE_DEAD: False
            }

        while subblock.advance():
            if subblock.match(_RenPLexerKeywords.ON_UPDATE):
                if seen[_RenPKeywords.ON_UPDATE]: 
                    subblock.error("only one 'on update' block allowed")
                data[_RenPKeywords.ON_UPDATE] = _renp_parse_on_block(subblock)
                seen[_RenPKeywords.ON_UPDATE] = True

            elif subblock.match(_RenPLexerKeywords.ON_EVENT):
                if seen[_RenPKeywords.ON_EVENT]: 
                    subblock.error("only one 'on event' block allowed")
                data[_RenPKeywords.ON_EVENT] = _renp_parse_on_block(subblock)
                seen[_RenPKeywords.ON_EVENT] = True

            elif subblock.match(_RenPLexerKeywords.ON_PARTICLE_DEAD):
                if seen[_RenPKeywords.ON_PARTICLE_DEAD]: 
                    subblock.error("only one 'on particle dead' block allowed")
                data[_RenPKeywords.ON_PARTICLE_DEAD] = _renp_parse_on_block(subblock)
                seen[_RenPKeywords.ON_PARTICLE_DEAD] = True
            
            elif subblock.keyword(_RenPLexerKeywords.PRESET):
                renpy.error("recursive presets are not allowed")
                #data[_RenPKeywords.PRESETS].append(_renp_parse_preset(subblock))
            
            else:
                return False
            
            subblock.expect_eol()
        return True

    def renp_execute_fast_particles_define_preset(data):
        preset_prefab = renparticles._RFDynamicBehaviorPreset()
        preset_prefab.behaviors[_RenPKeywords.ON_UPDATE] = data[_RenPKeywords.PRESET_DEFINE_DATA].get(_RenPKeywords.ON_UPDATE, {})
        preset_prefab.behaviors[_RenPKeywords.ON_EVENT] = data[_RenPKeywords.PRESET_DEFINE_DATA].get(_RenPKeywords.ON_EVENT, {})
        preset_prefab.behaviors[_RenPKeywords.ON_PARTICLE_DEAD] = data[_RenPKeywords.PRESET_DEFINE_DATA].get(_RenPKeywords.ON_PARTICLE_DEAD, {})

        renparticles.add_preset(data[_RenPKeywords.PRESET_NAME], preset_prefab, data[_RenPKeywords.PRESET_TYPE])
        
    renpy.register_statement("rparticles define preset", renp_parse_fast_particles_define_preset, None, execute_init=renp_execute_fast_particles_define_preset, block=_RenPKeywords.POSSIBLE)

# -------------------------------------------------------------------------------------------------------------------------------

    def renp_parse_fast_particles_reset(lexer):
        data = { _RenPKeywords.TAG: None }

        if lexer.eol():
            return data

        data[_RenPKeywords.TAG] = lexer.string()

        lexer.expect_eol()

        return data
 
    def renp_execute_fast_particles_reset(data):
        tag = data[_RenPKeywords.TAG] or _RenPKeywords.BASE_NAME

        system = renparticles._fast_particles_entries.get(tag, None)
        if system is not None:
            system.reset()

    renpy.register_statement("rparticles reset", renp_parse_fast_particles_reset, None, renp_execute_fast_particles_reset)

# -------------------------------------------------------------------------------------------------------------------------------

    # rparticles freeze ["particles_tag"[."subsystem"]]

    def renp_parse_fast_particles_freeze(lexer):
        data = { _RenPKeywords.TAG: None, _RenPKeywords.SYSTEM_ID: None }

        if lexer.eol():
            return data

        data[_RenPKeywords.TAG] = lexer.string()
        if lexer.match('.'):
            data[_RenPKeywords.SYSTEM_ID] = lexer.string()

        lexer.expect_eol()

        return data

    def renp_execute_fast_particles_freeze(data):
        tag = data[_RenPKeywords.TAG] or _RenPKeywords.BASE_NAME
        system_id = data.get(_RenPKeywords.SYSTEM_ID)
        
        system = renparticles._fast_particles_entries.get(tag, None)
        if not system:
            return
        
        if system_id:
            if isinstance(system, renparticles.RenParticleFastGroup):
                system.freeze_one(system_id)
            return
        
        system.freeze()

    renpy.register_statement("rparticles freeze", renp_parse_fast_particles_freeze, None, renp_execute_fast_particles_freeze)

# -------------------------------------------------------------------------------------------------------------------------------

    # rparticles unfreeze ["particles_tag"[."subsystem"]] [noredraw]

    def renp_parse_fast_particles_unfreeze(lexer):
        data = { _RenPKeywords.TAG: None, _RenPKeywords.SYSTEM_ID: None, _RenPKeywords.REDRAW: True }

        if lexer.eol():
            return data

        #<da fuq?>#
        checkpoint = lexer.checkpoint()
        if lexer.keyword( _RenPLexerKeywords.NOREDRAW):
            data[_RenPKeywords.REDRAW] = False
            lexer.expect_eol()
            return data
        lexer.revert(checkpoint)

        data[_RenPKeywords.TAG] = lexer.string()
        
        if lexer.match('.'):
            data[_RenPKeywords.SYSTEM_ID] = lexer.string()
        
        if lexer.keyword(_RenPLexerKeywords.NOREDRAW):
            data[_RenPKeywords.REDRAW] = False

        lexer.expect_eol()

        return data

    def renp_execute_fast_particles_unfreeze(data):
        tag = data[_RenPKeywords.TAG] or _RenPKeywords.BASE_NAME
        system_id = data.get(_RenPKeywords.SYSTEM_ID)
        redraw = data[_RenPKeywords.REDRAW]
        
        system = renparticles._fast_particles_entries.get(tag, None)
        if not system:
            return
        
        if system_id:
            if isinstance(system, renparticles.RenParticleFastGroup):
                system.unfreeze_one(system_id, redraw)
            return
            
        system.unfreeze(redraw)

    renpy.register_statement("rparticles unfreeze", renp_parse_fast_particles_unfreeze, None, renp_execute_fast_particles_unfreeze)

# -------------------------------------------------------------------------------------------------------------------------------

    def renp_parse_fast_particles_clear_cache(lexer):
        data = {
            _RenPLexerKeywords.DEEP: lexer.keyword(_RenPLexerKeywords.DEEP) is not None
        }

        lexer.expect_eol()
        return data

    def renp_execute_fast_particles_clear_cache(data):
        deep = data.get(_RenPLexerKeywords.DEEP, False)
        
        if deep:
            for tag, system in renparticles._fast_particles_entries.items():
                renpy.hide(tag, layer=system.layer)
            renparticles._fast_particles_entries.clear()
        else:
            for tag, system in list(renparticles._fast_particles_entries.items()):
                if not renpy.showing(tag, layer=system.layer):
                    renpy.hide(tag, layer=system.layer)
                    renparticles._fast_particles_entries.pop(tag, None)

    renpy.register_statement("rparticles clear cache", renp_parse_fast_particles_clear_cache, None, renp_execute_fast_particles_clear_cache)

# -------------------------------------------------------------------------------------------------------------------------------

    def renp_parse_fast_particles_continue(lexer):
        data = {_RenPKeywords.TAG: None,
                _RenPKeywords.LAYER: None, 
                _RenPKeywords.ZORDER: "0",
                }

        if lexer.eol():
            return data

        #<da fuq?>#
        checkpoint = lexer.checkpoint()
        was_show_component_keyword = False

        if lexer.keyword(_RenPLexerKeywords.ONLAYER):
            data[_RenPKeywords.LAYER] = lexer.simple_expression()
            was_show_component_keyword = True
        elif lexer.keyword(_RenPLexerKeywords.ZORDER):
            data[_RenPKeywords.ZORDER] = lexer.integer()
            was_show_component_keyword = True
        
        if was_show_component_keyword:
            while not lexer.eol():
                if lexer.keyword(_RenPLexerKeywords.ONLAYER):
                    data[_RenPKeywords.LAYER] = lexer.simple_expression()
                elif lexer.keyword(_RenPLexerKeywords.ZORDER):
                    data[_RenPKeywords.ZORDER] = lexer.integer()
                else:
                    renpy.error("unknown show component\ngot: {}".format(lexer.rest()))
            
            return data
            
        lexer.revert(checkpoint)

        data[_RenPKeywords.TAG] = lexer.string()

        #<Пошло оно всё в пизду.>#
        while not lexer.eol():
            if lexer.keyword(_RenPLexerKeywords.ONLAYER):
                data[_RenPKeywords.LAYER] = lexer.simple_expression()
            elif lexer.keyword(_RenPLexerKeywords.ZORDER):
                data[_RenPKeywords.ZORDER] = lexer.require(lexer.integer, "integer expected")
            else:
                    renpy.error("unknown show component\ngot: {}".format(lexer.rest()))

        lexer.expect_eol()

        return data

    def renp_execute_fast_particles_continue(data):
        tag = data[_RenPKeywords.TAG] or _RenPKeywords.BASE_NAME

        system = renparticles._fast_particles_entries.get(tag, None)
        if system is not None:
            layer = data[_RenPKeywords.LAYER] or system.layer
            system.layer = layer
            zorder = eval(data[_RenPKeywords.ZORDER])
            renpy.show(_RenPKeywords.BASE_NAME, what=system, layer=layer, tag=tag, zorder=zorder)

    renpy.register_statement("rparticles continue", renp_parse_fast_particles_continue, None, renp_execute_fast_particles_continue)

# -------------------------------------------------------------------------------------------------------------------------------
