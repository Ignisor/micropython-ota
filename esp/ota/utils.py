import uos

from ota import utarfile


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


def untar(file, destination):
    t = utarfile.TarFile(file)
    for i in t:
        target = '{}/{}'.format(destination, i.name)

        if i.type == utarfile.DIRTYPE:
            ensure_dirs(target)
        else:
            src_file = t.extractfile(i)
            dest_file = open(target, "wb")

            while True:
                buf = src_file.read(512)

                if not buf:
                    break
                dest_file.write(buf)

            dest_file.close()

