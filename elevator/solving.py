import requests
import time

url = 'http://localhost:8000'

FULL = 8

def start(user, problem, count, error_handler):
    uri = url + '/start' + '/' + user + '/' + str(problem) + '/' + str(count)
    respond = requests.post(uri)
    if respond.status_code != 200:
        error_handler.print_error('start', respond.status_code)
        return None
    return respond.json()


def oncalls(token, error_handler):
    uri = url + '/oncalls'
    respond = requests.get(uri, headers={'X-Auth-Token': token})
    if respond.status_code != 200:
        error_handler.print_error('start', respond.status_code)
        return None
    return respond.json()


def action(token, cmds, error_handler):
    uri = url + '/action'
    respond = requests.post(uri, headers={'X-Auth-Token': token}, json={'commands': cmds})
    if respond.status_code != 200:
        error_handler.print_error('start', respond.status_code)
        return None
    return respond.json()

def print_err_handler(func_name, code):
    print('[ERROR] %s : %d error occurred' % (func_name, code))


# status : STOPPED, UPWARD, DOWNWARD, OPENED
class Elevator(object):
    def __init__(self, id, floor=0, passengers=None, status='STOPPED', limit=(1, 25)):
        self.id = id
        self.floor = floor
        self.status = status
        self.passengers = []
        for p in passengers:
            self.passengers.append(Call(p['id'], p['start'], p['end']))
        self.ongoing = 0  # 0 up / 1 down
        self.limit = limit

    def update(self, floor, passengers, status):
        self.floor = floor
        self.passengers = []
        for p in passengers:
            if self.ongoing == 0 and p['end'] > self.limit[1]:
                p['end'] = self.limit[1]
            elif self.ongoing == 1 and p['end'] < self.limit[0]:
                p['end'] = self.limit[0]
            self.passengers.append(Call(p['id'], p['start'], p['end']))
        self.status = status
        if self.status in ('UPWARD', 'DOWNWARD') and floor in self.limit:
            self.ongoing = 1 - self.ongoing


class Call(object):
    def __init__(self, id, start, end):
        self.id = id
        self.start = start
        self.end = end


def simulator(user='tester', problem=0, count=4, low=1, high=25):
    ret = start(user, problem, count, print_err_handler)
    if not ret: return False
    token = ret['token']
    print('Token for %s is %s' % (user, token))
    elevators = {}
    curr_timestamp = ret['timestamp']
    up_calls = [{} for _ in range(26)]
    down_calls = [{} for _ in range(26)]
    for el in ret['elevators']:
        elevators[el['id']] = Elevator(el['id'], el['floor'], el['passengers'], el['status'], limit=(low, high))

    while True:
        time.sleep(0.01)
        resp = oncalls(token, print_err_handler)
        if not resp: return False
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
            flag = -1
            call_ids = []
            for p in el.passengers:
                if p.end == el.floor:
                    flag = 1 # UP/DOWN이면 STOP. STOP이면 OPEN. OPEN이면 EXIT 시키기 -> 다시 OPEN됨
                    call_ids.append(p.id)
            cmd = None
            # 현재 층에 내리는 사람 있으면 STOP
            if flag == 1:
                if el.status == 'UPWARD' or el.status == 'DOWNWARD':
                    cmd = 'STOP'
                elif el.status == 'STOPPED':
                    cmd = 'OPEN'
                else:
                    cmd = 'EXIT'
            # 엘리베이터가 꽉차지 않고 현재 층에 진행방향이 같은 call이 있으면 stop
            elif len(el.passengers) < FULL and \
                    ((el.ongoing == 0 and up_calls[el.floor])
                     or (el.ongoing == 1 and down_calls[el.floor])):
                if el.status == 'STOPPED':
                    cmd = 'OPEN'
                elif el.status == 'OPENED':
                    cmd = 'ENTER'
                else:
                    cmd = 'STOP'
                remain = FULL - len(el.passengers)
                dellist = []
                if cmd == 'ENTER':
                    if el.ongoing == 0:
                        for pp in up_calls[el.floor].values():
                            call_ids.append(pp.id)
                            dellist.append(pp.id)
                            remain -= 1
                            if remain == 0: break
                        for d in dellist:
                            del up_calls[el.floor][d]
                    else:
                        for pp in down_calls[el.floor].values():
                            call_ids.append(pp.id)
                            dellist.append(pp.id)
                            remain -= 1
                            if remain == 0: break
                        for d in dellist:
                            del down_calls[el.floor][d]
            # 엘리베이터가 가던 방향대로 가면됨
            # 단 맨 꼭대기와 맨 아래층에서 방향 전환 처리 필요! -> 그냥 STOPPED 해주는걸로 충분
            else:
                if el.status == 'OPENED': # 문 열려있으면 일단 닫자
                    cmd = 'CLOSE'
                elif el.status != 'STOPPED' and el.floor in el.limit:  # 엘리베이터 끝범위
                    cmd = 'STOP'
                else:
                    cmd = 'UP' if el.ongoing == 0 else 'DOWN'
            if call_ids:
                commands.append({'elevator_id': el.id, 'command': cmd, 'call_ids': call_ids})
            else:
                commands.append({'elevator_id': el.id, 'command': cmd, 'call_ids': call_ids})
        if commands:
            print('[INFO] commands : ', commands)
            resp = action(token, commands, print_err_handler)
            if not resp: return False
            curr_timestamp = resp['timestamp']
            print('[INFO] action respond:', resp)


if __name__ == '__main__':
    simulator(user='tester1', problem=2, count=4, high=25)
