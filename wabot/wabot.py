#!/usr/local/bin/python
# -*- coding: utf-8 -*-

'''
Copyright (c) <2012> Tarek Galal <tare2.galal@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this 
software and associated documentation files (the "Software"), to deal in the Software 
without restriction, including without limitation the rights to use, copy, modify, 
merge, publish, distribute, sublicense, and/or sell copies of the Software, and to 
permit persons to whom the Software is furnished to do so, subject to the following 
conditions:

The above copyright notice and this permission notice shall be included in all 
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR 
A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT 
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF 
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE 
OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import os
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir)
import datetime, sys
import socket
import time
import signal
import json

if sys.version_info >= (3, 0):
	raw_input = input

from Yowsup.connectionmanager import YowsupConnectionManager

class WhatsappListenerClient:

	def __init__(self, keepAlive = False, sendReceipts = False):
		self.sendReceipts = sendReceipts
		
		connectionManager = YowsupConnectionManager()
		connectionManager.setAutoPong(keepAlive)

		self.signalsInterface = connectionManager.getSignalsInterface()
		self.methodsInterface = connectionManager.getMethodsInterface()
		
		self.signalsInterface.registerListener("message_received", self.onMessageReceived)
		self.signalsInterface.registerListener("auth_success", self.onAuthSuccess)
		self.signalsInterface.registerListener("auth_fail", self.onAuthFailed)
		self.signalsInterface.registerListener("disconnected", self.onDisconnected)
		self.signalsInterface.registerListener("group_messageReceived", self.onGroupMessageReceived)
		self.signalsInterface.registerListener("group_imageReceived", self.onGroupImageReceived)
		self.signalsInterface.registerListener("group_gotParticipants", self.onParticipantsReceived)		

		self.cm = connectionManager

		#Set up irc connection
		self.network = 'irc.saunalahti.fi'
		self.port = 6667
		self.irc = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
	
	def login(self, username, password):
		self.username = username
		self.password = password
		self.methodsInterface.call("auth_login", (username, password))
		self.methodsInterface.call("presence_sendAvailableForChat", ("wabot",))
		self.methodsInterface.call("group_getParticipants", ("358412301234-1327669678@g.us",))

		#signal.signal(signal.SIGINT, self.handler)

		#Start irc connection with bot and join the channel
		self.irc.connect( ( self.network, self.port) )
		print self.irc.recv ( 4096 )
		self.irc.send ( 'NICK wabot\r\n' )
		self.irc.send ( 'USER botty botty botty :Python IRC\r\n' )
		self.irc.send ( 'JOIN #channel password\r\n' )		

		while True:
			data = self.irc.recv ( 4096 )
			if data.find ( 'PING' ) != -1:
				self.irc.send ( 'PONG ' + data.split() [ 1 ] + '\r\n' )
				#print "PINGPONG"
			if data.find(":!wabot") != -1:		
				self.sendMessageToGroup(data, ":!wabot")
			#print data

	def onAuthSuccess(self, username):
		print("Authed %s" % username)
		self.methodsInterface.call("ready")

	def onAuthFailed(self, username, err):
		print("Auth Failed!")
		self.irc.send("PRIVMSG #channel :Nick: Auth Failed: " + err + "\r\n")

	def onDisconnected(self, reason):
		print("Disconnected because %s" %reason)
		#f = open('dict', 'w')
		#json.dump(self.dict, f)
		#f.close()
		print ("Trying to reconnect")
		self.methodsInterface.call("auth_login", (self.username, self.password))		
	
	def onParticipantsReceived(self, jid, participants):
		print participants


	def onMessageReceived(self, messageId, jid, messageContent, timestamp, wantsReceipt, pushName, isBroadCast):
		formattedDate = datetime.datetime.fromtimestamp(timestamp).strftime('%d-%m-%Y %H:%M')
		print("%s [%s]:%s"%(jid, formattedDate, messageContent))

		if wantsReceipt and self.sendReceipts:
			self.methodsInterface.call("message_ack", (jid, messageId))
	
	#int messageId, str jid, str author, str messageContent, long timestamp, bool wantsReceipt, str pushName
	def onGroupMessageReceived(self, messageId, jid, author, messageContent, timestamp, wantsReceipt, pushName):
		formattedDate = datetime.datetime.fromtimestamp(timestamp).strftime('%d-%m-%Y %H:%M')
		#print ("MessageID: " , messageId , ", JID: " , jid , ", AUTHOR: " , author , ", Content: " , messageContent , ", TIME: " , formattedDate , ", Receipt: " , wantsReceipt , ", pushName: " , pushName)

		timenow = int(time.time())
		
		#Check if "new" message and sent receipt
		if ( (timenow - timestamp)/60 > 5):
			if wantsReceipt and self.sendReceipts:
                self.methodsInterface.call("message_ack", (jid, messageId))
			return

		#Send message to irc channels according to whatsapp group jid
		if (jid == "358555123650-1404802946@g.us"):
			data = "PRIVMSG #testchannel :<" + pushName + "> " + messageContent + "\r\n"
		elif (jid == "358412301234-1327669678@g.us"):
			data = "PRIVMSG #channel :<" + pushName + "> " + messageContent + "\r\n"

		print data
		self.irc.send(data)

		if wantsReceipt and self.sendReceipts:
			self.methodsInterface.call("message_ack", (jid, messageId))

	#int messageId,str jid,str author,str preview,str url,int size,bool receiptRequested
	def onGroupImageReceived(self, messageId, jid, author, preview, url, size, receiptRequested):
		
		sender = ""
		#if author in self.dict:
		#	print "Found"
		#	sender = self.dict[author]

		if (jid == "358555123650-1404802946@g.us"):
                        data = "PRIVMSG #testchannel :Kuva "+ sender+ ": " + url + "\r\n"
                elif (jid == "358412301234-1327669678@g.us"):
                        data = "PRIVMSG #channel :Kuva " + sender + ": " + url + "\r\n"

		self.irc.send(data)

		if receiptRequested and self.sendReceipts:
				self.methodsInterface.call("message_ack", (jid, messageId))

	#Send messages from irc to whatsapp
	def sendMessageToGroup(self, data, splitter):
		nick = data.split("!")[0]
		
		if data.find("#testchannel :") != -1:
			jid = "358555123650-1404802946@g.us"
		elif data.find("#channel :") != -1:
			jid = "358412301234-1327669678@g.us"

		message = nick[1::] + ": " + data.rsplit(splitter,1)[1]
		
		self.methodsInterface.call("message_send", (jid, message))
		print "Sent following message to whatsapp"
		print message, jid
	
