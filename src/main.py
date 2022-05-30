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


for path in project_dir.rglob('*.cs'):
    name = path.relative_to(project_dir)
    print('adding header to ', name)
    full_path = path.absolute()

    with open(full_path) as f:
        file_content = f.read()

    replaced = re.sub('\/\*(\*(?!\/)|[^*])*\*\/', '', file_content, 1)

    replaced = replaced.lstrip()
    replaced = license_content + replaced

    with open(full_path, 'w') as f:
        f.write(replaced)
