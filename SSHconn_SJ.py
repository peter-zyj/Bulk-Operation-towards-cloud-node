#!/usr/bin/env python
import re
import os,sys
import time
import socket
import struct
import pexpect
import optparse

#UPD
########SSH logon stuff############
default_passwd = "rootroot"
prompt_firstlogin = "Are you sure you want to continue connecting \(yes/no\)\?"
prompt_passwd = "root@.*'s password:"
prompt_logined = "\[root@.*\]#"
prompt_percentage = ".*100%.*"



def SSHClient(IP,cmd,prompt=prompt_logined):
    try:
	print "****%s****" % (prompt)
	result = "***"
        ssh = pexpect.spawn('ssh root@%s' % IP)
        result = ssh.expect([prompt_firstlogin, prompt_passwd, prompt, pexpect.TIMEOUT, prompt_percentage],timeout=20)

        ssh.logfile = None
        if result == 0:
	    ssh.sendline('yes')
	    ssh.expect(prompt_passwd)
	    ssh.sendline(default_passwd)
	    ssh.expect(prompt)
	    result = commandEmittor(ssh,cmd,prompt)
	    connectClose(ssh)
        elif result == 1:
	    ssh.sendline(default_passwd)
	    ssh.expect(prompt)
	    result = commandEmittor(ssh,cmd,prompt)
	    connectClose(ssh)
        elif result == 2:
	    #pass
	    result = commandEmittor(ssh,cmd,prompt)
	    connectClose(ssh)
        elif result == 3:
	    result = "Connection::"+"ssh to %s timeout" %IP
	elif result == 4:
	    pass
        return result
    except:
 	print "result is ",result
        print 'Mismatch BTW default expect or unexpected things happen!'
        debug = "Connection::"+ssh.before[:-1]
	print debug
        return debug
        #sys.exit(0)


def commandEmittor(ssh,cmd,prompt=prompt_logined):
	try:
            ssh.sendline(cmd)
	    ssh.expect(prompt)
	    return "Executed::"+ssh.before[:-1]
	except:
	    return "Command::"+ssh.before[:-1]



def connectClose(ssh):
	ssh.close()





if __name__ == '__main__':
    usage ="""
example: %prog -i "10.10.10.10" -c "pwd" -p "root@cos470-2"
"""
    parser = optparse.OptionParser(usage)

    parser.add_option("-i", "--InputIP", dest="IP",
                      default='Null',action="store",
                      help="the Input IP address specified by user")
    parser.add_option("-c", "--InpoutCommand", dest="cmd",
                      default='Null',action="store",
                      help="the Input Command line specified by user")
    parser.add_option("-p", "--InpoutPrompt,mand", dest="prompt",
                      default='Null',action="store",
                      help="the Input Prompt specified by user")


    (options, args) = parser.parse_args()

    argc = len(args)
    if argc != 0:
        parser.error("incorrect number of arguments")
        print usage
    else:
        if options.IP != "Null" and options.cmd != "Null":
	    if options.prompt != "Null":
            	result = SSHClient(options.IP, options.cmd, options.prompt)
	    else:
		result = SSHClient(options.IP, options.cmd)
	    print re.sub('.*root@',':P=root@',result)
	else:
	    print usage

