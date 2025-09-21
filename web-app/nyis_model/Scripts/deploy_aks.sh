kubectl set image deployment/$DEPLOYMENT_NAME $DEPLOYMENT_NAME=$FULL_IMAGE -n $NAMESPACE
kubectl rollout status deployment/$DEPLOYMENT_NAME -n $NAMESPACE