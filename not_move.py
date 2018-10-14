##!/usr/bin/env python

import rospy


from geometry_msgs.msg import Twist, Point, Quaternion
import tf
from transform_utils import quat_to_angle, normalize_angle
from math import radians, copysign, sqrt, pow, pi

import sys
sys.path.append("/home/shrc/workspace")
sys.path.append("/home/shrc/workspace/locater")
sys.path.append("home/shrc/.local/lib/python3.5/site-packages")
sys.path.append("/usr/local/lib/python3.5/dist-packages")
from locater import Locater


locater = Locater()


class move_to_direction():
    """docstring for move_to_direction"""
    def __init__(self):
        rospy.init_node('move_to_direction', anonymous=False)

        rospy.on_shutdown(self.shutdown)

        self.cmd_vel = rospy.Publisher('/cmd_vel', Twist, queue_size=5)

        self.rate = rospy.get_param('~rate', 50)
        r = rospy.Rate(self.rate)

        #max speed
        linear_speed = 0.26 
        #linear_speed = 0
        angular_speed = 2
        angular_tolerance = radians(1.0)

        self.tf_listener = tf.TransformListener()
        rospy.sleep(0.5)
        self.odom_frame = '/odom'

        try:
            self.tf_listener.waitForTransform(self.odom_frame, '/base_footprint', rospy.Time(), rospy.Duration(1.0))
            self.base_frame = '/base_footprint'
        except (tf.Exception, tf.ConnectivityException, tf.LookupException):
            try:
                self.tf_listener.waitForTransform(self.odom_frame, '/base_link', rospy.Time(), rospy.Duration(1.0))
                self.base_frame = '/base_link'
            except (tf.Exception, tf.ConnectivityException, tf.LookupException):
                rospy.loginfo("Cannot find transform between /odom and /base_link or /base_footprint")
                rospy.signal_shutdown("tf Exception")

        az, el, time = locater.get()
        # str = raw_input("goal direction:")
        str = az
        print ("goal direction is:", str)   ## str = [-pi,pi]

        goal_angle = float(str)

        if goal_angle < 0:
            # goal_angle = pi*2 - goal_angle
            goal_angle = - goal_angle
            angular_speed = - angular_speed
            
# these 4 sentences are commented by me
#        position = Point()

        # angular_duration = goal_angle / angular_speed

 #       move_cmd = Twist()
  #      move_cmd.linear.x = linear_speed
   #     move_cmd.angular.z = angular_speed

        (position, rotation) = self.get_odom()

        last_angle = rotation
        turn_angle = 0

# this while-loop is commented by me

    #    while  abs(turn_angle + angular_tolerance) < abs(goal_angle) and not rospy.is_shutdown():
    #        self.cmd_vel.publish(move_cmd)
    #        r.sleep()

    #        (position,rotation) = self.get_odom()

    #        delta_angle = normalize_angle(rotation - last_angle)

    #        turn_angle += delta_angle
    #        last_angle = rotation

        # ticks = int(goal_angle * self.rate)

        # for t in range(ticks):
        #     self.cmd_vel.publish(move_cmd)
        #     r.sleep()

        # angular_speed = 1.82

# these 4 sentences are commented by me
    #    move_cmd = Twist()
    #    move_cmd.linear.x = 0.26
    #    self.cmd_vel.publish(move_cmd)
    #    rospy.sleep(0.5)


    def get_odom(self):
        try:
            (trans, rot) = self.tf_listener.lookupTransform(self.odom_frame, self.base_frame, rospy.Time(0))
        except (tf.Exception, tf.ConnectivityException, tf.LookupTransform):
            rospy.loginfo("TF Exception")
            return

        return (Point(*trans), quat_to_angle(Quaternion(*rot)))


    def shutdown(self):
        rospy.loginfo("stopping the robot...")
        self.cmd_vel.publish(Twist())
        rospy.sleep(1)

if __name__ == '__main__':
    # str = 1.8
    try:
        while str != 'q':
            move_to_direction()
    except :
        rospy.loginfo("move to direction closed")


        
