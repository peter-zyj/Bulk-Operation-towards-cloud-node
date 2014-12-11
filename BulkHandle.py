#!/usr/bin/env python
import re
import os,sys
import time as yijun
import socket
import struct
import pexpect
import optparse
import logging
import threading


#UPD
########SSH logon stuff############
default_passwd = "rootroot"
prompt_firstlogin = "Are you sure you want to continue connecting \(yes/no\)\?"
prompt_passwd = "root@.*'s password:"
prompt_logined = "\[root@.*\]#"
prompt_percentage = ".*100%.*"



def SSHClient(logger,IP,cmd,name="root",passwd=default_passwd,prompt=prompt_logined,time=20):
	try:
		print ("****%s****" % (prompt))
		result = "***"
		ssh = pexpect.spawn('ssh %s@%s' % (name,IP))
		result = ssh.expect([prompt_firstlogin, prompt_passwd, prompt, pexpect.TIMEOUT, prompt_percentage],timeout=time)

		ssh.logfile = None
		if result == 0:
			ssh.sendline('yes')
			ssh.expect(prompt_passwd)
			ssh.sendline(passwd)
			ssh.expect(prompt)
			result = commandEmittor(logger,IP,ssh,cmd,prompt)
			connectClose(ssh)
		elif result == 1:
			ssh.sendline(passwd)
			ssh.expect(prompt)
			result = commandEmittor(logger,IP,ssh,cmd,prompt)
			connectClose(ssh)
		elif result == 2:
			#pass
			result = commandEmittor(logger,IP,ssh,cmd,prompt)
			connectClose(ssh)
		elif result == 3:
			result = "Connection::"+"ssh to %s timeout" %IP
		elif result == 4:
			pass
			return result
	except:
		# print ("result is ",result)
		print ('Mismatch BTW default expect or unexpected things happen!')
		debug = "Connection::"+ssh.before[:-1]
		print (debug)
		return (debug)
		#sys.exit(0)


def commandEmittor(logger,ip,ssh,cmd,prompt=prompt_logined):
	try:
		ssh.sendline(cmd)
		ssh.expect(prompt)
		content = "Executed::"+str(ssh.before[:-1])
		logger.debug(content)
		return content
	except:
		content = "Command::"+str(ssh.before[:-1])
		logger.debug(content)
		return content




def connectClose(ssh):
	ssh.close()


def action(ip,name,passwd,cmdlist,time=20):
	logger = logging.getLogger('Thread_%s' % (ip))
	logger.setLevel(logging.DEBUG)

	fileH = logging.FileHandler('log_%s' % (ip),'w')
	fileH.setLevel(logging.DEBUG)

	# create console handler and set level to debug
	ch = logging.StreamHandler()
	ch.setLevel(logging.DEBUG)

	# create formatter
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	fileH.setFormatter(formatter)
	# add formatter to ch
	ch.setFormatter(formatter)

	# add ch to logger
	logger.addHandler(fileH)
	logger.addHandler(ch)
	for i in cmdlist:
		if i != "":
			result = SSHClient(logger,ip,i,name,passwd,prompt_logined,time)










def execution(IPfile,CMDfile,time=20):
	ipf = open(IPfile,'r')
	clusterinfo = ipf.read()
	ipf.close()

	cmdf = open(CMDfile,'r')
	commandinfo = cmdf.read()
	cmdf.close()    

	listCluster = clusterinfo.split(os.linesep)
	listCommand = commandinfo.split(os.linesep)

	logging.debug(listCluster)
	logging.debug(listCommand)

	t = {}

	for i in range(len(listCluster)):
		if listCluster[i] != '':
			ip = listCluster[i].split(',')[1]
			name = listCluster[i].split(',')[2]
			passwd = listCluster[i].split(',')[3]

			t[i] = threading.Thread(name='Thread_%s' % (i), target=action, args=(ip,name,passwd,listCommand,time,))


	for i in range(len(listCluster)):
		#import time
		yijun.sleep(200)
		if listCluster[i] != '':
			t[i].start()







if __name__ == '__main__':
	usage ="""
example: %prog -f "clusterIP.txt" -c "command.txt" -l "log.log" [-t 600]
"""
	parser = optparse.OptionParser(usage)

	parser.add_option("-f", "--fileofaddr", dest="IPfile",
					  default='Null',action="store",
					  help="the Input IP address file specified by user")
	parser.add_option("-c", "--InpoutCommand", dest="CMDfile",
					  default='Null',action="store",
					  help="the Input Command file specified by user")
	parser.add_option("-l", "--InpoutLog", dest="LOGfile",
					  default='Null',action="store",
					  help="the Input Log file specified by user")
	parser.add_option("-t", "--InpoutPrompt,time", dest="time",
					  default='Null',action="store",
					  help="the Input time")

	(options, args) = parser.parse_args()

	argc = len(args)
	if argc != 0:
		parser.error("incorrect number of arguments")
		print (usage)
	else:
		if options.IPfile != "Null" and options.CMDfile != "Null":
			if options.LOGfile != "Null":
				logging.basicConfig(filename='%s' % (options.LOGfile), filemode='w',format='%(asctime)s:%(message)s',datefmt='%m/%d/%Y %I:%M:%S %p',level=logging.DEBUG)
				result = execution(options.IPfile, options.CMDfile, int(options.time))

		else:
			print (usage)

