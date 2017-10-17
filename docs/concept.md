# The Concept

[//]: # (Image References)

[ex2]: https://docs.google.com/drawings/d/e/2PACX-1vTcHhH99u6lWE00bMphRkEcwYNfcZjMMWhAsmiwxXB9RbjjPvV8yciBZpyy-v_bj7x0dVmuRnr4TGTx/pub?w=1415&h=905 "Music Graph with Playable Notes"

The goal here is to introduce the concept of the music graph.  We'll focus on high-level design and a few sample queries.  Future parts of this series will go into more detail on the exact implementation.

### What is RheingoldGraph?

The purpose of RheingoldGraph is to be a clean, flexible and extensible data system for storing and retrieving music information.  The final implementation of the music graph seeks to integrate music information from across multiple representational domains (see [Part II](storagemethods.md) for more information on music representation).  
Initially, the goal is to focus on the logical domain, which we can define as the core information required to represent a piece of music in both notation and performance - pitch, rhythm, harmony, tempo, dynamics, and articulation. (Footnote to Babbitt, MEI, and John Maxwell (1981) ).  Successful representation of the logical domain would include all of the information necessary to realize a piece of music in sonic form.


### Why do this at all?

RheingoldGraph has three reasons for existing:

1. As a store of musical information in a way that can immediately be put to use for music information retrieval (MIR) tasks
2. As an integral part of broader research into applying machine intelligence on music understanding
3. As a specific use case (music) to justify research into new data storage and retrieval concepts, insights from which can be applied to other (non-musical) domains.

In all three cases, our goal is to eventual have a clean abstraction above the lower levels issues of storing and retrieving music information.  With this in mind, the RheingoldGraph project seeks to streamline common low level data operations and eventually provide a clean API for use by both users and other future applications.

In all three cases, the goal is to improve on current storage methods.  An overview of current storage methods will be released in [Part II](storagemethods.md) of this series.

We can start 
    
We can demonstrate an example of this musical intelligence graph concept using Neo4j, an off-the-shelf property graph database.  We can also show the simplicity of this concept show using Cypher as a declarative query language.  Neo4j provides
There are a couple of reasons for these choices for an overview:
Neo4j Community is free and easy to run from a Docker image, meaning it’s simple and lightweight
Cypher is a clear, readable, declarative query language, suitable for demonstrations 
Neo4j includes a clean and simple GUI for query entry and immediate visualization of graph results without additional software or packages

Proposed methodology, using a simple melody line (from the opening of the Prelude from Bach’s Cello Suite No. 2 in d minor) as an example.
First, we build a music graph of the piece’s note information as it is contained in the printed score.  This information could be entered in the graph manually (via query language), or created by parsing an existing computer representation of the musical score (for example, MusicXML).
We build each node (vertex) of the graph with specific properties, representing the essential information of pitch and length.  We represent the note ordering via the relationships (edges) between these nodes.  Assuming we have a single line with no chordal or polyphonic content, this graph will be a single-branched, directed acyclic graph (TODO: confirm this terminology).
We make several choices to facilitate human readability of this graph, a requirement that we will relax in future phases of development.  Specifically, we have encoded note information with both a name (“D3”) as well as pitch class (“D”) and octave (3) information as separate properties.  This means we have repeated certain values in multiple properties.  While this technically breaks a rule we’d like to follow of not duplicating information, and is inefficient from a storage perspective, we allow for this duplication in this current example to facilitate human readability.  We also choose to encode note length as the inverse of the note’s duration in relation to a whole bar of music.  This means we represent an eighth note’s length as the integer 8.
There are two final details that we can dispense with shortly.  Because we choose to have our initial representation of our musical graph as being beholden to the notational specifics of the score, we must incorporate dot and tie information in our graph as well.  We encode a dot as a property of the Note node, and a tie as an additional edge between nodes.
Our musical graph, at this point, is as notable as much for what it leaves as for what it includes.  We dispense with several elements of written music at this point - barlines, key signature, and clef.  The logic for the choices will be made clear shortly.
Once we have built our initial representation of the notational aspects of our musical score, we transform these nodes into a playable representation.  Pitch in this case remains the same (we are not dealing with a transposing instrument).  We combine length, dots and ties into a single representation of duration.  We do not want to explicitly attach our representation to tempo, so instead of duration in time we define a duration in “ticks.”  We choose a tick resolution (for example, 480 ticks per beat) that is higher than the smallest quantization of rhythm found in the score, and at minimum the least common multiple of all note durations that are found in the score.  With these choices, we can represent all durations in a piece as integers.  The integers can then be translated to arbitrary duration in seconds by applying our “ticks per beat” to the “beats per minute” tempo of a given performance.
Since a core goal of our music graph is to facilitate natural and flexible analysis, we want to ensure that the linkage between symbolic and sonic representation remains a first-class citizen in our graph.  We allow for this by maintaining an edge mapping notation nodes to the nodes representing their sonic realization.  As we continue to extend this graph in the future, we will have the opportunity to additionally map the notation node to an actual sound itself.
    
    Once this is complete


Here is what we've built so far:

![alt text][ex2]



    


Querying the graph model with Cypher (declarative language)

(Example of getting the playable notes in order, and also the original notational representation)

```
MATCH (line:Line {name:"bach_xml"})-[r:START_PLAY|NEXT*]->(play:PlayableNote)
MATCH (play)<-[:PLAY_AS]-(note:Note)
RETURN line, play, note, size(r) AS Dist
ORDER BY Dist
```



## API

Writing the queries shown above - even in a declarative language such as Cypher - is something we would prefer to abstract away from as we build our music graph.  For this reason, we use a simple API built out of a handful of classes and functions.  This is a brief discussion of the initial "toy" API built to prove out the concept.  All of the source code implementing what is described below can be found in the [RheingoldGraph-Prototype](https://github.com/ryanpstauffer/RheingoldGraph-Prototype) Github repository.




While we may see a declarative query language as a handicap for its lack of execution specificity, it can still prove to quickly be a very powerful analytical tool. 


Next steps
Now that some of the fundamental concepts and structure of the music graph have been laid out, the next part of this description will demonstrate an implementation of the music graph using an imperative language, explicitly defining our traversal and allowing streaming output directly from the graph to MIDI.

Extensions

Many of the concepts of the music graph can be extended to other domains, because at its heart, the music graph is about storing arbitrary relationships and temporal information.
