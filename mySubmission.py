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
    # create Dict[loadNumber, heap[(float, Load)]], representing closest pickups from loadNumber dropoff
    closestPickups = defaultdict(lambda: [])
    for loadA in self.loads.values():
      for loadB in self.loads.values():
        heapq.heappush(closestPickups[loadA.dropoff], 
          (self.calcEuclidDist(loadA.dropoff, loadB.pickup), loadB))
    
    origin = Location(0, 0)
    for load in self.loads.values():
      heapq.heappush(closestPickups[origin],
        (self.calcEuclidDist(origin, load.pickup), load))

    delivered = set()
    currTime = 0
    curLoc = origin
    solution = [[]]
    while len(delivered) != len(self.loads):
      dist, nextLoad = closestPickups[curLoc][0]
      while nextLoad.loadNumber in delivered:
        heapq.heappop(closestPickups[curLoc])
        dist, nextLoad = closestPickups[curLoc][0]

      addedTime = dist + self.calcEuclidDist(nextLoad.pickup, nextLoad.dropoff) + \
        self.calcEuclidDist(nextLoad.dropoff, origin)
      if currTime + addedTime >= 12 * 60:
        solution.append([])
        curLoc = origin
        currTime = 0
      else:
        heapq.heappop(closestPickups[curLoc])
        solution[-1].append(nextLoad.loadNumber)
        delivered.add(nextLoad.loadNumber)
        currTime += dist + self.calcEuclidDist(nextLoad.pickup, nextLoad.dropoff)

    return solution
  
  def calcEuclidDist(self, locA, locB):
    return math.sqrt((locA.x - locB.x) ** 2 + (locA.y - locB.y) ** 2)
    
if __name__ == "__main__":
  if len(sys.argv) < 2:
    raise ValueError("Problem path not specified")

  vrpSolver = VRPSolver(sys.argv[1])
  solution = vrpSolver.solve()
  for driverPath in solution:
    print(driverPath)
