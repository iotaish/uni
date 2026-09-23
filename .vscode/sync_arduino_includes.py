#!/usr/bin/env python3
"""Sync UNO R4 WiFi build include paths into cpptools' fallback configuration."""
import json
import shlex
from pathlib import Path

workspace = Path(__file__).resolve().parent.parent
config_path = workspace / '.vscode/c_cpp_properties.json'
arduino_config = json.loads((workspace / '.vscode/arduino.json').read_text())
if arduino_config['board'] != 'arduino:renesas_uno:unor4wifi':
    raise SystemExit('Expected board arduino:renesas_uno:unor4wifi')

build_dir = (workspace / arduino_config.get('output', 'build')).resolve()
db_path = build_dir / 'compile_commands.json'
database = json.loads(db_path.read_text())
sketch_entry = next((entry for entry in database if entry['file'].endswith('.ino.cpp')), None)
if sketch_entry is None:
    raise SystemExit(f'No sketch compilation command in {db_path}')
arguments = sketch_entry.get('arguments') or shlex.split(sketch_entry['command'])
prefix = next((arg.removeprefix('-iprefix') for arg in arguments if arg.startswith('-iprefix')), None)
if not prefix:
    raise SystemExit('Missing -iprefix in sketch compilation command')
platform = Path(prefix).resolve()
variant = platform / 'variants/UNOWIFIR4'
include_file = variant / 'includes.txt'
if not include_file.is_file():
    raise SystemExit(f'Missing {include_file}')

paths = [str(workspace / Path(arduino_config['sketch']).parent), str(platform / 'cores/arduino'), str(variant)]
for argument in arguments:
    if argument.startswith('-I') and len(argument) > 2:
        paths.append(argument[2:])
for line in include_file.read_text().splitlines():
    for argument in shlex.split(line):
        key = '-iwithprefixbefore'
        if not argument.startswith(key):
            raise SystemExit(f'Unsupported includes.txt option: {argument}')
        paths.append(str(platform / argument[len(key):].lstrip('/')))
missing = [p for p in paths if not Path(p).is_dir()]
if missing:
    print('Skipping nonexistent include directories:\n' + '\n'.join(missing))
paths = [p for p in paths if Path(p).is_dir()]

defines = [arg[2:] for arg in arguments if arg.startswith('-D')]
for argument in arguments:
    if argument.startswith('@') and argument.endswith('defines.txt'):
        for flag in shlex.split(Path(argument[1:]).read_text()):
            if flag.startswith('-D'):
                defines.append(flag[2:])

config = json.loads(config_path.read_text())
selected = next((item for item in config['configurations'] if item['name'] in ('Arduino', 'uno_r4_wifi')), None)
if selected is None:
    raise SystemExit('Missing Arduino or uno_r4_wifi configuration')
selected['includePath'] = list(dict.fromkeys([*selected.get('includePath', []), *paths]))
selected['defines'] = list(dict.fromkeys([*selected.get('defines', []), *defines]))
selected['compilerPath'] = arguments[0]
config_path.write_text(json.dumps(config, ensure_ascii=False, indent=4) + '\n')
print(f'Synced {len(paths)} include paths and {len(defines)} defines from {include_file}')
