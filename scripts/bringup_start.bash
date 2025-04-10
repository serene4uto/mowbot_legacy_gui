export DISPLAY=:0
xhost +local:docker
docker start mowbot_humble
#docker exec -it -e DISPLAY=:0.0 -w /workspaces/mowbot/mowbot_ws mowbot_humble /bin/bash -c "\
docker exec -e DISPLAY=:0.0 -w /workspaces/mowbot/mowbot_ws mowbot_humble /bin/bash -c "\
        cd /workspaces/mowbot/mowbot_ws \
        && . ./install/setup.bash \
        && ros2 launch mowbot_bringup bringup.launch.py imu:=true madgwick:=true ntrip:=true \
                                                        gpsl:=true gpsr:=true dgps_compass:=true laser:=true \
                                                        sensormon:=true \
                                                        foxglove:=true \
    "
#foxglove:=true