#---------------------------------------------------------------------------------------------
#  Copyright (c) Peter Bjorklund. All rights reserved.
#  Licensed under the MIT License. See LICENSE in the project root for license information.
#---------------------------------------------------------------------------------------------
from pathlib import Path
import argparse
import re
import os
import sys
import subprocess
import string

GIT_DIRECTORY_NAME = '.git'

def find_git_directory(start_path: str) -> str | None:
    while True:
        if os.path.isdir(os.path.join(start_path, GIT_DIRECTORY_NAME)):
            return os.path.join(start_path, GIT_DIRECTORY_NAME)
        print(f"start_path: {start_path}")
        if start_path == '/' or start_path == '':
            return None
        start_path = os.path.dirname(start_path)


def get_git_origin_url(git_path: str) -> str:
    result = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=git_path,
        text=True,
        check=True
    )
    return result.stdout.strip()


def read_and_replace_license_text(license_filename : Path, origin_url: str) -> str:
    with open(license_filename) as f:
        license_content = string.Template(f.read())
    return license_content.substitute(origin=origin_url)


def find_all_source_files(project_dir: Path) -> list[Path]:
    extensions : tuple[str, str] = ('cs', 'c', 'h', 'go')

    all_files : list[Path] = []

    for extension in extensions:
        all_files += project_dir.rglob('*.' + extension)

    return all_files


def replace_header_in_file(project_dir: Path, path: Path, license_content_replaced: str) -> None:
    name = path.relative_to(project_dir)
    print('adding header to ', name)
    full_path = path.absolute()

    with open(full_path, encoding='utf8') as f:
        file_content = f.read()

    existing_external_header = re.match('^\s*\/\*\s(\*(?!\/)|[^*])*\*\/', file_content)
    if existing_external_header != None:
        print('skipping ', name, ' because it already has an external header')
        return

    replaced = re.sub('^\s*\/\*\-(\*(?!\/)|[^*])*\-\*\/', '', file_content, 1)

    replaced = replaced.lstrip()

    should_add_linebreak : bool = path.suffix == '.cs' or path.suffix == '.go'
    if should_add_linebreak:
        replaced = "\n" + replaced

    replaced = license_content_replaced + replaced

    with open(full_path, 'w', encoding='utf8') as f:
        f.write(replaced)


def main(project_dir: Path, license: Path) -> None:
    found_git_directory = find_git_directory(project_dir)
    if found_git_directory is None:
        print("could not find a git directory")
        sys.exit(-1)

    origin_url = get_git_origin_url(found_git_directory)
    if origin_url.endswith('.git'):
        origin_url = origin_url[:-4]

    if args.use_parent_origin:
        origin_url = os.path.dirname(origin_url)

    license_content_replaced = read_and_replace_license_text(license, origin_url)

    all_files = find_all_source_files(project_dir)

    for path in all_files:
        replace_header_in_file(project_dir, path, license_content_replaced)


parser = argparse.ArgumentParser(description='Process some file headers')
parser.add_argument('--license',dest='license', type=Path)
parser.add_argument('--path',dest='path', type=Path, default='.')
parser.add_argument('--use-parent-origin', action='store_true', dest='use_parent_origin')
args = parser.parse_args()

project_dir : Path = args.path
license : Path = args.license

main(project_dir, license)
