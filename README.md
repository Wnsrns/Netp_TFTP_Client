# 간단한 TFTP 클라이언트
이 프로그램은 Python으로 작성된 간단한 TFTP(Trivial File Transfer Protocol) 클라이언트입니다.
이 클라이언트는 파일을 가져오거나 전송하는 기능을 제공합니다.

## 사용법
### 파일 가져오기 (GET)
	$ python tftp_client.py 호스트주소 get 파일이름

### 파일 전송하기 (PUT)
	$ python tftp_client.py 호스트주소 put 파일이름

### 옵션
	-p 포트번호 또는 --port 포트번호: 선택적으로 사용할 TFTP 포트 번호를 지정합니다. 기본값은 69번 포트입니다.

## 사용 예시
### 파일 가져오기(GET)
	$ python tftp_client.py 203.250.133.88 get example.txt
### 파일 전송하기(PUT)
	$ python tftp_client.py 203.250.133.88 put example.txt

### 주의사항
	호스트 주소를 올바르게 입력해야 합니다.
	파일의 경로와 이름을 정확히 입력해야 합니다.
	필요에 따라 포트 번호를 변경할 수 있습니다.
