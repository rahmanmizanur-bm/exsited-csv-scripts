# JAR build scripts (jar folder)

This folder contains helper shell scripts used to build and copy project JAR files with Gradle. Current scripts include:

- `domain_jar.sh`
- `service_jar.sh`
- `service_faster_jar.sh`

Location: `c:\Users\Rahman\Desktop\Scripts\jar`

## Purpose

These scripts automate:
- changing to the project directory
- temporarily including modules in `settings.gradle` if needed
- running the Gradle jar task
- copying produced JARs to `in_app_libs`
- leaving short status artifacts in `/tmp` (e.g., `/tmp/notify-domain`, `/tmp/failed-domain`) and writing build logs to `/tmp/*.out`.

## Prerequisites

- Git Bash on Windows (you said you run the scripts in Git Bash).
- Java JDK installed and available in PATH.
- Gradle wrapper present in the project root (e.g., `./gradlew`).
- Sufficient file permissions to run scripts and write to `/tmp`.

## Important: set your project path first

Each script starts by changing directory to the project's root. Update the `cd` line to match your environment before running. The current example in `domain_jar.sh` is:

```bash
# Go to project directory
cd /d/PROJECTS/exsited-core || exit
```

Edit that line to point to your copy of the project. Example using a variable (recommended):

```bash
PROJECT_DIR="/d/PROJECTS/exsited-core"
cd "$PROJECT_DIR" || exit
```

If your projects are in another location, update the `PROJECT_DIR` accordingly. Some scripts also copy artifacts to the integration project path (e.g., `/d/PROJECTS/exsited-integration/in_app_libs/`); update those paths if needed.

## Make the scripts executable (once)

From Git Bash:

```bash
cd /c/Users/Rahman/Desktop/Scripts/jar
chmod +x *.sh
```

## How to run (simple)

Open Git Bash, go to this folder and run the script you need. Example (the exact command you said you use):

```bash
./service_jar.sh
```

That's it — the script will:
- change to the project directory you configured,
- run the Gradle build (`./gradlew :service:jar` or similar),
- copy built JARs to `in_app_libs`,
- write a build log to `/tmp/<scriptname>build.out`, and
- touch `/tmp/notify-<name>` on success or `/tmp/failed-<name>` on failure.

## Example: `domain_jar.sh` behavior

- Temporarily uncomments `include "domains"` in `settings.gradle` using `sed`.
- Runs `bash ./gradlew :domains:jar` and writes output to `/tmp/domainbuild.out`.
- On success copies `domains/build/libs/domains-0.1-plain.jar` into `in_app_libs/` and to the integration project's `in_app_libs/`.
- Reverts `settings.gradle` to its original state using `sed` at the end.

## Troubleshooting

- If the script exits quickly or with `exit`, inspect the top `cd` path — it may be wrong.
- Check the build log in `/tmp/*.out` (for example `/tmp/domainbuild.out`) for Gradle errors.
- If `sed` is not behaving as expected on Windows, ensure you run the scripts in Git Bash (the `sed -i` behavior differs between GNU sed and BSD sed).
- If you see permission errors when copying files, check the destination directory permissions.
- If the scripts don't revert `settings.gradle`, open the file and verify whether the `include` line was restored; if not, restore manually.

## Suggested improvements (optional)

- Centralize the project path near the top of each script (use `PROJECT_DIR` variable) to avoid editing multiple places.
- Add a `--dry-run` flag to print actions without executing them.
- Add a small wrapper to verify prerequisites (Java, `./gradlew` present) before starting.

---

If you want, I can: 
- update the scripts to use a `PROJECT_DIR` variable and a single place to change the path, and
- add a small `check-prereqs.sh` that verifies Java and `./gradlew` are available.

Tell me which of those you'd like and I can implement them next.