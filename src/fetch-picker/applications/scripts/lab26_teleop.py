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

import robot_api  

# 定义夹爪和手指的3D模型资源路径
GRIPPER_MESH = 'package://fetch_description/meshes/gripper_link.dae'
L_FINGER_MESH = 'package://fetch_description/meshes/l_gripper_finger_link.STL'
R_FINGER_MESH = 'package://fetch_description/meshes/r_gripper_finger_link.STL'

def axis_to_quaternion(axis):
    """
    将坐标轴转换为对应的四元数
    Args:
        axis: 坐标轴名称 ('x', 'y', 'z')
    Returns:
        Quaternion: 对应的四元数
    """
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
    """
    创建6自由度控制手柄
    包括三个轴的平移和旋转控制
    Returns:
        list: 包含所有控制手柄的列表
    """
    controls = []
    for ax in ['x', 'y', 'z']:
        # 创建平移控制手柄
        control_move = InteractiveMarkerControl()
        control_move.name = f"move_{ax}"
        control_move.interaction_mode = InteractiveMarkerControl.MOVE_AXIS
        control_move.orientation = axis_to_quaternion(ax)
        control_move.always_visible = True
        controls.append(copy.deepcopy(control_move))

        # 创建旋转控制手柄
        control_rotate = InteractiveMarkerControl()
        control_rotate.name = f"rotate_{ax}"
        control_rotate.interaction_mode = InteractiveMarkerControl.ROTATE_AXIS
        control_rotate.orientation = axis_to_quaternion(ax)
        control_rotate.always_visible = True
        controls.append(copy.deepcopy(control_rotate))
    return controls

def make_gripper_visualization():
    """
    创建夹爪的可视化标记
    包括夹爪主体和两个手指的3D模型
    Returns:
        list: 包含所有可视化标记的列表
    """
    markers = []
    offset_x = 0.166  # 夹爪相对于标记中心的偏移

    def mesh_marker(resource, y_offset=0):
        """创建单个3D模型标记"""
        m = Marker()
        m.type = Marker.MESH_RESOURCE
        m.mesh_resource = resource
        m.scale.x = m.scale.y = m.scale.z = 1.0
        m.color.r, m.color.g, m.color.b, m.color.a = 0.0, 1.0, 0.0, 1.0
        m.pose.position.x = offset_x
        m.pose.position.y = y_offset
        return m

    # 添加夹爪主体和两个手指的3D模型
    markers.append(mesh_marker(GRIPPER_MESH))
    markers.append(mesh_marker(L_FINGER_MESH, -0.06))
    markers.append(mesh_marker(R_FINGER_MESH, 0.06))
    return markers

class GripperTeleop:
    """夹爪遥操作类，提供交互式控制界面"""
    
    def __init__(self, arm, gripper, im_server):
        """
        初始化夹爪遥操作类
        Args:
            arm: 机械臂控制对象
            gripper: 夹爪控制对象
            im_server: 交互式标记服务器
        """
        self._arm = arm
        self._gripper = gripper
        self._im_server = im_server
        self._menu_handler = MenuHandler()
        self._current_marker_name = 'gripper_marker'

    def start(self):
        """启动夹爪遥操作界面"""
        rospy.loginfo("[Teleop] Starting gripper interactive marker...")
        gripper_marker = self.make_gripper_marker()
        self._im_server.insert(gripper_marker, feedback_cb=self.handle_feedback)

        # 检查初始位置是否可达
        pose = PoseStamped()
        pose.header.frame_id = 'base_link'
        pose.pose = gripper_marker.pose
        reachable = self._arm.check_pose(pose)
        rospy.loginfo(f"[Teleop] Initial IK check -> reachable: {reachable}")
        self.update_color(reachable)

        # 添加菜单选项
        self._menu_handler.insert('Go to Pose', callback=self.handle_feedback)
        self._menu_handler.insert('Open Gripper', callback=self.handle_feedback)
        self._menu_handler.insert('Close Gripper', callback=self.handle_feedback)
        self._menu_handler.apply(self._im_server, self._current_marker_name)
        self._im_server.applyChanges()

    def make_gripper_marker(self):
        """创建夹爪交互式标记"""
        im = InteractiveMarker()
        im.header.frame_id = 'base_link'
        im.name = self._current_marker_name
        im.description = "Gripper Teleop"
        im.scale = 0.25

        # 设置初始位置
        im.pose.position.x = 0.5
        im.pose.position.y = 0
        im.pose.position.z = 0.5
        im.pose.orientation.w = 1

        # 添加夹爪可视化
        control = InteractiveMarkerControl()
        control.always_visible = True
        control.interaction_mode = InteractiveMarkerControl.MENU
        control.markers.extend(make_gripper_visualization())
        im.controls.append(control)

        # 添加6自由度控制手柄
        im.controls.extend(make_6dof_controls())
        return im

    def handle_feedback(self, feedback):
        """
        处理交互式标记的反馈事件
        Args:
            feedback: 交互式标记的反馈信息
        """
        rospy.loginfo(f"[Feedback] Event type: {feedback.event_type}")
        pose = PoseStamped()
        pose.header.frame_id = 'base_link'
        pose.pose = feedback.pose

        if feedback.event_type == feedback.MENU_SELECT:
            # 处理菜单选择事件
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
            # 处理拖动结束事件
            rospy.loginfo("[Drag] Pose updated, checking IK...")
            reachable = self._arm.check_pose(pose)
            rospy.loginfo(f"[Drag] IK result: {reachable}")
            self.update_color(reachable)

    def update_color(self, reachable):
        """
        根据位置可达性更新标记颜色
        Args:
            reachable: 位置是否可达
        """
        rospy.loginfo("[Update] Updating marker color...")
        marker = self._im_server.get(self._current_marker_name)
        for m in marker.controls[0].markers:
            if reachable:
                m.color.r, m.color.g, m.color.b = 0.0, 1.0, 0.0  # 绿色表示可达
            else:
                m.color.r, m.color.g, m.color.b = 1.0, 0.0, 0.0  # 红色表示不可达
            m.color.a = 1.0
        self._im_server.insert(marker, feedback_cb=self.handle_feedback)
        rospy.sleep(0.01)  # 确保更新正常
        self._menu_handler.apply(self._im_server, self._current_marker_name)
        self._im_server.applyChanges()


class AutoPickTeleop(object):
    """自动抓取遥操作类，提供目标物体控制和自动抓取功能"""
    
    def __init__(self, arm, gripper, im_server):
        """
        初始化自动抓取遥操作类
        Args:
            arm: 机械臂控制对象
            gripper: 夹爪控制对象
            im_server: 交互式标记服务器
        """
        self._arm = arm
        self._gripper = gripper
        self._im_server = im_server
        self._menu_handler = MenuHandler()
        self._current_marker_name = 'target_marker'

    def start(self):
        """启动自动抓取遥操作界面"""
        # 创建并注册目标物体标记
        obj_marker = self.make_target_marker()
        self._im_server.insert(obj_marker, feedback_cb=self.handle_feedback)

        # 添加菜单选项
        self._menu_handler.insert('Pick Object', callback=self.handle_feedback)
        self._menu_handler.insert('Open Gripper', callback=self.handle_feedback)
        self._menu_handler.apply(self._im_server, self._current_marker_name)

        self._im_server.applyChanges()

    def make_target_marker(self):
        """创建目标物体交互式标记"""
        im = InteractiveMarker()
        im.header.frame_id = 'base_link'
        im.name = self._current_marker_name
        im.description = "Target Teleop"
        im.scale = 0.25
        im.pose.position.x = 0.7
        im.pose.position.z = 0.75
        im.pose.orientation.w = 1.0

        # 添加蓝色立方体表示目标物体
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
        control.markers.extend(make_gripper_visualization())  # 添加夹爪可视化
        im.controls.append(control)

        # 添加6自由度控制手柄
        im.controls.extend(make_6dof_controls())

        return im

    def handle_feedback(self, feedback):
        """
        处理交互式标记的反馈事件
        Args:
            feedback: 交互式标记的反馈信息
        """
        if feedback.event_type == feedback.MENU_SELECT:
            # 处理菜单选择事件
            if feedback.menu_entry_id == 1:  # Pick Object
                rospy.loginfo("[AutoPick] Pick Object requested.")
                marker = self._im_server.get(self._current_marker_name)
                target_pose = marker.pose

                # 创建预抓取位姿
                pre_grasp_pose = PoseStamped()
                pre_grasp_pose.header.frame_id = 'base_link'
                pre_grasp_pose.pose = copy.deepcopy(target_pose)

                # 执行抓取动作
                self._arm.move_to_pose(pre_grasp_pose)
                rospy.sleep(0.3)
                self._gripper.close()

            elif feedback.menu_entry_id == 2:  # Open Gripper
                rospy.loginfo("[AutoPick] Open Gripper requested.")
                self._gripper.open()

        elif feedback.event_type == feedback.MOUSE_UP:
            # 处理拖动结束事件
            rospy.loginfo("[AutoPick] Marker moved, checking IK...")
            pose = PoseStamped()
            pose.header.frame_id = 'base_link'
            pose.pose = feedback.pose
            reachable = self._arm.check_pose(pose)
            rospy.loginfo(f"[AutoPick] Pose reachable: {reachable}")
            self.update_color(reachable)

    def update_color(self, reachable):
        """
        根据位置可达性更新标记颜色
        Args:
            reachable: 位置是否可达
        """
        marker = self._im_server.get(self._current_marker_name)
        for m in marker.controls[0].markers:
            if m.type == Marker.CUBE:
                continue  # 保持蓝色立方体不变
            if reachable:
                m.color.r, m.color.g, m.color.b = 0.0, 1.0, 0.0  # 绿色表示可达
            else:
                m.color.r, m.color.g, m.color.b = 1.0, 0.0, 0.0  # 红色表示不可达
            m.color.a = 1.0
        self._im_server.insert(marker, feedback_cb=self.handle_feedback)
        self._menu_handler.apply(self._im_server, self._current_marker_name)
        self._im_server.applyChanges()

def main():
    """初始化并启动遥操作界面"""
    rospy.init_node('lab26_teleop')
    rospy.loginfo("[Main] Initializing teleop node...")

    # 初始化机器人控制接口
    arm = robot_api.Arm()
    gripper = robot_api.Gripper()

    # 创建交互式标记服务器
    im_server = InteractiveMarkerServer('gripper_im_server', q_size=2)
    auto_pick_im_server = InteractiveMarkerServer('auto_pick_im_server', q_size=2)

    # 启动夹爪遥操作界面
    teleop = GripperTeleop(arm, gripper, im_server)
    teleop.start()

    # 启动自动抓取遥操作界面
    auto_pick = AutoPickTeleop(arm, gripper, auto_pick_im_server)
    auto_pick.start()

    rospy.loginfo("[Main] Teleop interface ready. Waiting for user interaction...")
    rospy.spin()

if __name__ == '__main__':
    main()

