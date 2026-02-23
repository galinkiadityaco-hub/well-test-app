from pymodbus.client import ModbusTcpClient
import struct
import json
import time 
from datetime import datetime
from pathlib import Path
import requests

def new_entry(slave_id,id,success,description):
    #test_description=f"Test Performed for testid={id} in slave {slave_id}"
    test_description=description
    result="PASS" if success==True else "FAIL"
    time_stamp=datetime.now().strftime("%d%m%Y%H%M%S")
    entry={"id":id,"Description":test_description,"Result":result}
    Test_file=TEST_FOLDER+"/test_results_"+time_stamp+".json"
    file_contents=[]
    file_contents.append(entry)

    with open(Test_file,"w") as f:
        json.dump(file_contents,f,indent=4)
        print("new entry made in results folder")
    
    requests.post("http://127.0.0.1:5000/push",json=entry)
    print("sent data to web_server")

def config():
    with open("config.json","r") as f:
        return json.load(f)

failure_subsequence_number1=-1

def Test_subsequence(client,slave_id,id,oper,seq,choke_val):
    write_hr_id_oper_seq_choke_val(client,0,slave_id,id,oper,seq,choke_val)
    count=0
    while(read_ir(client,0,slave_id)!=seq and count<300):
        count+=5
        print("waiting")
        time.sleep(5)
    if(read_ir(client,0,slave_id)==seq and read_ir(client,1,slave_id)==2):
        return True
    else:
        return False

def Test_1(client,slave_id,id,oper,choke_val):
    global  failure_subsequence_number1
    success=True
    for seq in range(1,5):
        if(Test_subsequence(client,slave_id,id,oper,seq,choke_val)==False):
            success=False
            failure_subsequence_number1=seq
            print(f"failure at {failure_subsequence_number1}")
            break
        else:
            print(f"successful in test with seq= {seq}")
    new_entry(slave_id,id,success,"Test well routing from production to test")

def Test_2(client,slave_id,id,oper,choke_val):
    success=True
    if(Test_subsequence(client,slave_id,id,oper,5,choke_val)==False):
        success=False
        print(f"failure at 5")
        new_entry(slave_id,id,success,"Test well routing from test to production")
        
    else:
        print(f"succesfull in the test with seq = 5 ")
    if(success==True):Test_3(client,slave_id,id,oper,choke_val)

def Test_3(client,slave_id,id,oper,choke_val):
    success=True
    if(Test_subsequence(client,slave_id,id,oper,6,choke_val)==False):
        success=False
        print(f"failure at 6")
    else:
        print(f"succesfull in the test with seq = 6 ")
    new_entry(slave_id,id,success,"Test well routing from test to production")

def read_ir(client,reg,slave_id):
    temp_register=client.read_input_registers(reg,count=1,device_id=slave_id)
    return temp_register.registers[0]

def read_ir_float(client,reg,slave_id):
    temp_register=client.read_input_registers(reg,count=2,device_id=slave_id)
    raw_bytes=struct.pack('<HH',temp_register.registers[0],temp_register.registers[1])
    value=struct.unpack('<f',raw_bytes)
    print(value)
    return value

def write_hr_id_oper_seq_choke_val(client,reg,slave_id,id,oper,seq,choke_val):
    float_registers=hr_float_value_to_endian_convertor(choke_val)
    client.write_registers(reg,[id,oper,seq,float_registers[0],float_registers[1]],device_id=slave_id)
    print(f"Written into id,oper,seq,choke_val = {id},{oper},{seq},{float_registers[0]},{float_registers[1]}")

def hr_float_value_to_endian_convertor(value):
    float_bytes=struct.pack('<f',value)
    two_register=struct.unpack('<HH',float_bytes)
    return list(two_register)

if __name__=="__main__":
    specs=config()
    client=ModbusTcpClient(specs['host'],port=specs['port'])
    slave_id=specs['slave_id']
    TEST_FOLDER=specs['results_folder']
    Path(TEST_FOLDER).mkdir(parents=True,exist_ok=True)
    if client.connect():
        Test_1(client,slave_id,1,1,50)
        Test_2(client,slave_id,2,2,99.55)
        client.close()