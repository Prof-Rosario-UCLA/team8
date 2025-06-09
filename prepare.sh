#!/bin/bash

set -e

# Load environment variables from .env in development
if [[ ! -f ".env" ]]; then
    echo "Missing texify/gcs-access-key.json";
    exit 1;
fi

export $(cat .env | xargs);

# TODO(bliutech): refactor some of the logic to make the updates only apply for
# one service so that we do not need gcs-access-key.json for every CD workflow.
# Make sure that GCS access key is generated
if [[ ! -f "texify/gcs-access-key.json" ]]; then
    echo "Missing texify/gcs-access-key.json";
    exit 1;
fi

# Generate app.yaml files from templates
SERVICES=("api" "texify" "web");
for SERVICE in "${SERVICES[@]}"; do
    envsubst < "$SERVICE/app.template.yaml" > "$SERVICE/app.yaml";

    # Find and replace $SERVER_URL for web in cloudbuild.yaml
    sed "s|\$SERVER_URL|${SERVER_URL}|g" "$SERVICE/cloudbuild.template.yaml" > "$SERVICE/cloudbuild.yaml";
done

# Make sure no app.yaml files are missing
for SERVICE in "${SERVICES[@]}"; do
    if [[ ! -f "$SERVICE/app.yaml" ]]; then
        echo "Missing $SERVICE/app.yaml";
        exit 1 
    fi

    if [[ ! -f "$SERVICE/cloudbuild.yaml" ]]; then
        echo "Missing $SERVICE/cloudbuild.yaml";
        exit 1 
    fi
done

echo "Deployment configuration files generated!"
