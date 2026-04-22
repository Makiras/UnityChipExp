FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Asia/Shanghai \
    LANG=C.UTF-8 \
    LANGUAGE=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    MPLBACKEND=Agg \
    MPLCONFIGDIR=/tmp/matplotlib \
    JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64 \
    JDK_HOME=/usr/lib/jvm/java-17-openjdk-amd64

SHELL ["/bin/bash", "-lc"]

ARG VERILATOR_VERSION=v5.026
ARG SWIG_VERSION=v4.4.0
ARG GO_VERSION=1.25.1
ARG VERIBLE_VERSION=v0.0-3979-g786edf03
ARG PICKER_REPO=https://github.com/XS-MLVP/picker.git
ARG PICKER_BRANCH=isca26_ae
ARG PICKER_COMMIT=f1fe212
ARG BUILD_XSPCOMM_SWIG=python,java,golang

RUN apt-get update && apt-get install -y --no-install-recommends \
    autoconf \
    automake \
    bison \
    build-essential \
    ca-certificates \
    ccache \
    cmake \
    curl \
    fonts-dejavu-core \
    flex \
    g++ \
    gcc \
    git \
    gperf \
    help2man \
    libfl-dev \
    libpcre2-dev \
    libtool \
    make \
    numactl \
    openjdk-17-jdk \
    perl \
    pkg-config \
    python3 \
    python3-dev \
    python3-pip \
    python3-venv \
    tzdata \
    util-linux \
    wget \
    xz-utils \
    zlib1g-dev && \
    ln -fs /usr/share/zoneinfo/${TZ} /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata && \
    rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/verilator/verilator.git \
        --branch ${VERILATOR_VERSION} \
        --depth 1 \
        /tmp/verilator && \
    cd /tmp/verilator && \
    autoconf && \
    ./configure --prefix=/usr/local && \
    make -j"$(nproc)" && \
    make install && \
    rm -rf /tmp/verilator

RUN python3 -m pip install --no-cache-dir --upgrade pip && \
    python3 -m pip install --no-cache-dir cocotb==1.9.2 matplotlib

RUN git clone https://github.com/swig/swig.git \
        --branch ${SWIG_VERSION} \
        --depth 1 \
        /tmp/swig && \
    cd /tmp/swig && \
    ./autogen.sh && \
    ./configure --prefix=/usr/local && \
    make -j"$(nproc)" && \
    make install && \
    rm -rf /tmp/swig

RUN ARCH="$(uname -m)" && \
    case "${ARCH}" in \
        x86_64) GOARCH=amd64 ;; \
        aarch64) GOARCH=arm64 ;; \
        *) echo "Unsupported arch: ${ARCH}" && exit 1 ;; \
    esac && \
    wget -q "https://go.dev/dl/go${GO_VERSION}.linux-${GOARCH}.tar.gz" -O /tmp/go.tgz && \
    rm -rf /usr/local/go && \
    tar -C /usr/local -xzf /tmp/go.tgz && \
    rm -f /tmp/go.tgz

ENV PATH=${JAVA_HOME}/bin:/usr/local/go/bin:/usr/local/bin:/home/xyl/.local/bin:${PATH}

RUN ARCH="$(uname -m)" && \
    case "${ARCH}" in \
        x86_64) VERIBLE_ARCH=x86_64 ;; \
        aarch64) VERIBLE_ARCH=aarch64 ;; \
        *) echo "Unsupported arch: ${ARCH}" && exit 1 ;; \
    esac && \
    wget -q \
      "https://github.com/chipsalliance/verible/releases/download/${VERIBLE_VERSION}/verible-${VERIBLE_VERSION}-linux-static-${VERIBLE_ARCH}.tar.gz" \
      -O /tmp/verible.tar.gz && \
    tar -xzf /tmp/verible.tar.gz -C /usr/local --strip-components=1 && \
    rm -f /tmp/verible.tar.gz

RUN useradd -m -s /bin/bash xyl && \
    mkdir -p /home/xyl && \
    chown -R xyl:xyl /home/xyl

RUN git clone "${PICKER_REPO}" \
        --branch "${PICKER_BRANCH}" \
        --single-branch \
        /home/xyl/picker && \
    cd /home/xyl/picker && \
    git checkout "${PICKER_COMMIT}" && \
    export JAVA_HOME="$(dirname "$(dirname "$(readlink -f "$(command -v javac)")")")" && \
    export PATH="${JAVA_HOME}/bin:${PATH}" && \
    make init && \
    make BUILD_XSPCOMM_SWIG="${BUILD_XSPCOMM_SWIG}" && \
    make BUILD_XSPCOMM_SWIG="${BUILD_XSPCOMM_SWIG}" install && \
    make clean

RUN apt-get update && apt-get install -y --no-install-recommends time && \
    rm -rf /var/lib/apt/lists/*

RUN ldconfig

RUN find /usr/local -type d -exec chmod 755 {} + && \
    find /usr/local -type f -perm /111 -exec chmod 755 {} +

RUN verilator --version && \
    python3 --version && \
    cocotb-config --version && \
    swig -version | sed -n '1,4p' && \
    go version && \
    java -version && \
    gcc --version | sed -n '1p' && \
    picker --version

COPY . /home/xyl/exp
RUN chown -R xyl:xyl /home/xyl/exp

USER xyl
WORKDIR /home/xyl/exp

CMD ["/bin/bash"]
