
# 필요한 기능을 사용하기 위해 argparse 모듈 import
import argparse


# 함수 : 관련 있는 기능을 하는 코드들에 이름을 붙여 묶어 놓은 것
def do_somthing(a, b):
    c = a**b
    c = c*a

    return c


# 파이썬 코드 실행 시 인자를 받아올 수 있는 argparse 객체 선언
parser = argparse.ArgumentParser()

# 받아오려는 인자의 이름과 자료형 결정
parser.add_argument("--num1", type=int)
parser.add_argument("--num2", type=int)


# 코드 실행 시 입력한 인자를 파싱
arguments = parser.parse_args()
a_value = arguments.num1
b_value = arguments.num2


# 파싱한 값을 함수의 인자로 주고 함수 실행, 반환값을 저장
c = do_somthing(a_value, b_value)

# 출력
print(c)

