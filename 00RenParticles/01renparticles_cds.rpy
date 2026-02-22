python early:
    import re


    def renp_parse_fast_particles_show(lexer):
        data = { "on_update": [ ], "on_event": [ ], "on_particle_dead": [ ], "redraw": None, "sprite": [ ], "tag": None, "layer": "master", "zorder": "0", "lifetime": None }

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
                
                data["redraw"] = subblock.simple_expression()
                was_redraw = True

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

            elif on_block.keyword("function"):
                func_data = _renp_parse_function_keyword(on_block)
                block_data.append(func_data)

            on_block.expect_eol()
        
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
        on_update = _renp_eval_on_update(data["on_update"])
        on_event = _renp_eval_on_event(data["on_event"])
        on_particle_dead = _renp_eval_on_dead(data["on_particle_dead"])

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
            behavior = eval(content["func"])()
            props = _renp_eval_props(content["properties"])
            behavior.inject_properties(**props)
            on_block.append((behavior, props))
        return on_block

    def _renp_eval_on_update(on_update_data):
        return _renp_eval_on_block(on_update_data)

    def _renp_eval_on_event(on_event_data):
        return _renp_eval_on_block(on_event_data)

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

    def _renp_parse_function_keyword(lexer, allow_oneshot=True, allow_properties=True, expect_eol=True):
        func = lexer.simple_expression()
        properties = {}
        data = {"func": None, "properties": None}

        oneshot = None
        if allow_oneshot:
            properties["oneshot"] = lexer.keyword("oneshot") or "False"

        if allow_properties and lexer.match(':'):
            properties.update(_renp_parse_properties_properties(lexer))

        if expect_eol:
            lexer.expect_eol()
        
        return {"func": func, "properties": properties}

    def _renp_parse_emitter_keyword(subblock):
        data = { }

        oneshot = "False"
        if subblock.keyword("oneshot"):
            oneshot = "True"

        subblock.require(':')

        emitter_block = subblock.subblock_lexer()

        while emitter_block.advance():
            if emitter_block.keyword("function"):
                func_data = _renp_parse_function_keyword(emitter_block, False)
                
                data = {"func": func_data["func"], "properties": func_data["properties"], "type": 1}
                data["properties"]["oneshot"] = oneshot
                break
        
        return data

    def _renp_parse_properties_properties(lexer):
        properties = { }
        properties_block = lexer.subblock_lexer()

        while properties_block.advance():
            key = properties_block.word()
            value = properties_block.simple_expression()
            properties[key] = value
        
        return properties

    renpy.register_statement("rparticles", renp_parse_fast_particles_show, None, renp_execute_fast_particles_show, block="possible")