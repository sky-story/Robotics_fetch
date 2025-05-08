#!/usr/bin/env python

import rospy
import pickle
import os
from geometry_msgs.msg import PoseWithCovarianceStamped
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
import actionlib

POSE_FILE = '/fetch_ws/src/map_annotator/poses.pkl'

class MapAnnotator:
    def __init__(self):
        self.poses = self.load_poses()
        self.latest_pose = None
        rospy.Subscriber('/amcl_pose', PoseWithCovarianceStamped, self.pose_callback)
        self.client = actionlib.SimpleActionClient('move_base', MoveBaseAction)
        rospy.loginfo("Waiting for move_base action server...")
        self.client.wait_for_server()
        rospy.loginfo("Connected to move_base server.")

    def pose_callback(self, msg):
        self.latest_pose = msg.pose.pose

    def load_poses(self):
        if os.path.exists(POSE_FILE):
            with open(POSE_FILE, 'rb') as f:
                return pickle.load(f)
        return {}

    def save_poses(self):
        with open(POSE_FILE, 'wb') as f:
            pickle.dump(self.poses, f)

    def run(self):
        print("""Welcome to the map annotator!
Commands:
  list             List all saved poses.
  save <name>      Save current pose with given name.
  delete <name>    Delete pose with given name.
  goto <name>      Send robot to pose with given name.
  help             Show this help message.
""", flush=True)

        try:
            while not rospy.is_shutdown():
                cmd = raw_input("> ")
                if cmd == "list":
                    print("Poses:")
                    for name in self.poses:
                        print("  " + name)
                elif cmd.startswith("save "):
                    name = cmd[5:]
                    if self.latest_pose:
                        self.poses[name] = self.latest_pose
                        self.save_poses()
                        print("Saved pose: " + name)
                    else:
                        print("No pose received yet.")
                elif cmd.startswith("delete "):
                    name = cmd[7:]
                    if name in self.poses:
                        del self.poses[name]
                        self.save_poses()
                        print("Deleted pose: " + name)
                    else:
                        print("No such pose.")
                elif cmd.startswith("goto "):
                    name = cmd[5:]
                    if name in self.poses:
                        goal = MoveBaseGoal()
                        goal.target_pose.header.frame_id = "map"
                        goal.target_pose.header.stamp = rospy.Time.now()
                        goal.target_pose.pose = self.poses[name]
                        self.client.send_goal(goal)
                        self.client.wait_for_result()
                        print("Arrived at " + name)
                    else:
                        print("No such pose.")
                elif cmd == "help":
                    print("Commands:\n  list\n  save <name>\n  delete <name>\n  goto <name>\n  help")
                else:
                    print("Unknown command")
        except KeyboardInterrupt:
            print("\nExiting map annotator.")

if __name__ == '__main__':
    rospy.init_node('map_annotator')
    annotator = MapAnnotator()
    annotator.run()
