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

class Driver():
  def __init__(self, location):
    self.location = location
    self.driveTime = 0
    self.loadPath = []

  def __lt__(self, other):
    return self.driveTime < other.driveTime

  def __str__(self):
    return f"Driver driveTime: {self.driveTime}, loadPath: {self.loadPath}"

  def __repr__(self):
    return f"Driver driveTime: {self.driveTime}, loadPath: {self.loadPath}"

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
    
  def solve(self, numDrivers):
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
    finishedDrivers = []
    driverHeap = [(closestPickups[origin][0][0], Driver(origin)) for _ in range(numDrivers)]
    totalTime = 0
    while len(delivered) != len(self.loads):
      if not driverHeap:
        return (float('inf'), [])

      _, driver = heapq.heappop(driverHeap)
      curLoc = driver.location
      dist, nextLoad = closestPickups[curLoc][0]
      if nextLoad.loadNumber in delivered:
        while nextLoad.loadNumber in delivered:
          heapq.heappop(closestPickups[curLoc])
          dist, nextLoad = closestPickups[curLoc][0]
        heapq.heappush(driverHeap, (dist, driver))
        continue

      addedTime = dist + self.calcEuclidDist(nextLoad.pickup, nextLoad.dropoff) + \
        self.calcEuclidDist(nextLoad.dropoff, origin)
      currTime = driver.driveTime
      if currTime + addedTime >= 12 * 60:
        finishedDrivers.append(driver)
      else:
        heapq.heappop(closestPickups[curLoc])
        if closestPickups[curLoc]:
          heapq.heappush(driverHeap, (closestPickups[curLoc][0][0], driver))
        driver.loadPath.append(nextLoad.loadNumber)
        driveTime = dist + self.calcEuclidDist(nextLoad.pickup, nextLoad.dropoff)
        driver.driveTime += driveTime
        totalTime += driveTime
        driver.location = nextLoad.dropoff
        delivered.add(nextLoad.loadNumber)

    return (self.calcCost(numDrivers, totalTime), 
            [driver.loadPath for driver in finishedDrivers] + [driver.loadPath for _, driver in driverHeap])
  
  def calcCost(self, numDrivers, totalTime):
    return 500 * numDrivers + totalTime

  def calcEuclidDist(self, locA, locB):
    return math.sqrt((locA.x - locB.x) ** 2 + (locA.y - locB.y) ** 2)
    
if __name__ == "__main__":
  if len(sys.argv) < 2:
    raise ValueError("Problem path not specified")

  vrpSolver = VRPSolver(sys.argv[1])
  minCost = float('inf')
  bestSolution = []

  for i in range(1, len(vrpSolver.loads) + 1):
    cost, solution = vrpSolver.solve(i)
    if cost < minCost:
      minCost = cost
      bestSolution = solution

  for driverPath in bestSolution:
    print(driverPath)
