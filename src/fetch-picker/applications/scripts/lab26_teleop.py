#!/usr/bin/env python3

import rospy
import copy
import tf.transformations as tft
import numpy as np
from geometry_msgs.msg import PoseStamped, Quaternion, Point
from std_msgs.msg import ColorRGBA
from visualization_msgs.msg import InteractiveMarker, InteractiveMarkerControl, Marker
from interactive_markers.interactive_marker_server import InteractiveMarkerServer
from interactive_markers.menu_handler import MenuHandler

import robot_api  # 包含 Arm 和 Gripper 的封装类

# 网格资源路径
GRIPPER_MESH = 'package://fetch_description/meshes/gripper_link.dae'
L_FINGER_MESH = 'package://fetch_description/meshes/l_gripper_finger_link.STL'
R_FINGER_MESH = 'package://fetch_description/meshes/r_gripper_finger_link.STL'

def axis_to_quaternion(axis):
    if axis == 'x':
        q = tft.quaternion_about_axis(np.pi/2, (1, 0, 0))
    elif axis == 'y':
        q = tft.quaternion_about_axis(np.pi/2, (0, 1, 0))
    elif axis == 'z':
        q = tft.quaternion_about_axis(np.pi/2, (0, 0, 1))
    else:
        q = [0, 0, 0, 1]
    quat = Quaternion(*q)
    return quat

def make_6dof_controls():
    # 创建三个维度的移动和旋转控制
    controls = []
    for ax in ['x', 'y', 'z']:
        control_move = InteractiveMarkerControl()
        control_move.name = f"move_{ax}"
        control_move.interaction_mode = InteractiveMarkerControl.MOVE_AXIS
        control_move.orientation = axis_to_quaternion(ax)
        control_move.always_visible = True
        controls.append(copy.deepcopy(control_move))

        control_rotate = InteractiveMarkerControl()
        control_rotate.name = f"rotate_{ax}"
        control_rotate.interaction_mode = InteractiveMarkerControl.ROTATE_AXIS
        control_rotate.orientation = axis_to_quaternion(ax)
        control_rotate.always_visible = True
        controls.append(copy.deepcopy(control_rotate))
    return controls

def make_gripper_visualization():
    # 构造 gripper 和指头的 marker
    markers = []
    offset_x = 0.166

    def mesh_marker(resource, y_offset=0):
        m = Marker()
        m.type = Marker.MESH_RESOURCE
        m.mesh_resource = resource
        m.scale.x = m.scale.y = m.scale.z = 1.0
        m.color.r, m.color.g, m.color.b, m.color.a = 0.0, 1.0, 0.0, 1.0
        m.pose.position.x = offset_x
        m.pose.position.y = y_offset
        return m

    markers.append(mesh_marker(GRIPPER_MESH))
    markers.append(mesh_marker(L_FINGER_MESH, -0.06))
    markers.append(mesh_marker(R_FINGER_MESH, 0.06))
    return markers

class GripperTeleop:
    def __init__(self, arm, gripper, im_server):
        self._arm = arm
        self._gripper = gripper
        self._im_server = im_server
        self._menu_handler = MenuHandler()
        self._current_marker_name = 'gripper_marker'

    def start(self):
        rospy.loginfo("[Teleop] Starting gripper interactive marker...")
        gripper_marker = self.make_gripper_marker()
        self._im_server.insert(gripper_marker, feedback_cb=self.handle_feedback)

        # 初始化时检查颜色
        pose = PoseStamped()
        pose.header.frame_id = 'base_link'
        pose.pose = gripper_marker.pose
        reachable = self._arm.check_pose(pose)
        rospy.loginfo(f"[Teleop] Initial IK check -> reachable: {reachable}")
        self.update_color(reachable)

        # 添加菜单
        self._menu_handler.insert('Go to Pose', callback=self.handle_feedback)
        self._menu_handler.insert('Open Gripper', callback=self.handle_feedback)
        self._menu_handler.insert('Close Gripper', callback=self.handle_feedback)
        self._menu_handler.apply(self._im_server, self._current_marker_name)
        self._im_server.applyChanges()

    def make_gripper_marker(self):
        im = InteractiveMarker()
        im.header.frame_id = 'base_link'
        im.name = self._current_marker_name
        im.description = "Gripper Teleop"
        im.scale = 0.25

        im.pose.position.x = 0.5
        im.pose.position.y = 0
        im.pose.position.z = 0.5
        im.pose.orientation.w = 1

        control = InteractiveMarkerControl()
        control.always_visible = True
        control.interaction_mode = InteractiveMarkerControl.MENU
        control.markers.extend(make_gripper_visualization())
        im.controls.append(control)

        im.controls.extend(make_6dof_controls())
        return im

    def handle_feedback(self, feedback):
        rospy.loginfo(f"[Feedback] Event type: {feedback.event_type}")
        pose = PoseStamped()
        pose.header.frame_id = 'base_link'
        pose.pose = feedback.pose

        if feedback.event_type == feedback.MENU_SELECT:
            if feedback.menu_entry_id == 1:
                rospy.loginfo("[Menu] Go to pose requested.")
                self._arm.move_to_pose(pose)
            elif feedback.menu_entry_id == 2:
                rospy.loginfo("[Menu] Open gripper.")
                self._gripper.open()
            elif feedback.menu_entry_id == 3:
                rospy.loginfo("[Menu] Close gripper.")
                self._gripper.close()

        elif feedback.event_type == feedback.MOUSE_UP:
            rospy.loginfo("[Drag] Pose updated, checking IK...")
            reachable = self._arm.check_pose(pose)
            rospy.loginfo(f"[Drag] IK result: {reachable}")
            self.update_color(reachable)

    def update_color(self, reachable):
        rospy.loginfo("[Update] Updating marker color...")
        marker = self._im_server.get(self._current_marker_name)
        for m in marker.controls[0].markers:
            if reachable:
                m.color.r, m.color.g, m.color.b = 0.0, 1.0, 0.0
            else:
                m.color.r, m.color.g, m.color.b = 1.0, 0.0, 0.0
            m.color.a = 1.0
        self._im_server.insert(marker, feedback_cb=self.handle_feedback)
        rospy.sleep(0.01)  # 确保更新正常
        self._menu_handler.apply(self._im_server, self._current_marker_name)
        self._im_server.applyChanges()


class AutoPickTeleop(object):
    def __init__(self, arm, gripper, im_server):
        # 初始化：保存 arm、gripper、交互服务器
        self._arm = arm
        self._gripper = gripper
        self._im_server = im_server
        self._menu_handler = MenuHandler()
        self._current_marker_name = 'target_marker'

    def start(self):
        # 创建并注册交互式 Marker（表示目标物体）
        obj_marker = self.make_target_marker()
        self._im_server.insert(obj_marker, feedback_cb=self.handle_feedback)

        # 添加菜单项：Pick 和 Open
        self._menu_handler.insert('Pick Object', callback=self.handle_feedback)
        self._menu_handler.insert('Open Gripper', callback=self.handle_feedback)
        self._menu_handler.apply(self._im_server, self._current_marker_name)

        self._im_server.applyChanges()

    def make_target_marker(self):
        # 创建交互式 Marker，用于控制目标物体位置
        im = InteractiveMarker()
        im.header.frame_id = 'base_link'
        im.name = self._current_marker_name
        im.description = "Target Teleop"
        im.scale = 0.25
        im.pose.position.x = 0.7
        im.pose.position.z = 0.75
        im.pose.orientation.w = 1.0

        # 添加蓝色立方体表示物体本体
        control = InteractiveMarkerControl()
        control.always_visible = True

        box = Marker()
        box.type = Marker.CUBE
        box.scale.x = box.scale.y = box.scale.z = 0.05
        box.color.r = 0.0
        box.color.g = 0.0
        box.color.b = 1.0
        box.color.a = 1.0
        box.pose.position.x = 0.18  # 相对于中心稍微偏移

        control.markers.append(box)
        control.markers.extend(make_gripper_visualization())  # 加入 gripper 视觉标记
        im.controls.append(control)

        # 添加 6 自由度的拖动与旋转控件
        im.controls.extend(make_6dof_controls())

        return im

    def handle_feedback(self, feedback):
        if feedback.event_type == feedback.MENU_SELECT:
            # 点击菜单
            if feedback.menu_entry_id == 1:  # Pick Object
                rospy.loginfo("[AutoPick] Pick Object requested.")
                marker = self._im_server.get(self._current_marker_name)
                target_pose = marker.pose

                # 可添加 pre-grasp 偏移逻辑
                pre_grasp_pose = PoseStamped()
                pre_grasp_pose.header.frame_id = 'base_link'
                pre_grasp_pose.pose = copy.deepcopy(target_pose)
                # pre_grasp_pose.pose.position.x -= 0.1  # 向后偏移 10cm（可选）

                # 执行移动并关闭 gripper
                self._arm.move_to_pose(pre_grasp_pose)
                rospy.sleep(0.3)
                self._gripper.close()

            elif feedback.menu_entry_id == 2:  # Open Gripper
                rospy.loginfo("[AutoPick] Open Gripper requested.")
                self._gripper.open()

        elif feedback.event_type == feedback.MOUSE_UP:
            # 拖动后松开鼠标：检查新位置是否可达
            rospy.loginfo("[AutoPick] Marker moved, checking IK...")
            pose = PoseStamped()
            pose.header.frame_id = 'base_link'
            pose.pose = feedback.pose
            reachable = self._arm.check_pose(pose)
            rospy.loginfo(f"[AutoPick] Pose reachable: {reachable}")
            self.update_color(reachable)

    def update_color(self, reachable):
        # 根据 IK 结果更新 gripper 的颜色：绿色可达，红色不可达
        marker = self._im_server.get(self._current_marker_name)
        for m in marker.controls[0].markers:
            if m.type == Marker.CUBE:
                continue  # 不改变蓝色立方体颜色
            if reachable:
                m.color.r, m.color.g, m.color.b = 0.0, 1.0, 0.0  # 绿色
            else:
                m.color.r, m.color.g, m.color.b = 1.0, 0.0, 0.0  # 红色
            m.color.a = 1.0
        self._im_server.insert(marker, feedback_cb=self.handle_feedback)
        self._menu_handler.apply(self._im_server, self._current_marker_name)
        self._im_server.applyChanges()

def main():
    rospy.init_node('lab26_teleop')
    rospy.loginfo("[Main] Initializing teleop node...")

    # 初始化机器人 API
    arm = robot_api.Arm()
    gripper = robot_api.Gripper()

    # 创建交互式标记服务器
    im_server = InteractiveMarkerServer('gripper_im_server', q_size=2)
    auto_pick_im_server = InteractiveMarkerServer('auto_pick_im_server', q_size=2)

    # 启动 Gripper Teleop 控制界面
    teleop = GripperTeleop(arm, gripper, im_server)
    teleop.start()

    # 启动 AutoPick 控制界面（物体控制 + 自动抓取）
    auto_pick = AutoPickTeleop(arm, gripper, auto_pick_im_server)
    auto_pick.start()

    rospy.loginfo("[Main] Teleop interface ready. Waiting for user interaction...")
    rospy.spin()



if __name__ == '__main__':
    main()

