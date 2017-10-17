# Overview of Current Music Information Storage Methods

This comparison will be a significant part of my paper.

References:

* MusicXML paper (can I find one)
    - And discussion of why XML databases are not optimal

* Improvement ofn MusicXML paper...?


### Domains of Music Representation

There have been different attempts to clearly define the domains of music representation.

Babbitt

MEI


 Music information, in this case, refers to the information that is necessary to realize a piece of music in sonic form.  (Something about information needed to recreate the musical sound itself - not exactly, as a recording or Midi representation would, but from the point of view of the composer.)  A successful graph representation of a piece of music would contain the information necessary to perform it, analyze it, and compare it to other pieces of music.  This would mean that this graph representation would also contain the information necessary to  
This is distinct from music metadata, which is information about a piece of music, but is not directly related to realizing the music in aural form.  Metadata can be a very important in musical analysis, cataloguing, and recommendation systems, but is ancillary to the current problem at hand.
Likewise, this discussion of musical information is makes a distinction between representing the information that would allow for a sonic performance of a musical piece, and the information that provides a direct recreation of the sounds themselves (analog and digital recordings).


Without attempting to enter into a semantic debate on these domain names, the clear focus of this music data system is to store music information in the _logical_ domain

* Logical
* 'Gestural' (I hate this word, but need to find a better version of it - is there something from Curtis' book?)
* Analytical
* Graphical (avoid the use of this term b/c it will be confused with my GRAPH represenation)




The goal of this proposed data system for music representation is to not just encourage the storage of music information from multiple domains, but to explicitly link these representations.

The primary focus of early research is the logical domain.  The goal is to be able to encode and manipulate the core music ideas that a archetypal composer might have.  The goal of the logical domain is to capture, as clearly as possible and without excess - the composer's _intent_, free of editorial addition.  We might imagine the logical reprentation as a dismbodied abstraction of an Urtext score.  While in some modern music we may regard the layout of notes on the physical page of sheet music as an integral part of a composer's intent (For example, (Cage, etc)), in most Common Practice Period works we do not generally consider a change in the typesetting of the music to have an impact on it logic.
These ideas are chiefly concerned with the pitch and rhythm concepts the make up the simplest version of a piece.

Performance-specific information - what the MEI refers to as the 'gestural' domain - will be modelled last.


A Notational representation of music can be largely derived from the information we have derived in our logical representation.  If we are to be as true to our definition of 'logical,' we might go so far as to say a notational representaion of music - if it is perfectly true to the composers' intent - should contain information if and only if it appears 


This discussion is not focused on the audio features of recorded music.

How we store music information today:
Most human musicians produce and consume musical information in the form of symbolic musical notation.  This symbolic notation provides instructions to produce a composer’s desired pitches and timbres, as well as the alignment of these sounds in time.
This symbolic notation, while excellent for performance and human analysis, does not convey musical information in a way that can be directly stored and analyzed by a machine.  Why do we care about this?  We’d like an abstraction that allows for easy storage, retrieval, streaming performance, and analysis.

The specifics of the graph implementation will be discussed in a future part of this series.  In this part, we assume that we have a workable graph database as a backend, and an API wrapper that allows for the insertion and retrieval of specific parts of the musical graph.


We can note here an obvious observation - music is inherently temporal.  We can analyze a musical piece at different resolutions.  Taking a multi-movement work, such as a symphony, we can detail the succession of movement tempi and keys.  Within a single movement, we can note a structure of musical form (for example, sonata-allegro form).  Within a section, we can note the repetition and ordering of different phrase groups, subdivide further into phrases, then into notes.  Since a single note itself is perceived as variations in air pressure by our ears, .While we can observe and analyze a musical piece at different resolution.  We can s

We can break down the common methods of storing and representing musical information for computer or computer-aided analysis into two different buckets.


To add context to the following discussion, we can imagine a simple melodic analysis.
Detail here


MIDI representation and similar
Description

As a representation of the logical domain of music, MIDI representation poses certain issues.  It is impossible to separate a MIDI score from the performance-specific elements.  Even when a score is transcribed with exacting rhythm and pitch (which we might take as a clean representation of a composer's intent), the fact that we must by definition include dynamic content in our MIDI representation (stored as velocity) means that we can never escape the tyranny of a particualar performace.

Pros

Cons
Representations intended to reflect the pitch and duration of the musical notes in order to recreate a specific performance.  The best known of these is MIDI.  While quite effective in live performance settings, as well as for storing detailed representations of a performance, this type of storage is limited to pitch and time information.  Concurrency is not a first-class citizen - because MIDI information, whether live or saved to disk, are a serialized format, true concurrency is not supported. 

Even assuming that the MIDI performance we have saved is a 'canonical performance' representing the proper pitch, rhtyhm and dynamic content, the fact that MIDI is by definition a serialized representation poses several serious issues.  This means that true concurrebcy is not supported, violating our goals on 3 core levels:
1- Logical - Without concurrency we can never have a perfect logical represenation of a non-monophonic composers score, and even the order of note serialization for chordal content implies that there is the addition of 'interpretation' related to this ordering (in the form of a forced arpeggiation)
2 - Analysis - because we have to interpret 

Text-based representation
MusicXML, Lilypad, 

Pros
When built correctly, adequately contains all of the composer’s information conveyed on the page

Cons
Concise version are too simplistic to allow for arbitrary information to be added to the model
More flexible versions, such as MusicXML, can be extended to allow the addition of arbitrary, but suffer from many issues


Our goal is to store an arbitrary amount of musical information.  We should be able to change at will the tools we decide to apply for a particular analytical or performance task, without having to alter the technique of storage itself.

Representations intended to reflect music notation symbols themselves.  A common example of this is MusicXML, but there are many other examples of such a system.
    
The impetus for the creation of the music graph is to have a “third way.”  If we think from the perspective of a machine, we can free ourselves of many of the preconceptions we have about what music representation should be.  We can find that many part of musical information that are important in our 
A computer program doesn’t care about a musical staff
What can we dispense with
Musical staff: this is a construct to allow for pitches to be identified in human music notation.  If we 

    


By migrating musical representation from XML to a graph, we also simplify the addition of new information on notes at an arbitrary location within the piece.  Using the XML model, we are required to write in the middle of a file, which makes for more difficult file system operations.  In a graph representation, backed by a graph database, it is trivially easy to add metadata or information on top of an existing melody line.  In addition, we do not “weigh down” the existing information.  One can simply ignore this new information by choosing to traverse only the previously existing details.  Thus, we do not increase the parsing time to do common analysis operations.



References
