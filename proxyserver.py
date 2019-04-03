from __future__ import print_function
import socket
import threading
from thread import allocate_lock
import time
titleCache=['12','13','14']
fileCache=["file1","file2","file3"]
lockCache = allocate_lock()
def handleclient(conn,addr):
    #print("proxy ready")
    flag=0
    request = conn.recv(1024)
    if(len(request)>0 and request.split(' ')[0]=="GET" and ("localhost" in request or "127.0.0.1" in request)):
        first_line = request.split('\n')[0]
        print(first_line)
        # get url
        url = first_line.split(' ')[1]


        http_pos = url.find("://") # find pos of ://
        if (http_pos==-1):
            temp = url
        else:
            temp = url[(http_pos+3):] # get the rest of url

        port_pos = temp.find(":") # find the port pos (if any)

        # find end of web server
        webserver_pos = temp.find("/")

        if webserver_pos == -1:
            webserver_pos = len(temp)

        webserver = ""
        port = -1
        if (port_pos==-1 or webserver_pos < port_pos):

            # default port
            port = 80
            webserver = temp[:webserver_pos]

        else: # specific port
            port = int(  (temp[(port_pos+1):])     [:webserver_pos-port_pos-1])
            webserver = temp[:port_pos]
            print("webserver is"+webserver)

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((webserver, port))
        print(request)
        frsp_pos=request.find(' ')
        thsl_pos=0
        thsl_pos=request.find('://')+3
        thsl_pos+=request[thsl_pos:].find("/")
        request=request[:frsp_pos+1]+request[thsl_pos:]
        filename=request.split(' ')[1][1:]
    #    print("filename is "+filename)
        if filename in titleCache:
             #send the cached file
            print("present in cache")
            lockCache.acquire()
            fileCache.append(fileCache[titleCache.index(filename)])
            del fileCache[titleCache.index(filename)]
            del titleCache[titleCache.index(filename)]
            titleCache.append(filename)
            lockCache.release()
            #print(fileCache[titleCache.index(filename)])
            f = open(fileCache[titleCache.index(filename)],'r')
            l = f.read(1024)
            l=l.split('\n')[5]
            col_pos=l.find(':')
            ff=request.split('\n')
            kk='If-Modified-Since:'+l[col_pos+1:]
            ff.insert(1,kk)
            request='\n'.join(ff)
            # print(l[col_pos+1:])
            # print(request)
            f.close()
            s.send(request)
            data1=''
            while 1:
                # receive data from web server
                try:
                    #print("entered"  )
                    data = s.recv(4096)
                    if (len(data) > 0):
                        data1 += data
                        if "304" in data or "200" in data:
                            break
                        #conn.send(data) # send to browser/client
                    else:
                        break
                except: pass
            #do this if not modified
            #print(data1)
            if "304" in data1:
                print("Not modified")
                f = open(fileCache[titleCache.index(filename)],'r')
                #print("filename is " +fileCache[titleCache.index(filename)])
                l = f.read(1024)
                while (l):
                    conn.send(l)
                    #print('Sent ',repr(l))
                    l = f.read(1024)
                f.close()
            else:
                print("modified")
                filen=open(fileCache[titleCache.index(filename)],'wb')
                #print("filename is " +fileCache[titleCache.index(filename)])
                filen.write(data1)
                conn.send(data1)
                while 1:
                    # receive data from we b serve r
                    try:
                        #print("entered")
                        data = s.recv(1024)
                        if (len(data) > 0):
                            filen.write(data)
                            conn.send(data) # send to browser/client
                        else:
                            break
                    except: pass
                filen.close()
                #then file is  mo dified
        else:
            s.sendall(request)
            #s.sendall(request[:len(request)-2]+"If-Modified-Since: Wed, 14 Feb 2018 11:55:21 GMT\r\n\r\n")
            #del titleCache[0] append filename in titleCache
            #append fileCache[0] in fileCache del fileCache[0]
            data1=''
            flag=0
            while 1:
                # receive data from web server
                try:
                    #print("entered")
                    data = s.recv(4096)
                    if (len(data) > 0):
                        data1 += data
                        if "404" in data1 or 'no-cache' in data1:
                            flag=1
                        conn.send(data) # send to browser/client
                    else:
                        break
                except: pass
            print(data1)
            if flag==0:
                lockCache.acquire()
                if len(titleCache)==3:
                    fileCache.append(fileCache[0])
                    del fileCache[0]
                    del titleCache[0]
                titleCache.append(filename)
                lockCache.release()
                filen=open(fileCache[titleCache.index(filename)],'wb')
                #print("filename is " +fileCache[titleCache.index(filename)])
                filen.write(data1)
                while 1:
                    # receive data from web server
                    try:
                        #print("entered")
                        data = s.recv(4096)
                        if (len(data) > 0):
                            data1 += data
                            filen.write(data)
                            conn.send(data) # send to browser/client
                        else:
                            break
                    except: pass
                #print  (data1)
        s.close()
        conn.close()


port = 12345
b = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "127.0.0.1"
b.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
b.bind((host, port))
b.listen(5)

while True:
    conn, addr = b.accept()
    #print("accepted")
    #handleclient(conn,addr)
    thre = threading.Thread(target=handleclient , args=(conn,addr))
    thre.start()
    #conn.close()
