# Building and Testing EOS application 

Eos wallet application framework for Ledger devices

This follows the specification available in the doc/ folder

To use the generic wallet refer to `signTransaction.py`, `getPublicKey.py`
or Ledger EOS Wallet application [Anchor](https://www.greymass.com/anchor)

## Quick start guide

1) First make a new directory 
```shell
mkdir ledger-test
cd ledger-test
```

The [ledger-app-dev-tools](https://github.com/LedgerHQ/ledger-app-builder/pkgs/container/ledger-app-builder%2Fledger-app-dev-tools)
docker image contains all the required tools and libraries to **build**, **test** and **load** an application.

2) You can download the development env from the ghcr.io docker repository

```shell
docker pull ghcr.io/ledgerhq/ledger-app-builder/ledger-app-dev-tools:latest
```

3) You can then enter the docker, and the development environment. The eos-application code is mounted from the current working directory. Lets download that as well. Recommend changing to your development branch 

```shell
git clone https://github.com/eosnetworkfoundation/ledger-app.git
cd ledger-app
git checkout develop
```

4) Build per your platform

```shell
docker run --rm -ti -v "$(realpath .):/app" --user $(id -u $USER):$(id -g $USER) ghcr.io/ledgerhq/ledger-app-builder/ledger-app-builder:latest
bash-5.1$ cd /app
bash-5.1$ BOLOS_SDK=$NANOS_SDK make
```

5) Setup Ledger Blue - required python virtual environment, needed for testing and side loading app onto device

```shell
cd /app
# create python virtual env
python3 -m venv private_app_env
# activate python virtual env
source private_app_env/bin/activate  # On Windows, use private_app_env\Scripts\Activate.ps1
# Install Ledger blue (tool to load the app)
python3 -m pip install ledgerblue
```

## Compilation Options

From inside the container, use the following command to build the app:

```shell
bash-5.1$ cd /app
bash-5.1$ make DEBUG=1  # compile optionally with PRINTF
```

You can choose which device to compile and load for by setting the `BOLOS_SDK` environment variable to the following values:

- `BOLOS_SDK=$NANOS_SDK`
- `BOLOS_SDK=$NANOX_SDK`
- `BOLOS_SDK=$NANOSP_SDK`
- `BOLOS_SDK=$STAX_SDK`
- `BOLOS_SDK=$FLEX_SDK`

The application's code will be available from inside the docker container,
you can proceed to the following compilation steps to build your app. To build with [clang static analyzer](https://github.com/LedgerHQ/ledger-app-builder/pkgs/container/ledger-app-builder%2Fledger-app-dev-tools#code-static-analysis) see this example.

```shell
sudo docker run --user "$(id -u)":"$(id -g)" --rm -ti -v "$(realpath .):/app" ledger-app-builder:latest
bash-5.1$ make scan-build
```

## Testing Via The Emulator 

### `Linux`


### `MacOS`

XQuartz is the official X server implementation for macOS.

Download and install XQuartz from:
👉 https://www.xquartz.org
After installation, *restart* your computer for changes to take effect. 

#### Setup MacOS
1) Start XTerm with `open -a XQuartz` 
2) update XQuartz->Settings to allow `network connection`. Shutdown XQuartz
3) run  `xhost + 127.0.0.1` to allow access XTerm Access 
4) Start with `open -a XQuartz` 

```
cd ledger-app # enter directory for EOS Ledger App
sudo docker run --rm -ti -v "$(pwd -P):/app" --user $(id -u):$(id -g) -v "/tmp/.X11-unix:/tmp/.X11-unix" -e DISPLAY="host.docker.internal:0" ghcr.io/ledgerhq/ledger-app-builder/ledger-app-dev-tools:latest
source private_app_env/bin/activate
speculos build/nanos/bin/app.elf --model nanos
```


### Setup Linux 

### Loading on a physical device

This step will vary slightly depending on your platform.

> Your physical device must be connected, unlocked and the screen showing the dashboard (not inside an application).

First make sure you have the proper udev rules added on your host.
See [udev-rules](https://github.com/LedgerHQ/udev-rules)

```
sudo wget -O /etc/udev/rules.d/20-hw1.rules https://raw.githubusercontent.com/LedgerHQ/udev-rules/master/20-hw1.rules
sudo udevadm control --reload-rules
```

#### Physical Device 

> It is assumed you have [Python](https://www.python.org/downloads/) installed on your computer.

Run these commands on your host from the app's source folder once you have built the app
for the device you want:

```shell
# Load the app.
python3 -m ledgerblue.runScript --scp --fileName bin/app.apdu --elfFile bin/app.elf
```

## Unit Tests

The application comes with functional tests,
implemented with Ledger's [Ragger](https://github.com/LedgerHQ/ragger) test framework.
They are located in the directory `tests/functional`.

Install the tests requirements:

```shell
pip install -r tests/functional/requirements.txt
```

Then you can:

Run the functional tests (here for nanos but available for any device once you have built the binaries):

```shell
pytest tests/functional/ --tb=short -v --device nanos
```

Or run your app directly with Speculos

```shell
speculos --model nanos build/nanos/bin/app.elf
```

## References

Full instructions are on [Ledger Developer Portal](https://developers.ledger.com/docs/device-app/develop/quickstart)

## Developer Notes

[Setup Tools, Emulator, and Testing](./docs/Ledger-Developer-Notes.md)


