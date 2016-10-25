from time import time
from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import LineReceiver
import click
import json


class SyncplayClientProtocol(LineReceiver):
    def __init__(self, factory):
        self.factory = factory

    def connectionLost(self, reason):
        click.echo('Connection lost: {}'.format(reason))

    def connectionMade(self):
        """Logs into the Syncplay server after the TCP connection is
        established. Also sends details about the current file loaded into mpv
        and sets the user as ready.
        """
        data = {'username': self.factory.username,
                'room': {'name': self.factory.room_name},
                'version': '1.2.7'}
        if self.factory.password:
            data['password'] = self.factory.password
        self.sendData({'Hello': data})
        self.setFile()
        self.setReady(True)

    def lineReceived(self, line):
        data = json.loads(str(line, 'utf8'))
        if 'State' in data:
            self.stateReceive(data['State'])
        elif 'Set' in data:
            self.setReceive(data['Set'])
        else:
            print(data)

    @property
    def playstate(self):
        return {'paused': self.factory.player.paused,
                'position': self.factory.player.position}

    def setReceive(self, data):
        if 'ready' in data:
            if data['ready']['isReady']:
                click.echo('{} is ready'.format(data['ready']['username']))
            else:
                click.echo('{} is not ready'.format(data['ready']['username']))
        elif 'user' in data:
            for user in data['user']:
                if 'file' in data['user'][user]:
                    filename = data['user'][user]['file']['name']
                    duration = data['user'][user]['file']['duration'] / 60
                    filesize = data['user'][user]['file']['size']
                    click.echo('{} set the file to {},'
                               ' {:g} minutes and {} bytes'
                               .format(user, filename, duration, filesize))
                else:
                    print(data['user'])
        else:
            print(data)

    def setFile(self):
        """Sends the current mpv file details to Syncplay server. Sends the
        filename raw.
        """
        file_info = {'duration': self.factory.player.duration,
                     'name': self.factory.player.filename,
                     'size': self.factory.player.filesize}
        self.sendData({'Set': {'file': file_info}})

    def setReady(self, value):
        """Sets the user ready status to value (boolean)."""
        ready = {'ready': {'isReady': value, 'manuallyInitiated': False}}
        self.sendData({'Set': ready})

    def stateReceive(self, data):
        self.clientLatencyStart = time()
        if 'ignoringOnTheFly' in data:
            self.factory.player.seek(data['playstate']['position'])
            self.factory.player.pause(data['playstate']['paused'])
        diff = self.factory.player.position - data['playstate']['position']
        if abs(diff) > 3:
            self.factory.player.seek(data['playstate']['position'])
        if 'clientLatencyCalculation' in data['ping']:
            self.rtt = time() - data['ping']['latencyCalculation']
        else:
            self.rtt = 0
        self.stateSend(data)

    def stateSend(self, data):
        newData = {'State': {}}
        try:
            if data['ignoringOnTheFly']['server'] == 1:
                newData['State']['ignoringOnTheFly'] = {'server': 1}
        except KeyError:
            pass
        latencyCalculation = data['ping']['latencyCalculation']
        newData['State']['playstate'] = self.playstate
        if self.clientLatencyStart:
            clientLatencyCalculation = time() - self.clientLatencyStart
        else:
            clientLatencyCalculation = time()
        newData['State']['ping'] = {
            'clientRtt': self.rtt,
            'clientLatencyCalculation': clientLatencyCalculation,
            'latencyCalculation': latencyCalculation
        }
        self.sendData(newData)

    def sendData(self, data):
        """Sends a message to the Syncplay server. Accepts a dictionary, which
        is turned into a JSON string before being converted to a byte-string
        and sent as a line.
        """
        data = json.dumps(data, separators=(',', ':'))
        self.sendLine(data.encode('utf8'))


class SyncplayClientFactory(ClientFactory):
    def __init__(self, player, username='', password='', room=''):
        self.player = player
        self.username = username
        self.password = password
        self.room_name = room

    def buildProtocol(self, addr):
        protocol = SyncplayClientProtocol(self)
        return protocol
