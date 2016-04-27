from datetime import datetime
import multiprocessing
import threading
import sys, time, socket, random, Queue
import uuid

# cite: http://stackoverflow.com/questions/19846332/python-threading-inside-a-class
# yay decorators
#def threaded(fn):
    #""" 
    #Creates a new thread to run the function fn. Use by writing "@threaded" above function to thread.

    #fn: function 
    #returns: None 
    #"""
    #def wrapper(*args, **kwargs):
    #    Thread(target=fn, args=args, kwargs=kwargs).start()
    #return wrapper
class BulbQueue(Queue.Queue, object):
    def __init__(self):
        super(BulbQueue, self).__init__()
        self.queuesize = 0

    def empty(self):
        return super(BulbQueue, self).empty()

    def size(self):
        return self.queuesize

    def get(self):
        if not self.empty():
            self.queuesize -= 1
            return super(BulbQueue, self).get() 
        else:
            return None

    def put(self, item):
        if not super(BulbQueue, self).full():
            super(BulbQueue, self).put(item)
            self.queuesize += 1
        else:
            None

class Bulb(multiprocessing.Process):
    def __init__(self, id):
        super(Bulb, self).__init__()
        self.id = id
        self.uuid = uuid.uuid4()
        self.uuid_dict = {}
        self.bulb_list = None
        self.leader = None
        self.new_election = False
        self.q = BulbQueue()

        self.uuid_dict[self.uuid] = self

    def register_bulbs(self, all_bulb_objects):
        self.bulb_list = all_bulb_objects

    def send_uuid(self):
        #print "Is the thread getting here? \n"
        for bulb in self.bulb_list:
            bulb.q.put(self.uuid)
            bulb.uuid_dict[self.uuid] = self
            #print "I'm bulb " + str(bulb.id) +  " What about here? The dict: " + str(bulb.uuid_dict) + "\n"

    def get_max_uuid(self):
        curr_uuid = self.q.get()
        curr_max = curr_uuid
        while not self.q.empty():
            curr_uuid = self.q.get()
            if curr_uuid > curr_max:
                curr_max = curr_uuid
        return curr_max


    #@threaded
    def leader_election(self):
        #print "is this working? \n"
        self.leader = None
        timeout = time.time() + 1
        while True:
            if time.time() > timeout:
                break
            #if self.queue.qsize() == 12:
            #    self.leader = get_max_uuid()
                #print "Do I ever get here? " + str(self.leader.id) + "\n"
            #    break
        self.leader = self.uuid_dict[self.get_max_uuid()]
        #print "Or here? " + str(self.leader.id) + "\n" 
        """if (self == self.leader):
            sys.stderr.write("I actually exited. I'm the leader. " + "id: " + str(self.id) + ", leader: " + str(self.leader.id) + "\n")
            return"""
        #print "id: " + str(self.id) + ", leader: " + str(self.leader.id) + "\n"
        sys.stderr.write("id: " + str(self.id) + ", leader: " + str(self.leader.id) + "\n")
        self.new_election = False
        if self.leader.id == self.id:
            print "Hi, I'm the leader: " + str(self.id) + "\n"
            #self.set_up_leader_socket()
        else:
            print "Hi, I'm a follower: " + str(self.id) + "\n"
            connection_timeout = random.randint(1,20)
            #self.connect_to_leader_socket(connection_timeout, time.time())
        #sys.stderr.write("Number of bulbs in dict: " + str(len(self.uuid_dict)) + " I'm thread " + str(self.id) + "\n")
        #self.ping_leader_socket()
        #print "I got here and I'm bulb " + str(self.id) + "\n"

    #@threaded
    """def set_up_leader_socket(self):
        try:
            self.leader_socket.shutdown(socket.SHUT_RDWR)
            self.leader_socket.close()
        except:
            pass
        try: 
            self.leader_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.leader_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                self.leader_socket.bind(('', self.leader_socket_port))
            except socket.error as msg:
                sys.stderr.write("Bind failed. Error Code : " \
                        + str(msg[0]) + " Message : " + str(msg[1]) + "\n")
                sys.exit()
            self.leader_socket.listen(12)
            try:
                self.leader_socket.shutdown(socket.SHUT_RDWR)
            except:
                pass
            self.leader_socket.close()
            print "Successfully started socket at port " + str(self.leader_socket_port) + "\n"
        except Exception, e: 
            sys.stderr.write("Exception: " + str(e))
            self.set_up_leader_socket() 

    #@threaded
    def connect_to_leader_socket(self, connection_timeout, start_time):
        print "Do I get here? \n"
        if self.new_election: 
            print "New election started by someone else. I am " + str(self.id) + "\n"
            self.leader_election()
        #elif time.time() < start_time + connection_timeout:
        try:
            self.follower_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #print self.follower_socket_port
            #print type(self.follower_socket_port)
            self.follower_socket.connect(('', self.leader_socket_port))
            print "\n" + str(self.id) + str(self.id) + str(self.id) + " Sucessfully started follower socket for " + str(self.id) + "\n"
        except Exception, e:
            sys.stderr.write("Connecting follower socket exception " + str(e) + "\n")
            self.connect_to_leader_socket(connection_timeout, start_time)
        else:
            try:
                self.follower_socket.connect(('', self.leader_socket_port))
                self.connect_to_leader_socket(connection_timeout, time.time())
            except Exception, e:
                self.setup_new_election()
                print "Let's start a new leader election after timeout: " + str(connection_timeout) + ". I am " + str(self.id) + "\n"
                self.leader_election()

    #@threaded
    def ping_leader_socket(self):
        msg = "Are you alive?"
        while True or not self.new_election:
            try:
                self.follower_socket.send(msg.encode())
            except Exception, e:
                self.setup_new_election()
                break
        self.leader_election()

    def setup_new_election(self):
        self.new_election = True
        for bulb in self.bulb_list:
            bulb.new_election = True  
            bulb.empty_uuid_dict()
            sys.stderr.write("I emptied my dictionary, see: " + str(bulb.uuid_dict) + "\n")
        for bulb in self.bulb_list:
            sys.stderr.write("Dictionary size: " + str(len(self.uuid_dict)))
            try:
                bulb.send_uuid()
                #sys.stderr.write("I'm bulb number " + str(self.id) + "\n")
                if (bulb.id == bulb.leader.id):
                    sys.stderr.write("This shouldn't have worked. Fuck you. \n")
            except Exception, e:
                sys.stderr("Beautiful exception \n")
                pass"""

    def run(self):
        print "Hi I'm bulb_" + str(self.id) + " And my queue size is: " + str(self.q.size()) + "\n"
        self.leader_election()






