#!/bin/bash

# 设置路径
WS_PATH="/fetch_ws"
PKG_PATH="$WS_PATH/src/fetch-picker"
ROBOT_API_PATH="$PKG_PATH/robot_api"
LOCAL_PATH=~/local

# Step 1: 下载 IKFast 插件
mkdir -p $LOCAL_PATH
cd $LOCAL_PATH
if [ ! -d "$LOCAL_PATH/fetch_ros" ]; then
    git clone https://github.com/fetchrobotics/fetch_ros.git
fi

# Step 2: 复制 IKFast 插件到工作空间
cp -r fetch_ros/fetch_ikfast_plugin $PKG_PATH/

# Step 3: 构建插件
cd $WS_PATH
source /opt/ros/noetic/setup.bash
catkin build fetch_ikfast_plugin

# Step 4: 创建 config 和 launch 文件夹
mkdir -p $ROBOT_API_PATH/launch
mkdir -p $ROBOT_API_PATH/config

# Step 5: 拷贝配置文件
roscp fetch_moveit_config move_group.launch $ROBOT_API_PATH/launch/
roscp fetch_moveit_config planning_context.launch $ROBOT_API_PATH/launch/
roscp fetch_moveit_config kinematics.yaml $ROBOT_API_PATH/config/

# Step 6: 修改 kinematics.yaml（写入 IKFast 配置）
KIN_FILE=$ROBOT_API_PATH/config/kinematics.yaml
cat <<EOT > $KIN_FILE
arm:
  kinematics_solver: fetch_arm/IKFastKinematicsPlugin
  kinematics_solver_search_resolution: 0.005
  kinematics_solver_timeout: 0.005
  kinematics_solver_attempts: 3

arm_with_torso:
  kinematics_solver: kdl_kinematics_plugin/KDLKinematicsPlugin
  kinematics_solver_search_resolution: 0.005
  kinematics_solver_timeout: 0.005
  kinematics_solver_attempts: 3
EOT

# Step 7: 替换 launch 文件中的 include 路径
sed -i 's#<include file="$(find fetch_moveit_config)/launch/planning_context.launch" />#<include file="$(find robot_api)/launch/planning_context.launch" />#' \
  $ROBOT_API_PATH/launch/move_group.launch

sed -i 's#<rosparam command="load" file="$(find fetch_moveit_config)/config/kinematics.yaml"/>#<rosparam command="load" file="$(find robot_api)/config/kinematics.yaml"/>#' \
  $ROBOT_API_PATH/launch/planning_context.launch

echo "✅ Lab 25 IKFast 插件配置完成！"
echo "👉 你现在可以运行："
echo "    source ~/.bashrc"
echo "    roslaunch robot_api move_group.launch"
