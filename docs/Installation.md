# Installation

## Environment Policy

- Poetry is used only in development environments.
- Production and deployment environments should install runtime packages from `requirements.txt`.
- `requirements.txt` is generated from the current Poetry runtime lock set and is the supported deployment input.

## Prerequisite

- `master` and future releases are now targeted against Python 3.11 or newer,
- make sure you have python `pip` installed,

  > **FreeBSD:**
  > $ pkg install py311-pip

  > **Debian:**
  > $ apt install python3-pip

- make sure you have python `virtualenv` installed,

  > **FreeBSD:**
  > $ pkg install py311-virtualenv

  > **Debian:**
  > $ apt install python3-virtualenv

- `git` optional but highly recommended
- service supervision [`runit`](http://smarden.org/runit/) or similar as [`daemontools`](https://cr.yp.to/daemontools.html)

## Preparation

The default project location is assumed to be in the /opt directory, but this is a matter of user choice.

If you choose a different location, remember to modify the startup scripts.

- ZFS-based file system

```
zfs create -o mountpoint=/opt zroot/opt
```

- alternative old way

```
mkdir /opt
```

## Getting source

The preferred method is to use `git`:

```
cd /opt
git clone https://github.com/Szumak75/AASd.git
```

or download zipped source from github and extract it to `/opt` directory.

## Initialize the virtual environment

```
cd /opt/AASd
python3 -m venv .venv
```

## Activate the virtual environment

- csh

```
source /opt/AASd/.venv/bin/activate.csh
```

- sh

```
. /opt/AASd/.venv/bin/activate
```

## Install the requirements with `pip`

This is the recommended installation path for production and deployment
environments.

```
cd /opt/AASd
pip install --upgrade pip
pip install -r requirements.txt
```

## Development Workflow

Poetry is reserved for development work such as dependency management, testing,
linting, type checking, and documentation generation.

Typical development setup:

```bash
poetry install
poetry run pytest
make docs
```

If runtime dependencies are changed in Poetry, `requirements.txt` should be
refreshed before preparing a production deployment.

## Generating a configuration file

A non-existent configuration file will be generated automatically the first time you run the program.

The location of the configuration file for a STABLE or RELEASE project is '/etc/aasd.conf'\
For DEVEL version: '/var/tmp/aasd.conf'

```
% ./aasd.py -d
[AASd]: [Config] Config initialization...
[AASd]: [Config] ... complete
[AASd->WARNING]: [Config] config file '/etc/aasd.conf' does not exist
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

When you refresh an existing configuration file with `-U`, the daemon still adds
only missing module-level settings by default. The main daemon section remains
manual-edit only, with one exception: `plugins_dir` can be updated from the
command line with `-P`.

```bash
./aasd.py -P /tmp -U
```

If `plugins_dir` is missing in an older configuration file, the same update mode
adds it with the default value `./plugins`.

## Password encryption

This function requires explanation at the current stage of preparing the system for operation.

Many current and future modules require configuring variables containing passwords for authenticating connections to external services, such as smtp servers, databases, etc.

It was assumed that these passwords would be encrypted with a simple two-sided algorithm.\
This, of course, does not protect against password interception, but limits its readability.

For example, to add the password for the `memailalert` module to the `smtp_pass` variable, we run the project as follows:

```
% ./aasd.py -p --section=memailalert --varname=smtp_pass
Receive password encoder options.
Enter password: Qwerty12
Config file "/etc/aasd.conf" updated.
```

As a result of executing this command, the `smtp_pass` variable will be assigned an encoded string of characters:

```
% grep 'smtp_pass' /etc/aasd.conf|head -2
# smtp_pass [str] - smtp auth password for sending emails.
smtp_pass = "//4AAD0AAABZAAAAJwAAAFQAAABWAAAAIQAAAEcAAABIAAAA"
```

## Preparation to launch the project with `runit`

The project in the `/opt/AASd/docs/runit` directory contains a prepared startup schema for `runit`.\
The schema has two functions:

- starts a logger that captures diagnostic information sent by the daemon to stdout, tags it with the '**AASd**' tag and sends it to syslog,
- starts the main daemon process and keeps it running,

### FreeBSD syslog configuration

Syslog configuration example.

```
% cat /etc/syslog.d/aasd.conf
!AASd
*.*               /var/log/aasd.log
```

Example of a log archiving system configuration.

```
% cat /etc/newsyslog.conf.d/aasd.conf
/var/log/aasd.log    644 7 1000  * J
```

Reloading the new syslog configuration:

```
service syslogd reload
```

### Starting daemon with `runit`

You must copy the folder with the startup schema to the destination appropriate for the configured `runit` manager schemas. The AASd daemon will be started automatically.

Please check the contents of the `/var/log/aasd.log` log file to see if all project subsystems have been initialized correctly.
