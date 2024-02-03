import sys 

class Location():
  def __init__(self, x, y):
    self.x = x
    self.y = y

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
      print(f"Could not read file at path '{file_path}'")

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
    
if __name__ == "__main__":
  if len(sys.argv) < 2:
    raise ValueError("Problem path not specified")

  vrpSolver = VRPSolver(sys.argv[1])