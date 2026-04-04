# Docker Build Notes

This file is only for building and debugging the Docker image.
Do not use it as the reviewer-facing reproduction guide yet.

## Goal

Build a self-contained image that:

- uses Ubuntu 22.04
- builds `verilator` from source
- installs `cocotb==1.9.2`
- builds `swig` from source
- installs `go1.25.1`
- clones `picker` from the remote `isca26_ae` branch
- pins `picker` to commit `f1fe212`
- copies this repository into `/home/xyl/exp`

The Docker build must not depend on a local `/home/xyl/picker` checkout.

## Current Dockerfile

The image definition is:

- [docker/Dockerfile](/home/xyl/exp/docker/Dockerfile)

The Dockerfile already fetches `picker` from GitHub:

```dockerfile
ARG PICKER_REPO=https://github.com/XS-MLVP/picker.git
ARG PICKER_BRANCH=isca26_ae
ARG PICKER_COMMIT=f1fe212
```

## Build Command

Run from the repository root:

```bash
cd /home/xyl/exp
sudo docker build --network=host -f docker/Dockerfile -t exp-repro:dev .
```

To force a clean rebuild:

```bash
cd /home/xyl/exp
sudo docker build --no-cache --network=host -f docker/Dockerfile -t exp-repro:dev .
```

## Optional Build Args

If the pinned picker revision changes, override it explicitly:

```bash
cd /home/xyl/exp
sudo docker build \
  --network=host \
  --build-arg PICKER_BRANCH=isca26_ae \
  --build-arg PICKER_COMMIT=f1fe212 \
  -f docker/Dockerfile \
  -t exp-repro:dev .
```

Other useful overrides:

```bash
--build-arg VERILATOR_VERSION=v5.026
--build-arg SWIG_VERSION=v4.4.0
--build-arg GO_VERSION=1.25.1
--build-arg BUILD_XSPCOMM_SWIG=python,java,golang
```

## Expected Tool Versions

The target environment should match these versions as closely as possible:

- `picker`: branch `isca26_ae`, commit `f1fe212`
- `verilator`: `5.026`
- `python3`: `3.10.x`
- `cocotb`: `1.9.2`
- `openjdk`: `17`
- `golang`: `1.25.1`
- `gcc/g++`: `11.x`
- `cmake`: Ubuntu 22.04 package
- `swig`: `4.4.0`

## Container Layout

The image is intended to provide these paths:

- `/home/xyl/picker`
- `/home/xyl/exp`
- `/usr/local/bin/picker`
- `/usr/local/share/picker`
- `/usr/local/lib/libxspcomm*`

This mirrors the current experiment scripts so they can run without immediate path rewrites.

## Current Validated Result

The current Dockerfile has been validated to build successfully with:

```bash
cd /home/xyl/exp
sudo docker build --network=host -f docker/Dockerfile -t exp-repro:dev .
```

Important details from the validated build:

- `picker` is cloned from the remote `isca26_ae` branch
- `picker` is checked out to `f1fe212`
- `JAVA_HOME` must be set during `picker` build so `FindJNI` succeeds
- `--network=host` is recommended for environments that rely on host-side proxy/network settings

## Smoke Test Plan

After the image builds successfully:

1. Start an interactive shell.
2. Check installed tools.
3. Run a small `rocket` smoke test first.

Suggested commands:

```bash
docker run --rm -it exp-repro:dev bash
```

Inside the container:

```bash
picker --version
verilator --version
python3 --version
cocotb-config --version
go version
java -version
gcc --version | head -n 1
```

Then try a minimal smoke test:

```bash
cd /home/xyl/exp
make -C rocket/picker clean
bash rocket/picker/build_time.sh
```

If that succeeds, continue with:

```bash
bash rocket/picker/run_time.sh
```

Then move on to:

- `rocket/cocotb`
- `rocket/multilang`
- `coupledL2`

## Debugging Notes

If the image fails during `picker` build:

- verify the remote branch and commit still exist
- verify `make init` inside picker still succeeds non-interactively
- verify `BUILD_XSPCOMM_SWIG=python,java,golang` still matches the current experiment needs

If the image fails during experiment execution:

- check that `picker --version` is available in `PATH`
- check `/usr/local/share/picker` exists
- check `libxspcomm` is visible from `/usr/local/lib`
- check `cocotb-config --version`

## Not Done Yet

This file does not mean the Docker flow is validated.
It only documents the current build target and the commands needed to debug the image build.
