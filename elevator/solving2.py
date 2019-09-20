import requests
import time
import enum


FULL = 8

########### API ##############
url = 'http://localhost:8000'

def start(user, problem, count, error_handler):
    uri = url + '/start' + '/' + user + '/' + str(problem) + '/' + str(count)
    respond = requests.post(uri)
    if respond.status_code != 200:
        error_handler.print_error('start', respond.status_code)
        raise Exception('API response : %d' % respond.status_code)
    return respond.json()

def oncalls(token, error_handler):
    uri = url + '/oncalls'
    respond = requests.get(uri, headers={'X-Auth-Token': token})
    if respond.status_code != 200:
        error_handler.print_error('start', respond.status_code)
        raise Exception('API response : %d' % respond.status_code)
    return respond.json()

def action(token, cmds, error_handler):
    uri = url + '/action'
    respond = requests.post(uri, headers={'X-Auth-Token': token}, json={'commands': cmds})
    if respond.status_code != 200:
        error_handler.print_error('start', respond.status_code)
        raise Exception('API response : %d' % respond.status_code)
    return respond.json()

def print_err_handler(func_name, code):
    print('[ERROR] %s : %d error occurred' % (func_name, code))

##################data######################

class EStatus(enum.Enum):
    STOPPED = enum.auto()
    OPENED = enum.auto()
    UPWARD = enum.auto()
    DOWNWARD = enum.auto()

# status : STOPPED, UPWARD, DOWNWARD, OPENED
class Elevator(object):
    def __init__(self, id, floor=0, passengers=None, status=EStatus.STOPPED, limit=(1, 25)):
        self.id = id
        self.floor = floor
        self.status = status
        self.passengers = []
        for p in passengers:
            self.passengers.append(Call(p['id'], p['start'], p['end']))
        self.direction = 0  # 0 up / 1 down
        self.limit = limit

    def update(self, floor, passengers, status:EStatus):
        self.floor = floor
        self.passengers = []
        for p in passengers:
            if self.direction == 0 and p['end'] > self.limit[1]:
                p['end'] = self.limit[1]
            elif self.direction == 1 and p['end'] < self.limit[0]:
                p['end'] = self.limit[0]
            self.passengers.append(Call(p['id'], p['start'], p['end']))
        self.status = status
        if self.status.name in ('UPWARD', 'DOWNWARD') and floor in self.limit:
            self.direction = 1 - self.direction


class Call(object):
    def __init__(self, id, start, end):
        self.id = id
        self.start = start
        self.end = end


def simulator(user='tester', problem=0, count=4, low=1, high=25):
    ret = start(user, problem, count, print_err_handler)
    token = ret['token']
    print('Token for %s is %s' % (user, token))
    elevators = {}
    curr_timestamp = ret['timestamp']
    up_calls = [{} for _ in range(26)]
    down_calls = [{} for _ in range(26)]
    for el in ret['elevators']:
        elevators[el['id']] = Elevator(el['id'], el['floor'], el['passengers'], EStatus[el['status']], limit=(low, high))
    while True:
        time.sleep(0.01)
        resp = oncalls(token, print_err_handler)
        print('[INFO] oncalls :', resp)
        curr_timestamp = resp['timestamp']
        if resp['is_end']:
            return True
        elif curr_timestamp > 5000:
            return False
        # call 있으면 처리 queue에 추가
        for newcall in resp['calls']:
            if newcall['start'] - newcall['end'] > 0: # down
                down_calls[newcall['start']][newcall['id']] = Call(newcall['id'], newcall['start'], newcall['end'])
            else:  # up
                up_calls[newcall['start']][newcall['id']] = Call(newcall['id'], newcall['start'], newcall['end'])
        # 현재 elevator 상태 반영
        for el in resp['elevators']:
            elevators[el['id']].update(el['floor'], el['passengers'], el['status'])
        commands = []
        # elevator 처리
        for el in elevators.values():
            # 엘리베이터 상태 코드에 따른 처리
            if el.status == EStatus.STOPPED:
                pass
            if el.status == EStatus.OPENED:
                pass
            if el.status == EStatus.UPWARD:
                pass
            if el.status == EStatus.DOWNWARD:
                pass
        if commands:
            print('[INFO] commands : ', commands)
            resp = action(token, commands, print_err_handler)
            curr_timestamp = resp['timestamp']
            print('[INFO] action respond:', resp)


if __name__ == '__main__':
    simulator(user='tester1', problem=2, count=4, high=25)
