import os
import socket
import threading
import crc16
import time
import random
import string
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto import Random
import ast

def Main():
		port=4000;
		socket1=socket.socket(); 
		host='10.50.6.167'
		socket1.bind((host,port));
		socket1.listen(5);

		while True: 
			connection, address = socket1.accept();
			print "Host:<",socket.gethostname(),">is connedted to the host:<",address,">"
			t2 = threading.Thread(target=authenticate, args=('RetdThread',connection,address))
			t2.start() 
		socket1.close()
		
def generatet_key(publickey,random_string):
	print "random_string:",random_string
	publickey=RSA.importKey(publickey)
	encrypted_key = publickey.encrypt(random_string, 32)
	return encrypted_key

def generate_random_str():
	char_set = string.ascii_lowercase + string.ascii_uppercase + string.digits
	random_string=''.join(random.sample(char_set*16,16))
	return random_string

def dest_key(th,connection,destination,source,random_string):
	port=7000
	sock_Obj1=socket.socket()
	sock_Obj1.connect((destination,port))
	print "Sending key to destination"
	sock_Obj1.send("hkey");
	print "Receiving Public Key for destination server"
	publickey=sock_Obj1.recv(1024)
	key=generatet_key(publickey,random_string)
	print "Key Sent to destination"
	h_key=source+"::"+str(key)
	print "h_key",h_key
	sock_Obj1.send(h_key)
	sock_Obj1.close()

def source_key(th,connection,key):
	print "Sending key to source"
	connection.send(str(key));
	connection.close()
		
def authenticate(th,connection,address):
		source=address[0]
		destination=connection.recv(1024)
		mes=source+':'+destination
		print mes
		ip_address='10.50.6.167'
		port=3000
		sock_Obj=socket.socket()
		sock_Obj.connect((ip_address,port))
		sock_Obj.send(str(mes))
		x=sock_Obj.recv(1024)
		if(x[:2]=='Ok'):
			print "Resources ok"
			connection.send('Ok')
			publickey=connection.recv(1024)
			random_string=generate_random_str()
			key=generatet_key(publickey,random_string)
			print "Accepting Public key for source client"
			t3=threading.Thread(target=source_key,args=('RetdThread1',connection,key))
			t3.start()
			t4=threading.Thread(target=dest_key,args=('RetdThread2',connection,destination,source,random_string))
			t4.start()
					
Main()