#!/usr/bin/env python
import rospy
from ctypes import c_ushort
from dwl_planners.msg import WholeBodyTrajectory
from dwl_planners.msg import WholeBodyState
from sensor_msgs.msg import JointState


class JointStatePublisher():
    def __init__(self):
        # Defining the subscriber
        rospy.Subscriber("whole_body_trajectory", WholeBodyTrajectory, self.callback)
        
        # Defining the publisher
        self.pub = rospy.Publisher('joint_states', JointState, queue_size=5)


    def callback(self, msg):
        state = WholeBodyState()
        
        # Setting the current state
        state = msg.current_state
        
        # Publishing the current joint state
        self.publishJointState(state);
        rospy.sleep(0.5)
        
        # Publishing the joint state trajectory
        for i in range(len(msg.trajectory)):
            duration = msg.trajectory[i].time - state.time
            rospy.sleep(duration)
            state = msg.trajectory[i]
            self.publishJointState(state)
       
        
    def publishJointState(self, state):
        msg = JointState()
        
        # Setting the time
        msg.header.stamp = rospy.Time.now()
        
        # Setting the virtual joint states
        num_virtual_joints = len(state.base_ids)
        num_joints = (num_virtual_joints + len(state.joints))
        
        # Initializing the joint state sizes
        msg.name = num_joints * [""]
        msg.position = num_joints * [0.0]
        msg.velocity = num_joints * [0.0]
        msg.effort = num_joints * [0.0]
        
        # Setting the whole-body state message
        for i in range(num_joints):
            if i < num_virtual_joints:
                base_id = ord(state.base_ids[i])
                msg.name[i] = state.base_names[i]
                msg.position[i] = state.base[base_id].position
                msg.velocity[i] = state.base[base_id].velocity
                msg.effort[i] = state.base[base_id].effort
            else:
                msg.name[i] = state.joint_names[i-num_virtual_joints]
                msg.position[i] = state.joints[i-num_virtual_joints].position;
                msg.velocity[i] = state.joints[i-num_virtual_joints].velocity;
                msg.effort[i] = state.joints[i-num_virtual_joints].effort;
                
        # Publishing the current joint state       
        self.pub.publish(msg)
        


if __name__ == '__main__':
    rospy.init_node('joint_state_publisher')
        
    jsp = JointStatePublisher()
    
    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()
