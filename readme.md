# Earthquake Notification App on Linux

Data source: https://earthquake.usgs.gov

### How to use
```Bash
DOCKER_BUILDKIT=1 docker build --progress=plain .
nohup ./equake.sh > /dev/null &
```
