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

        SPRITE = "sprite"
        IMAGES = "images"

        SUBSYSTEMS = "subsystems"
        TAG = "tag"
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

        EMITTER = "emitter"

        CUSTOM = "custom"

        RANDOM = "random"
        RANGE = "range"
        CONSTANT = "constant"

        SYSTEM = "system"

        AS = "as"

        PROP_BLOCK = "block"

    redraw_asap_aliases = {
        "asap",
        "fastest",
        "fast"
    }

    def renp_parse_fast_particles_show(lexer):
        data = {
            _RenPKeywords.TAG: None, 
            _RenPKeywords.LAYER: "master", 
            _RenPKeywords.ZORDER: "0", 
            _RenPKeywords.MULTIPLE: False, 
            _RenPKeywords.SUBSYSTEMS: [], 
            _RenPKeywords.REDRAW: "None"
        }

        while not lexer.match(':'):
            if lexer.keyword(_RenPLexerKeywords.AS):
                data[_RenPKeywords.TAG] = lexer.image_name_component()
            elif lexer.keyword(_RenPLexerKeywords.ONLAYER):
                data[_RenPKeywords.LAYER] = lexer.simple_expression()
            elif lexer.keyword(_RenPLexerKeywords.ZORDER):
                data[_RenPKeywords.ZORDER] = lexer.simple_expression()
            elif lexer.keyword(_RenPLexerKeywords.MULTIPLE):
                data[_RenPKeywords.MULTIPLE] = True
            
            if lexer.eol():
                renpy.error("rparticles: subblock required")

        lexer.expect_eol()
        subblock = lexer.subblock_lexer()

        if data[_RenPKeywords.MULTIPLE]:
            while subblock.advance():
                if subblock.keyword(_RenPKeywords.REDRAW):
                    data[_RenPKeywords.REDRAW] = _renp_parse_redraw(subblock)
                elif subblock.keyword(_RenPLexerKeywords.SYSTEM):
                    subblock.require(':')
                    subblock.expect_eol()
                    sub_data = _renp_get_default_system_data(_RenParserType.SubSystem)
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
        tag = data.get(_RenPKeywords.TAG)
        layer = data[_RenPKeywords.LAYER]
        zorder = eval(data[_RenPKeywords.ZORDER])
        redraw = eval(data[_RenPKeywords.REDRAW])

        if data[_RenPKeywords.MULTIPLE]:
            subsystems = [_renp_eval_system(system) for system in data[_RenPKeywords.SUBSYSTEMS]]
            displayable = renparticles.RenParticleFastGroup(subsystems, redraw)
        else:
            displayable = _renp_eval_system(data)

        print(displayable.get_info())

        renpy.show(tag, what=displayable, layer=layer, zorder=zorder)

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

        lifetime_type = system[_RenPKeywords.LIFETIME][_RenPKeywords.TYPE]
        lifetime_timings = eval(system[_RenPKeywords.LIFETIME][_RenPKeywords.TIMINGS])

        particles_data = renparticles.ParticlesData(images=images, tag=system.get(_RenPKeywords.TAG, None), lifetime_type=lifetime_type, lifetime_timings=lifetime_timings)
        system = renparticles.RenParticlesFast(on_update, on_event, on_particle_dead, particles_data, eval(system.get(_RenPKeywords.REDRAW, "None")), eval(system.get(_RenPKeywords.CACHE, "False")))

        return system

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
                behavior = renparticles.static_shortcuts[shortcuts_block].get(shortcut, None)
                if behavior is None:
                    _renp_shortcut_error(shortcuts_block, shortcut)

            elif content[_RenPKeywords.TYPE] == _RenParserType.InnerPreset:
                behavior = _renp_try_get_preset_behavior("general", preset[_RenPKeywords.SHORTCUT])

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

    def _renp_eval_high_level_presets(presets, on_update, on_event, on_particle_dead):
        for preset in presets:
            preset_behavior = _renp_try_get_preset_behavior("general", preset[_RenPKeywords.SHORTCUT])
            
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
        
        elif isinstance(props_raw, basestring):
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
    # sprite_property ::= <expression_jit> | <image tag> {";" sprite_property}*
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

    def _renp_parse_custom_keyword(lexer, allow_oneshot=True, allow_properties=True, expect_eol=True):
        func = lexer.simple_expression()
        properties = {}

        if allow_oneshot:
            properties[_RenPKeywords.ONESHOT] = "True" if lexer.keyword(_RenPKeywords.ONESHOT) else "False"

        if allow_properties and lexer.match(':'):
            properties.update(_renp_parse_properties(lexer))

        if expect_eol:
            lexer.expect_eol()
        
        return {_RenPKeywords.FUNC: func, _RenPKeywords.PROPERTIES: properties, _RenPKeywords.TYPE: _RenParserType.Func}

    def _renp_parse_shortcut(lexer, what_block=_RenPKeywords.BEHAVIORS, allow_oneshot=True, allow_properties=True, expect_eol=True):
        shortcut = lexer.word()
        properties = { }

        if allow_oneshot:
            properties[_RenPKeywords.ONESHOT] = "True" if lexer.keyword(_RenPKeywords.ONESHOT) else "False"

        if allow_properties and lexer.match(':'):
            properties.update(_renp_parse_properties(lexer))

        if expect_eol:
            lexer.expect_eol()

        return {_RenPKeywords.SHORTCUT: shortcut, _RenPKeywords.SHORTCUTS_BLOCK: what_block, _RenPKeywords.PROPERTIES: properties, _RenPKeywords.TYPE: _RenParserType.Shortcut}

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
        available = ", ".join(renparticles.static_shortcuts[shortcuts_block].keys())
        renpy.error(
            "Unknown shortcut '{}' in '{}' block.\n"
            "Available shortcuts: {}".format(shortcut, shortcuts_block, available)
        )

    def _renp_preset_error(preset_block, shortcut):
        available = ", ".join(renparticles.static_shortcuts[_RenPKeywords.PRESETS][preset_block].keys())
        renpy.error(
            "Unknown shortcut '{}' in '{}' block.\n"
            "Available shortcuts: {}".format(shortcut, preset_block, available)
        )

    def _renp_inner_preset_multiple_blocks_error(preset_behavior):
        renpy.error(
            "Preset '{}' must have exactly one active block. "
            "Current blocks: on_update={}, on_event={}, on_particle_dead={}. "
            "Expected: exactly one block to be active (not None).".format(
                preset_behavior.__class__.__name__,
                preset_behavior.behaviors.get(_RenPKeywords.ON_UPDATE) is not None,
                preset_behavior.behaviors.get(_RenPKeywords.ON_EVENT) is not None,
                preset_behavior.behaviors.get(_RenPKeywords.ON_PARTICLE_DEAD) is not None
            )
        )

    renpy.register_statement("rparticles", renp_parse_fast_particles_show, None, renp_execute_fast_particles_show, block=_RenPKeywords.POSSIBLE)