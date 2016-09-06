#!/usr/bin/env python3
import os
import re
from tempfile import mkstemp
from zipapp import create_archive
from zipfile import ZipFile, ZIP_DEFLATED


def zipfile_module(zip_file, module_name):
    module = __import__(module_name)
    module_path = os.path.dirname(module.__file__)
    for dirpath, _, filenames in os.walk(module_path):
        for filename in filenames:
            if '__pycache__' in dirpath:
                continue
            if re.search('\.(py[cod]|so)$', filename):
                continue
            if re.search('\$py\.class$', filename):
                continue
            target_path = os.path.join(dirpath, filename)
            store_path = target_path.replace(module_path, module_name)
            zip_file.write(target_path, store_path)
            print('write %r done' % store_path)


def main():
    export_filename = 'bilibili-live.pyz'
    _, temp_path = mkstemp()
    with ZipFile(temp_path, 'w', compression=ZIP_DEFLATED) as target:
        zipfile_module(target, 'requests')
        zipfile_module(target, 'pyasn1')
        zipfile_module(target, 'rsa')
        zipfile_module(target, 'bilibili_live_kit')
        target.write('bilibili-live.py', '__main__.py')
    create_archive(temp_path, export_filename, '/usr/bin/env python3')
    os.chmod(export_filename, 0o744)


if __name__ == '__main__':
    main()
