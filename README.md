# apt_prepare
Creates the necessary apt repository files for a local apt repository

## Usage
```bash
./apt_prepare.py
```

* The first time the program is run it will create a config file *~/.apt_prepare/apt_prepare.ini*, which needs to be edited by the user
* The second run will create the necessary apt repository files.  You will need to enter your gpg passphrase for program to work.
* Subsequent runs will only create the apt repository files if new repository files were added since last run.

## Config File - apt_sync.ini
```ini
[APT_SYNC]
LogLevel = INFO
DEBRepository = /opt/apt-mirror/raspbian/stretch

[APT_DATA]
LastModified = 
```
* Valid values for *LogLevel* are *DEBUG, INFO, WARN, ERROR*
* *DEBRepository* is the location of the apt repository
* *LastModified* is used by the program to write the *DEBRepository* directory last modified time, in EPOCH format

## Basic logic of the program
```bash
apt-ftparchive packages /opt/apt-mirror/raspbian/stretch > /opt/apt-mirror/raspbian/stretch/Packages
gzip -c /opt/apt-mirror/raspbian/stretch/Packages > /opt/apt-mirror/raspbian/stretch/Packages.gz
apt-ftparchive release /opt/apt-mirror/raspbian/stretch > /opt/apt-mirror/raspbian/stretch/Release
gpg --yes --clearsign -o /opt/apt-mirror/raspbian/stretch/InRelease /opt/apt-mirror/raspbian/stretch/Release
gpg --yes -abs -o /opt/apt-mirror/raspbian/stretch/Release.gpg /opt/apt-mirror/raspbian/stretch/Release
```
