FROM ubuntu:22.04
# to use ubuntu 24.04 can reference here: https://www.youtube.com/watch?v=fY7u6PiV8qA

ENV DEBIAN_FRONTEND=noninteractive

# Source tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    gawk wget git diffstat unzip texinfo chrpath socat \
    && rm -rf /var/lib/apt/lists/*

# Build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc build-essential cpio xz-utils \
    && rm -rf /var/lib/apt/lists/*

# Python tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip python3-pexpect python3-git python3-jinja2 \
    && rm -rf /var/lib/apt/lists/*

# Utils
RUN apt-get update && apt-get install -y --no-install-recommends \
    debianutils iputils-ping openssh-client file locales zstd lz4 \
    && rm -rf /var/lib/apt/lists/*

# Dev libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    libegl1-mesa libsdl2-dev \
    && rm -rf /var/lib/apt/lists/*

# Setting locale for yocto build
RUN locale-gen en_US.UTF-8

ENV LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8

# Install kas
RUN pip3 install --no-cache-dir kas

# DNS tools for testing
RUN apt-get update && apt-get install -y dnsutils curl 

# Install faketime for signing keys
# RUN apt-get update && apt-get install -y --no-install-recommends faketime

# non-root user setup
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=1000
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && apt-get update && apt-get install -y sudo \
    && echo "$USERNAME ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

USER $USERNAME

RUN git config --global user.name "Yocto Builder" \
    && git config --global user.email "builder@linnie.local" \
    && git config --global safe.directory '*'
    
WORKDIR /workspaces/linnie

CMD ["/bin/bash"]