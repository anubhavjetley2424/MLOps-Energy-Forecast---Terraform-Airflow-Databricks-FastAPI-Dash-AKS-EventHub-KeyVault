#!/bin/bash
set -e

ACR_NAME=$1
IMAGE_NAME=$2
TAG=${3:-latest}

echo "Logging into Azure Container Registry $ACR_NAME..."
az acr login --name $ACR_NAME

FULL_IMAGE_NAME="$ACR_NAME.azurecr.io/$IMAGE_NAME:$TAG"
docker tag $IMAGE_NAME:$TAG $FULL_IMAGE_NAME
docker push $FULL_IMAGE_NAME
