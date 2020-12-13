import asyncio
msgs = [b'Hello I am Raspi  ',b'I am from space     ',b'Nice to meet u']
c = 0
class EchoServer(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport
    def data_recieved(self,data):
        im = data.decode('utf-8')
        if im[0] =='H':
            self.transport.write(msgs[0])
        if im[0] =='I':
            self.transport.write(msgs[1])
        else:
            self.transport.write(msgs[2])
        
loop = asyncio.get_event_loop()
coro= loop.create_server(EchoServer,'',10000)
server = loop.run_until_complete(coro)
try:
    loop.run_forever()
except:
    pass

server.close()
loop.run_until_complete(server.wait_closed())
loop.close()
        