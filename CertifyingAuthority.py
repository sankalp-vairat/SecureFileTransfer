import os
import socket
import threading
import crc16
import time
import MySQLdb

def Main():
	port=3000;
	socket1=socket.socket(); 
	host='10.50.6.167'
	socket1.bind((host,port));
	socket1.listen(1024);
	while True: 
		connection, address = socket1.accept();
		print "Host:<",socket.gethostname(),">is connedted to the host:<",str(address),">"
		t2 = threading.Thread(target=authenticate, args=('RetdThread',connection,address))
		t2.start() 
	socket1.close()

def db_check(ip_address):
	print ip_address
	db = MySQLdb.connect("localhost","root","spartan","ca" )
	cursor = db.cursor()
	sql="select * from ip_address where address='%s' and authorize='Y'" % ip_address;
	print sql
	cursor.execute(sql)
	count=cursor.rowcount
	if(count>0):
		return True
	else:
		return False
	
	
def authenticate(th,connection,address):
	mes=connection.recv(1024)
	print mes
	x1=map(str,mes.split(':'))
	print x1
	source=x1[0]
	destination=x1[1]
	status=db_check(source)
	if(status==True):
		status=db_check(destination)
		if(status==True):
			status=db_check(address[0])
			if(status==True):
				print "All resources are ok"
				connection.send('Ok')
			else:
				print "Not a valid AS"
				connection.send("NOK")
		else:
			print "Not a valid destination"
			connection.send("NOK")
	else:
		print "Not a valid source"
		connection.send("NOK")

	connection.close()

Main()