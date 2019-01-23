import uos
import urequests


def ensure_dirs(path):
    split_path = path.split('/')
    if len(split_path) > 1:
        for i, fragment in enumerate(split_path):
            parent = '/'.join(split_path[:-i])
            try:
                uos.mkdir(parent)
            except OSError:
                pass


def move_f(source, destination):
    """Move file or directory with subfiles"""
    try:
        content = uos.listdir(source)
    except OSError:
        content = None

    if not content:
        uos.rename(source, destination)
        return

    for item in content:
        move_f('{}/{}'.format(source, item), '{}/{}'.format(destination, item))


def download_file(url, save_path):
    response = urequests.get(url)

    with open(save_path, 'wb') as target_file:
        target_file.write(response.content)
