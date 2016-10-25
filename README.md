# Sopu

## Description

Sopu is ~~a shitty~~ an unofficial version of the [Syncplay](http://syncplay.pl/) client designed for [mpv](https://mpv.io/) (command-line) and OS X after I ran into a myriad of problems trying to get the official client working. It's built using [Twisted](https://twistedmatrix.com/trac/) for networking and [Click](http://click.pocoo.org/5/) for the command-line interface.

Note that the client is not very good and full of shit code. But then again, it works better for me than the actual Syncplay client, so there's at least some value.

## Installation

Install the client using pip. At no point during development did I think about Python 2.x, so I have zero expectations of it working with it. It's also not a bad idea to isolate the installation into a [virtualenv](https://virtualenv.pypa.io/en/stable/) of its own.

    pip install git+https://github.com/Hamuko/Sopu

## Usage

For basic usage, just give Sopu the server address as the only argument, e.g. `sopu syncplay.pl:8995`. You will be prompted for additional information steps before connecting if not enough is provided via options.

### Options

```
  --room TEXT      Room to join in the server
  --socket TEXT    Address for the mpv UNIX socket
  --username TEXT  Desired username to join server with
  --password TEXT  Server password
  --help           Show this message and exit.
```
