#!/usr/bin/env python3
import os
import zipapp
import zipfile
from tempfile import mkstemp
from zipfile import ZipFile


def zipfile_module(zip_file, module_name):
    module = __import__(module_name)
    module_path = module.__path__[0]
    for directory_path, dirs, files in os.walk(module_path):
        for file_name in files:
            if '__pycache__' in directory_path:
                continue
            if file_name.endswith('.pyc') or file_name.endswith('.pyo'):
                continue
            store_path = os.path.join(directory_path.replace(module_path, module_name), file_name)
            target_path = os.path.join(directory_path, file_name)
            print('write', store_path)
            zip_file.write(target_path, store_path)


def main():
    export_filename = 'bilibili-live.pyz'
    _, temp_path = mkstemp()
    with ZipFile(temp_path, 'w', compression=zipfile.ZIP_DEFLATED) as target:
        zipfile_module(target, 'requests')
        zipfile_module(target, 'pyasn1')
        zipfile_module(target, 'rsa')
        zipfile_module(target, 'bilibili_live_kit')
        target.write('bilibili-live.py', '__main__.py')
    zipapp.create_archive(temp_path, export_filename, '/usr/bin/env python3')
    os.chmod(export_filename, 0o744)


if __name__ == '__main__':
    main()
