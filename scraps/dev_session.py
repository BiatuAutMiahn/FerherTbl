# import sys
# sys.path.append(".")

# Run Tests
import InfCommon as Inf
import time
session=Inf.Session("DevSessionTest","20190622022734")
print(vars(session))
session.Start()
print(vars(session))
time.sleep(5)
session.Close()
