
"""Write to a handful of file descriptors, to test the childFDs= argument of
reactor.spawnProcess()
"""

import os, sys

debug = 0

if debug: stderr = os.fdopen(2, "w")

if debug: print("this is stderr", file=stderr)

abcd = os.read(0, 4)
if debug: print("read(0):", abcd, file=stderr)
if abcd != "abcd":
    sys.exit(1)

if debug: print("os.write(1, righto)", file=stderr)

os.write(1, "righto")

efgh = os.read(3, 4)
if debug: print("read(3):", efgh, file=stderr)
if efgh != "efgh":
    sys.exit(2)

if debug: print("os.close(4)", file=stderr)
os.close(4)

eof = os.read(5, 4)
if debug: print("read(5):", eof, file=stderr)
if eof != "":
    sys.exit(3)

if debug: print("os.write(1, closed)", file=stderr)
os.write(1, "closed")

if debug: print("sys.exit(0)", file=stderr)
sys.exit(0)
