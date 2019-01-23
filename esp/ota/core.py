import uos
import ujson
import urequests

from ota.utils import https_get_to_file, move_f, untar

PROVIDERS = {
    'github': 'https://api.github.com/repos/{owner}/{repo}',
}


class Firmware(object):
    def __init__(self):
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
        endpoint = '/legacy.tar.gz/master'

        response = urequests.get(self.__base_url + endpoint)

        with open('latest.tar.gz', 'wb') as target_file:
            target_file.write(response.content)

    @staticmethod
    def __unpack_firmware(file='latest.tar.gz', dest='firmware'):
        try:
            uos.rmdir(dest)
        except OSError:
            pass

        uos.mkdir(dest)

        untar(file, dest)

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

    def update(self, force=False, verbose=2):
        if not force and self.has_latest_version():
            if verbose > 0:
                print('Firmware already up to date (version: {})'.format(self.version))

            return False

        if self.version is not None:
            if verbose > 1:
                print('Storing backup of current firmware version...')
            Firmware.backup()

        if verbose > 1:
            print('Downloading new firmware...')
        self.__download_latest()

        if verbose > 1:
            print('Unpacking new firmware...')
        Firmware.__unpack_firmware()
        uos.remove('latest.tar.gz')
