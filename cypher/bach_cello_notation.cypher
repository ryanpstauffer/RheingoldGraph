// Bach Cello Suite No. 2, Prelude (first measure)

// Create the line
CREATE (line:Line {name: 'bach_cello'})

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

// Map all notes to the line
(n1)-[:IN_LINE]->(line)
(n2)-[:IN_LINE]->(line)
(n3)-[:IN_LINE]->(line)
(n4)-[:IN_LINE]->(line)
(n5)-[:IN_LINE]->(line)
(n6)-[:IN_LINE]->(line)
(n7)-[:IN_LINE]->(line)

// Create ordering relationships
(line)-[:START]->(n1)
(n1)-[:NEXT]->(n2)
(n2)-[:NEXT]->(n3)
(n3)-[:NEXT]->(n4)
(n4)-[:NEXT]->(n5)
(n5)-[:NEXT]->(n6)
(n6)-[:NEXT]->(n7)

// Add ties
(n3)-[:TIE]->(n4)






