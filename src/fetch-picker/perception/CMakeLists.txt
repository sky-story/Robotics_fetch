cmake_minimum_required(VERSION 3.0.2)
project(perception)

find_package(catkin REQUIRED COMPONENTS
  roscpp
  rospy
  sensor_msgs
  pcl_ros
  tf
  rosbag
)

catkin_package(
  INCLUDE_DIRS include
  LIBRARIES perception_crop
)

catkin_python_setup()

include_directories(
  include
  ${catkin_INCLUDE_DIRS}
)

# ----------------------------
# Executable: save_cloud
# ----------------------------
add_executable(perception_save_cloud_main src/save_cloud_main.cpp)
set_target_properties(perception_save_cloud_main PROPERTIES OUTPUT_NAME save_cloud PREFIX "")
add_dependencies(perception_save_cloud_main ${${PROJECT_NAME}_EXPORTED_TARGETS} ${catkin_EXPORTED_TARGETS})
target_link_libraries(perception_save_cloud_main
  ${catkin_LIBRARIES}
)

# ----------------------------
# Executable: point_cloud_demo
# ----------------------------
add_executable(perception_point_cloud_demo src/point_cloud_demo.cpp)
set_target_properties(perception_point_cloud_demo PROPERTIES OUTPUT_NAME point_cloud_demo PREFIX "")
add_dependencies(perception_point_cloud_demo ${${PROJECT_NAME}_EXPORTED_TARGETS} ${catkin_EXPORTED_TARGETS})
# 链接 crop 库
target_link_libraries(perception_point_cloud_demo
  perception_crop
  ${catkin_LIBRARIES}
)

# ----------------------------
# Library: perception_crop
# ----------------------------
add_library(perception_crop src/crop.cpp)
add_dependencies(perception_crop ${${PROJECT_NAME}_EXPORTED_TARGETS} ${catkin_EXPORTED_TARGETS})
target_link_libraries(perception_crop ${catkin_LIBRARIES})

# 下采样库
add_library(perception_downsample src/downsample.cpp)
add_dependencies(perception_downsample ${${PROJECT_NAME}_EXPORTED_TARGETS} ${catkin_EXPORTED_TARGETS})
target_link_libraries(perception_downsample ${catkin_LIBRARIES})

# 链接下采样库到 demo 可执行文件
target_link_libraries(perception_point_cloud_demo
  perception_crop
  perception_downsample
  ${catkin_LIBRARIES}
)

# 导出下采样库
catkin_package(
  INCLUDE_DIRS include
  LIBRARIES perception_crop perception_downsample
)

