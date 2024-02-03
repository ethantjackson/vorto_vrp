from collections import defaultdict
import heapq
import math
import sys 

class Location():
  def __init__(self, x, y):
    self.x = x
    self.y = y
  
  def __hash__(self):
    return hash((self.x, self.y))

class Load():
  def __init__(self, loadNumber, pickup, dropoff):
    self.loadNumber = loadNumber
    self.pickup = pickup
    self.dropoff = dropoff

class Route():
  def __init__(self, path, cost):
    self.path = path
    self.cost = cost

class VRPSolver():
  def __init__(self, problemPath):
    try:
      f = open(problemPath, "r")
      content = f.read()
      f.close()
    except:
      print(f"Could not read file at path '{problemPath}'")

    # create Dict[loadNumber, Load]
    self.loads = {}
    entries = content.splitlines()
    for entry in entries[1:]:
      tokens = entry.split()
      loadNumber = int(tokens[0])
      pickup = tokens[1][1:-1].split(",")
      pickupLoc = Location(float(pickup[0]), float(pickup[1]))
      dropoff = tokens[2][1:-1].split(",")
      dropoffLoc = Location(float(dropoff[0]), float(dropoff[1]))
      self.loads[loadNumber] = Load(loadNumber, pickupLoc, dropoffLoc)
    
  def solve(self):
    origin = Location(0, 0)
    savings = {}
    for numA, loadA in self.loads.items():
      for numB, loadB in self.loads.items():
        if numA == numB:
          continue
        savings[(numA, numB)] = self.calcEuclidDist(origin, loadA.dropoff) + self.calcEuclidDist(origin, loadB.pickup) \
          - self.calcEuclidDist(loadA.dropoff, loadB.pickup)
    
    savingsDesc = sorted(savings.items(), key=lambda item: item[1], reverse=True)
    routes = {}
    for (numA, numB), saving in savingsDesc:
      loadA = self.loads[numA]
      loadB = self.loads[numB]
      if not numA in routes and not numB in routes:
        pathCost = self.calcPathCost([numA, numB])
        if pathCost <= 12*60:
          routes[numA] = routes[numB] = Route([numA, numB], pathCost)

      elif not numA in routes or not numB in routes:
        aIsRouted = numA in routes
        if aIsRouted and routes[numA].path[-1] != numA:
          continue
        elif not aIsRouted and routes[numB].path[0] != numB:
          continue
        route = routes[numA] if aIsRouted else routes[numB]
        addedLoad = loadB if aIsRouted else loadA
        newCost = route.cost - saving + self.calcEuclidDist(origin, addedLoad.pickup) \
          + self.calcEuclidDist(addedLoad.pickup, addedLoad.dropoff) + self.calcEuclidDist(addedLoad.dropoff, origin) 
        if newCost > 12*60:
          continue
        route.cost = newCost
        if aIsRouted:
          route.path.append(numB)
          routes[numB] = route
        else:
          route.path.insert(0, numA)
          routes[numA] = route

    for loadNum in self.loads:
      if loadNum in routes:
        continue
      routes[loadNum] = Route([loadNum], -1)
    # print(routes)
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
  
  def calcCost(self, numDrivers, totalTime):
    return 500 * numDrivers + totalTime

  def calcEuclidDist(self, locA, locB):
    return math.sqrt((locA.x - locB.x) ** 2 + (locA.y - locB.y) ** 2)
    
if __name__ == "__main__":
  if len(sys.argv) < 2:
    raise ValueError("Problem path not specified")

  vrpSolver = VRPSolver(sys.argv[1])

  solution = vrpSolver.solve()
  for driverPath in solution:
    print(driverPath)
