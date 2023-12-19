'''
$ tftp ip_address [-p port_mumber] <get|put> filename
'''
# 필요한 모듈 임포트
import socket
import argparse
from struct import pack

# TFTP 프로토콜을 위한 상수 정의
DEFAULT_PORT = 69
# 데이터 512byte 단위로 수행
BLOCK_SIZE = 512    
# 전송 모드는 octet으로 지정
DEFAULT_TRANSFER_MODE = 'octet' 


# TFTP 작업을 위한 Opcode 값
OPCODE = {'RRQ': 1, 'WRQ': 2, 'DATA': 3, 'ACK': 4, 'ERROR': 5}  
#TFTP에서 정의한 전송 모드. 본 코드에서는 octet 사용
MODE = {'netascii': 1,'octet': 2, 'mail': 3}    

#TFTP에서의 오류 코드와 그 의미
ERROR_CODE = {
    0: "Not defined, see error message (if any).",
    1: "File not found.",
    2: "Access violation.",
    3: "Disk full or allocation exceeded.",
    4: "Illegal TFTP operation.",
    5: "Unknown transfer ID.",
    6: "File already exists.",
    7: "No such user."
}

# 서버로 WRQ를 전송하는 함수
def send_wrq(filename, mode):
    # TFTP 형식애 따라 struct.pack을 사용하여 WRQ 메시지 패킹
    format = f'>h{len(filename)}sB{len(mode)}sB'
    wrq_message = pack(format, OPCODE['WRQ'], bytes(filename, 'utf-8'), 0, bytes(mode, 'utf-8'), 0)
    # WRQ 메시지를 서버로 전송
    sock.sendto(wrq_message, server_address)
    print("wrq_message:",wrq_message)

# 서버로 RRQ를 전송하는 함수
def send_rrq(filename, mode):
    # TFTP 형식에 따라 struct.pack을 사용하여 RRQ 메시지 패킹
    format = f'>h{len(filename)}sB{len(mode)}sB'
    rrq_message = pack(format, OPCODE['RRQ'], bytes(filename, 'utf-8'), 0, bytes(mode, 'utf-8'), 0)
    # RRQ 메시지를 서버로 전송
    sock.sendto(rrq_message, server_address)
    print("rrq_message:",rrq_message)
    
# 서버에게 ACK을 보내는 함수
def send_ack(seq_num, server):
    # TFTP 형식에 띠리 struct.pack을 사용하여 ACK 메시지 패킹
    format = f'>hh'  
    ack_message = pack(format, OPCODE['ACK'], seq_num)
    # ACK 메시지 서버로 전송
    sock.sendto(ack_message, server)
    print("seq_num:", seq_num)
    print("ack_message:", ack_message)

#서버로부터 데이터 받는 함수
def receive_data(filename):
    # 기대되는 블럭 번호 초기화
    expected_block_number=1
    # 수신 된 데이터를 쓸 이진 쓰기 모드로 파일 열기
    file = open(filename, 'wb')
    while True:
        # 서버는 데이터를 전송하기 위해 새로운 포트 생성
        # 데이터와 서버의 새 소켓 주소 받음
        data, server_new_socket = sock.recvfrom(516)
        # 수신된 데이터에서 Opcode 추출
        opcode = int.from_bytes(data[:2], 'big')
        
        # 메시지 유형 확인 후 메시지 유형이 DATA면 실행
        if opcode == OPCODE['DATA']:
            # 수신된 데이터에서 블록 번호 추출
            block_number = int.from_bytes(data[2:4], 'big')
            # 블록 번호가 기대한 번호와 같다면 실행
            if block_number == expected_block_number:
                # 받은 블록에 대해서 ACK 보내기
                send_ack(block_number, server_new_socket)
                # 데이터에서 파일 블록 추출하고 파일에 작성
                file_block = data[4:]
                file.write(file_block)
                expected_block_number = expected_block_number +1
                print("--File content--")
                print(file_block.decode())
            # 블록 번호가 기대한 번호와 다르면 실생(데이터 전송 중 오류)
            else:
                # 현재 블록 번호에 대한 승인 다시 보내기
                send_ack(block_number, server_new_socket)
        # 메시지 유형이 ERROR면 실행
        elif opcode == OPCODE['ERROR']:
            # 서버로부터 받은 오류 처리
            error_code = int.from_bytes(data[2:4], byteorder='big')
            print(ERROR_CODE[error_code])
            break

        # 메시지 유형이 DATA, ERROR가 모두 아닐 경우 실행
        else:
            break

        #파일 블록이 블록 크기보다 작을 때(마지막 데이터일 때) 파일 닫기
        if len(file_block) < BLOCK_SIZE:    
            file.close()
            print("File downloading complete.")
            break


#서버에 데이터를 전송하는 함수
def send_data(filename):
    # 소켓의 타임아웃 설정
    sock.settimeout(5)
    # ACK과 서버 주소 받기
    ack, address = sock.recvfrom(4)
    try:
        # 이진 읽기 모드로 파일 열기
        with open(filename, 'rb') as file:
            block_number = 1

            while True:
                # 파일에서 데이터 블록 읽기
                file_block = file.read(BLOCK_SIZE)
                if not file_block:
                    break
                
                # TFTP 형식에 따라 데이터 패킷 패킹
                data_packet = pack(f'>hh{len(file_block)}s', OPCODE['DATA'], block_number, file_block)
                # 데이터 패킷을 서버로 전송
                sock.sendto(data_packet, address)
                print(f"Sent block {block_number}")
                
                try:
                    # 서버로부터 승인 받기
                    ack, address = sock.recvfrom(4)
                    ack_opcode = int.from_bytes(ack[:2], 'big')
                    ack_block_number = int.from_bytes(ack[2:], 'big')

                    # Opcode가 ACK이고, ACK의 블록 넘버가 기존의 블록 넘버와 같으면 실행(정상적인 데이터 전송)
                    if ack_opcode == OPCODE['ACK'] and ack_block_number == block_number:
                        block_number += 1
                        print(f"{ack_block_number} ACK received.")
                    
                    # 비정상적인 데이터 전송일 시 실행
                    else:   
                        print("Unexpected ACK.\nRetrying...")
                # 설정한 시간이 지나면 종료(timeout)
                except socket.timeout:
                    print("Timeout.\nRetrying...")
                
                # 파일 블록이 블록 크기보다 작을 때(마지막 데이터일 때) 소켓 닫기
                if len(file_block) < 512:
                    print("File uploading complete.")
                    sock.close()
                    break
                
                # 파일 블록이 블록 크기보다 크거나 같을 떄(마지막 데이터가 아닐 떄) 진행
                else:
                    continue

    # 파일이 존재하지 않을 경우 오류 처리
    except FileNotFoundError:
        error_message = f"Error: File '{filename}' not found."
        print(error_message)
        send_error(ERROR_CODE[1])  # Sending 'File not found' error to the server


# 터미널에서 사용자로부터 입력을 받기 위해 argparse 모듈을 사용
parser = argparse.ArgumentParser(description='TFTP client program')
parser.add_argument(dest="host", help="Server IP address", type=str)
parser.add_argument(dest="operation", help="get or put a file", type=str)
parser.add_argument(dest="filename", help="name of file to transfer", type=str)
parser.add_argument("-p", "--port", dest="port", type=int)
args = parser.parse_args()

# UDP 소켓 생성
server_ip = "203.250.133.88"
server_port = 69
server_address = (server_ip, server_port)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 모드 설정 octet 사용
mode = DEFAULT_TRANSFER_MODE
operation = args.operation
filename = args.filename

    #get 실행
if operation.lower() == 'get':
    send_rrq(filename, mode)
    receive_data(filename)

        #put 실행
elif operation.lower() == 'put':
    send_wrq(filename, mode)
    send_data(filename)

# 소켓 연결 종료
sock.close()
