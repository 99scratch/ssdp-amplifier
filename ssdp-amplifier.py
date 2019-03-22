	

    from scapy.all import *
    from struct import *
    import sys
    import socket
    import time
    import threading
    import random
    from threading import Thread
     
     
    ########################
    #Remember the SSDP scanner keeps all packets received, so make sure you sort them example command:
     
    #Notice: THIS HAS ONLY BEEN TESTED ON A DEDICATED SERVER VPS's MAY NOT WORK.
     
     
    #Here is a small list of commands that can help you sort your list:
     
    #This command removes the length of the responce and puts the output in line-by-line list format:
    #cat scannedlist.txt | awk '{print $1}' | sort -u | sort -R > output.txt
     
    #This next command sorts for all packets over 300 byte reply size and saves the output to a list:
    #cat scannedlist.txt | awk '$2 > 300' | awk 'print $1' | sort -u | sort -R > output.txt
     
    #This next command sorts for all reflectors that replyed with 10 or more packets (this is my favorite):
    #cat scannedlist.txt | sort | uniq -c | awk '$2 > 10' | awk 'print $2' | sort -u | sort -R > output.txt
    ########################
     
    if len (sys.argv) != 4:
            print "Usage: ./" + sys.argv[0] + " [ip-start] [ip-end] [output]\n      Notice: This script requires Scapy (available with apt-get or yum installs\n    Notice: THIS HAS ONLY BEEN TESTED ON A DEDICATED SERVER VPS's MAY NOT WORK.\n   V.1.0 Made by XXX"
            sys.exit()
     
    mydestport = random.randint(400,65535)
    conf.verb = 0
    data = "M-SEARCH * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\nMAN: \"ssdp:discover\"\r\nMX: 2\r\nST: ssdp:all\r\n\r\n"
    recv = 0
     
     
    def eth_addr (a) :
      b = "%.2x:%.2x:%.2x:%.2x:%.2x:%.2x" % (ord(a[0]) , ord(a[1]) , ord(a[2]), ord(a[3]), ord(a[4]) , ord(a[5]))
      return b
     
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.connect(('google.com', 80))
    myhost = sock.getsockname()[0]
    sock.close()
     
           
    def ipRange(start_ip, end_ip):
       start = list(map(int, start_ip.split(".")))
       end = list(map(int, end_ip.split(".")))
       temp = start
       ip_range = []
       
       ip_range.append(start_ip)
       while temp != end:
          start[3] += 1
          for i in (3, 2, 1):
             if temp[i] == 256:
                temp[i] = 0
                temp[i-1] += 1
          ip_range.append(".".join(map(str, temp)))
     
       return ip_range
     
    ip_range = ipRange(sys.argv[1], sys.argv[2])
     
    def startscan():
            total = 0      
            for server in ip_range:
                   
                    sys.stdout.write("\rSent %d Packets | Received %d Packets" % (total, recv))
                    sys.stdout.flush()     
                    packet = IP(dst=server)/UDP(sport=mydestport,dport=1900)/Raw(load=data)
                    send(packet)
                    total = total + 1
     
    def listen():
            global recv
            try:
                s = socket.socket( socket.AF_PACKET , socket.SOCK_RAW , socket.ntohs(0x0003))
            except socket.error , msg:
                sys.exit()
     
     
            while True:
                packet = s.recvfrom(65565)
         
     
                packet = packet[0]
         
                eth_length = 14
         
                eth_header = packet[:eth_length]
                eth = unpack('!6s6sH' , eth_header)
                eth_protocol = socket.ntohs(eth[2])
     
                if eth_protocol == 8 :
                    ip_header = packet[eth_length:20+eth_length]
                     
                    iph = unpack('!BBHHHBBH4s4s' , ip_header)
     
                    version_ihl = iph[0]
                    version = version_ihl >> 4
                    ihl = version_ihl & 0xF
     
                    iph_length = ihl * 4
     
                    ttl = iph[5]
                    protocol = iph[6]
                    s_addr = socket.inet_ntoa(iph[8]);
                    d_addr = socket.inet_ntoa(iph[9]);
     
     
                    if protocol == 17 :
                        u = iph_length + eth_length
                        udph_length = 8
                        udp_header = packet[u:u+8]
     
                        udph = unpack('!HHHH' , udp_header)
                 
                        source_port = udph[0]
                        dest_port = udph[1]
                        length = udph[2]
                        checksum = udph[3]
                 
                        if dest_port == mydestport :
                            if d_addr == myhost :
     
                                    list = open(sys.argv[3], 'a')
                                    list.write("%s %d\n" % (s_addr, length))
                                    recv = recv + 1
     
                        h_size = eth_length + iph_length + udph_length
                        data_size = len(packet) - h_size
                 
                        data = packet[h_size:]
     
    if __name__ == '__main__':
        Thread(target = startscan).start()
        Thread(target = listen).start()



