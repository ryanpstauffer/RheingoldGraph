# RheingoldGraph Prototype Readme #

RheingoldGraph Prototype is a demonstration of an initial concept of a graph representation of musical information.

## Setup

### Midi

#### Dependencies

* [RtMidi](https://www.music.mcgill.ca/~gary/rtmidi/)
* [Mido](https://mido.readthedocs.io/en/latest/index.html)
* python-rtmidi

#### Mac

Using [Homebrew](https://brew.sh), setting up RtMidi is as simple as:
```
brew install rtmidi
```

Our python dependencies will be installed during the creation of our virtual environment below.

##### Opening a MIDI port

To use Midi with our prototype, you'll need to setup a MIDI port.

Use Mac OSX Audio MIDI Setup to open up an IAC Driver MIDI Port

Let's call it 'PythonMido'

(Add Screenshots here)

You'll need to link a Midi instrument to be able to play the output.  An easy test setup if you're on a Mac is to simply start up GarageBand. 


### Neo4j
[Neo4j](https://neo4j.com/) is a native property graph database.  It provides a simple backend database for this prototype.  An easy way to deploy Neo4j is with Docker.  If you're not already running Docker, please see the [Docker](https://www.docker.com) website for official installation instructions.

The RheingoldGraph prototype don't require any plugins or changes to the native Neo4j Community distribution.

#### Running Neo4j with Docker locally
```
docker run --rm -p 7474:7474 -p 7687:7687 \
-v ~/Projects/Rheingold/neo4j/demo/data:/data \
-v ~/Projects/Rheingold/neo4j/demo/logs:/logs \
-v ~/Projects/Rheingold/neo4j/demo/import/:/var/lib/neo4j/import/ \
neo4j:latest
```

By default Neo4j requires authentication. The first time you connect to your database, you have to login with Username 'neo4j' and Password 'neo4j', then set a new password.

### Create a virtual environment for this project with all dependencies, then activate it
```
conda-env create --name rheingoldgraph -f environment.yml
source activate rheingoldgraph
```
