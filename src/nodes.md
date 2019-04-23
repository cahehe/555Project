
## DV-Hop:

Computes a location estimate based on distance vectors

### Overview:

  - The algorithm first performs several distance vector computations --one for each reference node (rover)
  - The reference nodes compute a "correction value" based on the density of the network in each "direction"
  - The nodes relay these correction values until each node has received one
  - Each node uses its correction values multiplied by hop distances to approximate the true distances from each reference
  - Each node then triangulates its position based on these coarse distance estimates

### Results:

  - The estimate sure is coarse!
  - Networks that aren't well connected or have non-uniform density perform extra horribly
  - Nodes often calculate the same position

## DV-Distance:

Computes a location estimate based on distance vectors weighted by hop distance

### Overview:

  - The algorithm first performs several distance vector computations --this time weighted by actual distance
  - Each node then triangulates its position based on these distance estimates

### Results:

  - The estimate is just as coarse, but this time biased away from the center
  - Nodes almost never calculate the same position

