'''
Created on Oct 12, 2016

@author: mwitt_000
'''
import queue
import threading
from email.message import Message
from pyxb.bundles.wssplat.raw.soapenc import byte_


## wrapper class for a queue of packets
class Interface:
    ## @param maxsize - the maximum size of the queue storing packets
    #  @param cost - of the interface used in routing
    def __init__(self, maxsize=0):
        self.in_queue = queue.Queue(maxsize);
        self.out_queue = queue.Queue(maxsize);
    
    ##get packet from the queue interface
    # @param in_or_out - use 'in' or 'out' interface
    def get(self, in_or_out):
        try:
            if in_or_out == 'in':
                pkt_S = self.in_queue.get(False)
#                 if pkt_S is not None:
#                     print('getting packet from the IN queue')
                return pkt_S
            else:
                pkt_S = self.out_queue.get(False)
#                 if pkt_S is not None:
#                     print('getting packet from the OUT queue')
                return pkt_S
        except queue.Empty:
            return None
        
    ##put the packet into the interface queue
    # @param pkt - Packet to be inserted into the queue
    # @param in_or_out - use 'in' or 'out' interface
    # @param block - if True, block until room in queue, if False may throw queue.Full exception
    def put(self, pkt, in_or_out, block=False):
        if in_or_out == 'out':
#             print('putting packet in the OUT queue')
            self.out_queue.put(pkt, block)
        else:
#             print('putting packet in the IN queue')
            self.in_queue.put(pkt, block)
            
        
## Implements a network layer packet (different from the RDT packet 
# from programming assignment 2).
# NOTE: This class will need to be extended to for the packet to include
# the fields necessary for the completion of this assignment.
class NetworkPacket:
    ## packet encoding lengths 
    dst_addr_S_length = 2
    prot_S_length = 1
    
    ##@param dst_addr: address of the destination host
    # @param data_S: packet payload
    # @param prot_S: upper layer protocol for the packet (data, or control)
    def __init__(self, dst_addr, prot_S, data_S):
        self.dst_addr = dst_addr
        self.data_S = data_S
        self.prot_S = prot_S
        
    ## called when printing the object
    def __str__(self):
        return self.to_byte_S()
        
    ## convert packet to a byte string for transmission over links
    def to_byte_S(self):
        byte_S = str(self.dst_addr).zfill(self.dst_addr_S_length)
        if self.prot_S == 'data':
            byte_S += '1'
        elif self.prot_S == 'control':
            byte_S += '2'
        else:
            raise('%s: unknown prot_S option: %s' %(self, self.prot_S))
        #byte_S+='#'
        byte_S += self.data_S
        return byte_S
    ## extract a packet object from a byte string
    # @param byte_S: byte string representation of the packet
    @classmethod
    def from_byte_S(self, byte_S):
        dst_addr = int(byte_S[0 : NetworkPacket.dst_addr_S_length])
        prot_S = byte_S[NetworkPacket.dst_addr_S_length : NetworkPacket.dst_addr_S_length + NetworkPacket.prot_S_length]
        if prot_S == '1':
            prot_S = 'data'
        elif prot_S == '2':
            prot_S = 'control'
        else:
            raise('%s: unknown prot_S field: %s' %(self, prot_S))
        data_S = byte_S[NetworkPacket.dst_addr_S_length + NetworkPacket.prot_S_length : ]        
        return self(dst_addr, prot_S, data_S)
    

    

## Implements a network host for receiving and transmitting data
class Host:
    
    ##@param addr: address of this node represented as an integer
    def __init__(self, addr):
        self.addr = addr
        self.intf_L = [Interface()]
        self.stop = False #for thread termination
    
    ## called when printing the object
    def __str__(self):
        return 'Host_%s' % (self.addr)
       
    ## create a packet and enqueue for transmission
    # @param dst_addr: destination address for the packet
    # @param data_S: data being transmitted to the network layer
    def udt_send(self, dst_addr, data_S):
        p = NetworkPacket(dst_addr, 'data', data_S)
        print('%s: sending packet "%s"' % (self, p))
        self.intf_L[0].put(p.to_byte_S(), 'out') #send packets always enqueued successfully
        
    ## receive packet from the network layer
    def udt_receive(self):
        pkt_S = self.intf_L[0].get('in')
        if pkt_S is not None:
            print('%s: received packet "%s"' % (self, pkt_S))
       
    ## thread target for the host to keep receiving data
    def run(self):
        print (threading.currentThread().getName() + ': Starting')
        while True:
            #receive data arriving to the in interface
            self.udt_receive()
            #terminate
            if(self.stop):
                print (threading.currentThread().getName() + ': Ending')
                return
        


## Implements a multi-interface router described in class
class Router:
    
    ##@param name: friendly router name for debugging
    # @param num_intf: number of bidirectional interfaces
    # @param rt_tbl_D: routing table dictionary (starting reachability), eg. {1: {1: 1}} # packet to host 1 through interface 1 for cost 1
    # @param max_queue_size: max queue length (passed to Interface)
    def __init__(self, name, num_intf, rt_tbl_D, max_queue_size):
        self.stop = False #for thread termination
        self.name = name
        #create a list of interfaces
        self.intf_L = []
        for i in range(num_intf):
            self.intf_L.append(Interface(max_queue_size))
        #set up the routing table for connected hosts
        self.rt_tbl_D = rt_tbl_D
        print(self.name)
        #print(self.rt_tbl_D)
        self.routerNum=4
        self.hostNum=3
        self.RoutingTable = self.setInitialData(self.rt_tbl_D,self.routerNum,self.hostNum,name) 
        #print(self.RoutingTable)
        
        
    ## called when printing the object
    def __str__(self):
        return 'Router_%s' % (self.name)
    def setInitialData(self,table1,routerNum,hostNum,name):
        
        #print(table1)
        table = [[-1 for x in range(hostNum)] for y in range(routerNum)] 
        #print(table)
        myIndex=self.checkIndex(name)
        i=1
        while i<=hostNum:
            #print(table1.get(i,"none"))
            #print(i)
            if(table1.get(i,"none")!="none"):
                #print(table1[i])
                j=0
                while j<2:
                    #print(table1[i].get(j,"none"))
                    if(table1[i].get(j,"none")!="none"):
                        table[myIndex][i-1]=table1[i].get(j,"none")
                        if(table[myIndex][i-1]>9):
                            table[myIndex][i-1]=int(table[myIndex][i-1]/10)
                    j+=1
            i+=1
        #print(table)
        return table
        
        #print(myIndex)
    ## look through the content of incoming interfaces and 
    # process data and control packets
    def checkIndex(self,c):
        if c=="A":
            return 0
        elif c=="B":
            return 1
        elif c=="C":
            return 2
        elif c=="D":
            return 3
        elif c=="E":
            return 4
    def checkName(self,c):
        if c=="A":
            return 0
        elif c=="B":
            return 1
        elif c=="C":
            return 2
        elif c=="D":
            return 3
        elif c=="E":
            return 4    
    def process_queues(self):
        for i in range(len(self.intf_L)):
            pkt_S = None
            #get packet from interface i
            pkt_S = self.intf_L[i].get('in')
            #if packet exists make a forwarding decision
            if pkt_S is not None:
                p = NetworkPacket.from_byte_S(pkt_S) #parse a packet out
                if p.prot_S == 'data':
                    self.forward_packet(p,i)
                elif p.prot_S == 'control':
                    self.update_routes(p, i)
                else:
                    raise Exception('%s: Unknown packet type in packet %s' % (self, p))
            
    ## forward the packet according to the routing table
    #  @param p Packet to forward
    #  @param i Incoming interface number for packet p
    def forward_packet(self, p, i):
        try:
            # TODO: Here you will need to implement a lookup into the 
            # forwarding table to find the appropriate outgoing interface
            # for now we assume the outgoing interface is (i+1)%2
            #self.intf_L[(i+1)%2].put(p.to_byte_S(), 'out', True)
            dst = p.dst_addr
            y=i
            i=1
            minInt=-1;
            minCost=10000
            while i<=self.hostNum:
                if(self.rt_tbl_D.get(i,"none")!="none" and i==dst):
                    j=0
                    while j<2:
                        if(self.rt_tbl_D[i].get(j,"none")!="none"):
                            x=self.rt_tbl_D[i].get(j,"none")
                            if(x>9):
                                temp=x%10
                                x=int(x/10)
                            if(x<minCost):
                                minCost=x
                                minInt=j
                        j+=1
                i+=1
            #print(minCost)
            #print(minInt)
            self.intf_L[minInt].put(p.to_byte_S(), 'out', True)            
                    
            #print(info)
            #table=info[3].split('[',',',']')
            #table=info[2].replace("[","")
            #table=table.replace("]","")
            print('%s: forwarding packet "%s" from interface %d to %d' % (self, p, y, minInt))
        except queue.Full:
            print('%s: packet "%s" lost on interface %d' % (self, p, i))
            pass
        
    ## forward the packet according to the routing table
    #  @param p Packet containing routing information
    def update_routes(self, p, i):
        #TODO: add logic to update the routing tables and
        # possibly send out routing updates
        print('%s: Received routing update %s from interface %d' % (self, p, i))
        
        info=str(p).split("#")
        #print(info)
        #table=info[3].split('[',',',']')
        table=info[2].replace("[","")
        table=table.replace("]","")
        #print(table)
        table1=table.split(",")
        table2 = [[-1 for x in range(self.hostNum)] for y in range(self.routerNum)]
        i=0
        j=0
        k=0
        #print(table1)
        #print(len(table1))
        while i< len(table1):
            if(k==self.hostNum):
                #print(table2[j])
                j+=1
                k=0
            #print(i)
            #print(k)
            table2[j][k]=int(table1[i])
            i+=1
            k+=1
        #print("HI")
        #print(table2)
        i=0
        while i<self.routerNum:
            j=0
            while j<self.hostNum:
                if(self.RoutingTable[i][j]==-1):
                    self.RoutingTable[i][j]=10000
                if(table2[i][j]==-1):
                    table2[i][j]=10000
                j+=1
            i+=1
        i=0
        flag=0
        while i<self.routerNum:
            j=0
            while j<self.hostNum:
                if(self.RoutingTable[i][j]>table2[i][j]):
                    self.RoutingTable[i][j]=table2[i][j]
                    flag=1
                j+=1
            i+=1
        i=0
        while i<self.routerNum:
            j=0
            while j<self.hostNum:
                if(self.RoutingTable[i][j]==10000):
                    self.RoutingTable[i][j]=-1
                j+=1
            i+=1
        print("New Updated ", end="")
        self.print_routes()
        if(flag==1):
            if(self.name=='A'):
                self.send_routes(1)
                #self.send_routes(1)
            elif(self.name=='B'):
                self.send_routes(0)
                self.send_routes(1)
            elif(self.name=='C'):
                self.send_routes(0)
                self.send_routes(1)
            elif(self.name=='D'):
                self.send_routes(0)
    ## send out route update
    # @param i Interface number on which to send out a routing update
    def send_routes(self, i):
        # a sample route update packet
        str1="#"+self.name+"#"+str(self.RoutingTable)
        p = NetworkPacket(0, 'control', str1)
        try:
            #TODO: add logic to send out a route update
            print('%s: sending routing update "%s" from interface %d' % (self, p, i))
            self.intf_L[i].put(p.to_byte_S(), 'out', True)
        except queue.Full:
            print('%s: packet "%s" lost on interface %d' % (self, p, i))
            pass
        
    ## Print routing table
    def print_routes(self):
        print('%s: routing table' % self)
        i=0
        print("   ",end="")
        while i<self.hostNum:
            print("%d " % (i+1),end="")
            i+=1
        print("")
        i=0
        while i<self.routerNum:
            j=0
            print("%s "%chr(i+65),end="")
            while j<self.hostNum:
                print("%d "%self.RoutingTable[i][j],end="")
                j+=1
            print("")
            i+=1
        print("\n")
        #print("String: ")
        #print(str(self.RoutingTable))
        #TODO: print the routes as a two dimensional table for easy inspection
        # Currently the function just prints the route table as a dictionary
        #print(self.rt_tbl_D)
    ## thread target for the host to keep forwarding data
    def run(self):
        print (threading.currentThread().getName() + ': Starting')
        while True:
            self.process_queues()
            if self.stop:
                print (threading.currentThread().getName() + ': Ending')
                return 