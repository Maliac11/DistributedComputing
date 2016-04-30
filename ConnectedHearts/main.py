from hearts import *
from control_pi import *
from multiprocessing.queues import Queue
from multiprocessing import Array
import ctypes
from webcam-pulse.get_pulse import *

""" 
	Get pulse! 
"""
parser = argparse.ArgumentParser(description='Webcam pulse detector.')
parser.add_argument('--serial', default=None,
                    help='serial port destination for bpm data')
parser.add_argument('--baud', default=None,
                    help='Baud rate for serial transmission')
parser.add_argument('--udp', default=None,
                    help='udp address:port destination for bpm data')

args = parser.parse_args()
App = getPulseApp(args)
pulse_val = App.main_loop()
while pulse_val == 0:
    pulse_val = App.main_loop()
print "FINISHED with pulse " + str(pulse_val)

bulb_objects_dict = {}

#print type_of_array.bytes()

#test_if_queue_works = Queue()
#print test_if_queue_works

hosts = ['192.168.1.20', '192.168.1.21']

uuid_list = Array(ctypes.c_uint64, 12)
""" 
    One power strip has ip 192.168.1.20; the other, .21
    .20 will control bulbs 0-5
    .21 will control bulbs 6-11
"""
power_strip_on_list = Array('i', 12)


for i in range(0, 12):
    p = Bulb(id = i, uuid_list = uuid_list, turned_on_list = power_strip_on_list)
    #print p.uuid
    bulb_objects_dict[p.uuid] = p

for bulb in bulb_objects_dict.values():
    bulb.register_bulbs(bulb_objects_dict)
    bulb.send_uuid()

pi = Pi(bpm = pulse_val, turned_on_list = power_strip_on_list, hosts = hosts)
pi.start()

for bulb in bulb_objects_dict.values():
   bulb.start()

for bulb in bulb_objects_dict.values():
  print "joining!"
  bulb.join()

pi.join()

#for bulb in bulb_objects_list:
    #bulb.leader_election()