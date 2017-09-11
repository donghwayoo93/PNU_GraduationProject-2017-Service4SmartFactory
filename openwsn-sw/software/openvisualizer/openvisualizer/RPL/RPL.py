# Copyright (c) 2010-2013, Regents of the University of California. 
# All rights reserved. 
#  
# Released under the BSD 3-Clause license as published at the link below.
# https://openwsn.atlassian.net/wiki/display/OW/License
'''
Module which coordinates RPL DIO and DAO messages.

.. moduleauthor:: Xavi Vilajosana <xvilajosana@eecs.berkeley.edu>
                  January 2013
.. moduleauthor:: Thomas Watteyne <watteyne@eecs.berkeley.edu>
                  April 2013
'''
import logging
log = logging.getLogger('RPL')
log.setLevel(logging.ERROR)
log.addHandler(logging.NullHandler())

import threading
import struct
from datetime import datetime

from pydispatch import dispatcher

from openvisualizer.eventBus import eventBusClient
import SourceRoute
import openvisualizer.openvisualizer_utils as u

import socket
import json
import RPL_MASK as MASK

class RPL(eventBusClient.eventBusClient):
    
    _TARGET_INFORMATION_TYPE           = 0x05
    _TRANSIT_INFORMATION_TYPE          = 0x06
    
    # Period between successive DIOs, in seconds.
    DIO_PERIOD                         = 10
    
    ALL_RPL_NODES_MULTICAST            = [0xff,0x02]+[0x00]*13+[0x1a]
    
    # http://www.iana.org/assignments/protocol-numbers/protocol-numbers.xml 
    IANA_ICMPv6_RPL_TYPE               = 155
    
    # RPL DIO (RFC6550)
    DIO_OPT_GROUNDED                   = 1<<7 # Grounded
    # Non-Storing Mode of Operation (1)
    MOP_DIO_A                          = 0<<5
    MOP_DIO_B                          = 0<<4
    MOP_DIO_C                          = 1<<3
    # most preferred (7) as I am DAGRoot
    PRF_DIO_A                          = 1<<2
    PRF_DIO_B                          = 1<<1
    PRF_DIO_C                          = 1<<0

    # IPC Socket RPL.py <-> test_server_json.py
    IPC_HOST                           = 'localhost'
    IPC_PORT                           = 25800
    IPC_SOCKET                         = ''

    # leaf movement check
    CURRENT_PARENT_ADDR                = ''
    FORMER_PARENT_ADDR                 = ''
    
    def __init__(self):
        
        # log
        log.info("create instance")
        
        # store params
        
        # initialize parent class
        eventBusClient.eventBusClient.__init__(
            self,
            name                  = 'RPL',
            registrations         =  [
                {
                    'sender'      : self.WILDCARD,
                    'signal'      : 'networkPrefix',
                    'callback'    : self._networkPrefix_notif,
                },
                {
                    'sender'      : self.WILDCARD,
                    'signal'      : 'infoDagRoot',
                    'callback'    : self._infoDagRoot_notif,
                },
                {
                    'sender'      : self.WILDCARD,
                    'signal'      : 'getSourceRoute',
                    'callback'    : self._getSourceRoute_notif,
                },
            ]
        )
        
        # local variables
        self.stateLock            = threading.Lock()
        self.state                = {}
        self.networkPrefix        = None
        self.dagRootEui64         = None
        self.sourceRoute          = SourceRoute.SourceRoute()
        self.latencyStats         = {}

        # IPC Socket Create
        self.IPC_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    #======================== public ==========================================
    
    def close(self):
        # nothing to do
        self.IPC_SOCKET.close()
        pass
    
    #======================== private =========================================
    
    #==== handle EventBus notifications
    
    def _networkPrefix_notif(self,sender,signal,data):
        '''
        Record the network prefix.
        '''
        # store
        with self.stateLock:
            self.networkPrefix    = data[:]
    
    def _infoDagRoot_notif(self,sender,signal,data):
        '''
        Record the DAGroot's EUI64 address.
        '''
        
        # stop of we don't have a networkPrefix assigned yet
        if not self.networkPrefix:
            log.error("infoDagRoot signal received while not have been assigned a networkPrefix yet")
            return
        
        newDagRootEui64 = data['eui64'][:]
        
        with self.stateLock:
           sameDAGroot = (self.dagRootEui64==newDagRootEui64)
        
        # register the DAGroot
        if data['isDAGroot']==1 and (not sameDAGroot):
            
            # log
            log.info("registering DAGroot {0}".format(u.formatAddr(newDagRootEui64)))
            
            # register
            self.register(
                sender            = self.WILDCARD,
                signal            = (
                    tuple(self.networkPrefix + newDagRootEui64),
                    self.PROTO_ICMPv6,
                    self.IANA_ICMPv6_RPL_TYPE
                ),
                callback          = self._fromMoteDataLocal_notif,
            )
            
            # store DAGroot
            with self.stateLock:
                self.dagRootEui64 = newDagRootEui64
        
        # unregister the DAGroot
        if data['isDAGroot']==0 and sameDAGroot:
            
            # log
            log.info("unregistering DAGroot {0}".format(u.formatAddr(newDagRootEui64)))
            
            # unregister from old DAGroot
            self.unregister(
                sender            = self.WILDCARD,
                signal            = (
                    tuple(self.networkPrefix + newDagRootEui64),
                    self.PROTO_ICMPv6,
                    self.IANA_ICMPv6_RPL_TYPE
                ),
                callback          = self._fromMoteDataLocal_notif,
            )
            
            # clear DAGroot
            with self.stateLock:
                self.dagRootEui64 = None
    
    def _fromMoteDataLocal_notif(self,sender,signal,data):
        '''
        Called when receiving fromMote.data.local, probably a DAO.
        '''      
        # indicate data to topology
        self._indicateDAO(data)
        return True
    
    def _getSourceRoute_notif(self,sender,signal,data):
        destination = data
        return self.sourceRoute.getSourceRoute(destination)


    #===== added
    def _adjust_DIO_Period(self, Src, Dest, input_uri, dio_period):
        send_data = {'type' : 'DIO', 'src_addr' : str(Src), 'dst_addr' : str(Dest), 'uri' : str(input_uri), 'period' : str(dio_period)}
        self.IPC_SOCKET.sendto(json.dumps(send_data), (self.IPC_HOST, self.IPC_PORT))

        print ''
        print 'IPC : DIO ADJUSTMENT MSG SENT'
        print ''

    def _adjust_DAO_Period(self, Dest, input_uri, dao_period):
        send_data = {'type' : 'DAO', 'src_addr' : str(Dest), 'dst_addr' : str(Dest), 'uri' : str(input_uri), 'period' : str(dao_period)}
        self.IPC_SOCKET.sendto(json.dumps(send_data), (self.IPC_HOST, self.IPC_PORT))

        print ''
        print 'IPC : DAO ADJUSTMENT MSG SENT'
        print ''

    def _compareIpv6Addr(self, ipv6_addr, parent):
        if(ipv6_addr == MASK.WORKER_DEVICE_ADDR):
            print ''
            print ipv6_addr + ' attached to ' + parent
            return True
        else:
            return False

    def _checkParentChanged(self):
        global source_suffix_ipv6
        if(self.CURRENT_PARENT_ADDR == self.FORMER_PARENT_ADDR):
            return False
        else:
            print ''
            print ' Former parent : ' + self.FORMER_PARENT_ADDR
            print 'Current parent : ' + self.CURRENT_PARENT_ADDR + '\n'
            if(self.FORMER_PARENT_ADDR != ''):
                # to current leaf node's ex-parent : reset dio period to default
                self._adjust_DIO_Period(source_suffix_ipv6, self.FORMER_PARENT_ADDR, 'ex', 10)
            self.FORMER_PARENT_ADDR = self.CURRENT_PARENT_ADDR
            return True
    
    #===== receive DAO
    
    def _indicateDAO(self,tup):
        '''
        Indicate a new DAO was received.
        
        This function parses the received packet, and if valid, updates the
        information needed to compute source routes.
        '''
        
        # retrieve source and destination
        try:
            source                = tup[0]
            if len(source)>8: 
                source=source[len(source)-8:]
            dao                   = tup[1]

        except IndexError:
            log.warning("DAO too short ({0} bytes), no space for destination and source".format(len(dao)))
            return
        
        # log
        if log.isEnabledFor(logging.DEBUG):
            output                = []
            output               += ['received DAO:']
            output               += ['- source :      {0}'.format(u.formatAddr(source))]
            output               += ['- dao :         {0}'.format(u.formatBuf(dao))]
            output                = '\n'.join(output)
            log.debug(output)


        # to compare DAO source addr and Worker device ipv6 addr
        source_suffix_ipv6 = '{0}'.format(u.formatIPv6Addr(source))
        print source_suffix_ipv6


        # DAO example
        # Upper Part
        # [0, 64, 0, 0, 187, 187, 0, 0, 0, 0, 0, 0, 20, 21, 146, 204, 0, 0, 0, 1,
        # Downer Part
        # 6, 20, 0, 0, 11, 170, 187, 187, 0, 0, 0, 0, 0, 0, 20, 21, 146, 204, 0, 0, 0, 1]

        # retrieve DAO header
        dao_header                = {}
        dao_transit_information   = {}
        dao_target_information    = {}
        
        try:
            # Upper Part
            # RPL header
            dao_header['RPL_InstanceID']    = dao[0]   # 0
            dao_header['RPL_flags']         = dao[1]   # 64 => D flag set
            dao_header['RPL_Reserved']      = dao[2]   # 0
            dao_header['RPL_DAO_Sequence']  = dao[3]   # 0
            # DODAGID
            dao_header['DODAGID']           = dao[4:20] # Mote ip ex) bbbb::1415:92cc:0:1

            # Downer Part
            dao                             = dao[20:]
            # retrieve transit information header and parents
            parents                         = []
            children                        = []

            while len(dao)>0:
                # in case, dao[0] = 0x06
                if   dao[0]==self._TRANSIT_INFORMATION_TYPE: 
                    # transit information option
                    dao_transit_information['Transit_information_type']             = dao[0]  # 0x06
                    dao_transit_information['Transit_information_length']           = dao[1]  #  20
                    dao_transit_information['Transit_information_flags']            = dao[2]  #   0
                    dao_transit_information['Transit_information_path_control']     = dao[3]  #   0
                    dao_transit_information['Transit_information_path_sequence']    = dao[4]  #  11
                    dao_transit_information['Transit_information_path_lifetime']    = dao[5]  # 170
                    # address of the parent
                    prefix        =  dao[6:14]                                                # bbbb::
                    parents      += [dao[14:22]]                                              # 1415:92cc:0:1
                    dao           = dao[22:]                                                  #
                # in case, dao[0] = 0x05
                elif dao[0]==self._TARGET_INFORMATION_TYPE:
                    dao_target_information['Target_information_type']               = dao[0]
                    dao_target_information['Target_information_length']             = dao[1]
                    dao_target_information['Target_information_flags']              = dao[2]
                    dao_target_information['Target_information_prefix_length']      = dao[3]
                    # address of the child
                    prefix        =  dao[4:12]
                    children     += [dao[12:20]]
                    dao           = dao[20:]
                else:
                    log.warning("DAO with wrong Option {0}. Neither Transit nor Target.".format(dao[0]))
                    return
        except IndexError:
            log.warning("DAO too short ({0} bytes), no space for DAO header".format(len(dao)))
            return
        

        # DAO Parent Information
        parent_suffix_ipv6 = ''
        for p in parents:
            parent_suffix_ipv6 += '{0}'.format(u.formatIPv6Addr(p))    
        # print parent_suffix_ipv6

        
        # log
        output               = []
        output              += ['']
        output              += ['received RPL DAO from {0}:{1}'.format(u.formatIPv6Addr(self.networkPrefix),u.formatIPv6Addr(source))]
        output              += ['- parents:']
        for p in parents:
            output          += ['   {0}:{1}'.format(u.formatIPv6Addr(self.networkPrefix),u.formatIPv6Addr(p))]
        output              += ['- children:']
        for p in children:
            output          += ['   {0}:{1}'.format(u.formatIPv6Addr(self.networkPrefix),u.formatIPv6Addr(p))]
        output               = '\n'.join(output)
        if log.isEnabledFor(logging.DEBUG):
            log.debug(output)
        print output

        # Here!!
        # Check Who sent the DAO and Where the Leaf Node is attached
        # ex) bbbb::1415:92cc:0:3 => leaf node
        #     bbbb::1415:92cc:0:2 => sub-root
        #     bbbb::1415:92cc:0:1 => root

        #     received DAO from bbbb::1415:92cc:0:3
        #     - parents:
        #        bbbb:1415:92cc:0:2
        #     => Node 3 is child of Node 2
        
        # if you get here, the DAO was parsed correctly

        # 
        if(self._compareIpv6Addr(source_suffix_ipv6, parent_suffix_ipv6) == True):
            self.CURRENT_PARENT_ADDR = parent_suffix_ipv6
            if(self._checkParentChanged()):
                # to current leaf node : set dao period loosely
                self._adjust_DAO_Period(source_suffix_ipv6, 'ex', 60)
                # to current leaf node's parent : set dio period loosely
                self._adjust_DIO_Period(source_suffix_ipv6, parent_suffix_ipv6, 'ex', 20)
                
        
        # update parents information with parents collected -- calls topology module.
        self.dispatch(          
            signal          = 'updateParents',
            data            =  (tuple(source),parents)  
        )
        
        #with self.dataLock:
        #    self.parents.update({tuple(source):parents})
