import sys
from . import main

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt as e:
        print("Cancelled by user")
