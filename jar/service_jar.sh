#!/bin/bash

rm -f /tmp/notify-service
rm -f /tmp/failed-service

cd /d/PROJECTS/exsited-core || exit

# Clean up old JARs
rm -f services/build/libs/services-0.1-plain.jar
rm -f in_app_libs/services-0.1-plain.jar

# Enable 'services' module
sed -i 's#//include "services"#include "services"#g' settings.gradle

# Timestamped log file
timestamp=$(date +"%Y-%m-%d_%H-%M-%S")
logfile="/tmp/servicebuild_${timestamp}.out"

# Build
bash ./gradlew :services:jar > "$logfile" 2>&1

# Check result
if [ $? -eq 0 ]; then
  cp services/build/libs/services-0.1-plain.jar in_app_libs/
  rm -f /d/PROJECTS/exsited-integration/in_app_libs/services-0.1-plain.jar
  cp services/build/libs/services-0.1-plain.jar /d/PROJECTS/exsited-integration/in_app_libs/
  touch /tmp/notify-service
  echo "✅ Build successful! services-0.1-plain.jar copied successfully."
  echo "🪵 Log file: $logfile"
else
  touch /tmp/failed-service
  echo "❌ Build failed. Check log for details:"
  echo "🪵 $logfile"
fi

# Revert 'services' include
sed -i 's#include "services"#//include "services"#g' settings.gradle
