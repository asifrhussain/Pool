#!/usr/bin/python


import threading
import time

##################################################
### Module for a thread safe pool of resources ###
##################################################


class Pool():

    ### initialize with an optional list of resources
    def __init__(self, resources=[]):
        self.resource_list = []  # list of resources
        if isinstance(resources, list):
            for r in resources:
                self.resource_list.append((r, threading.Lock()))
        self.open_flag = False # open/close flag
        self.resource_lock = threading.Lock()  # resource list lock

    ### set pool to open to allow aquire and release calls
    def open(self):
        self.open_flag = True

    ### check if pool is set to open
    def is_open(self):
        return self.open_flag

    ### get the index of a resource in the resource list
    def resource_index(self, resource):
        for x in range(len(self.resource_list)):
            if id(self.resource_list[x][0]) == id(resource):
                return x
        return -1

    ### close the pool immediately if now is False(default), if now is True wait until all resources have been released
    def close(self, now=False):
        self.open_flag = False
        if not now:
            pass
        else:
            closed = False
            while not closed: # poll to check if all resources are free
                self.resource_lock.acquire()
                closed = True
                for r in self.resource_list:
                    acquire = r[1].acquire(False)
                    if not acquire:
                        closed = False
                        break
                    else:
                        r[1].release()
                self.resource_lock.release()
        return

    ### add a resource if not present
    def add(self, resource):
        self.resource_lock.acquire()
        index = self.resource_index(resource)
        if index == -1:
            self.resource_list.append((resource, threading.Lock()))
            self.resource_lock.release()
            return True
        else:
            self.resource_lock.release()
            return False

    ### remove a resource if present, when now is False(default) remove immediately, when now is True wait until released
    def remove(self, resource, now=False):
        if not now:
            self.resource_lock.acquire()
            index = self.resource_index(resource)
            if index == -1:
                self.resource_lock.release()
                return False
            else:
                self.resource_list.pop(index)
                self.resource_lock.release()
                return True
        else:
            if now:
                acquired = False
                while not acquired: # poll to check if resource has been released
                    self.resource_lock.acquire()
                    index = self.resource_index(resource)
                    if index == -1:
                        self.resource_lock.release()
                        return False
                    else:
                        acquired = self.resource_list[index][1].acquire(False)
                        if acquired:
                            self.resource_list[index][1].release()
                            self.resource_list.pop(index)
                            self.resource_lock.release()
                            return True
                    self.resource_lock.release()
            return True

    ### method to acquire a resource
    def acquire(self, timeout=None):
        if not self.open_flag:
            raise Exception('Pool Closed!')
        if len(self.resource_list)==0:
            raise Exception('Pool Empty!')
        begin_time = time.time()
        acquired = False
        while not acquired: # poll to check for free resources
            self.resource_lock.acquire()
            for r in self.resource_list:
                acquired = r[1].acquire(False)
                if acquired:
                    self.resource_lock.release()
                    return r[0]
                if timeout is not None and (time.time()-begin_time > timeout): # timeout if specified
                    self.resource_lock.release()
                    return None
            self.resource_lock.release()

    ### release the resource if present
    def release(self, resource):
        self.resource_lock.acquire()
        index = self.resource_index(resource)
        if (index == -1):
            self.resource_lock.release()
            return False
        else:
            self.resource_list[index][1].release()
            self.resource_lock.release()
            return True
