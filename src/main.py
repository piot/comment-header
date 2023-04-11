#---------------------------------------------------------------------------------------------
#  Copyright (c) Peter Bjorklund. All rights reserved.
#  Licensed under the MIT License. See LICENSE in the project root for license information.
#---------------------------------------------------------------------------------------------
from pathlib import Path
import argparse
import re

parser = argparse.ArgumentParser(description='Process some file headers')
parser.add_argument('--license',dest='license', type=Path)
parser.add_argument('--path',dest='path', type=Path, default='.')
args = parser.parse_args()

project_dir : Path = args.path
license : Path = args.license

with open(license) as f:
    license_content = f.read()

extensions : tuple[str, str] = ('cs', 'c', 'h', 'go')

all_files : list[Path] = []

for extension in extensions:
    all_files += project_dir.rglob('*.' + extension)

for path in all_files:
    name = path.relative_to(project_dir)
    print('adding header to ', name)
    full_path = path.absolute()

    with open(full_path, encoding='utf8') as f:
        file_content = f.read()

    existing_external_header = re.match('^\s*\/\*\s(\*(?!\/)|[^*])*\*\/', file_content)
    if existing_external_header != None:
        print('skipping ', name, ' because it already has an external header')
        continue

    replaced = re.sub('^\s*\/\*\-(\*(?!\/)|[^*])*\-\*\/', '', file_content, 1)

    replaced = replaced.lstrip()

    should_add_linebreak : bool = path.suffix == '.cs' or path.suffix == '.go'
    if should_add_linebreak:
        replaced = "\n" + replaced

    replaced = license_content + replaced

    with open(full_path, 'w', encoding='utf8') as f:
        f.write(replaced)
