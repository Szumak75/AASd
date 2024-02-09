# Installation

## Prerequisite

- `master` and future releases is now targeted against Python 3.9 or newer,
- make sure you have python `pip` installed,
    > **FreeBSD:**
    > $ pkg install py39-pip

    > **Debian:**
    > $ apt install python3-pip

- make sure you have python `virtualenv`  installed,
    > **FreeBSD:**
    > $ pkg install py39-virtualenv

    > **Debian:**
    > $ apt install python3-virtualenv
- `git` optional but highly recommended
- service supervision [`runit`](http://smarden.org/runit/) or similar as [`daemontools`](https://cr.yp.to/daemontools.html)

## Preparation

The default project location is assumed to be in the /opt directory, but this is a matter of user choice.

If you choose a different location, remember to modify the startup scripts.

- ZFS-based file system

```
$ zfs create -o mountpoint=/opt zroot/opt
```

- alternative old way

```
$ mkdir /opt
```

## Getting source

The preferred method is to use `git`:

```
$ cd /opt
$ git clone https://github.com/Szumak75/AASd.git
```

or download zipped source from github and extract it to `/opt` directory.


## Initialize the virtual environment

```
$ cd /opt/AASd
$ python3 -m venv .venv
```

## Activate the virtual environment

- csh

```
$ source /opt/AASd/.venv/bin/activate.csh
```

- sh

```
$ . /opt/AASd/.venv/bin/activate
```

## Install the requirements with `pip`

```
$ cd /opt/AASd
$ pip install --upgrade pip
$ pip install -r requirements.txt
```

## Generating a configuration file

A non-existent configuration file will be generated automatically the first time you run the program.

The location of the configuration file for a STABLE or RELEASE project is '/etc/aasd.conf'\
For DEVEL version: '/var/tmp/aasd.conf'

```
$ ./aasd.py -d
[AASd]: [Config] Config initialization...
[AASd]: [Config] ... complete
[AASd->WARNING]: [Config] config file '/etc/aasd.conf' not exist
[AASd->WARNING]: [Config] try to create default one
[AASd->DEBUG]: [Config] Found communication modules list: ['memailalert', 'memailalert2']
[AASd->DEBUG]: [Config] Found running modules list: ['memailtest', 'micmp', 'mlmspayment', 'mtest']
[AASd->DEBUG]: [Config] config file saved successful
[AASd->DEBUG]: [Config] try to load config file: '/etc/aasd.conf'...
[AASd->DEBUG]: [Config] config file loaded successful
[AASd]: [Config] list of modules to enable: ['']
[AASd->DEBUG]: [ThLoggerProcessor] Start.
[AASd]: starting...
[AASd->DEBUG]: [ThDispatcher] entering to the main loop
[AASd->DEBUG]: [Config] found module list: ['memailalert', 'memailalert2']
[AASd->DEBUG]: [Config] found module list: ['memailtest', 'micmp', 'mlmspayment', 'mtest']
[AASd]: entering to the main loop
^C[AASd->DEBUG]: TERM or INT signal received.
[AASd->DEBUG]: [ThDispatcher] stop signal received
[AASd->DEBUG]: [ThDispatcher] exit from loop
[AASd->DEBUG]: [ThLoggerProcessor] stopping...
[AASd->DEBUG]: [ThLoggerProcessor] Stop.
```

To interrupt a running process, send the interrupt signal [ctrl]-[c] or the TERM signal with the kill command.

The configuration file is divided into sections containing variables.\
The main section `[aasd]` contains the `salt` variable used to simply encrypt password variables.\
The second important variable is `modules` - it is a list of modules that we want to activate after configuration.\
The remaining sections contain a description and configuration variables of the current module list.

## Password encryption

This function requires explanation at the current stage of preparing the system for operation.

Many current and future modules require configuring variables containing passwords for authenticating connections to external services, such as smtp servers, databases, etc.

It was assumed that these passwords would be encrypted with a simple two-sided algorithm.\
This, of course, does not protect against password interception, but limits its readability.

For example, to add the password for the `memailalert` module to the `smtp_pass` variable, we run the project as follows:

```
$ ./aasd.py -p --section=memailalert --varname=smtp_pass
Receive password encoder options.
Enter password: Qwerty12
Config file "/etc/aasd.conf" updated.
```

As a result of executing this command, the `smtp_pass` variable will be assigned an encoded string of characters:

```
$ grep 'smtp_pass' /etc/aasd.conf|head -2
# smtp_pass [str] - smtp auth password for sending emails.
smtp_pass = "//4AAD0AAABZAAAAJwAAAFQAAABWAAAAIQAAAEcAAABIAAAA"
```

## Preparation to launch the project

## Integration and start with `runit`
