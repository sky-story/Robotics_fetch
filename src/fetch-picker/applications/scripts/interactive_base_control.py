#!/usr/bin/env python3

import rospy
import math
from geometry_msgs.msg import Point
from visualization_msgs.msg import Marker, InteractiveMarker, InteractiveMarkerControl, InteractiveMarkerFeedback
from interactive_markers.interactive_marker_server import InteractiveMarkerServer
import robot_api

class BaseInteractiveControl:
    def __init__(self):
        rospy.loginfo("Initializing interactive marker controller...")
        self.base = robot_api.Base()
        self.server = InteractiveMarkerServer("base_control_marker")
        self._busy = False  # ✅ 防止重复触发

        # 创建四个控制按钮
        self._create_marker("forward", Point(1.0, 0.0, 0.1), "Go Forward", self._handle_forward, [0.0, 0.6, 0.8])
        self._create_marker("backward", Point(-1.0, 0.0, 0.1), "Go Backward", self._handle_backward, [0.7, 0.0, 0.7])
        self._create_marker("turn_left", Point(0.0, 1.0, 0.1), "Turn Left", self._handle_turn_left, [0.0, 0.9, 0.1])
        self._create_marker("turn_right", Point(0.0, -1.0, 0.1), "Turn Right", self._handle_turn_right, [0.9, 0.2, 0.0])

        self.server.applyChanges()
        rospy.loginfo("Interactive marker controller ready.")

    def _create_marker(self, name, position, description, callback, rgb_color):
        int_marker = InteractiveMarker()
        int_marker.header.frame_id = "base_link"
        int_marker.name = name
        int_marker.description = description
        int_marker.pose.position = position  # ✅ 控制按钮在 base_link 的相对位置
        int_marker.scale = 0.4

        box_marker = Marker()
        box_marker.type = Marker.CUBE
        box_marker.scale.x = 0.25  # ✅ 控制按钮的大小
        box_marker.scale.y = 0.25
        box_marker.scale.z = 0.25
        box_marker.color.r = rgb_color[0]
        box_marker.color.g = rgb_color[1]
        box_marker.color.b = rgb_color[2]
        box_marker.color.a = 1.0

        control = InteractiveMarkerControl()
        control.interaction_mode = InteractiveMarkerControl.BUTTON
        control.always_visible = True
        control.markers.append(box_marker)
        int_marker.controls.append(control)

        self.server.insert(int_marker, callback)

    def _handle_forward(self, feedback):
        if feedback.event_type != InteractiveMarkerFeedback.BUTTON_CLICK:
            return
        if self._busy:
            rospy.logwarn("Busy: Ignoring extra forward click.")
            return
        self._busy = True
        rospy.loginfo("Clicked: go forward")
        self.base.go_forward(0.5)
        self._busy = False

    def _handle_backward(self, feedback):
        if feedback.event_type != InteractiveMarkerFeedback.BUTTON_CLICK:
            return
        if self._busy:
            rospy.logwarn("Busy: Ignoring extra backward click.")
            return
        self._busy = True
        rospy.loginfo("Clicked: go backward")
        self.base.go_forward(-0.5)
        self._busy = False

    def _handle_turn_left(self, feedback):
        if feedback.event_type != InteractiveMarkerFeedback.BUTTON_CLICK:
            return
        if self._busy:
            rospy.logwarn("Busy: Ignoring extra turn left click.")
            return
        self._busy = True
        rospy.loginfo("Clicked: turn left")
        self.base.turn(math.radians(30))
        self._busy = False

    def _handle_turn_right(self, feedback):
        if feedback.event_type != InteractiveMarkerFeedback.BUTTON_CLICK:
            return
        if self._busy:
            rospy.logwarn("Busy: Ignoring extra turn right click.")
            return
        self._busy = True
        rospy.loginfo("Clicked: turn right")
        self.base.turn(math.radians(-30))
        self._busy = False

def main():
    rospy.init_node('interactive_base_control')
    BaseInteractiveControl()
    rospy.spin()

if __name__ == '__main__':
    main()
