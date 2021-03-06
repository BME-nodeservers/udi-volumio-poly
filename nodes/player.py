import udi_interface
import requests
import write_nls

LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom

class VolumioNode(udi_interface.Node):
    # class variables
    status= None

    def __init__(self, polyglot, primary, address, name, url, notify):
        self.poly = polyglot
        self.id = address
        self.sources = []
        self.url = url
        self.notify = notify

        # call the default init
        super(VolumioNode, self).__init__(polyglot, primary, address, name)

        # Get the source list for the player
        self.getSourceList()


    """ Called after node has been added """
    def setNotification(self):
        LOGGER.debug('Status: {}'.format(self.send_command('getState')))
        info = self.send_command('getState')
        self.status(info, True)

        # set up notifications
        self.post_request('pushNotificationUrls', {"url": self.notify})
        LOGGER.debug('{}'.format(self.send_command('pushNotificationUrls')))


    def send_command(self, command, value=None):
        cmds = ['play', 'toggle', 'stop', 'pause', 'prev', 'next', 'clearQueue']
        cmdv = ['playplaylist', 'repeat', 'random', 'volume']

        url = self.url + '/api/v1/'
        if command in cmds:
            url += 'commands?cmd=' + command
        elif command in cmdv:
            url += 'commands?cmd=' + command + '&' + value
        else:
            if value is not None:
                url += command + '?' + value
            else:
                url += command

        LOGGER.debug('sending: {}'.format(url))
        c = requests.get(url)
        LOGGER.debug('send_command retuned: {}'.format(c.text))
        try:
            jdata = c.json()
        except Exception as e:
            LOGGER.error('GET {} failed: {}'.format(url, c.text))
            jdata = ''
        c.close()

        return jdata

    def post_request(self, command, body):
        url = self.url + '/api/v1/' + command

        c = requests.post(url, json=body)

        try:
            jdata = c.json()
        except Exception as e:
            LOGGER.error('GET {} failed: {}'.format(url, c.text))
            jdata = ''
        c.close()

        return jdata

    """
      Use replaceAndPlay to add items to the queue or replace what's
      currently playing with something new.

      This will probably be used to select things like Pandora or a
      playlist or is it just used to add individual tracks?
    """
    def replaceAndPlay(self):
        pass

    def status(self, info, force=False):
        self.setDriver('SVOL', int(info['volume']), True, force)
        self.setDriver('DUR', int(info['duration']), True, force)
        if info['status'].lower() == 'stop':
            self.setDriver('MODE', 0, True, force)
        elif info['status'].lower() == 'play':
            self.setDriver('MODE', 2, True, force)
        else:
            self.setDriver('MODE', 1, True, force)

        if info['random']:
            self.setDriver('GV4', 1, True, force)
        else:
            self.setDriver('GV4', 0, True, force)

        if info['repeat']:
            self.setDriver('GV5', 1, True, force)
        else:
            self.setDriver('GV5', 0, True, force)

    def getSourceList(self):
        src_cnt = 0
        self.sources = []
        root = self.send_command('browse')
        for src in root['navigation']['lists']:
            LOGGER.debug('Found {}'.format(src['uri']))
            if src['uri'] == 'favourites':
                self.sources.append({'name': 'Favourites', 'uri': 'favourites'})
            elif src['uri'] == '/pandora':
                try:
                    stations = self.send_command('browse', 'uri=/pandora')
                    sl = stations['navigation']['lists'][0]['items']
                    for s in sl:
                        LOGGER.debug('found: {} {}'.format(s['name'], s['uri']))
                        self.sources.append({'name': 'Pandora: {}'.format(s['name']), 'uri': s['uri']})
                except Exception as e:
                    LOGGER.error('Failed to get Pandora stations: {}'.format(e))
            elif src['uri'] == 'spotify':
                try:
                    stations = self.send_command('browse', 'uri=spotify')
                    for group in stations['navigation']['lists']:
                        LOGGER.debug('Group title: {}'.format(group['title']))
                        if 'My Music' in group['title']:
                            for sl in group['items']:
                                LOGGER.debug('{} -> {}'.format(sl['title'], sl['uri']))
                                mymusic = self.send_command('browse', 'uri={}'.format(sl['uri']))
                                for s in mymusic['navigation']['lists'][0]['items']:
                                
                                    if s['type'] == 'playlist':
                                        LOGGER.debug('found: {} {}'.format(s['title'], s['uri']))
                                        self.sources.append({'name': 'Spotify: {}'.format(s['title']), 'uri': s['uri']})
                except Exception as e:
                    LOGGER.error('Failed to get Spotify stations: {}'.format(e))

        playlists = self.send_command('listplaylists')
        for play in playlists:
            LOGGER.debug('Found {}'.format(play))
            self.sources.append({'name': play, 'uri': 'playplaylist'})

        """
        #Save source list to customData
        if 'customData' in self.polyConfig:
            customdata = self.polyConfig['customData']
        else:
            customdata = {}
        customdata['sourceList'] = self.sources
        self.poly.saveCustomData(customdata)
        """

    def process_cmd(self, cmd=None):
        LOGGER.debug('ISY sent: {}'.format(cmd))
        if cmd is not None:
            if cmd['cmd'] == 'PLAY':
                self.send_command('play')
            elif cmd['cmd'] == 'PAUSE':
                self.send_command('pause')
            elif cmd['cmd'] == 'NEXT':
                self.send_command('next')
            elif cmd['cmd'] == 'PREV':
                self.send_command('prev')
            elif cmd['cmd'] == 'STOP':
                self.send_command('stop')
            elif cmd['cmd'] == 'VOLUME':
                self.send_command('volume', 'volume=' + cmd['value'])
            elif cmd['cmd'] == 'SHUFFLE':
                if cmd['value'] == '0':
                    value = 'false'
                else:
                    value = 'true'
                self.send_command('random', 'value=' + value)
            elif cmd['cmd'] == 'REPEAT':
                if cmd['value'] == '0':
                    value = 'false'
                else:
                    value = 'true'
                self.send_command('repeat', 'value=' + value)
            elif cmd['cmd'] == 'SOURCE':
                LOGGER.debug('selected source now = {}'.format(cmd['value']))
                idx = int(cmd['value'])
                try:
                    src = self.sources[idx]
                    LOGGER.debug('Found source entry {}'.format(src))
                    # what are the different playback mechinims. 
                    #   pandora or spotify
                    #   favorites
                    #   playlists
                    self.send_command('stop')
                    self.send_command('clearQueue')
                    if 'pandora' in src['uri']:
                        self.send_command('browse', 'uri=' + src['uri'])
                        self.send_command('repeat', 'value=false')
                        self.send_command('random', 'value=false')
                        self.send_command('next')
                        self.send_command('play')
                    elif 'spotify' in src['uri']:
                        self.send_command('browse', 'uri=' + src['uri'])
                        self.send_command('repeat', 'value=false')
                        self.send_command('random', 'value=false')
                        self.send_command('next')
                        self.send_command('play')
                    elif src['name'] == 'Favourites':
                        self.send_command('browse', 'uri=' + src['uri'])
                        self.send_command('repeat', 'value=false')
                        self.send_command('random', 'value=true')
                        self.send_command('play')
                    else: # playlist
                        self.send_command('playplaylist', 'name=' + src['name'])
                        self.send_command('repeat', 'value=false')
                        self.send_command('random', 'value=true')
                        self.send_command('next')
                        self.send_command('play')

                    self.setDriver('GV1', idx, True)
                except Exception as e:
                    LOGGER.error('Error trying to start source {} ({})'.format(src, e))

    commands = {
            'VOLUME': process_cmd,
            'SOURCE': process_cmd,
            'PLAY': process_cmd,
            'PAUSE': process_cmd,
            'STOP': process_cmd,
            'SHUFFLE': process_cmd,
            'REPEAT': process_cmd,
            'PREV': process_cmd,
            'NEXT': process_cmd,
            }

    drivers = [
            {'driver': 'ST', 'value': 1, 'uom': 2},       # player status
            {'driver': 'GV1', 'value': 0, 'uom': 25},     # Source
            {'driver': 'SVOL', 'value': 0, 'uom': 12},    # Volume
            {'driver': 'DUR', 'value': 0, 'uom': 58},     # duration
            {'driver': 'TIMEREM', 'value': 0, 'uom': 58}, # remaining
            {'driver': 'GV4', 'value': 0, 'uom': 25},     # shuffle
            {'driver': 'GV5', 'value': 0, 'uom': 25},     # repeat
            {'driver': 'MODE', 'value': 0, 'uom': 25},    # play/pause
            ]

    
