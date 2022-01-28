import os.path

from Melodie.studio.handler_filesystem import get_all_file_items
from tests.config import resources_path


def test_fs_items():
    items = get_all_file_items(os.path.join(resources_path, "fs_demo"))
    assert len(items) == 3
    items_set = set()
    for item in items:
        items_set.add((item['name'], item['type']))
    assert ('test.py', 'file') in items_set
    assert ('test', 'directory') in items_set
    assert ('README.md', 'file') in items_set
