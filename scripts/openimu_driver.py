#!/usr/bin/env python3

import rospy
import sys
import math
from time import time, sleep
from sensor_msgs.msg import Imu, MagneticField
from tf.transformations import quaternion_from_euler

try:
    from ros_openimu.src.aceinna.tools import OpenIMU
except:  # pylint: disable=bare-except
    temp = (sys.path[0])
    temp2 = temp[0:(len(temp)-7)]
    sys.path.append(temp2 + 'src')
    #sys.path.append('./src')
    from aceinna.tools import OpenIMU


class OpenIMUros:
    def __init__(self):

        self.port = rospy.get_param('port', '/dev/ttyS2')
        self.baudrate = rospy.get_param('baudrate', '115200')


        self.openimudev = OpenIMU(
		device_type='IMU',
		com_port=self.port,
		baudrate=self.baudrate
	)

        rospy.loginfo(self.port)
        rospy.loginfo(self.baudrate)

        self.openimudev.startup()

    def close(self):
        self.openimudev.close()

    def readimu(self):
        readback = self.openimudev.getdata('a2')
        return readback

if __name__ == "__main__":
    rospy.init_node("openimu_driver")

    pub_imu = rospy.Publisher('imu_acc_ar', Imu, queue_size=1)
    pub_mag = rospy.Publisher('imu_mag', MagneticField, queue_size=1)

    imu_msg = Imu()             # IMU data
    mag_msg = MagneticField()   # Magnetometer data
    
    rate = rospy.Rate(200)   # 200Hz
    seq = 0
    frame_id = 'OpenIMU'
    convert_rads = math.pi /180
    convert_tesla = 1/10000

    openimu_wrp = OpenIMUros()
    rospy.loginfo("OpenIMU driver initialized.")
    sleep(5)

    while not rospy.is_shutdown():
        #read the data - call the get imu measurement data
        readback = openimu_wrp.readimu()
        #publish the data m/s^2 and convert deg/s to rad/s

        if(readback):
            imu_msg.header.stamp = rospy.Time.now()
            imu_msg.header.frame_id = frame_id
            imu_msg.header.seq = seq

#imudata =[time_ms, time_s, roll, pitch, heading, xrate, yrate, zrate, xaccel, yaccel, zaccel]


            q = quaternion_from_euler(readback[2], readback[3], readback[4])

            imu_msg.orientation_covariance[0] = -1 
            imu_msg.orientation.x = q[0]
            imu_msg.orientation.y = q[1]
            imu_msg.orientation.z = q[2]
            imu_msg.orientation.w = q[3]
            
            
            imu_msg.linear_acceleration.x = readback[8]
            imu_msg.linear_acceleration.y = readback[9]
            imu_msg.linear_acceleration.z = readback[10]
            imu_msg.linear_acceleration_covariance[0] = -1
            imu_msg.angular_velocity.x = readback[5] * convert_rads
            imu_msg.angular_velocity.y = readback[6] * convert_rads
            imu_msg.angular_velocity.z = readback[7] * convert_rads
            imu_msg.angular_velocity_covariance[0] = -1
            
            pub_imu.publish(imu_msg)
            seq = seq + 1
            

            rate.sleep()
    openimu_wrp.close()         # exit



