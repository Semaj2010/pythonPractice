import asyncio

@asyncio.coroutine
def receiver():
    print("Ready to receive")
    while True:
        n = (yield)
        print("Got %s" % n)

r = receiver()
r.__next__()
r.send(1)
r.send(2)
r.send("Hello World")
r.close()