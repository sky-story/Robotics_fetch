#!/usr/bin/env python

import rospy
from nav_msgs.msg import Odometry
from visualization_msgs.msg import Marker
from geometry_msgs.msg import Point
from std_msgs.msg import ColorRGBA

class PathVisualizer:
    def __init__(self):
        self._points = []
        self._last_position = None
        self._marker_pub = rospy.Publisher('/visualization_marker', Marker, queue_size=10)
        rospy.Subscriber('/odom', Odometry, self.odom_callback)

    def odom_callback(self, msg):
        pos = msg.pose.pose.position
        new_point = Point(pos.x, pos.y, pos.z)
        
        if self._last_position is None or self.distance(new_point, self._last_position) > 0.1:
            self._points.append(new_point)
            self._last_position = new_point
            self.publish_marker()

    def distance(self, p1, p2):
        return ((p1.x - p2.x)**2 + (p1.y - p2.y)**2 + (p1.z - p2.z)**2)**0.5

    def publish_marker(self):
        marker = Marker()
        marker.header.frame_id = "odom"
        marker.type = Marker.LINE_STRIP
        marker.action = Marker.ADD
        marker.pose.orientation.w = 1.0
        marker.scale.x = 0.02
        marker.color = ColorRGBA(1.0, 0.0, 0.0, 1.0)
        marker.points = self._points
        marker.id = 1
        marker.lifetime = rospy.Duration()  # 永久显示
        self._marker_pub.publish(marker)

def wait_for_time():
    while rospy.Time().now().to_sec() == 0:
        pass

def main():
    rospy.init_node('path_marker')
    wait_for_time()
    PathVisualizer()
    rospy.spin()

if __name__ == '__main__':
    main()
