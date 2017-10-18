# Setup

The instructions below walkthrough how to setup the prototype in a Mac OSX environment.

There are 3 key parts of the setup:

* Midi (for playback)
* Neo4j (for the graph database backend)
* Python and dependencies

## Midi

### Dependencies

* [RtMidi](https://www.music.mcgill.ca/~gary/rtmidi/)
* [Mido](https://mido.readthedocs.io/en/latest/index.html)
* python-rtmidi

### Setup

Using [Homebrew](https://brew.sh), setting up RtMidi is as simple as:
```
brew install rtmidi
```

Our python dependencies will be installed during the creation of our virtual environment below.

### Opening a MIDI port

To use Midi with our prototype, you'll need to setup a MIDI port.

Use Mac OSX Audio MIDI Setup to open up an IAC Driver MIDI Port

Let's call it 'PythonMido'

(_Add Screenshots here_)

You'll need to link a Midi instrument to be able to play the output.  An easy test setup if you're on a Mac is to simply start up GarageBand. 


## Neo4j
[Neo4j](https://neo4j.com/) is a native property graph database.  It provides a simple backend database for this prototype.  An easy way to deploy Neo4j is with Docker.  If you're not already running Docker, please see the [Docker](https://www.docker.com) website for official installation instructions.

The RheingoldGraph prototype don't require any plugins or changes to the native Neo4j Community distribution.

### Running Neo4j with Docker locally
If you already have Docker installed and running, simply run a container from the standard Neo4j.  We mount several directories in order to persist our database data even after our container is shutdown.

```
docker run --rm -p 7474:7474 -p 7687:7687 \
-v ~/Projects/Rheingold/neo4j/demo/data:/data \
-v ~/Projects/Rheingold/neo4j/demo/logs:/logs \
-v ~/Projects/Rheingold/neo4j/demo/import/:/var/lib/neo4j/import/ \
neo4j:latest
```
Note: By default Neo4j requires authentication. The first time you connect to your database, you have to login with Username 'neo4j' and Password 'neo4j', then set a new password.

## Python and Dependencies

### Dependencies
* __Python 3.6__
* __conda__ package and environment manager
* All __Python dependencies__ found in the environment.yml file

### Download and install MiniConda

A simple and lightweight way to get up and running with Python 3.6 and conda is to download [Miniconda](https://conda.io/miniconda.html)

#### Mac
Follow the instructions at the link above, or download and install from the command line
```
curl -O https://repo.continuum.io/miniconda/Miniconda3-latest-MacOSX-x86_64.sh
sudo bash Miniconda3-latest-MacOSX-x86_64.sh
```

#### Linux
```
curl -O https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
sudo bash Miniconda3-latest-Linux-x86_64.sh
```

#### Creating a Virtual Environment
Create a virtual environment for this project with all dependencies, then activate it
```
conda-env create --name rheingoldgraph -f environment.yml
source activate rheingoldgraph
```
