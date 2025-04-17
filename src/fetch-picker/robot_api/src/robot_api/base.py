#!/usr/bin/env python3

import rospy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from tf.transformations import euler_from_quaternion
import copy
import math

class Base(object):
    """Base controls the mobile base portion of the Fetch robot."""

    def __init__(self):
        self._pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
        self._odom_sub = rospy.Subscriber('/odom', Odometry, self._odom_callback)
        self._latest_odom = None
        rospy.sleep(1.0)  # 等待连接建立

    def move(self, linear_speed, angular_speed):
        msg = Twist()
        msg.linear.x = linear_speed
        msg.angular.z = angular_speed
        self._pub.publish(msg)

    def stop(self):
        self.move(0.0, 0.0)

    def _odom_callback(self, msg):
        self._latest_odom = msg

    def _get_current_position(self):
        return self._latest_odom.pose.pose.position

    def _get_current_yaw(self):
        ori = self._latest_odom.pose.pose.orientation
        _, _, yaw = euler_from_quaternion([ori.x, ori.y, ori.z, ori.w])
        return yaw

    def go_forward(self, distance, speed=0.1):
        while self._latest_odom is None:
            rospy.sleep(0.1)

        rospy.loginfo(f"[go_forward] Start moving {distance:.2f} meters...")

        start = copy.deepcopy(self._get_current_position())
        rate = rospy.Rate(10)
        direction = -1 if distance < 0 else 1
        distance = abs(distance)

        def dist_moved(current, start):
            dx = current.x - start.x
            dy = current.y - start.y
            return math.sqrt(dx*dx + dy*dy)

        start_time = rospy.Time.now()

        while not rospy.is_shutdown():
            current_pos = self._get_current_position()
            moved = dist_moved(current_pos, start)
            remaining = distance - moved

            rospy.loginfo(f"[go_forward] Moved: {moved:.3f} / {distance:.3f}, Remaining: {remaining:.3f}")
            rospy.loginfo(f"[go_forward] Current position: x={current_pos.x:.3f}, y={current_pos.y:.3f}")

            if remaining <= 0.01:
                break

            linear_speed = max(0.05, min(0.5, remaining))
            self.move(direction * linear_speed, 0)
            rate.sleep()

            if rospy.Time.now() - start_time > rospy.Duration(15.0):
                rospy.logwarn("[go_forward] Timeout! Breaking loop.")
                break

        self.stop()
        rospy.loginfo("[go_forward] Stopped.")

    def turn(self, angular_distance, speed=0.5):
        while self._latest_odom is None:
            rospy.sleep(0.1)

        rospy.loginfo(f"[turn] Start turning {math.degrees(angular_distance):.2f} degrees...")

        def normalize_angle(angle):
            return math.atan2(math.sin(angle), math.cos(angle))

        start_yaw = self._get_current_yaw()
        target_yaw = normalize_angle(start_yaw + angular_distance)

        rate = rospy.Rate(10)
        start_time = rospy.Time.now()

        while not rospy.is_shutdown():
            current_yaw = self._get_current_yaw()
            error = normalize_angle(target_yaw - current_yaw)
            remaining = abs(error)

            rospy.loginfo(f"[turn] Current yaw: {math.degrees(current_yaw):.2f}°, Target: {math.degrees(target_yaw):.2f}°, Remaining: {math.degrees(remaining):.2f}°")

            if remaining < 0.01:
                break

            direction = 1 if error > 0 else -1
            angular_speed = max(0.5, min(1.5, remaining))
            self.move(0, direction * angular_speed)
            rate.sleep()

            if rospy.Time.now() - start_time > rospy.Duration(15.0):
                rospy.logwarn("[turn] Timeout! Breaking loop.")
                break

        self.stop()
        rospy.loginfo("[turn] Stopped.")
