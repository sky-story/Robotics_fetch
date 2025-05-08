import rospy
from your_package_name.srv import StringService

def call_service():
	rospy.init_node('string_client')
	rospy.wait_for_service('/send_string')
	proxy = rospy.ServiceProxy('/send_string', StringService)
	message = "Hello, I am client!"
	response = proxy(message)
	rospy.loginfo("Received response: %s", response.result)

if __name__ == '__main__':
	call_service()
