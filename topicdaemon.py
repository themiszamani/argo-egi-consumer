#!/usr/bin/env python

import sys
import os
import time
import stomp
import logging
from daemon import Daemon
from topiclistener import TopicListener
from messagefilewritter import MessageFileWritter

# topis deamon defaults
defaultMsgServer = 'msg.cro-ngi.hr'
defaultMsgServerPort = 6163
defaultDaemonConfigFile = os.path.dirname(os.path.abspath(__file__)) + '/topicdaemon.conf' 
defaultDaemonPIDFile = os.path.dirname(os.path.abspath(__file__)) + '/topicdaemon.pid'
defaultDaemonStdIn = '/dev/null'
defaultDaemonStdOut = os.path.dirname(os.path.abspath(__file__)) + '/std.out'
defaultDaemonStdErr = os.path.dirname(os.path.abspath(__file__)) + '/std.err'
defaultDaemonName = 'topicdaemon'

defaultTopics = '/topic/grid.probe.metricOutput.EGEE.ngi.*'

defaultMessageWritterConfig = os.path.dirname(os.path.abspath(__file__)) + '/messagewritter.conf'

defaultDebugOutput = 0

class TopicDaemon(Daemon):
	def run(self):
		
		logging.basicConfig()
	
		#load config
		configFile = None
		configFields = dict()
		if os.path.isfile(defaultDaemonConfigFile):
			configFile = open(defaultDaemonConfigFile, 'r')
			lines = configFile.readlines()
		
			for line in lines:
				if line[0] == '#':
					continue
				splitLine = line.split('=')
            			if len(splitLine) > 1:
                			key = splitLine[0].strip()
                			value = splitLine[1].strip()
                                        value = value.decode('string_escape')
					if value[0] == "'":
						if value [-1] == "'":
							value = value[1:-1]
						else:
							continue
					elif value[0] == '"':
                                                if value [-1] == '"':
                                                        value = value[1:-1]
                                                else:
                                                        continue
                                        else:
                                            value = int(value)
                			configFields[key] = value

			configFile.close()

		# create listener
                listener = TopicListener()

		#apply config
		if 'topics' in configFields:
                	listener.topics = configFields['topics'].split(';')
            	else:
                	listener.topics = defaultTopics.split(';')
 
		if 'messageWritterConfig' in configFields:
                        messageWritterConfig = configFields['messageWritterConfig']
                else:
                        messageWritterConfig = defaultMessageWritterConfig
		
                # sys.stdout.write("Config fields:\n%r\n" % configFields)
                # sys.stdout.flush()

		# create stomp connection
		msgServer = defaultMsgServer
		if 'msgServer' in configFields:
                        msgServer = configFields['msgServer']
		msgServerPort = defaultMsgServerPort
		if 'msgServerPort' in configFields:
                        msgServerPort = int(configFields['msgServerPort'])
		messageWritterConfig = defaultMessageWritterConfig
		if 'messageWritterConfig' in configFields:
                        messageWritterConfig = configFields['messageWritterConfig']
		debugOutput = defaultDebugOutput
                if 'debugOutput' in configFields:
                        debugOutput = configFields['debugOutput']
		
		conn = stomp.Connection([(msgServer,msgServerPort)])

		# message writter
		msgWritter = MessageFileWritter()
		msgWritter.loadConfig(messageWritterConfig)
		listener.messageWritter = msgWritter

		# loop
		retryCount = 0
                listener.connectedCounter = 0
		listener.debugOutput = debugOutput
		while True:
			if not listener.connected:
				listener.connectedCounter -= 1
				if listener.connectedCounter <= 0:
					
					# start connection
					conn.set_listener('topiclistener', listener)
					try:
                				conn.start()
                				conn.connect()
						for topic in listener.topics: 			
							conn.subscribe(destination=topic, ack='auto')
						retryCount = 0
						listener.connectedCounter = 100
					except:
						retryCount += 1
						if retryCount < 10:
							listener.connectedCounter = retryCount * 10
						else:
							listener.connectedCounter = 100
			time.sleep(1)
		
		sys.stdout.write("%s ended\n" % self.name)
                sys.stdout.flush()

if __name__ == "__main__":
	daemon = TopicDaemon(defaultDaemonPIDFile, defaultDaemonStdIn, defaultDaemonStdOut, defaultDaemonStdErr, defaultDaemonName)
	if len(sys.argv) == 2:
		if 'start' == sys.argv[1]:
			daemon.start()
		elif 'stop' == sys.argv[1]:
			daemon.stop()
		elif 'restart' == sys.argv[1]:
			daemon.restart()
		elif 'status' == sys.argv[1]:
                        daemon.status()
		else:
			print "Unknown command"
			sys.exit(2)
		sys.exit(0)
	else:
		print "usage: %s start|stop|restart|status" % sys.argv[0]
		sys.exit(2)
