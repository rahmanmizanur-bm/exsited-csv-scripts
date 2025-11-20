#!/bin/bash

rm -f /tmp/notify-service-faster
rm -f /tmp/failed-service-faster

cd /d/PROJECTS/exsited-core || exit

# Remove old jar
rm -f services_faster/build/libs/services_faster-0.1-plain.jar

# Enable the 'services_faster' module
sed -i 's#//include "services_faster"#include "services_faster"#g' settings.gradle

# Clean existing source directories
rm -rf services_faster/grails-app/services
rm -rf services_faster/grails-app/taglib
rm -rf services_faster/grails-app/controllers
rm -rf services_faster/src

# Copy from main project
cp -r grails-app/services services_faster/grails-app/
cp -r grails-app/taglib services_faster/grails-app/
cp -r grails-app/controllers services_faster/grails-app/
cp -r src services_faster/

# Remove unneeded directories
rm -rf services_faster/src/integration-test
rm -rf services_faster/src/main/resources
rm -rf services_faster/src/main/webapp

# Build log file with timestamp
timestamp=$(date +"%Y-%m-%d_%H-%M-%S")
logfile="/tmp/servicefasterbuild_${timestamp}.out"

# Run Gradle build
bash ./gradlew :services_faster:jar > "$logfile" 2>&1

# Check build result
if [ $? -eq 0 ]; then
  rm -f /d/PROJECTS/exsited-integration/in_app_libs/services_faster-0.1-plain.jar
  cp services_faster/build/libs/services_faster-0.1-plain.jar /d/PROJECTS/exsited-integration/in_app_libs/
  touch /tmp/notify-service-faster
  echo "✅ Build successful! services_faster-0.1-plain.jar copied successfully."
  echo "🪵 Log file: $logfile"
else
  touch /tmp/failed-service-faster
  echo "❌ Build failed. Check log for details:"
  echo "🪵 $logfile"
fi

# Clean up after build
rm -rf services_faster/grails-app/services
rm -rf services_faster/grails-app/taglib
rm -rf services_faster/grails-app/controllers
rm -rf services_faster/src

# Disable the 'services_faster' module again
sed -i 's#include "services_faster"#//include "services_faster"#g' settings.gradle
