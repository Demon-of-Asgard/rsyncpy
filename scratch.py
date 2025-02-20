import datetime as dt 
import pathlib as plib

now = dt.datetime.now() 
delta = dt.timedelta(days=2)
print(f"{now=} {delta=} {now+delta=}")

test = plib.Path("test")

try:
    test.mkdir()
except FileExistsError:
    print(f"{test} already exist.")