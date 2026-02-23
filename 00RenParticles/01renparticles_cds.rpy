python early:
    import re


    class _RenParserType:
        Func = 333
        Shortcut = 666
        Emitter = 999

        GeneralPreset = 1332
        InnerPreset = 1665
        # UpdatePreset = 1665
        # EventPreset = 1998
        # ParticleDeadPreset = 2331

        PresetsTypes = (GeneralPreset, InnerPreset)

    redraw_asap_aliases = {
        "asap",
        "fastest",
        "fast"
    }

    def renp_parse_fast_particles_show(lexer):
        data = {"presets": [ ], "on_update": [ ], "on_event": [ ], "on_particle_dead": [ ], "redraw": None, "sprite": [ ], "tag": None, "layer": "master", "zorder": "0", "lifetime": None }

        while not lexer.match(':'):
            if lexer.keyword("as"):
                data["tag"] = lexer.image_name_component()

            elif lexer.keyword("onlayer"):
                data["layer"] = lexer.simple_expression()
            
            elif lexer.keyword("zorder"):
                data["zorder"] = lexer.integer()
            
            if lexer.eol():
                renpy.error("subblock required")

        lexer.expect_eol()
        
        subblock = lexer.subblock_lexer()

        was_on_update = False
        was_on_event = False
        was_on_particle_dead = False
        was_redraw = False
        while subblock.advance():
            if subblock.keyword("sprite"):
                if data["sprite"]:
                    renpy.error("there can be only one 'sprite' instruction")

                data["sprite"] = _renp_parse_sprites_keyword(subblock)
            
            elif subblock.keyword("lifetime"):
                if data["lifetime"] is not None:
                    renpy.error("there can be only one 'lifetime' instruction")
                
                data["lifetime"] = _renp_parse_lifetime_keyword(subblock)

            elif subblock.keyword("redraw"):
                if was_redraw:
                    renpy.error("there can be only one 'redraw' instruction")
                
                for alias in redraw_asap_aliases:
                    if subblock.keyword(alias):
                        data["redraw"] = "0.0"
                        break
                else:
                    data["redraw"] = subblock.float()
                    
                was_redraw = True

            elif subblock.keyword("preset"):
                data["presets"].append(_renp_parse_preset(subblock))

            elif subblock.match("on update"):
                if was_on_update:
                    renpy.error("there can be only one 'on update' block")

                data["on_update"] = renp_parse_on_update_block(subblock)
                was_on_update = True

            elif subblock.match("on event"):
                if was_on_event:
                    renpy.error("there can be only one 'on event' block")
                    
                data["on_event"] = renp_parse_on_event_block(subblock)
                was_on_event = True

            elif subblock.match("on particle dead"):
                if was_on_particle_dead:
                    renpy.error("there can be only one 'on particle dead' block")

                data["on_particle_dead"] = renp_parse_on_particle_dead_block(subblock)
                was_on_particle_dead = True
            
            subblock.expect_eol()
        
        return data

    def _renp_parse_on_block(subblock):
        block_data = [ ]

        subblock.require(':')
        on_block = subblock.subblock_lexer()

        while on_block.advance():
            if on_block.keyword("emitter"):
                emitter_data = _renp_parse_emitter_keyword(on_block)
                block_data.append(emitter_data)

            elif on_block.keyword("preset"):
                preset_data = _renp_parse_preset(on_block, _RenParserType.InnerPreset)
                block_data.append(preset_data)

            elif on_block.keyword("custom"):
                func_data = _renp_parse_custom_keyword(on_block)
                block_data.append(func_data)

            #<Потенциальный шорткат>#
            else:
                shortcut_data = _renp_parse_shortcut(on_block)
                block_data.append(shortcut_data)

            on_block.expect_eol()
        
        #renpy.error("wih?\n{}".format(block_data))
        return block_data

    def renp_parse_on_update_block(subblock):
        return _renp_parse_on_block(subblock)

    def renp_parse_on_event_block(subblock):
        return _renp_parse_on_block(subblock)

    def renp_parse_on_particle_dead_block(subblock):
        return _renp_parse_on_block(subblock)

    def renp_execute_fast_particles_show(data):
        on_update = [ ]
        on_event = [ ]
        images = _renp_eval_images(data["sprite"])

        on_update_preset = [ ]
        on_event_preset = [ ]
        on_particle_dead_preset = [ ]
        _renp_eval_high_level_presets(data["presets"], on_update_preset, on_event_preset, on_particle_dead_preset)

        on_update = _renp_eval_on_update(data["on_update"])
        on_event = _renp_eval_on_event(data["on_event"])
        on_particle_dead = _renp_eval_on_particle_dead(data["on_particle_dead"])

        #<Объединяем списки>#
        on_update = on_update_preset + on_update
        on_event = on_event_preset + on_event
        on_particle_dead = on_particle_dead_preset + on_particle_dead

        lifetime_type = data["lifetime"]["type"]
        lifetime_timings = eval(data["lifetime"]["timings"])

        particles_data = renparticles.ParticlesData(images=images, tag=data["tag"], lifetime_type=lifetime_type, lifetime_timings=lifetime_timings)
        particles = renparticles.RenParticlesFast(on_update, on_event, on_particle_dead, particles_data, eval(data["redraw"]))

        print("EXECUTE RENPARTICLES:\n{}".format(particles.get_info()))
        
        renpy.show(data["tag"], what=particles, layer=data["layer"], zorder=eval(data["zorder"]))

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
            if content["type"] in (_RenParserType.Func, _RenParserType.Emitter):
                behavior = eval(content["func"])

            elif content["type"] == _RenParserType.Shortcut:
                shortcuts_block = content["shortcuts_block"]
                shortcut = content["shortcut"]
                behavior = renparticles.static_shortcuts[shortcuts_block].get(shortcut, None)
                if behavior is None:
                    _renp_shortcut_error(shortcuts_block, shortcut)

            elif content["type"] == _RenParserType.InnerPreset:
                behavior = _renp_try_get_preset_behavior("general", preset["shortcut"])

            behavior = behavior()
            props = _renp_eval_props(content["properties"])

            if content["type"] not in _RenParserType.PresetsTypes:
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

    def _renp_eval_on_update(on_update_data):
        return _renp_eval_on_block(on_update_data)

    def _renp_eval_on_event(on_event_data):
        return _renp_eval_on_block(on_event_data)

    def _renp_eval_high_level_presets(presets, on_update, on_event, on_particle_dead):
        for preset in presets:
            preset_behavior = _renp_try_get_preset_behavior("general", preset["shortcut"])
            
            preset_behavior = preset_behavior()
            props = _renp_eval_props(preset["properties"])
            preset_behavior.inject_properties(**props)
            behaviors = preset_behavior.build()
            on_update.extend([(behavior, behavior.m_properties or {}) for behavior in behaviors["on_update"]])
            on_event.extend([(behavior, behavior.m_properties or {}) for behavior in behaviors["on_event"]])
            on_particle_dead.extend([(behavior, behavior.m_properties or {}) for behavior in behaviors["on_particle_dead"]])

    def _renp_try_get_preset_behavior(preset_block, shortcut):
        preset_behavior = renparticles.static_shortcuts["presets"][preset_block].get(shortcut, None)
        if preset_behavior is None:
            _renp_shortcut_error("{}->{}".format(preset["shortcuts_block"], "general"), shortcut)

        return preset_behavior

    def _renp_eval_on_particle_dead(on_particle_dead_data):
        return _renp_eval_on_block(on_particle_dead_data)

    def _renp_eval_props(props_raw):
        props = { }
        for key, raw_value in props_raw.items():
            value = eval(raw_value)
            props[key] = value
    
        return props

    # lifetime ::= "constant" <postive number> | "range" <range behavior>
    # range behavior ::= <random range>
    # random range ::= "random" <2D positive number tuple>
    def _renp_parse_lifetime_keyword(lexer):
        data = { "type": None, "timings": None }

        if lexer.keyword("range"):
            if lexer.keyword("random"):
                data["type"] = "range-random"
                data["timings"] = lexer.simple_expression()
        
        elif lexer.keyword("constant"):
            data["type"] = "constant"
            data["timings"] = lexer.simple_expression()
        
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
            properties["oneshot"] = "True" if lexer.keyword("oneshot") else "False"

        if allow_properties and lexer.match(':'):
            properties.update(_renp_parse_properties_properties(lexer))

        if expect_eol:
            lexer.expect_eol()
        
        return {"func": func, "properties": properties, "type": _RenParserType.Func}

    def _renp_parse_shortcut(lexer, what_block="behaviors", allow_oneshot=True, allow_properties=True, expect_eol=True):
        shortcut = lexer.word()
        properties = { }

        if allow_oneshot:
            properties["oneshot"] = "True" if lexer.keyword("oneshot") else "False"

        if allow_properties and lexer.match(':'):
            properties.update(_renp_parse_properties_properties(lexer))

        if expect_eol:
            lexer.expect_eol()

        return {"shortcut": shortcut, "shortcuts_block": what_block, "properties": properties, "type": _RenParserType.Shortcut}

    def _renp_parse_preset(lexer, what_type=_RenParserType.GeneralPreset):
        shortcut_data = _renp_parse_shortcut(lexer, "presets", False)
        shortcut_data["type"] = what_type

        return shortcut_data

    def _renp_parse_emitter_keyword(subblock):
        data = { }

        if subblock.keyword("custom"):
            data = _renp_parse_custom_keyword(subblock)
        else:
            data = _renp_parse_shortcut(subblock, "emitters")
        
        return data

    def _renp_parse_properties_properties(lexer):
        properties = { }
        properties_block = lexer.subblock_lexer()

        while properties_block.advance():
            key = properties_block.word()
            value = properties_block.simple_expression()
            properties[key] = value
        
        return properties

    def _renp_shortcut_error(shortcuts_block, shortcut):
        available = ", ".join(renparticles.static_shortcuts[shortcuts_block].keys())
        renpy.error(
            "Unknown shortcut '{}' in '{}' block.\n"
            "Available shortcuts: {}".format(shortcut, shortcuts_block, available)
        )

    def _renp_inner_preset_multiple_blocks_error(preset_behavior):
        renpy.error(
            "Preset '{}' must have exactly one active block. "
            "Current blocks: on_update={}, on_event={}, on_particle_dead={}. "
            "Expected: exactly one block to be active (not None).".format(
                preset_behavior.__class__.__name__,
                preset_behavior.behaviors.get('on_update') is not None,
                preset_behavior.behaviors.get('on_event') is not None,
                preset_behavior.behaviors.get('on_particle_dead') is not None
            )
        )

    renpy.register_statement("rparticles", renp_parse_fast_particles_show, None, renp_execute_fast_particles_show, block="possible")