'''
Created on Oct 12, 2016

@author: mwitt_000
'''
import network
import link
import threading
from time import sleep
import sys

##configuration parameters
router_queue_size = 0 #0 means unlimited
simulation_time = 9 #give the network sufficient time to transfer all packets before quitting

if __name__ == '__main__':
    object_L = [] #keeps track of objects, so we can kill their threads
    
    #create network hosts
    client1 = network.Host(1)
    object_L.append(client1)
    client2 = network.Host(2)
    object_L.append(client2)
    server = network.Host(3)
    object_L.append(server)
    #print("HI")
    #create routers and routing tables for connected clients (subnets)
    router_a_rt_tbl_D = {3: {1: 31},3:{1:12},1:{0:7},2:{0:6}} # packet to host 1 through interface 1 for cost 1
    router_a = network.Router(name="A", 
                              num_intf = 2,
                              rt_tbl_D = router_a_rt_tbl_D, 
                              max_queue_size=router_queue_size)
    object_L.append(router_a)
    router_b_rt_tbl_D = {3: {1: 33},1:{0:60},2:{0:60}} # packet to host 2 through interface 1 for cost 3
    router_b = network.Router(name="B", 
                              num_intf = 2, 
                              rt_tbl_D = router_b_rt_tbl_D, 
                              max_queue_size=router_queue_size)
    object_L.append(router_b)
    router_c_rt_tbl_D = {3: {1: 33},1:{0:40},2:{0:40}} # packet to host 1 through interface 1 for cost 1
    router_c = network.Router(name="C", 
                              num_intf = 2,
                              rt_tbl_D = router_c_rt_tbl_D, 
                              max_queue_size=router_queue_size)
    object_L.append(router_c)
    router_d_rt_tbl_D = {3: {1: 3},1:{0:21},1:{0:52},2:{0:31},2:{0:22}} # packet to host 1 through interface 1 for cost 1
    router_d = network.Router(name="D", 
                              num_intf = 2,
                              rt_tbl_D = router_d_rt_tbl_D, 
                              max_queue_size=router_queue_size)
    object_L.append(router_d)    
    #create a Link Layer to keep track of links between network nodes
    link_layer = link.LinkLayer()
    object_L.append(link_layer)
    
    #add all the links
    link_layer.add_link(link.Link(client1, 0, router_a, 0))
    link_layer.add_link(link.Link(client2, 0, router_a, 0))
    link_layer.add_link(link.Link(router_a, 1, router_b, 0))
    link_layer.add_link(link.Link(router_a, 1, router_c, 0))
    link_layer.add_link(link.Link(router_b, 1, router_d, 0))
    link_layer.add_link(link.Link(router_c, 1, router_d, 0))
    link_layer.add_link(link.Link(router_d, 1, server, 0))
    
    
    #start all the objects
    thread_L = []
    for obj in object_L:
        thread_L.append(threading.Thread(name=obj.__str__(), target=obj.run)) 
    
    for t in thread_L:
        t.start()
    
    #send out routing information from router A to router B interface 0
    for obj in object_L:
        if str(type(obj)) == "<class 'network.Router'>":
            if(obj.name=='A'):
                obj.send_routes(1)
                #self.send_routes(1)
            elif(obj.name=='B'):
                obj.send_routes(0)
                obj.send_routes(1)
            elif(obj.name=='C'):
                obj.send_routes(0)
                obj.send_routes(1)
            elif(obj.name=='D'):
                obj.send_routes(0)
    
    
    sleep(4)
    #create some send events    
    for i in range(1):
        client1.udt_send(3, 'Sample client data %d' % i)
    
    #give the network sufficient time to transfer all packets before quitting
    sleep(simulation_time)
    
    #print the final routing tables
    for obj in object_L:
        if str(type(obj)) == "<class 'network.Router'>":
            obj.print_routes()
    
    #join all threads
    for o in object_L:
        o.stop = True
    for t in thread_L:
        t.join()
        
    print("All simulation threads joined")



# writes to host periodically