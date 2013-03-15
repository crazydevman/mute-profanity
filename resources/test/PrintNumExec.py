#!/usr/bin/env python

import time
import sys

def main():
    count = int(sys.argv[1])
    i = 0
    while i < count:
        time.sleep(0.1)
        i += 1
        print i
        sys.stdout.flush()

if __name__ == "__main__":
    main()