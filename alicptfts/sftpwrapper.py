# Adapted from Mathew Newville's code
# https://github.com/pyepics/newportxps/blob/master/newportxps/ftp_wrapper.py

import pysftp
from io import BytesIO

class SFTPWrapper():
    def __init__(self):
        self.host = None
        self.username = None
        self.password = None
        self._conn = None

    def connect(self, host=None, username=None, password=None):
        self.host = host
        self.username = username
        self.password = password
        try:
            self._conn = pysftp.Connection(host=self.host,
                                           username=self.username,
                                           password=self.username)
        except:
            print('SFTP Error: SFTP connection to {0} failed'.format(self.host))
            print('May need to add the host keys for the XPS to the')
            print('ssh known_hosts file, using a command like this:')
            print(' ssh-keyscan {0} >> ~/.ssh/known_hosts'.format(self.host))
            raise

    def close(self):
        if self._conn is not None:
            self._conn.close()
        self._conn = None

    def cwd(self, remotedir):
        try:
            self._conn.cwd(remotedir)
        except IOError:
            print('Error: Could not find path')
            raise

    def save(self, remotefile, localfile):
        "Save a remote file to a local file"
        try:
            self._conn.get(remotepath=remotefile, localpath=localfile)
        except IOError:
            print('Error: Could not save file')
            raise

    def put(self, localfile, remotefile):
        try:
            self._conn.put(localpath=localfile, remotepath=remotefile)
        except IOError:
            print('SFTP Error: Remote path does not exist')
            raise
        except OSError:
            print('SFTP Error: Local file does not exist')
            raise

        else:
            return True

    def getlines(self, remotefile):
        "Read text of a remote file"
        tmp = BytesIO()
        try:
            self._conn.getfo(remotefile, tmp)
        except:
            print('SFTP Error: Could not read remotefile')
            raise
        else:
            tmp.seek(0)
            text = bytes2str(tmp.read())
            return(text.split('\n'))

def bytes2str(s):
    FTP_ENCODING = 'latin-1'
    return str(s, FTP_ENCODING)
    