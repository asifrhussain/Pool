#!/usr/bin/python

class Counter:
    
    def __init__(self, name):
        self.count=0
        self.name=name

    def increment(self):
        self.count+=1
 
    def decrement(self):
        self.count-=1


from Pool import *
from threading import Thread
import time


def thread1(pool):
    obj=pool.acquire()
    print 'thread1 acquired',obj.name
    time.sleep(20)
    print 'release1',pool.release(obj)

def thread2(pool):
    obj=pool.acquire()
    print 'thread2 acquired',obj.name
    print 'adding three',pool.add(c3)
    obj.increment()
    time.sleep(10)
    print 'release2',pool.release(obj)

def thread3(pool):
    obj=pool.acquire()
    print 'thread3 acquired',obj.name
    print 'removing two',pool.remove(c2,now=True) 
    print 'release3',pool.release(obj)

def thread4(pool):
    obj=pool.acquire()
    print 'thread4 acquired',obj.name
    obj.increment()
    print 'release4',pool.release(obj)

c1=Counter('one')
c2=Counter('two')
c3=Counter('three')

p=Pool([c1])

print 'adding one',p.add(c1)
print 'adding two',p.add(c2)


p.open()

for r in p.resource_list:
    print r[0].name,r[0].count

t1 = Thread(target=thread1, args=(p,))
t1.start()

t2 = Thread(target=thread2, args=(p,))
t2.start()

t3 = Thread(target=thread3, args=(p,))
t3.start()

t4 = Thread(target=thread4, args=(p,))
t4.start()

print 'Closing...'
p.close(now=True)
for r in p.resource_list:
    print r[0].name,r[0].count
print 'Done.'



