import rospy
from string_service_demo.srv import StringService

def main():
	rospy.init_node('string_service_client')
	rospy.wait_for_service('/send_string')
	proxy = rospy.ServiceProxy('/send_string', StringService)

	message = "Hello from client!"
	response = proxy(message)
	rospy.loginfo("Response: %s", response.result)

if __name__ == "__main__":
	main()
