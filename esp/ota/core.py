import uos
import ujson
import urequests

from ota.utils import move_f, download_file, ensure_dirs

PROVIDERS = {
    'github': 'https://api.github.com/repos/{owner}/{repo}',
}


class Firmware(object):
    def __init__(self, verbose=2):
        self.verbose = verbose

        self.version = self.__get_version()
        self.conf = self.__get_conf()

        self.__base_url = self.__get_base_url()

    def __get_version(self):
        try:
            with open('.version') as version_file:
                version = version_file.read()
        except OSError:
            version = None

        return version

    def __get_conf(self):
        with open('ota_conf.json') as conf_file:
            conf_json = conf_file.read()

        return ujson.loads(conf_json)

    def __get_base_url(self):
        provider = self.conf['remote']['provider']
        base_url = PROVIDERS.get(provider.lower())

        if not base_url:
            raise ValueError('{} is not supported. '
                             'Available providers: {}'.format(provider, ', '.join(PROVIDERS.keys())))

        base_url = base_url.format(**self.conf['remote'])

        return base_url

    def remote_version(self):
        endpoint = '/commits/master'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/50.0.2661.102 Safari/537.36',
            'Accept': 'application/vnd.github.VERSION.sha',
        }
        response = urequests.get(self.__base_url + endpoint, headers=headers)

        if response.status_code != 200:
            raise ValueError('Error while getting version from server '
                             '"{}: {} ({})"'.format(response.status_code, response.reason, response.text))

        return response.text.strip()

    def has_latest_version(self):
        return self.version == self.remote_version()

    def __download_latest(self):
        target = 'firmware'
        try:
            uos.rmdir(target)
        except OSError:
            pass

        uos.mkdir(target)

        self.__download_from_git(git_dir=self.conf.get('root_dir', '', target=target))

    def __download_from_git(self, git_dir='', target_dir='firmware'):
        endpoint = '/contents/' + git_dir

        response = urequests.get(self.__base_url + endpoint)
        paths_data = response.json()

        for path in paths_data:
            if path['download_url']:
                if self.verbose > 1:
                    print('Downloading {}...'.format(path['path']))
                download_file(path['download_url'], '{}/{}'.format(target_dir, path['path']))
            else:
                ensure_dirs('{}/{}'.format(target_dir, path['path']))
                self.__download_from_git(path['path'], target_dir=target_dir)

    @staticmethod
    def backup(dir_to_backup='firmware'):
        target = 'backup'
        try:
            uos.rmdir(target)
        except OSError:
            pass

        uos.mkdir(target)

        move_f(dir_to_backup, target)

    @staticmethod
    def restore_backup(dir_to_restore='firmware'):
        target = 'backup'
        try:
            uos.rmdir(dir_to_restore)
        except OSError:
            pass

        uos.mkdir(dir_to_restore)
        move_f(target, dir_to_restore)

    def update(self, force=False):
        if not force and self.has_latest_version():
            if self.verbose > 0:
                print('Firmware already up to date (version: {})'.format(self.version))

            return False

        if self.version is not None:
            if self.verbose > 1:
                print('Storing backup of current firmware version...')
            Firmware.backup()

        if self.verbose > 1:
            print('Downloading new firmware...')
        self.__download_latest()

        if self.verbose > 1:
            print('Unpacking new firmware...')

