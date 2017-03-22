import os
import socket
import threading
import crc16
import time
import MySQLdb
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto import Random
import ast
import random

def database_conn():
	db = MySQLdb.connect("localhost","root","spartan","cn" )
	cursor = db.cursor()
	return cursor,db

def generatet_public_key():
	random_generator = Random.new().read
	key = RSA.generate(1024, random_generator) 
	return key

def decrypt_using_private_key(key,h_key):
	decrypted_key = key.decrypt(ast.literal_eval(str(h_key)))
	return decrypted_key


def receive_File():
	print "Enter 'Y/y' for receiving file:"
	user_Response=raw_input(" ")
	if user_Response[:]=='Y' or user_Response[:]=='y':       
		print "Please enter the host name:"
		host_Name=raw_input()
		cursor,db=database_conn()
		sql = "SELECT name,address,port FROM ip_address where name='%s'" % host_Name
		print sql
		try:
			# Execute the SQL command
			cursor.execute(sql)
			# Fetch all the rows in a list of lists.
			count = cursor.rowcount
			if(count==1 ):
				results = cursor.fetchall()
				for row in results:
					name = row[0]
					address = row[1]
					port = row[2]
					# Now print fetched result
					print "name=%s,address=%s,port=%d" % \
					(name, address, port)
					#print "hello1"
					sock_Obj=socket.socket()
					sock_Obj.connect((address,port))
					#print "hello2"
					th = threading.Thread(target=download, args=("RetdThread",sock_Obj,address))
					#print "hello3"
					th.start()
					#print "hello4"					
					break
			else:
				db.close()
				print "IP address not found."
				receive_File()
	
		except:
			db.close()
			print "Error: unable to fetch data"
			receive_File()
	else:
		
		receive_File()
	


def fetch_key(address):
	cursor,db=database_conn()
	sql = "SELECT hash_k FROM hash_key where address='%s'" % address
	print sql
	hash_key=''
	try:
		
		cursor.execute(sql)
		
		count = cursor.rowcount
		if(count>0 ):
			results = cursor.fetchall()
			for row in results:
				hash_key = row[0]
		
				print "hash_key=%s" % \
				(hash_key)
				break;
	except:
		db.close()
		print "Error: unable to fetch hash_key data"
	db.close()
	return hash_key



def delete_key(address):
	cursor,db=database_conn()
	sql = "delete from hash_key where address='%s'" % address
	print sql
	hash_key=''
	try:
		
		cursor.execute(sql)
		db.commit()
		
	except:
		db.close()
		print "Error: unable to fetch hash_key data"
		return False
	db.close()
	return True



def download(t,sock,address):
	print "downloading file"
	sock.send("File")
	a=sock.recv(1024)
	print "downloading started"
	#print "Number of files:",a
	a=long(a)
	a1 =a #test53
	while a1>0:
		sock.send("OK")
		data=sock.recv(1024);
		x=data
		print "Receiving file:",x
		x1=map(str,data.split(':'))
		file_name=x1[0]
		file_Size=x1[1]
		filename_size_CRC=x1[2]
		filename_Size=''.join(file_name)
		filename_Size=filename_Size+':'+file_Size
		ycname=crc16.crc16xmodem(filename_Size)
		
		print 'Calculated CRC:',str(ycname)
		print 'Received CRC:',filename_size_CRC
		if str(ycname)==filename_size_CRC: 
			sock.send("nmcrc")
			start_time=time.clock()
			print("downloading data ...");
			print os.path.splitext(file_name)[0]
			print file_name
			if not os.path.exists(os.path.splitext(file_name)[0]):os.makedirs(os.path.splitext(file_name)[0])
			savedPath = os.getcwd()
			os.chdir(os.path.splitext(file_name)[0])
			file_name='encrypted_'+file_name
			f = open(file_name, 'wb')
			
			recievd=0
			while recievd < int(file_Size):
				data=sock.recv(1024);
				o=data
				length=len(o)
				#print "length:",length
				received_CRC=''
				received_Data=''
				for i in range(length-5,length):
					received_CRC=received_CRC+o[i]
				for i in range(0,length-5):
					received_Data=received_Data+o[i]	
				ycdata=crc16.crc16xmodem(received_Data)
				ycdata=str(ycdata)
				#print "Received CRC Packets:",received_CRC
				#print "Calculated CRC Packet:-",ycdata
				if(len(ycdata)<5):
					for i in range(5-len(ycdata)):
						ycdata='0'+ycdata
				if str(ycdata)==received_CRC: 
					sock.send("crc");
					recievd=recievd+len(received_Data);
					f.write(received_Data);
					
					#print "Transfered"
				else:
					print 'Filedata packet is currupted for filr',file_name; 
					break
			f.close()
			
			end_time=time.clock()
			print 'end_time',end_time
			print 'start_time',start_time
			w=end_time-float(start_time)
			print'file transfer time ',w,'s';
			hash_k=fetch_key(address)
			#print "AES key:",hash_k
			#hash_k=escape_character(hash_k)
			print "AES key:",hash_k
			if(hash_k==''):
				print 'No hash key available to decrypt.'
			else:
				file_decryption(hash_k,file_name,file_Size)
			
		else: 
			print 'File Information packet is currupted for filr',file_name; #CRC
		os.chdir(savedPath);
		#w=s-e;
		#print "File Transfer time:",w,"ms";
		#s1.close();
		a1-=1
		print "Number of files remaining",a1
		# if a1 == 0:
			# a1 = a
			# print"--------------------------------------------"
			# print "Files are again getting updated"
	status=delete_key(address)
	if(status==True):
		print "Key successfully deleted from database."
	else:
		"Unable to delete key entries from database. Please delete them manually."
	sock.close()
	receive_File()     		

def Main():
	port=6000;
	socket1=socket.socket(); 
	host='10.50.6.167'
	socket1.bind((host,port));
	#socket1.bind((socket.gethostbyname(socket.getfqdn()),port));
	socket1.listen(5);
	t1 = threading.Thread(target=receive_File)
	t1.start()
	while True: 
		connection, address = socket1.accept();
		print "Host:<",socket.gethostname(),">is connedted to the host:<",address,">"
		t2 = threading.Thread(target=send, args=('RetdThread',connection,address))
		t2.start() 
	socket1.close() 

def file_encryption(hash_key, filename , destination, filesize ):
	chunk_size = 64*1024
	encrypted_file = destination+'_'+filename
	filesize = str(filesize).zfill(16)
	IV = ''

	for i in range(16):
		IV += chr(random.randint(0, 0xFF))
	encryptor = AES.new(hash_key, AES.MODE_CBC, IV)
	with open(filename, 'rb') as infile:
		with open(encrypted_file, 'wb') as outfile:
			outfile.write(IV)
			while True:
				chunk = infile.read(chunk_size)
				if len(chunk) == 0:
					break
				elif len(chunk) % 16 != 0:
					chunk += ' ' * (16 - (len(chunk) % 16))
				outfile.write(encryptor.encrypt(chunk))
	return encrypted_file

def file_decryption(key, filename,filesize):
	chunksize = 64*1024
	decrypted_file = filename[10:]
	
	with open(filename, 'rb') as infile:
		IV = infile.read(16)
		decryptor = AES.new(key, AES.MODE_CBC, IV)
		with open(decrypted_file, 'wb') as outfile:
			while True:
				chunk = infile.read(chunksize)
				if len(chunk) == 0:
					break
				outfile.write(decryptor.decrypt(chunk))
			outfile.truncate(int(filesize))
	print "File %s Decrypted Successfully:"% decrypted_file
				
def send(th,connection,address):
	#print "Please enter the directory:"
	#directory=raw_input("")
	#print directory
	
	type=connection.recv(1024)
	if(type[:4]=="File"):
		print "File download request received"
		ip_address='10.50.6.167'
		port=4000
		sock_Obj=socket.socket()
		sock_Obj.connect((ip_address,port))
		print "Checking validity with Authentication Server"
		sock_Obj.send(address[0])
		#connection.send(address)
		as_response=sock_Obj.recv(1024)
		if as_response[:2]=='Ok':
			print "Valid Client"
			print "Connction OK"
			key=generatet_public_key()
			sock_Obj.send(key.publickey().exportKey())
			h_key=sock_Obj.recv(1024)
			print "key received:"
			key=decrypt_using_private_key(key,h_key)
			print key;
			savedPath=''
			directory='C:/Users/hp-pc/Desktop/ontology/'
			files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory,f))]
			count=len(files)	
			connection.send(str(count))
			#for file in files:
			k=0
			while k<len(files):
				# if(k==len(files)):
					# time.sleep(10); #test53
					# #if(raw_input()=='stop'):
					# #	break
					# k=0
				file=files[k]
				uresp=connection.recv(1024)
				if uresp[:2] == 'OK':
					print "Sending File-",directory+file; 
					file_Name=directory+file
					size=os.path.getsize(file_Name);
					print size
					savedPath = os.getcwd()
					os.chdir(directory)
					#Encrypted file name
					file_Name=directory+file_encryption(key,file,address[0],size)
					filename_Size=''.join(file)
					filename_Size=filename_Size+':'+str(size)
					filename_Size_CRC=crc16.crc16xmodem(filename_Size) 
					filename_Size=filename_Size+':'+str(filename_Size_CRC)
					connection.send(filename_Size);
					uresp = connection.recv(1024)
					if uresp[:5] == 'nmcrc': 
						with open(file_Name, 'rb') as f:
							byte = f.read(1019);
							while byte != "":
								print "length:",len(byte)
								ybyte=crc16.crc16xmodem(byte)
								ybyte=str(ybyte)
								print "CRC:",ybyte
								if(len(ybyte)<5):
									for i in range(5-len(ybyte)):
										ybyte='0'+ybyte
								print "CRC:",ybyte
								byte=byte+ybyte
								print "length:",len(byte)
						
								connection.send(byte);
								uresp=connection.recv(1024)
								#print "last response"
								if uresp[:3] == 'crc':
									print "in CRC"
									byte = f.read(1019);
									print "length in CRC:",len(byte)
					
					os.remove(file_Name)
					time.sleep(5);
				k=k+1
			#connection.close()
			os.chdir(savedPath)
		else:
			print "Resources are not ok"
			#connection.close()
	elif(type[:4]=="hkey"):
		key=generatet_public_key()
		connection.send(key.publickey().exportKey())
		h_key=connection.recv(1024)
		#print "h_key",h_key
		x1=map(str,h_key.split('::'))
		#print x1[0]
		#print x1[1]
		h_key=decrypt_using_private_key(key,x1[1])
		print "h_key",h_key
		cursor,db=database_conn()
		sql="select * from ip_address where address='%s'" % x1[0]
		cursor.execute(sql)
		count=cursor.rowcount
		if(count>0):
			sql = "insert into hash_key(address,hash_k)\
			VALUES ('%s','%s')" % \
			(x1[0],h_key)
			#print "sql",sql
			try:
				cursor.execute(sql)
				db.commit()
				print "Commit done."
			except:
				db.rollback()
		else:
			print "Wrong hash key received"
		#connection.close()

Main()