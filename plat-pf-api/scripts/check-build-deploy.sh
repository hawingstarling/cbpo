#!/bin/bash
if [[ ${DEPLOYMENT_TYPE} == "production" ]]
then
  GCLOUD_IMAGE_REPO=${REGISTRY}/${PROJECT_PRODUCTION_ID}/${PROJECT_PRODUCTION_APP}
  IMAGE=${GCLOUD_IMAGE_REPO}:${VERSION}
  VERSION_EXISTED=$(gcloud container images list-tags ${GCLOUD_IMAGE_REPO} | grep ${VERSION} | wc -l)
  if [[ ${VERSION_EXISTED} == 0 ]]
  then
    gcloud builds submit --tag ${IMAGE} .
  else
    echo "${IMAGE} EXISTED"
  fi
else
  GCLOUD_IMAGE_REPO=${REGISTRY}/${PROJECT_ID}/${PROJECT_NAME}
  IMAGE=${GCLOUD_IMAGE_REPO}:${VERSION}
  VERSION_EXISTED=$(gcloud container images list-tags ${GCLOUD_IMAGE_REPO} | grep ${VERSION} | wc -l)
  if [[ ${VERSION_EXISTED} == 0 ]]
  then
    docker build -t ${IMAGE} .
    VERSION_EXISTED=$(gcloud container images list-tags ${GCLOUD_IMAGE_REPO} | grep ${VERSION} | wc -l)
    if [[ ${VERSION_EXISTED} == 0 ]]
    then
      docker push ${IMAGE};
    else
      echo "${IMAGE} EXISTED"
    fi
    docker rmi -f $(docker images ${GCLOUD_IMAGE_REPO} -q)
  else
    echo "${IMAGE} EXISTED"
  fi
fi
