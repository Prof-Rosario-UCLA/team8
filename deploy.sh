#!/bin/bash

set -e

if [[ $BUILD_MODE != "CD" ]]; then
    # Load environment variables from .env in development
    export $(cat .env | xargs);
else
    # Environment variables should already be loaded in GitHub Actions
    # TODO(bliutech): generate gcs-access-key.json
    echo "TODO"
fi

if [[ ! -f "texify/gcs-access-key.json" ]]; then
    echo "Missing texify/gcs-access-key.json";
    exit 1;
fi

# Generate app.yaml files from templates
SERVICES=("api" "texify" "web");
for SERVICE in "${SERVICES[@]}"; do
    envsubst < "$SERVICE/app.template.yaml" > "$SERVICE/app.yaml";
done

# Run Cloud Build
gcloud builds submit --config=cloudbuild.yaml .;

# Remove all app.yaml files
for SERVICE in "${SERVICES[@]}"; do
    rm "$SERVICE/app.yaml";
done
