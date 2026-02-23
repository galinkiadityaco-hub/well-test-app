import asyncio
import time 
from pymodbus.server import StartAsyncTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusDeviceContext, ModbusServerContext

async def run_server():
    data_1=[0]*7
    slave1=ModbusDeviceContext(
        ir=ModbusSequentialDataBlock(0,data_1),
        hr=ModbusSequentialDataBlock(0,data_1)
    )
    context=ModbusServerContext(slave1,single=True)
    context[1].setValues(4,0,[5,2,1])
   
    
    await StartAsyncTcpServer(context,address=('127.0.0.1',502))


if __name__=="__main__":
    print("Server running at 127.0.0.1 port 502")
    asyncio.run(run_server())
