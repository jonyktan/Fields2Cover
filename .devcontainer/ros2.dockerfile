FROM osgeo/gdal:ubuntu-full-3.6.3

LABEL NAME="fields2cover" \
      VERSION="2.0.0" \
      DESC="Fields2Cover is a complete coverage path planning package for autonomous robots" \
      MAINTAINER="Gonzalo Mier"


ENV DEBIAN_FRONTEND noninteractive

WORKDIR /workspaces/
RUN mkdir -p /usr/include/new_gdal && \
    cp -r /usr/include/gdal* /usr/include/new_gdal/ && \
    cp /usr/include/ogr* /usr/include/new_gdal/ && \
    cp /usr/include/cpl* /usr/include/new_gdal/ && \
    mv /usr/include/new_gdal/ /usr/include/gdal/

RUN apt-get update --allow-insecure-repositories -y && \
    apt-get install -y --allow-unauthenticated --no-install-recommends ca-certificates


RUN if gdalinfo --version | grep -o " 3\.[0-2]\."; then \
      apt-get install wget && \
      wget https://github.com/Kitware/CMake/releases/download/v3.17.2/cmake-3.17.2-Linux-x86_64.sh \
      -q -O /tmp/cmake-install.sh \
      && chmod u+x /tmp/cmake-install.sh \
      && mkdir /usr/bin/cmake \
      && /tmp/cmake-install.sh --skip-license --prefix=/usr/bin/cmake \
      && rm /tmp/cmake-install.sh; \
    else \
      apt install -y  --allow-unauthenticated --no-install-recommends cmake ; \ 
    fi

ENV PATH="/usr/bin/cmake/bin:${PATH}"


RUN apt-get install -y --allow-unauthenticated --no-install-recommends \
                    build-essential \
                    ca-certificates \
                    doxygen \
                    g++ \
                    git \
                    gnuplot \
                    lcov \
                    libboost-dev \
                    libgeos-dev \
                    libgtest-dev \
                    libtbb-dev \
                    libeigen3-dev \
                    libpython3-dev \
                    python3 \
                    python3-pip \
                    python3-matplotlib \
                    python3-pytest \
                    python3-tk \
                    ranger \
                    vim \
                    libtinyxml2-dev \
                    nlohmann-json3-dev
#                    && \
#                    apt-get autoclean && \
#                    apt-get autoremove && \
#                    apt-get clean && \
#                    rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install gcovr setuptools
RUN python3 -c "import matplotlib" && \
    echo "backend: Agg" > ~/.config/matplotlib/matplotlibrc

RUN apt-get install -y libgtest-dev \
    && cd /usr/src/gtest \
    && cmake CMakeLists.txt \
    && make \
    && (cp *.a /usr/lib/ 2>\dev\null || :) \
    && (cp lib/*.a /usr/lib/ 2>\dev\null || :)

RUN if gdalinfo --version | grep -o " 3\.[0-2]\."; then \
      apt-get install -y --no-install-recommends  --allow-unauthenticated autoconf automake autotools-dev libpcre2-dev bison \
      && git clone https://github.com/swig/swig.git \
      && cd swig \
      && ./autogen.sh \
      && ./configure \
      && make -j8 \
      && make install; \
    else \
      apt-get install -y --no-install-recommends  --allow-unauthenticated swig; \
    fi

RUN wget https://github.com/google/or-tools/releases/download/v9.9/or-tools_amd64_ubuntu-22.04_cpp_v9.9.3963.tar.gz -q -O /tmp/ortools.tar.gz \
    && mkdir -p /tmp/ortools \
    && tar -zxf /tmp/ortools.tar.gz -C /tmp/ortools --strip-components=1 \
    && cp -r /tmp/ortools/bin/. /usr/bin \
    && cp -r /tmp/ortools/include/. /usr/include \
    && cp -r /tmp/ortools/lib/. /usr/lib \
    && cp -r /tmp/ortools/lib/cmake/. /usr/share \
    && cp -r /tmp/ortools/share/. /usr/share/ortools

WORKDIR /workspaces/Fields2Cover


### NEW ###

# Copy Fields2Cover
COPY . /workspaces/Fields2Cover

# Compile Fields2Cover
WORKDIR /workspaces/Fields2Cover/build
# RUN cmake ..
# RUN make -j$(nproc)
# RUN make install

# Compile for Python
RUN cmake -DBUILD_PYTHON=ON ..
RUN make -j$(nproc)
RUN make install

SHELL ["/bin/bash", "-c"]

# Set default user env vars
ARG USERNAME=user
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Install Dependencies
RUN apt update \
    && apt --no-install-recommends install -y \
    sudo \
    bash-completion

# Update PATH
ENV PATH="/root/.local/bin:/home/$USERNAME/.local/bin:${PATH}"

# Create the user
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    # [Optional] Add sudo support. Omit if you don't need to install software after connecting.
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# [Optional] Set the default user. Omit if you want to keep the default as root.
USER $USERNAME

# TODO: Install ROS 2 Humble (for Ubuntu 22.04)
ARG ROS_DISTRO=humble
# Add ROS 2 GPG key with apt
RUN sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
# Add repo to sources list
RUN echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
# Update apt repo caches and install ROS 2 (Desktop for development)
RUN sudo apt update \
    && sudo apt install -y ros-${ROS_DISTRO}-desktop
# Install colcon
RUN sudo apt --no-install-recommends install -y \
    python3-colcon-common-extensions

# Set up environment
RUN source /opt/ros/${ROS_DISTRO}/setup.bash
RUN echo "source /opt/ros/${ROS_DISTRO}/setup.bash" >> ~/.bashrc

RUN echo "source /usr/share/colcon_cd/function/colcon_cd.sh" >> ~/.bashrc
RUN echo "export _colcon_cd_root=/opt/ros/${ROS_DISTRO}" >> ~/.bashrc
RUN echo "source /etc/bash_completion" >> ~/.bashrc

# TODO: Set up ROS 2 workspace inside image. 
WORKDIR /home/$USERNAME/ros2_ws

# Default command: start bash
CMD ["bash"]


# TODO: Create ROS 2 pkg on host, to mount into container
# TODO: Create ROS 2 service server that imports fields2cover as f2c. Test i/o of f2c.
