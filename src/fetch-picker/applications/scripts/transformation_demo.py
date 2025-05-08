#!/usr/bin/env python

import math
import numpy as np
from geometry_msgs.msg import Point, Pose, PoseStamped
from std_msgs.msg import ColorRGBA
import visualization_msgs.msg
import rospy
import tf.transformations as tft

def wait_for_time():
    while rospy.Time().now().to_sec() == 0:
        pass

def cosd(degs):
    return math.cos(degs * math.pi / 180)

def sind(degs):
    return math.sin(degs * math.pi / 180)

# 可视化坐标系
def axis_marker(pose_stamped):
    marker = visualization_msgs.msg.Marker()
    marker.ns = 'axes'
    marker.header = pose_stamped.header
    marker.pose = pose_stamped.pose
    marker.type = marker.LINE_LIST
    marker.scale.x = 0.1

    # X 红色
    marker.points += [Point(0, 0, 0), Point(1, 0, 0)]
    marker.colors += [ColorRGBA(1, 0, 0, 1)] * 2
    # Y 绿色
    marker.points += [Point(0, 0, 0), Point(0, 1, 0)]
    marker.colors += [ColorRGBA(0, 1, 0, 1)] * 2
    # Z 蓝色
    marker.points += [Point(0, 0, 0), Point(0, 0, 1)]
    marker.colors += [ColorRGBA(0, 0, 1, 1)] * 2

    return marker

# 从矩阵转换为 Pose 类型
def transform_to_pose(matrix):
    pose = Pose()
    # TODO:fill this out
    translation = tft.translation_from_matrix(matrix)
    quaternion = tft.quaternion_from_matrix(matrix)
    pose.position.x, pose.position.y, pose.position.z = translation
    pose.orientation.x, pose.orientation.y, pose.orientation.z, pose.orientation.w = quaternion
    return pose

# 可视化一个箭头（方向）
def arrow_marker(point):
    marker = visualization_msgs.msg.Marker()
    marker.ns = 'arrow'
    marker.type = marker.ARROW
    marker.header.frame_id = 'frame_a'
    marker.points = [Point(0, 0, 0), point]
    marker.scale.x = 0.1
    marker.scale.y = 0.15
    marker.color.r = 1
    marker.color.g = 1
    marker.color.a = 1
    return marker

def main():
    rospy.init_node('transformation_demo')
    wait_for_time()

    viz_pub = rospy.Publisher('visualization_marker', visualization_msgs.msg.Marker, queue_size=1)
    rospy.sleep(0.5)

    # 定义变换矩阵：frame B 相对于 frame A
    b_in_a = np.array([
        [cosd(45), -sind(45), 0, 0],
        [sind(45),  cosd(45), 0, 0],
        [0,         0,        1, 0.5],
        [0,         0,        0, 1]
    ])

    # 可视化 frame B 的坐标轴
    ps = PoseStamped()
    ps.header.frame_id = 'frame_a'
    ps.pose = transform_to_pose(b_in_a)
    viz_pub.publish(axis_marker(ps))

    rospy.sleep(0.5)

    # 变换一个点：B 中的 (1, 0, 0)，变换为 A 中的坐标
    point_in_b = np.array([1, 0, 0, 1])  # 同质坐标
    point_in_a = np.dot(b_in_a, point_in_b)
    rospy.loginfo("point in B: {}".format(point_in_b))
    rospy.loginfo("point in A: {}".format(point_in_a))

    point = Point(point_in_a[0], point_in_a[1], point_in_a[2])
    viz_pub.publish(arrow_marker(point))

if __name__ == '__main__':
    main()
