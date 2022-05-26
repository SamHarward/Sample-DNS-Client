import socket
import os

while True:
    target_IP = "8.8.8.8"
    port = 53
    hostname = input(">")
    if hostname == "exit":
        exit(0)

    # Get hostname from cmd line input, and optional DNS server target
    hostname = hostname.split()
    if len(hostname) > 3 or hostname[0] != "my-dns-client" or len(hostname) == 1:
        print("Format: my-dns-client <hostname> <DNS server; Default: 8.8.8.8>")
        continue
    if len(hostname) == 3:
        target_IP = hostname[2]
    hostname = hostname[1]

    print("Preparing DNS query...")
    # Generate 2 random bytes for ID
    ID = os.urandom(2)
    header = b'\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00'
    header = ID + header
    hostname = hostname.split('.')
    query = b''
    for name in hostname:
        length = len(name)
        if length > 255:
            print("Hostname is too long, try again")
            continue
        query += bytes([length])
        query += name.encode('utf-8')
    query += b'\x00'
    query += b'\x00\x01'
    query += b'\x00\x01'
    packet = header + query
    sock =  socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sent = 0
    print("Contacting DNS server...")
    done = False
    while (sent < 3):
        sent += 1
        print("Sending DNS query, attempt number " + str(sent))
        try:
            sock.sendto(packet, (target_IP, port))
            data = sock.recvfrom(1024)[0]
        except:
            if (sent > 2):
                done = True
            continue
        if (type(data) != type(b'/x00')):
            if (sent > 2):
                done = True
        print("DNS response received (attempt " + str(sent) + " of 3)")
        sent = 3
    if (done):
        continue
    response_id = str(hex(data[0])) + str(hex(data[1]))[2:]
    print("header.ID = " + response_id)
    response_QR = (data[2]>>7)&0x01
    print("header.QR = " + str(response_QR))
    response_OPCODE = (data[2]>>3)&0x07
    print("header.OPCODE = " + str(response_OPCODE))
    response_AA = (data[2]>>2)&0x01
    print("header.AA = " + str(response_AA))
    response_TC = (data[2]>>1)&0x01
    print("header.TC = " + str(response_TC))
    response_RD = data[2]&0x01
    print("header.RD = " + str(response_RD))
    response_RA = (data[3]>>7)&0x01
    print("header.RA = " + str(response_RA))
    response_Z = (data[3]>>4)&0x07
    print("header.Z = " + str(response_Z))
    response_RCODE = data[3]&0x0F
    print("header.RCODE = " + str(response_RCODE))
    response_QDCOUNT = data[4]*256 + data[5]
    print("header.QDCOUNT = " + str(response_QDCOUNT))
    response_ANCOUNT = data[6]*256 + data[7]
    print("header.ANCOUNT = " + str(response_ANCOUNT))
    response_NSCOUNT = data[8]*256 + data[9]
    print("header.NSCOUNT = " + str(response_NSCOUNT))
    response_ARCOUNT = data[10]*256 + data[11]
    print("header.ARCOUNT = " + str(response_ARCOUNT))
    dataindex = 12

    for i in range(response_QDCOUNT):
        qname = ""
        while(data[dataindex] != 0):
            size = data[dataindex]
            dataindex += 1
            word = data[dataindex:dataindex+size]
            qname += word.decode()
            qname += "."
            dataindex += size
        dataindex = dataindex + 1
        qname = qname[:-1]
        print("question" + str(i) + ".QNAME = " + qname)
        print("question" + str(i) + ".QTYPE = " +  str(data[dataindex]*256 + data[dataindex+1]))
        dataindex = dataindex + 2
        print("question" + str(i) + ".QCLASS = " + str(data[dataindex]*256 + data[dataindex+1]))
        dataindex = dataindex + 2

    for i in range(response_ANCOUNT):
        dataindex = dataindex + 2
        print("answer" + str(i) + ".NAME = " + qname)
        print("answer" + str(i) + ".TYPE = " + str(data[dataindex] * 256 + data[dataindex + 1]))
        dataindex = dataindex + 2
        print("answer" + str(i) + ".CLASS = " + str(data[dataindex] * 256 + data[dataindex + 1]))
        dataindex = dataindex + 2
        print("answer" + str(i) + ".TTL = " + str(data[dataindex] * 256 * 256 * 256 + data[dataindex + 1] * 256 * 256 + data[dataindex + 2] * 256 + data[dataindex + 3]))
        dataindex = dataindex + 4
        ardlength = data[dataindex] * 256 + data[dataindex + 1]
        print("answer" + str(i) + ".RDLENGTH = " + str(ardlength))
        dataindex = dataindex + 2
        rdata = ""
        print("answer" + str(i) + ".RDATA = " + str(data[dataindex]) + "." + str(data[dataindex+1]) + "." + str(data[dataindex+2]) + "." + str(data[dataindex+3]))