import math
import sys 
from typing import Dict, List, Tuple

class LoadNumber(int):
  pass

class Location():
  def __init__(self, x: int, y: int):
    self.x = x
    self.y = y

class Load():
  def __init__(self, pickup: Location, dropoff: Location):
    self.pickup = pickup
    self.dropoff = dropoff

class Route():
  def __init__(self, path: List[LoadNumber], cost: int):
    self.path = path
    self.cost = cost

class VRPSolver():
  def __init__(self, problemPath: str):
    try:
      f = open(problemPath, "r")
      content = f.read()
      f.close()
    except:
      print(f"Could not read file at path '{problemPath}'")

    self.loads: Dict[LoadNumber, Load] = {}
    entries = content.splitlines()
    for entry in entries[1:]:
      tokens = entry.split()
      loadNumber = int(tokens[0])
      pickup = tokens[1][1:-1].split(",")
      pickupLoc = Location(float(pickup[0]), float(pickup[1]))
      dropoff = tokens[2][1:-1].split(",")
      dropoffLoc = Location(float(dropoff[0]), float(dropoff[1]))
      self.loads[loadNumber] = Load(pickupLoc, dropoffLoc)
    
  def solve(self):
    origin = Location(0, 0)
    savings: Dict[Tuple[LoadNumber, LoadNumber], float] = {}
    for numA, loadA in self.loads.items():
      for numB, loadB in self.loads.items():
        if numA == numB:
          continue
        savings[(numA, numB)] = self.calcEuclidDist(origin, loadA.dropoff) + self.calcEuclidDist(origin, loadB.pickup) \
          - self.calcEuclidDist(loadA.dropoff, loadB.pickup)
    
    savingsDesc = sorted(savings.items(), key=lambda item: item[1], reverse=True)
    routes: Dict[LoadNumber, Route] = {}
    for (numA, numB), saving in savingsDesc:
      loadA = self.loads[numA]
      loadB = self.loads[numB]
      # LoadA and LoadB have no assigned route, connect them if possible
      if not numA in routes and not numB in routes:
        pathCost = self.calcPathCost([numA, numB])
        if pathCost <= 12 * 60:
          routes[numA] = routes[numB] = Route([numA, numB], pathCost)
      # LoadA xor LoadB have an assigned route, add new load to existing route if possible
      elif not numA in routes or not numB in routes:
        aIsRouted = numA in routes
        if aIsRouted and routes[numA].path[-1] != numA:
          continue
        elif not aIsRouted and routes[numB].path[0] != numB:
          continue
        existingRoute = routes[numA] if aIsRouted else routes[numB]
        addedLoad = loadB if aIsRouted else loadA
        newCost = existingRoute.cost - saving + self.calcEuclidDist(origin, addedLoad.pickup) \
          + self.calcEuclidDist(addedLoad.pickup, addedLoad.dropoff) + self.calcEuclidDist(addedLoad.dropoff, origin) 
        if newCost > 12 * 60:
          continue
        existingRoute.cost = newCost
        if aIsRouted:
          existingRoute.path.append(numB)
          routes[numB] = existingRoute
        else:
          existingRoute.path.insert(0, numA)
          routes[numA] = existingRoute
      # LoadA and LoadB have an assigned route, merge their routes if possible
      else:
        aRoute = routes[numA]
        bRoute = routes[numB]
        if aRoute.path[-1] != numA or bRoute.path[0] != numB:
          continue
        if aRoute.path[0] == numB or bRoute.path[-1] == numA:
          continue
        newCost = aRoute.cost + bRoute.cost - saving
        if newCost > 12 * 60:
          continue
        aRoute.cost = newCost
        aRoute.path += bRoute.path
        for numB in bRoute.path:
          routes[numB] = aRoute

    # Dispatch individual drivers for each remaining load
    for loadNum in self.loads:
      if loadNum in routes:
        continue
      routes[loadNum] = Route([loadNum], -1)

    solution = set(routes.values())
    return [route.path for route in solution]
  
  def calcPathCost(self, path):
    prev = Location(0, 0)
    pathTime = 0
    for loadNum in path:
      pathTime += self.calcEuclidDist(prev, self.loads[loadNum].pickup)
      pathTime += self.calcEuclidDist(self.loads[loadNum].pickup, self.loads[loadNum].dropoff)
      prev = self.loads[loadNum].dropoff
    pathTime += self.calcEuclidDist(prev, Location(0, 0))
    return pathTime
  
  def calcEuclidDist(self, locA, locB):
    return math.sqrt((locA.x - locB.x) ** 2 + (locA.y - locB.y) ** 2)
    
if __name__ == "__main__":
  if len(sys.argv) < 2:
    raise ValueError("Problem path not specified")

  vrpSolver = VRPSolver(sys.argv[1])
  solution = vrpSolver.solve()
  for driverPath in solution:
    print(driverPath)
