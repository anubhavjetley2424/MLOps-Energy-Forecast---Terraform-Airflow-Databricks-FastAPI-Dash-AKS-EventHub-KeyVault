#!/bin/bash
set -e

IMAGE_NAME=$1
TAG=${2:-latest}

echo "Building Docker image $IMAGE_NAME:$TAG..."
docker build -t $IMAGE_NAME:$TAG .
docker images | grep $IMAGE_NAME
