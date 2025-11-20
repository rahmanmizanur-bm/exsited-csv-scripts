#!/bin/bash

rm -f /tmp/notify-domain
rm -f /tmp/failed-domain

# Go to project directory
cd /d/PROJECTS/exsited-core || exit

# Clean up old JARs
rm -f domains/build/libs/domains-0.1-plain.jar
rm -f in_app_libs/domains-0.1-plain.jar

# Temporarily include the 'domains' module
sed -i 's#//include "domains"#include "domains"#g' settings.gradle

# Build the JAR
bash ./gradlew :domains:jar > /tmp/domainbuild.out 2>&1

# Check build result
if [ $? -eq 0 ]; then
  cp domains/build/libs/domains-0.1-plain.jar in_app_libs/
  rm -f /d/PROJECTS/exsited-integration/in_app_libs/domains-0.1-plain.jar
  cp domains/build/libs/domains-0.1-plain.jar /d/PROJECTS/exsited-integration/in_app_libs/
  touch /tmp/notify-domain
  echo "✅ Build successful! domains-0.1-plain.jar has been copied."
else
  touch /tmp/failed-domain
  echo "❌ Build failed. Check /tmp/domainbuild.out for details."
fi

# Revert settings.gradle back
sed -i 's#include "domains"#//include "domains"#g' settings.gradle
