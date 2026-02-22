(* Основная структура *)
fast_particles_show ::= "rparticles" ":" NEWLINE
                        { sprite_statement | redraw_statement | on_update_statement | on_event_statement }*

(* Секции *)
sprite_statement   ::= "sprite" sprite_property_list NEWLINE
redraw_statement   ::= "redraw" expression NEWLINE
on_update_statement ::= "on" "update" ":" NEWLINE { emitter_statement | function_statement }*
on_event_statement  ::= "on" "event" ":" NEWLINE function_statement*

(* Свойства спрайта *)
sprite_property_list ::= sprite_property { ";" sprite_property }*
sprite_property      ::= expression_jit | image_tag
expression_jit       ::= ("expr" | "expression") expression
image_tag            ::= <любая строка, не начинающаяся с expr/expression>

(* On update блок *)
emitter_statement   ::= "emitter" ":" NEWLINE emitter_body
emitter_body        ::= "function" expression [ ":" NEWLINE property_block ]
property_block      ::= { identifier expression NEWLINE }*

function_statement  ::= "function" expression [ "oneshot" ] NEWLINE

(* Базовые элементы *)
expression           ::= <любое Ren'Py выражение>
identifier           ::= <слово>
NEWLINE              ::= <конец строки>