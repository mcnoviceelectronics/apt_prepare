#!/usr/bin/env python3

# Created by MCNoviceElectronics
# March 2018
# Vist: https://mcnoviceelectronics.wordpress.com

from apt_prepare_config import APT_Prepare_Config

import datetime
import logging
import os
import signal
import subprocess

_config_dir = '.apt_prepare'
_config_file = 'apt_prepare.ini'

#
# Custom logging formatter for exceptions
#   makes them all one line
#
class OneLineExceptionFormatter(logging.Formatter):
    def formatException(self, exc_info):
        result = super().formatException(exc_info)
        result = result.replace('\n', ' ')
        return repr(result)

    def format(self, record):
        result = super().format(record)
        if record.exc_text:
            result = result.replace("\n", "")
        return result

#
# Handles signals and cleans up everything
#
def sig_handler(signum, frame):
    logging.shutdown()
    quit()

#
#  Setup the custom logger
#
def setup_logging(log_level):
    handler = logging.StreamHandler()
    formatter = OneLineExceptionFormatter('%(asctime)s|%(filename)s|%(name)s|%(levelname)s|%(lineno)d|%(message)s')
    handler.setFormatter(formatter)
    root = logging.getLogger('APT_PREPARE')
    root.setLevel(os.environ.get('LOGLEVEL', log_level))
    root.addHandler(handler)
    return root

def run_shell_cmd(shell_cmd, func_txt='run_shell_cmd'):
    p_status = -1
    try:
        logging.debug('%s shell command: %s', func_txt, shell_cmd)
        p = subprocess.Popen(shell_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()
        p_status = p.wait()
        logging.debug('Output: %s', output)
        if p_status != 0:
            logging.error('Shell cmd status: %d', p_status)
            logging.error('Error msg: %s', err)
    except:
        logging.exception('Exception in %s', func_txt)
        raise SystemExit

    return p_status, output

def get_dir_modify_time(dir_location):
    dir_modify_unix_ts = int(os.path.getmtime(dir_location))
    logging.info('Mod time: %s (%s)',
                 dir_modify_unix_ts,
                 datetime.datetime.fromtimestamp(int(dir_modify_unix_ts)).strftime('%Y-%m-%d %H:%M:%S'))
    return dir_modify_unix_ts

def main():
    #INIT everything
    try:
        setup_logging('INFO')
        apt_prepare_config = APT_Prepare_Config(log_level='INFO')
        deb_repository, last_modified \
            = apt_prepare_config.setup_config(_config_dir, _config_file)
    except SystemExit:
        logging.warn('Config needs to be setup, exiting')
        logging.shutdown()
        quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    ftparchive_packages_cmd = 'apt-ftparchive packages ' + deb_repository + ' > ' \
                                + deb_repository + '/Packages'
    gzip_packages_cmd = 'gzip -c ' + deb_repository + '/Packages > ' + \
                            deb_repository + '/Packages.gz'
    ftparchive_release_cmd = 'apt-ftparchive release ' + deb_repository + ' > ' + \
                                deb_repository + '/Release'
    gpg_clearsign_cmd = 'gpg --yes --clearsign -o ' + deb_repository + '/InRelease ' + \
                            deb_repository + '/Release'
    gpg_sign_cmd = 'gpg --yes -abs -o ' + deb_repository + '/Release.gpg ' + \
                        deb_repository + '/Release'


    deb_rep_unix = get_dir_modify_time(deb_repository)
    try:
        if last_modified is None or deb_rep_unix > last_modified:
            run_shell_cmd(ftparchive_packages_cmd, 'ftparchive_packages_cmd')
            run_shell_cmd(gzip_packages_cmd, 'gzip_packages_cmd')
            run_shell_cmd(ftparchive_release_cmd, 'ftparchive_release_cmd')
            run_shell_cmd(gpg_clearsign_cmd, 'gpg_clearsign_cmd')
            run_shell_cmd(gpg_sign_cmd, 'gpg_sign_cmd')
            deb_rep_unix = get_dir_modify_time(deb_repository)
            apt_prepare_config.update_last_modified(deb_rep_unix)
            logging.info('All Good')
        else:
            logging.info('Directory has not been modified, doing nothing')
    except SystemExit:
        logging.error('Problem while running commands, exiting')
        quit()
    finally:
        logging.shutdown()

if __name__ == "__main__":
    main()
