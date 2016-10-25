from .mediaplayer import MediaPlayer
from .protocol import SyncplayClientFactory
from twisted.internet import reactor
import click
import hashlib


@click.command()
@click.option('--room', prompt=True,
              help='Room to join in the server')
@click.option('--socket', default='/tmp/mpvsocket',
              help='Address for the mpv UNIX socket')
@click.option('--username', prompt=True,
              help='Desired username to join server with')
@click.option('--password', default='',
              help='Server password')
@click.argument('server')
def main(server, room, socket, username, password):
    try:
        host, port = server.split(':')
        port = int(port)
    except ValueError:
        click.echo('ERROR: Invalid server, must be in format HOST:PORT')
        exit(1)
    socket_string = click.style('--input-ipc-server={}'.format(socket),
                                bold=True)
    click.echo('Please start mpv with desired file and option {} and'
               ' press enter to continue'.format(socket_string))
    input()

    player = MediaPlayer(socket)
    connection_kwargs = {'username': username, 'room': room}
    if password:
        hasher = hashlib.md5()
        hasher.update(bytes(password, 'utf8'))
        connection_kwargs['password'] = hasher.hexdigest()
    factory = SyncplayClientFactory(player, **connection_kwargs)
    reactor.connectTCP(host, port, factory)
    reactor.run()


if __name__ == '__main__':
    main()
