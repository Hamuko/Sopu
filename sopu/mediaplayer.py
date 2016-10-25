import time
import json
import threading
import socket
from twisted.internet import reactor


class MediaPlayerProperty():
    def __init__(self, property_, request_id):
        self.property = property_
        self.request_id = request_id

    @property
    def command(self):
        return {'command': ['get_property', self.property],
                'request_id': self.request_id}


class MediaPlayer():
    """MediaPlayer class is a representation of the mpv media player connected
    via the mpv JSON IPC protocol (https://mpv.io/manual/master/#json-ipc). The
    class uses a UNIX socket to connect to mpv and uses a daemon thread to
    listen to responses from mpv.
    """
    PROPERTY_PAUSED = MediaPlayerProperty('pause', 1)
    PROPERTY_POSITION = MediaPlayerProperty('time-pos', 2)
    PROPERTY_DURATION = MediaPlayerProperty('duration', 3)
    PROPERTY_FILESIZE = MediaPlayerProperty('file-size', 4)
    PROPERTY_FILENAME = MediaPlayerProperty('filename', 5)

    def __init__(self, address):
        """Initialize the socket using the supplied address and start the
        listener thread.
        """
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.socket.connect(address)
        self.listen_thread = threading.Thread(target=self.listen)
        self.listen_thread.daemon = True
        self.listen_thread.start()

    def _send(self, command):
        """Send a command to the mpv socket. Accepts a dictionary and turns it
        to a JSON byte-string before sending it to the socket.
        """
        data = (json.dumps(command, separators=(',', ':')).encode('utf8'))
        self.socket.send(data + b'\n')

    def _get_property(self, player_property, variable):
        """Sends a command to the player requesting a property. Blocks until
        property is returned and saved to specified instance variable.
        """
        setattr(self, variable, None)
        self._send(player_property.command)
        while getattr(self, variable) is None:
            time.sleep(0.05)
        return getattr(self, variable)

    @property
    def duration(self):
        """Returns the total length of the current file as seconds (float).
        Blocks until a value is returned.
        """
        return self._get_property(MediaPlayer.PROPERTY_DURATION, '_duration')

    @property
    def filename(self):
        """Returns the file name of the current file as a string. Blocks until
        a value is returned.
        """
        return self._get_property(MediaPlayer.PROPERTY_FILENAME, '_filename')

    @property
    def filesize(self):
        """Returns the filesize of the current file as bytes (integer). Blocks
        until a value is returned.
        """
        return self._get_property(MediaPlayer.PROPERTY_FILESIZE, '_filesize')

    def handle_event(self, data):
        """Triggers callbacks based on incoming events."""
        """TODO: Implement the method."""
        pass

    def handle_data(self, data):
        """Sets private instance variables to data returned by mpv. The
        association between a value and property is done using the constant
        request IDs that have been assigned to a particular property in the
        code.
        """
        if 'request_id' not in data:
            return
        if data['request_id'] == MediaPlayer.PROPERTY_PAUSED.request_id:
            self._paused = data['data']
        elif data['request_id'] == MediaPlayer.PROPERTY_POSITION.request_id:
            self._position = data['data']
        elif data['request_id'] == MediaPlayer.PROPERTY_DURATION.request_id:
            self._duration = data['data']
        elif data['request_id'] == MediaPlayer.PROPERTY_FILESIZE.request_id:
            self._filesize = data['data']
        elif data['request_id'] == MediaPlayer.PROPERTY_FILENAME.request_id:
            self._filename = data['data']

    def listen(self):
        """Method to be ran in a separate thread. Listens to the mpv UNIX
        socket and sends events to MediaPlayer.handle_event and data responses
        to MediaPlayer.handle_data.
        """
        while True:
            response_data = self.socket.recv(1024)
            for message in str(response_data, 'utf8').strip().split('\n'):
                try:
                    response = json.loads(message)
                except json.decoder.JSONDecodeError:
                    reactor.stop()
                if 'event' in response:
                    self.handle_event(response)
                if 'error' in response and response['error'] == 'success':
                    self.handle_data(response)

    def pause(self, state):
        """Tells the player to set paused status to state (boolean).
        Asynchronous command and not verified in any way.
        """
        command = {'command': ['set_property', 'pause', state]}
        self._send(command)

    @property
    def paused(self):
        """Returns a boolean value indicating if the player is paused or not.
        Blocks until a value is returned.
        """
        return self._get_property(MediaPlayer.PROPERTY_PAUSED, '_paused')

    @property
    def position(self):
        """Returns the current playback position as seconds (float). Blocks
        until a value is returned.
        """
        return self._get_property(MediaPlayer.PROPERTY_POSITION, '_position')

    def seek(self, position):
        """Seeks the player to the position in seconds (float).
        Asynchronous command and not verified in any way.
        """
        command = {'command': ['set_property', 'time-pos', position]}
        self._send(command)
