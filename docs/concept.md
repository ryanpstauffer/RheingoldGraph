# The Concept

[//]: # (Image References)

[BachCelloScore]: resources/BachCelloScoreExample.png "Cello Suite No. 2 in d minor, Prelude (Opening) - Bach, J.S."

[BachCelloMusicGraphEx1]: https://docs.google.com/drawings/d/e/2PACX-1vTK6m4qwAGEwU0JZ556ZV1JTQh5f-HoQHJRe3-LGXrHc-7Lo2B5YVsPItlnzjSud09msv_eLeJhPPzM/pub?w=1431&h=782 "Bach Cello Music Graph"

[BachCelloMusicGraphEx2]: https://docs.google.com/drawings/d/e/2PACX-1vTcHhH99u6lWE00bMphRkEcwYNfcZjMMWhAsmiwxXB9RbjjPvV8yciBZpyy-v_bj7x0dVmuRnr4TGTx/pub?w=1415&h=905 "Bach Cello Music Graph with Playable Notes"

The goal here is to introduce the concept of the music graph.  We'll focus on high-level design and a few sample queries.  Future parts of this series will go into more detail on the exact implementation.

### What is RheingoldGraph?

The purpose of RheingoldGraph is to be a clean, flexible and extensible data system for storing and retrieving music information.  The final implementation of the music graph seeks to integrate music information from across multiple representational domains (see [Part II](storagemethods.md) for more information on music representation).  
Initially, the goal is to focus on the logical domain, which we can define as the core information required to represent a piece of music in both notation and performance - pitch, rhythm, harmony, tempo, dynamics, and articulation. (Footnote to Babbitt, MEI, and John Maxwell (1981) ).  Successful representation of the logical domain would include all of the information necessary to realize a piece of music in sonic form.


### Why do this at all?

RheingoldGraph has three reasons for existing:

1. As a store of musical information in a way that can immediately be put to use for music information retrieval (MIR) tasks
2. As an integral part of broader research into applying machine intelligence on music understanding
3. As a specific use case (music) to justify research into new data storage and retrieval concepts, insights from which can be applied to other (non-musical) domains

In all three cases, our goal is to eventual have a clean abstraction above the lower levels issues of storing and retrieving music information.  With this in mind, the RheingoldGraph project seeks to streamline common low level data operations and eventually provide a clean API for use by both users and other future applications.

In all three cases, the goal is to improve on current storage methods.  An overview of current storage methods will be released in [Part II](storagemethods.md) of this series.

### Starting point
Let's start with an concrete example using a simple melody line from the opening of the Prelude from [Bach’s Cello Suite No. 2 in d minor](http://imslp.org/wiki/Cello_Suite_No.2_in_D_minor,_BWV_1008_(Bach,_Johann_Sebastian)).

We normally think of representing music in a couple of primary ways - __notation representation__ and __performance representation__.  

#### Notational Representation
Music notation seeks to encode musical logic into a format that is readable by humans for performance and analysis.

This could be music notation on a printed page, like this:

![alt text][BachCelloScore]

We can also have a notational representation in an XML type format, which can be used to store, modify, and transfer music information between computer applications.  Since XML music notation is very verbose, we'll start with the first two notes. 
```xml
<note>
    <pitch>
        <step>D</step>
        <octave>3</octave>
    </pitch>
    <duration>2</duration>
    <voice>1</voice>
    <type>eighth</type>
    <stem>down</stem>
    <beam number="1">begin</beam>
</note>
<note>
    <pitch> 
        <step>F</step>
        <octave>3</octave>
    </pitch>
    <duration>2</duration>
    <voice>1</voice>
    <type>eighth</type>
    <stem>down</stem>
    <beam number="1">end</beam>
</note>
```

#### Performance-specific representation
We can also encode the specifics of a single performance.  The most widespread modern form of this is MIDI (or [Musical Instrument Digital Interface](Musical Instrument Digital Interface)).  MIDI is a binary serialized format not meant to be human-readable.  Simplistically, MIDI message contains "NOTE ON" and "NOTE OFF" messages for different pitches, in addition to other information on dynamics and instrument programs.  Note that MIDI itself contains no audio, only the instructions to create it, and in this way is another variation on a representation of the core logic of a piece of music.

### Thinking differently
There are issues with all of the above methods of music representation - which we'll dive into in Part III.  For now, let's imagine another way of representing the same information from our Bach Cello Suite.

![alt text][BachCelloMusicGraphEx1]

We can represent all of the core musical information from Bach with a few simple elements that have been properly ordered in time.  Each note is represented by a __vertex__ in our graph.  Each vertex is connected by one or more __edges__.  Let's go deeper into what information is actually stored in each vertex and how we construct this graph.

### Building our graph
For our RheingoldGraph prototype, we use an off-the-shelf property graph database called Neo4j, along with its declarative query language, Cypher.  There are several reasons to use Neo4j as a demonstration prototype:

* Neo4j Community is free and easy to run from an official Docker image, meaning it takes only seconds to get running
* Cypher is a clear and concise query language, suitable for building a proof-of-concept 
* Neo4j includes a clean and simple GUI for query execution and immediate visualization of graph results, without the need for additional software or packages
* Neo4j has a lightweight and officially supported Python driver

We start building our music graph with note information that we would find in the printed score.  This information could be entered into the graph directly using Cypher
```
// Create the line
CREATE (line:Line {name: 'bach_cello'}

// Create notes
CREATE (n1:Note {
                  name: "D3",
                  pitchClass: "D",
                  octave: 3, 
                  length: 8, 
                  dot:0
                })
CREATE (n2:Note {
                  name: "F3",
                  pitchClass: "F",
                  octave: 3, 
                  length: 8, 
                  dot:0
                })
CREATE (n3:Note {
                  name: "A3",
                  pitchClass: "A",
                  octave: 3, 
                  length: 4, 
                  dot:0
                })
CREATE (n4:Note {
                  name: "A3",
                  pitchClass: "A",
                  octave: 3, 
                  length: 16, 
                  dot:0
                })
CREATE (n5:Note {
                  name: "F3",
                  pitchClass: "F",
                  octave: 3, 
                  length: 16, 
                  dot:0
                })
CREATE (n6:Note {
                  name: "E3",
                  pitchClass: "E",
                  octave: 3, 
                  length: 16, 
                  dot:0
                })
CREATE (n7:Note {
                  name: "D3",
                  pitchClass: "D",
                  octave: 3, 
                  length: 16, 
                  dot:0
                })

// Create ordering relationships
(line)-[:START]->(n1)
CREATE (n1)-[:NEXT]->(n2)
CREATE (n2)-[:NEXT]->(n3)
CREATE (n3)-[:NEXT]->(n4)
CREATE (n4)-[:NEXT]->(n5)
CREATE (n5)-[:NEXT]->(n6)
CREATE (n6)-[:NEXT]->(n7)

// Add ties
CREATE (n3)-[:TIE]->(n4);
```
_For the full examples, see the [repository](https://github.com/ryanpstauffer/RheingoldGraph-Prototype) on Github_

It's easy to see how pedantic this process can become, and it certainly won't scale for a full piece.  Instead, we automate the load process from an existing computer representation of the musical score (for example, MusicXML).  For this demonstration, we wrote a simple Python MusicXML parser that parses a monophonic MusicXML score and adds it to our music graph.

#### Initial Graph
Regardless of what tool we use, we build each vertex (node) of the graph with specific properties, representing the essential information of pitch and rhythm.  We represent the note ordering via the edges connecting these nodes.  Assuming we have a single line with no chordal or polyphonic content, this graph will be a single-branched, directed acyclic graph.

Since this demonstration is aiming for simplicity and ease of explanation, we have encoded note information with both a name (“D3”) as well as separate properties for pitch class (“D”) and octave (3).  For the full implementation, we'll remove this duplicate property information, minimizing potential intra-vertex consistency issues and improving storage efficiency.  We also choose to encode note length as the inverse of the note’s duration in relation to a whole bar of music.  This means we represent an eighth note’s length as the integer 8.  To complete are representation of rhythm, we also must incorporate dot and tie information in our graph as well.  We encode the number of dots as a property of the Note vertex, and we encode a tie as an additional edge between vertices.

#### Playable Representation
Next, we transform this initial graph into a playable representation.  The main transformation is to combine length, dots and ties into a single representation of duration.  In order to allow for future variation in tempo, we define a duration in “ticks” instead of time.  Using a tick resolution (for example, 480 ticks per beat) that is larger than the least common multiple of all note durations that are found in the score, we can represent all durations as integers.  These integers can later be translated to an arbitrary duration in seconds based on the tempo of a given performance.
Since a core goal of our music graph is to facilitate natural and flexible analysis, we want to ensure that the linkage between symbolic and sonic representation remains a first-class citizen in our graph.  We ensure this with edges connecting our notation vertices to the vertices representing their sonic realization.

Here is our graph after we add our playable representation:
![alt text][BachCelloMusicGraphEx2]

### Querying our model
To query the above information (and create the image), we need to ensure that we retrieve our playable notes in the correct order.  Here is a sample Cypher query that gets us our playable notes along with their original notational representation.
```
MATCH (line:Line {name:"bach_xml"})-[r:START_PLAY|NEXT*]->(play:PlayableNote)
MATCH (play)<-[:PLAY_AS]-(note:Note)
RETURN line, play, note, size(r) AS Dist
ORDER BY Dist
```

Writing queries like this - even in a declarative language like Cypher - is something we prefer to abstract away from as in the full music graph.  For this reason, we use a simple API built out of a handful of classes and functions for our prototype.  Part III of this series will go into more detail on this API.  Until then, you can view all of the source code in the [RheingoldGraph-Prototype](https://github.com/ryanpstauffer/RheingoldGraph-Prototype) Github repository.


### Next steps
Now that some of the fundamental concepts and structure of the music graph have been laid out, the next part of this description will demonstrate an implementation of the music graph using an imperative language, explicitly defining our traversal and allowing streaming output directly from the graph to MIDI.  As we continue to extend this graph in the future, we will also have the opportunity to map the notation node to an actual sound itself.

CONCLUSION NEEDED


### Footnotes

Notated examples via [Noteflight](https://www.noteflight.com/)

Fascinating video from Xerox PARC describing one of the first attempts to build computer music notation software in 1980.  To give a sense of the time period this from John Maxwell devotes a few sentences describe the use of a new device called a "Mouse."
