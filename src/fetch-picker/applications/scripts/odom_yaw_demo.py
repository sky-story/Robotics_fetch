#!/usr/bin/env python

import rospy
from nav_msgs.msg import Odometry
from tf.transformations import quaternion_matrix
import math

def quaternion_to_yaw(q):
    mat = quaternion_matrix([q.x, q.y, q.z, q.w])
    x = mat[0, 0]
    y = mat[1, 0]
    theta = math.atan2(y, x)
    return theta  # 弧度制

def callback(msg):
    pos = msg.pose.pose.position
    ori = msg.pose.pose.orientation
    yaw = quaternion_to_yaw(ori)
    yaw_deg = yaw * 180.0 / math.pi

    rospy.loginfo("Position: x=%.2f, y=%.2f" % (pos.x, pos.y))
    rospy.loginfo("Yaw (degrees): %.2f" % yaw_deg)

def main():
    rospy.init_node('odom_yaw_demo')
    rospy.Subscriber('/odom', Odometry, callback)
    rospy.spin()

if __name__ == '__main__':
    main()
