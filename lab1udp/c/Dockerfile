FROM alpine

COPY . /cversion
WORKDIR /cversion/
RUN apk update; \
    apk add cmake; \
    apk add g++; \
    apk add make; \
    mkdir build; \
    cd build; \
    cmake ..; \
    cmake --build .
WORKDIR /cversion/build