# Setup Emulator for Ledger Devices

First step is to setup the emulator `speculos`. [Ledger Manual](https://speculos.ledger.com/user/docker.html). 
## Install Emulator on Linux

```console
pip install speculos
```

## Run and use the emulator

```shell
./speculos.py build/nanos/bin/app.elf
```

> You can go to `http://127.0.0.1:5000/` for another interface and more data


### Install on Mac Silicon 

1) Clone [speculos git repo](https://github.com/LedgerHQ/speculos)
2) Mac Silicon Patch Dockerfile

```Dockerfile
# before
FROM ghcr.io/ledgerhq/speculos-builder:latest AS builder
# after
FROM speculos-builder:latest AS builder
```

3) Build Docker Container Image 

```sh
cd speculos
docker build -f build.Dockerfile -t speculos-builder:latest .
docker build -f Dockerfile -t speculos:latest .
```
