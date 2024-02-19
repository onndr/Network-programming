cmake_minimum_required(VERSION 3.26)
project(c_server C)

set(CMAKE_C_STANDARD 11)

add_executable(c_client c_client.c)
add_executable(c_server c_server.c)
