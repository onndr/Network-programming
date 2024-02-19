#!/bin/bash
# ./docker.sh [ create | run | car | rm ] [ c | py ]

if [[ $# -lt 2 ]]; then
  echo "usage: ./docker.sh [ create | run | car ] [ c | py ]"
  exit 1
fi

cmd=$1
image_name="z34_$2_test"
version=$2


if [[ "$cmd" =~ ^(create|run|car|rm)$ ]]; then
  echo "$cmd $version"
else
  echo "Unknown command: $cmd"
  exit 1
fi

if [ "$version" == "c" ]; then
  cd c || exit
else
  cd python || exit
fi

if [[ "$cmd" != "run" ]]; then
  docker image rm "$image_name"
  docker build . -t "$image_name" || exit
fi
if [[ "$cmd" != "create" ]]; then
  docker run --network z34_network -it "$image_name" ash
fi

