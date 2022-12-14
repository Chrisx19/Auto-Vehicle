#!/usr/bin/env python3
import rospy
import pixy
from std_msgs.msg import Float32
from geometry_msgs.msg import Twist
from ctypes import *
from pixy import *

print("Pixy2 Python SWIG Example -- Get Blocks")

pixy.init ()
pixy.change_prog ("color_connected_components");

class Blocks (Structure):
  _fields_ = [ ("m_signature", c_uint),
    ("m_x", c_uint),
    ("m_y", c_uint),
    ("m_width", c_uint),
    ("m_height", c_uint),
    ("m_angle", c_uint),
    ("m_index", c_uint),
    ("m_age", c_uint) ]

blocks = BlockArray(100)
frame = 0
cont = 0
dead_zone = 105

def mapfloat(x, in_min, in_max, out_min, out_max):
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

rospy.init_node("pixy_node")
cmd_vel_pub = rospy.Publisher("/cmd_vel_AV", Twist, queue_size = 1)

while not rospy.is_shutdown():
  count = pixy.ccc_get_blocks (100, blocks)
  vel = Twist()

  signature = blocks[0].m_signature
  x = blocks[0].m_x
  y = blocks[0].m_y
  width = blocks[0].m_width
  height = blocks[0].m_height
  if count > 0:
    cx = (x + (width / 2))
    cy = (y + (height / 2))
    cx = mapfloat(cx, 0, 320, -700, 700)
    cy = mapfloat(cy, 0, 200, 0, 63)
    area = width * height

    for index in range (0, count):

      print('area %3d' % area, 'cx = %d' % cx)
      if ( cx > -dead_zone and cx < dead_zone):
        cx = 0

      if (cx < 0):
        vel.linear.x = 60
        vel.angular.z = cx
      elif cx > 0:
        vel.linear.x = 60
        vel.angular.z = cx
      else:
        vel.linear.x = 63

      if (area > 15000):
        vel.linear.x = 0
        vel.angular.z = 0
      
  else:
    cont += 1
    if (cont == 100):
      cont = 0
      cx = 0

  cmd_vel_pub.publish(vel)
  rospy.sleep(0.1)