from threading import *
from time import sleep
import asyncio


runThread = 1

class c1(Thread):
    def run(self):
        print('c1')

async def loop(client):
    while (runThread == 1):
        print('c2') 
        sleep(1)

class c2(Thread):
    def __init__(self, client):
        self.client = client

    def run(self):
        
        asyncio.run(loop(self.client))

    




x = c1()
y = c2()

#x.start()
#y.start()



