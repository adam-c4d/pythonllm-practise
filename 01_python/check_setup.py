import sys
import numpy, pandas, sklearn, fastapi

print("Python:", sys.version.split()[0])
print("Interpreter:", sys.executable)
for lib in (numpy, pandas, sklearn, fastapi):
    print(f"{lib.__name__:10} {lib.__version__}")
