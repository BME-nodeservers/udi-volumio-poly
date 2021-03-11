#!/usr/bin/env python3
"""
Polyglot v3 node server Volumio Media Server control.
Copyright (C) 2021 Robert Paauwe
"""
import udi_interface
import sys
import time
import json
import requests
import threading
import dns.resolver
import write_nls
from nodes import myserver
from nodes import player

LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom

class Controller(udi_interface.Node):
    id = 'Volumio'
    def __init__(self, polyglot, primary, address, name):
        super(Controller, self).__init__(polyglot, primary, address, name)
        self.poly = polyglot
        self.name = name
        self.address = address
        self.primary = primary
        self.configured = False
        self.server = None
        self.player_list = {}

        self.Parameters = Custom(polyglot, 'customparams')
        self.Notices = Custom(polyglot, 'notices')

        self.poly.subscribe(polyglot.CUSTOMPARAMS, self.parameterHandler)
        self.poly.subscribe(polyglot.START, self.start, address)
        self.poly.ready()
        self.poly.addNode(self)

    # Process changes to customParameters
    def parameterHandler(self, params):
        self.Parameters.load(params)
        validPlayer = False
        
        if len(self.Parameters) == 0:
            self.Notices['config'] = 'Please enter IP address/name of Volumio server'
            self.configured = False
            return

        for name in self.Parameters:
            if self.Parameters[name] is not '':
                validPlayer = True
                self.createNode(name, self.Parameters[name])

        if not validPlayer:
            self.Notices['config'] = 'Please enter IP address/name of Volumio server'
            self.configured = False
            return

        write_nls.write_nodedef(LOGGER, self.player_list)
        write_nls.write_nls(LOGGER, self.player_list)
        self.poly.updateProfile()

        for name in self.player_list:
            self.poly.addNode(self.player_list[name]['node'])

        self.configured = True
        self.Notices.clear()

    def start(self):
        LOGGER.info('Starting node server')
        self.poly.setCustomParamsDoc()

        while not self.configured:
            LOGGER.debug('Waiting for configuration')
            time.sleep(5)

        LOGGER.info('Starting notification web server process')
        self.start_server()

        LOGGER.info('Node server started')

    def getIP(self, local):
        myres = dns.resolver.Resolver()
        myres.nameservers = ['224.0.0.251']
        myres.port = 5353
        try:
            ip = myres.resolve(local, 'A')
            return ip[0].to_text()
        except:
            LOGGER.error('Failed to resolve {} to IP address'.format(local))

        return local

    def createNode(self, name, ip):
        if ip.endswith('local'):
            ip = self.getIP(ip)

        url = 'http://' + ip

        # notification URL
        notify = 'http://' + self.poly.network_interface['addr'] + ':8383/' + name

        address = 'volumio_' + ip.split('.')[3]
        node = player.VolumioNode(self.poly, self.address, address, name, url, notify)

        cnt = 0
        src_map = {}
        for src in node.sources:
            src_map[cnt] = (src, cnt)
            cnt += 1


        self.player_list[name] = {'node_id': address, 'sources': src_map, 'node': node}

    def query(self):
        for node in self.nodes:
            self.nodes[node].reportDrivers()

    # Delete the node server from Polyglot
    def delete(self):
        LOGGER.info('Removing node server')

    def stop(self):
        self.server.Stop = True
        self.server.socket.close()
        LOGGER.info('Stopping node server')

    def web_server(self):
        """
        Notifications:
          Send a post to pushNotificationsUrls?url=<our server process>
        """
        try:
            self.server = myserver.Server(('', 8383), myserver.VHandler)
            self.server.serve_forever(self)
        except Exception as e:
            LOGGER.error('web server failed: {}'.format(e))

    """
      TODO: figure out how to deal with notification server....
    """
    def start_server(self):
        LOGGER.error('Starting notification server')
        self.notification_thread = threading.Thread(target = self.web_server)
        self.notification_thread.daemon = True
        self.notification_thread.start()


    drivers = [
            {'driver': 'ST', 'value': 1, 'uom': 2},       # node server status
            ]

    
