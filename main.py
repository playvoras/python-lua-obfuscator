import random
import json
import re
import string
import os

def encrypt_string(input_str):
    return ''.join(['\\x{:02x}'.format(ord(c)) for c in input_str])

def get_random_useless_code():
    with open("./ignore-me.json", "r", encoding='utf-8') as file:
        data = json.load(file)

    code_snippets = data['code']
    useless_code = random.choice(code_snippets)
    variable_name_length = random.randint(5, 15)
    possible_characters = string.ascii_letters
    variable_name = ''.join(random.choice(possible_characters) for _ in range(variable_name_length))
    useless_code = useless_code.replace('_', variable_name)
    useless_code = re.sub(r"(['\"])(.*?)\1", lambda m: f"{m.group(1)}{encrypt_string(m.group(2))}{m.group(1)}", useless_code)
    return useless_code

def obfuscate(lua_code):
    local_names = re.findall(r"(?<=local )([a-zA-Z_][a-zA-Z0-9_]*)\b", lua_code)
    function_names = re.findall(r"(?<=function )([a-zA-Z_][a-zA-Z0-9_]*)\b", lua_code)
    start_names = re.findall(r"^([a-zA-Z_][a-zA-Z0-9_]*)\b", lua_code)
    names = local_names + function_names + start_names
    
    used_names = set()
    lua_keywords = ["and", "break", "do", "else", "elseif", "end", "false", "for", "function", "if", "in", "local", "nil", "not", "or", "repeat", "return", "then", "true", "until", "while"]
    
    for name in names:
        if name not in lua_keywords:
            new_name = None
            while new_name is None or new_name in used_names:
                variable_name_length = random.randint(5, 15)
                possible_characters = string.ascii_letters
                new_name = ''.join(random.choice(possible_characters) for _ in range(variable_name_length))
            used_names.add(new_name)
            lua_code = re.sub(rf"\b{name}\b", lambda m: new_name if (m.string[:m.start()].count('"') % 2 == 0 and m.string[m.end():].count('"') % 2 == 0) else m.group(0), lua_code)

    lines = lua_code.split('\n')
    for i in range(len(lines)):
        for _ in range(random.randint(1, 5000)):
            lines[i] += ' ' + get_random_useless_code()

    lua_code = ' '.join(lines)
    lua_code = re.sub(r'"([^"]*)"', lambda m: f'"{encrypt_string(m.group(1))}"', lua_code)
    lua_code = re.sub(r"\b(end|;)\b", lambda m: f"{m.group(0)} {get_random_useless_code()}", lua_code)

    return lua_code

if __name__ == "__main__":
    with open("input.lua", "r", encoding='utf-8') as lua_file:
        lua_code = lua_file.read()

    obfuscated_code = obfuscate(lua_code)

    with open("output.lua", "w", encoding='utf-8') as output_file:
        output_file.write(obfuscated_code)
