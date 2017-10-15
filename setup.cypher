// Neo4j Setup Script to initially prepare the music graph

CREATE CONSTRAINT ON (note:Note) ASSERT note.uuid IS UNIQUE;
CREATE CONSTRAINT ON (line:Line) ASSERT line.name is UNIQUE;