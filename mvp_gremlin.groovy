// Rheingold Gremlin MVP
println 'Rheingold-gremlin MVP'

graph = TinkerGraph.open()
g = graph.traversal()

// Create the musical line
l0 = g.addV('Line').property('name', 'bachCello').next()

// Create notes
n0 = g.addV('Note').property('name', 'D3').
                    property('pitchClass', 'D').
                    property('octave', 3).
                    property('length', 8).
                    property('dot', 0).next()

n1 = g.addV('Note').property('name', 'F3').
                    property('pitchClass', 'F').
                    property('octave', 3).
                    property('length', 8).
                    property('dot', 0).next()

n2 = g.addV('Note').property('name', 'A3').
                    property('pitchClass', 'A').
                    property('octave', 3).
                    property('length', 4).
                    property('dot', 0).next()

n3 = g.addV('Note').property('name', 'A3').
                    property('pitchClass', 'A').
                    property('octave', 3).
                    property('length', 1).
                    property('dot', 0).next()

n4 = g.addV('Note').property('name', 'F3').
                    property('pitchClass', 'F').
                    property('octave', 3).
                    property('length', 16).
                    property('dot', 0).next()

n5 = g.addV('Note').property('name', 'E3').
                    property('pitchClass', 'E').
                    property('octave', 3).
                    property('length', 16).
                    property('dot', 0).next()

n6 = g.addV('Note').property('name', 'D3').
                    property('pitchClass', 'D').
                    property('octave', 3).
                    property('length', 16).
                    property('dot', 0).next()

// Create ordering relationships
g.addE('start').from(l0).to(n0).next()
g.addE('next').from(n0).to(n1).next()
g.addE('next').from(n1).to(n2).next()
g.addE('next').from(n2).to(n3).next()
g.addE('next').from(n3).to(n4).next()
g.addE('next').from(n4).to(n5).next()
g.addE('next').from(n5).to(n6).next()

// Add ties
g.addE('tie').from(n2).to(n3).next()

println 'MVP Graph loaded'

// Get the notes in order for our line
temp1 = g.V().hasLabel('Line').has('name', 'bachCello').out('start').next()
temp2 = g.V(temp1).out('next').next()
// Continue iterating through this method
