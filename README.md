# RheingoldGraph Readme

RheingoldGraph is a graph representation of musical information.  So far, the build has been focused on getting the core functionality and features correct rather than scale and optimization.

## Setup

These instructions walkthrough how to setup RheingoldGraph in a Mac OSX environment.

There are 3 key parts of the setup:

* Midi (for playback)
* Gremlin Server and TinkerGraph (for a graph computing framework)
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

Use Mac OSX Audio MIDI Setup to open up an IAC Driver MIDI Port.  Let's call it __PythonMido__.

You'll need to link a Midi instrument to be able to play the output.  An easy test setup if you're on a Mac is to simply start up GarageBand. 

## Gremlin Server and TinkerGraph
Gremlin Server is part of the [Apache TinkerPop](tinkerpop.apache.org) graph computing framework.  As a initial backend, we're using [TinkerGraph](tinkerpop.apache.org/docs/current/reference/#tinkergraph-gremlin).  TinkerGraph provides a simple in-memory, non-transactional graph engine for RheingoldGraph.  It's easy to configure and startup, and provides all the core functionality we need right now for feature building ad unit testing.

### Downloading and running Gremlin Server
RheingoldGraph is being developed to run on TinkerPop>=3.3.0.  Most testing has focused on TinkerPop 3.3.1, which can be download [here](https://www.apache.org/dyn/closer.lua/tinkerpop/3.3.1/apache-tinkerpop-gremlin-server-3.3.1-bin.zip).

#### Setup
_Automated setup script coming soon!_

* Unzip the file
* Add an alias
```
alias gremserv='~/my/tinkerpop/server/bin/gremlin-server.sh'
```
* Copy the Rheingold conf/ directory contents to the Gremlin Server conf/ directory 

### Deploying Gremlin Server and TinkerGraph via Kubernetes
_Coming soon!_

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

If you want to use RheingoldGraph with TensorFlow and Magenta models, then use the environment_magenta.yml file
```
conda env create --name rheingold_magenta -f environment_magenta.yml 
source activate rheingold_magenta
```

## RheingoldGraph Basics

There will be a Jupyter notebook coming soon with a more detailed walktrhough.

```python
# Connect to an existing Gremlin Server via Websocket
server_uri = 'ws://localhost:8182/gremlin'
session = Session(server_uri)

# Add an XML file to the graph
session.add_lines_from_xml(filename='scores/BachCelloSuiteDminPrelude.xml', 
                             piece_name='bach_cello')

# View the line we just added
session.graph_summary()

# Total Vertices: 644
# Total Edges: 1292
# Number of Lines: 1
# ----------------
# bach_cello: 643

# Play our line over an open MIDI port
midi_port = 'IAC Driver MidoPython'
session.play_line(line_name='bach_cello', qpm=80, midi_port=midi_port)

# Remove our line from the graph
session.drop_line(line_name='bach_cello')
```

We can also interface RheingoldGraph directly with TensorFlow models, such as those developed by Google's Magenta project.
```python
# Use our line as a primer for generating new melodies
# from a trained TensorFlow (Magenta) model
bundle_file = '~/magenta_data/mag/basic_rnn.mag'
session.generate_melody_from_trained_model(trained_model_name='melody_rnn_generator', 
                                           bundle_file=bundle_file,
                                           sequence_generator,
                                           primer_line_name='tester_bach',
                                           primer_len=11,
                                           num_outputs=2,
                                           qpm=80,
                                           num_steps=150)

# INFO:tensorflow:Wrote 1 line to the graph.
# INFO:tensorflow:Wrote line bach_cello_magenta_20180204_2030
 
# Play our newly added melody
session.play_line('bach_cello_magenta_20180204_2030')
```
