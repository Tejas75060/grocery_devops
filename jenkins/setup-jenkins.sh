#!/usr/bin/env bash
# Run a self-configuring Jenkins controller for the Grocery CI/CD demo.
# - JCasC pre-creates the 'grocery-ci' pipeline job (no setup wizard)
# - installs python3/docker-cli/git inside the controller so the pipeline runs
# - provides a local registry on :5051 as the push target
set -euo pipefail
cd "$(dirname "$0")/.."

JENKINS_HOME_VOL=grocery_jenkins_home

echo "==> Local registry on :5051 (push target)"
docker rm -f grocery-registry-ci >/dev/null 2>&1 || true
docker run -d --name grocery-registry-ci -p 5051:5000 registry:2 >/dev/null

echo "==> Starting Jenkins (JCasC, plugins auto-installed)"
docker rm -f jenkins >/dev/null 2>&1 || true
docker run -d --name jenkins \
  -p 8080:8080 -p 50000:50000 \
  -v "$JENKINS_HOME_VOL":/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v "$(pwd)/jenkins/casc.yaml":/var/jenkins_home/casc.yaml:ro \
  -e CASC_JENKINS_CONFIG=/var/jenkins_home/casc.yaml \
  -e JAVA_OPTS="-Djenkins.install.runSetupWizard=false" \
  jenkins/jenkins:lts-jdk17 >/dev/null

echo "==> Installing plugins (JCasC, job-dsl, pipeline, git, docker, junit)"
sleep 5
docker exec jenkins jenkins-plugin-cli --plugins \
  configuration-as-code job-dsl workflow-aggregator git docker-workflow junit timestamper >/tmp/jplug.log 2>&1 || true

echo "==> Installing build tools inside the controller (python3, docker-cli, git)"
docker exec -u root jenkins bash -c '
  set -e
  apt-get update -qq
  apt-get install -y -qq python3 python3-venv python3-pip git curl >/dev/null
  if ! command -v docker >/dev/null; then
    ARCH=$(uname -m)   # aarch64 on Apple Silicon, x86_64 on Intel
    curl -fsSL "https://download.docker.com/linux/static/stable/${ARCH}/docker-27.1.1.tgz" -o /tmp/d.tgz
    tar xzf /tmp/d.tgz -C /tmp
    cp /tmp/docker/docker /usr/local/bin/docker
  fi
  chmod 666 /var/run/docker.sock || true
' >/tmp/jtools.log 2>&1 || true

echo "==> Restarting Jenkins to apply plugins + JCasC"
docker restart jenkins >/dev/null
echo "Waiting for Jenkins to come up..."
until curl -fsS http://localhost:8080/login >/dev/null 2>&1; do sleep 3; done
echo "Jenkins is up at http://localhost:8080  (admin/admin)"
echo "Job 'grocery-ci' is pre-created. Trigger it from the UI or:"
echo "  curl -s -XPOST http://admin:admin@localhost:8080/job/grocery-ci/build"
