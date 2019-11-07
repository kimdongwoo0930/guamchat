from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import requests, re
import sys
import pandas as pd
import time as t
import xmltodict
import json
import urllib.request as ul
import datetime as dt
app = Flask(__name__)


lunch = []

dinner = []

isRefreshed = 0

updatedtime = 0

bus_stn_setting_list = []

isSetting = False

settingTime = 0



bus_stn_dict_01 = {'봉천역': ['21508', 0], '두산아파트입구': ['21526', 0], '현대시장': ['21536', 0], '구암초등학교정문': ['21545', 0],

                   '성현동주민센터': ['21565', 0], '구암어린이집앞': ['21575', 0], '숭실대입구역2번출구': ['20810', 0],

                   '봉천고개현대아파트': ['20820', 0], '봉현초등학교_01': ['21236', 0], '관악드림타운115동': ['21239', 0]}

bus_stn_dict_5513 = {'관악구청': ['21130', 5], '서울대입구': ['21252', 1], '봉천사거리, 봉천중앙시장': ['21131', 7],

                     '봉원중학교, 행운동우성아파트': ['21132', 8], '관악푸르지오아파트': ['21133', 7], '봉현초등학교': ['21236', 2],

                     '벽산블루밍벽산아파트303동앞': ['21247', 0]}

bus_stn_dict_13 = {'대방역2번출구앞': ['20834', 2], '현대아파트': ['20007', 2], '노량진역': ['20867', 1],

                   '우성아파트': ['20878', 1], '건영아파트': ['20894', 0], '신동아상가': ['20897', 0],

                   '동작등기소': ['20730', 2], '부강탕': ['20913', 0], '밤골': ['20918', 0], '약수맨션': ['20891', 1],

                   '빌라삼거리, 영도교회': ['20922', 0], '방범초소': ['20924', 0], '벽산아파트': ['21910', 0]}



homeBusStop13 = ['관악드림타운북문 방면 (동작13)', '벽산아파트 방면 (동작13)']

homeBusStop5513 = ['관악드림타운북문 방면 (5513)', '벽산아파트 방면 (5513)']
#A:관악드림타운방면 B:벽산아파트 방면
homeBusStop01 = ['관악드림타운북문 방면 (관악01)', '벽산아파트 방면 (관악01)']

bus_01 = ['21508','21893','21517','21883','21536','21871','21555','21244','21243','21242','21241','21240','21239','21237','21236','20166','20810']

key ="fef2WSoMFkV557J%2BKKEe0LmP4Y1o8IsH6x4Lv4p0pArUHTs6sk6sHVGaNfkFZRM2sSUn5Uvw0JzETmEyk5VeoA%3D%3D"

#cafe = tCafeteria("B100005528","SEOUL","HIGH")
#res = cafe.parseSchedule()


def bus(n,busSt,busNo):
    print("Attempt to get the {}, {}, {} bus info...".format(n, busSt, busNo))
    url = 'http://ws.bus.go.kr/api/rest/stationinfo/getStationByUid?ServiceKey=fef2WSoMFkV557J%2BKKEe0LmP4Y1o8IsH6x4Lv4p0pArUHTs6sk6sHVGaNfkFZRM2sSUn5Uvw0JzETmEyk5VeoA%3D%3D&arsId=' + busSt
    request = ul.Request(url)
    response = ul.urlopen(request)
    rescode = response.getcode()
    if rescode ==200:
        responsedata = response.read()
        Rd = xmltodict.parse(responsedata)
        Rdj=json.dumps(Rd)
        Rdd=json.loads(Rdj)
        busRdd=Rdd["ServiceResult"]["msgBody"]["itemList"]
        if len(busRdd) > 30:
            bus01 = busRdd["arrmsg1"]
            bus02 = busRdd["arrmsg2"]
            id01 = busRdd["vehId1"]
            d02 = busRdd["vehId2"]
        else:
            bus01 = busRdd[n]["arrmsg1"]
            bus02 = busRdd[n]["arrmsg2"]
            id01 = busRdd[n]["vehId1"]
            id02 = busRdd[n]["vehId2"]
            
        bus01 = '곧' if bus01 == '곧 도착' else bus01
        bus01 = bus01.replace('분', '분 ').replace('초후', '초 후 ').replace('번째', ' 정류장')
        bus01 = '전 정류장 출발' if bus01 == '0 정류장 전' else bus01
        bus02 = bus02.replace('분', '분 ').replace('초후', '초 후 ').replace('번째', ' 정류장')
        
        return[bus01,bus02]

def foodie(n, isForce):

    global isRefreshed, updatedtime, lunch, dinner

    print("Attempting to access in Meal table, Updated = {}".format(['False', 'True'][isRefreshed]))

    y, m, d = map(str, str(dt.datetime.now())[:10].split('-'))

    # 2018.10.29 형식

    ymd = y + '.' + m + '.' + d

    currenttime = int(t.time())

    dayList = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    weekendRefresh = 0

    # 일요일, 새로고침되지 않았을 때 실행 (다른 방법 필요할듯, 업데이트 날짜 가져와서 7일 내이면 넘기고, 아니면 업데이트 하는 식으로)

    # food함수 내에는 고쳐질 게 많다. 토요일, 일요일에 리턴하는 0값을 처리해야 함.

    # 또, 방학이나 공휴일처럼 평일이지만 배식하지 않는 경우를 추가해줘야 함.

    # -> 500000초 (약 5.7일) 초과 시 자동 업데이트, 단 foodie 함수가 활성화돼야 함



    print("Time elasped after task built : {}".format(currenttime - updatedtime))

    if ((currenttime - updatedtime) > 500000) or (isRefreshed == 0) or (lunch == []) or (isForce):
        if isForce:
            print('Forcing to update')
        print('Getting meals, wait for moment...')
        # 중식 r1, 석식 r2

        r1 = requests.get(
            "http://stu.sen.go.kr/sts_sci_md01_001.do?"
            "schulCode=B100005528&schMmealScCode=2&schulCrseScCode=4&schYmd=" + ymd)
        r2 = requests.get(
            "http://stu.sen.go.kr/sts_sci_md01_001.do?"
            "schulCode=B100005528&schMmealScCode=3&schulCrseScCode=4&schYmd=" + ymd)
        c1 = r1.content
        c2 = r2.content
        html1 = BeautifulSoup(c1, "html.parser")
        html2 = BeautifulSoup(c2, "html.parser")
        tr1 = html1.find_all('tr')
        td1 = tr1[2].find_all('td')
        tr2 = html2.find_all('tr')
        td2 = tr2[2].find_all('td')

        td1 = ["급식이 없습니다.\n" for i in range(7)] if td1 == [] else td1

        td2 = ["급식이 없습니다.\n" for i in range(7)] if td2 == [] else td2

        for i in range(1, 6):

            td1[i] = str(td1[i])

            td2[i] = str(td2[i])

            tempdish1 = td1[i].replace('<td class="textC">', '').replace('<br/>', '\n', -1).replace('</td>',
                                                                                                    '').replace('&amp;',
                                                                                                          ', ').replace(
                '\n', '\n- ', -1)
            dish1 = '- ======== -\n- '
            for _ in tempdish1:
                if _ in '1234567890.':
                    continue
                else:
                    dish1 += _
            tempdish2 = td2[i].replace('<td class="textC">', '').replace('<br/>', '\n', -1).replace('</td>',

                                                                                                    '').replace('&amp;',

                                                                                                                ', ').replace(
                '\n', '\n- ', -1)
            dish2 = '- ======== -\n- '
            for _ in tempdish2:
                if _ in '1234567890.':
                    continue
                else:

                    dish2 += _
            lunch.append(dish1 + '======== -')
            dinner.append(dish2 + '======== -')



        lunch += ['메뉴가 없습니다.'] * 2
        dinner += ['메뉴가 없습니다.'] * 2
        updatedtime = int(t.time())
        isRefreshed = 1
        if weekendRefresh == 0:
            weekendRefresh = 1
        print("Meal task has been built / refreshed!")



    # 주말에 함수 호출시에 리프레시 0으로 맞춰주자

    if n == 'Sun':
      if weekendRefresh == 0:
            isRefreshed = 0



    return [str(dayList.index(n)), m, d]
                        
@app.route('/message', methods=['POST'])
def Message():  
            
    content = request.get_json()
    content = content['userRequest']
    content = content['utterance']
    
    if content == "버스안내":
        dataSend ={
        "version" : '2.0',
            "template" : {
                "outputs" :[
                {
                    "simpleText" :{
                        "text" : '노선 및 방향을 선택해 주세요'
                    }
                }
                ],
                "quickReplies" : [
                    {
                        "action" : 'message',
                        "label" : '관악01-등교',
                        "messageText" : '관악01 - 등교'
                    },
                    {
                        "action" : 'message',
                        "label" : '관악01-하교',
                        "messageText" : '관악01 - 하교'
                    },
                    {
                        "action" : 'message',
                        "label" : '동작13-등교',
                        "messageText" : '동작13 - 등교'
                    },
                    {
                        "action" : 'message',
                        "label" : '동작13-하교',
                        "messageText" : '동작13 - 하교'
                    },
                    {
                        "action" : 'message',
                        "label" : '5513-등교',
                        "messageText" : '5513 - 등교'
                    },
                    {
                        'action' : 'message',
                        'label' : '5513-하교',
                        'messageText' : '5513 - 하교'
                    }
                  ]  
                }
        }
    elif content == "관악01 - 하교":
        dataSend = {
        'version' : '2.0',
            'template' : {
                'outputs' : [
                    {
                        'simpleText' :{
                            'text' : '관악01 버스 방향을 선택해 주세요'
                        }
                    }
                ],
                'quickReplies' : [
                    {
                        'action' : 'message',
                        'label' : '관악드림타운북문 방면 (관악01)',
                        'messageText' : '관악드림타운북문 방면 (관악01)'
                    },
                    {
                        'action' : 'message',
                        'label' : '벽산아파트 방면 (관악01)',
                        'messageText' : '벽산아파트 방면 (관악01)'
                    }
                ]
            }
        }
    elif content == "5513 - 하교":
        dataSend = {
        'version' : '2.0',
            'template' : {
                'outputs' : [
                    {
                        'simpleText' :{
                            'text' : '관악01 버스 방향을 선택해 주세요'
                        }
                    }
                ],
                'quickReplies' : [
                    {
                        'action' : 'message',
                        'label' : '관악드림타운북문 방면 (관악01)',
                        'messageText' : '관악드림타운북문 방면 (관악01)'
                    },
                    {
                        'action' : 'message',
                        'label' : '벽산아파트 방면 (관악01)',
                        'messageText' : '벽산아파트 방면 (관악01)'
                    }
                ]
            }
        }
    elif content == "동작13 - 하교":
        dataSend = {
        'version' : '2.0',
            'template' : {
                'outputs' : [
                    {
                        'simpleText' :{
                            'text' : '동작13 버스 방향을 선택해 주세요'
                        }
                    }
                ],
                'quickReplies' : [
                    {
                        'action' : 'message',
                        'label' : '관악드림타운북문 방면 (동작13)',
                        'messageText' : '관악드림타운북문 방면 (동작13)'
                    },
                    {
                        'action' : 'message',
                        'label' : '벽산아파트 방면 (동작13)',
                        'messageText' : '벽산아파트 방면 (동작13)'
                    }
                ]
            }
        }
    elif content == "관악01 - 등교":
        dataSend = {
        'version' : '2.0',
            'template' : {
                'outputs' : [
                    {
                        'simpleText' :{
                            'text' : '정류장을 선택해주세요.'
                        }
                    }
                ],
                'quickReplies' : [
                    {
                        'action' : 'message',
                        'label' : '봉천역',
                        'messageText' : '봉천역'
                    },
                    {
                        'action' : 'message',
                        'label' : '두산아파트입구',
                        'messageText' : '두산아파트입구'
                    },
                    {
                        'action' : 'message',
                        'label' : '현대시장',
                        'messageText' : '현대시장'
                    },
                    {
                        'action' : 'message',
                        'label' : '구암초등학교정문',
                        'messageText' : '구암초등학교정문'
                    },
                    {
                        'action' : 'message',
                        'label' : '성현동주민센터',
                        'messageText' : '성현동주민센터'
                    },
                    {
                        'action' : 'message',
                        'label' : '구암어린이집앞',
                        'messageText' : '구암어린집앞'
                    },
                    {
                        'action' : 'message',
                        'label' : '관악드림타운115동',
                        'messageText' : '관악드림타운115동'
                    },
                    {
                        'action' : 'message',
                        'label' : '봉현초등학교',
                        'messageText' : '봉현초등학교-01'
                    },
                    {
                        'action' : 'message',
                        'label' : '봉천고개현대아파트',
                        'messageText' : '봉천고개현대아파트'
                    },
                    {
                        'action' : 'message',
                        'label' : '숭실대입구역2번출구',
                        'messageText' : '숭실대입구역2번출구'
                    }
                ]
            }
        }
    elif content == "동작13 - 등교":
        dataSend = {
        'version' : '2.0',
            'template' : {
                'outputs' : [
                    {
                        'simpleText' :{
                            'text' : '정류장을 선택해주세요.'
                        }
                    }
                ],
                'quickReplies' : [
                    {
                        'action' : 'message',
                        'label' : '대방역2번출구앞',
                        'messageText' : '대방역2번출구앞'
                    },
                    {
                        'action' : 'message',
                        'label' : '현대아파트',
                        'messageText' : '현대아파트'
                    },
                    {
                        'action' : 'message',
                        'label' : '노량진역',
                        'messageText' : '노량진역'
                    },
                    {
                        'action' : 'message',
                        'label' : '우성아파트',
                        'messageText' : '우성아파트'
                    },
                    {
                        'action' : 'message',
                        'label' : '건영아파트',
                        'messageText' : '건영아파트'
                    },
                    {
                        'action' : 'message',
                        'label' : '신동아상가',
                        'messageText' : '신동아상가'
                    },
                    {
                        'action' : 'message',
                        'label' : '동작등기소',
                        'messageText' : '동작등기소'
                    },
                    {
                        'action' : 'message',
                        'label' : '부강탕',
                        'messageText' : '부강탕'
                    },
                    {
                        'action' : 'message',
                        'label' : '밤골',
                        'messageText' : '밤골'
                    },
                    {
                        'action' : 'message',
                        'label' : '약수맨션',
                        'messageText' : '약수맨션'
                    },
                    {
                        'action' : 'message',
                        'label' : '빌라삼거리, 영도교회',
                        'messageText' : '빌라삼거리, 영도교회'
                    },
                    {
                        'action' : 'message',
                        'label' : '방범초소',
                        'messageText' : '방범초소'
                    },
                    {
                        'action' : 'message',
                        'label' : '벽산아파트',
                        'messageText' : '벽산아파트'
                    }
                ]
            }
        }
    elif content == "5513 - 등교":
        dataSend = {
        'version' : '2.0',
            'template' : {
                'outputs' : [
                    {
                        'simpleText' :{
                            'text' : '정류장을 선택해주세요.'
                        }
                    }
                ],
                'quickReplies' : [
                    {
                        'action' : 'message',
                        'label' : '관악구청',
                        'messageText' : '관악구청'
                    },
                    {
                        'action' : 'message',
                        'label' : '서울대입구',
                        'messageText' : '서울대입구'
                    },
                    {
                        'action' : 'message',
                        'label' : '봉천사거리, 봉천중앙시장',
                        'messageText' : '봉천사거리, 봉천중앙시장'
                    },
                    {
                        'action' : 'message',
                        'label' : '봉원중학교, 행운동우성아파트',
                        'messageText' : '봉원중학교, 행운동우성아파트'
                    },
                    {
                        'action' : 'message',
                        'label' : '관악푸르지오아파트',
                        'messageText' : '관악푸르지오아파트'
                    },
                    {
                        'action' : 'message',
                        'label' : '봉현초등학교',
                        'messageText' : '봉현초등학교'
                    },
                    {
                        'action' : 'message',
                        'label' : '벽산블루밍벽산아파트303동앞',
                        'messageText' : '벽산블루밍변산아파트303동앞'
                    }
                ]
            }
        }
    elif content == "급식안내":
        dataSend = {
        'version' : '2.0',
            'template' : {
                'outputs' : [
                    {
                        'simpleText' :{
                            'text' : '중 / 석식을 선택해 주세요.'
                        }
                    }
                ],
                'quickReplies' : [
                    {
                        'action' : 'message',
                        'label' : '중식',
                        'messageText' : '중식'
                    },
                    {
                        'action' : 'message',
                        'label' : '석식',
                        'messageText' : '석식'
                    }
                ]
            }
        }
    elif content in ['중식','석식']:
        tmr = 0
        flist = foodie(str(t.ctime())[:3], 0)
        day, m, d = map(int, flist)
        if int(str(t.ctime())[11:13]) > 16:  # 5시가 지나면 내일 밥을 보여준다
            tmr = 1
            if day < 6:
                day += 1
            else:
                day = 0
        dataSend = {
            "version": "2.0",
            "template":{
                "outputs":[
                    {
                        "simpleText":{
                            "text": "{}의 {}  \n {} / {} ( {} )  \n {}".format('오늘' if tmr == 0 else '내일',
                                                                              '중식' if content == '중식' else '석식',
                                                                              m, d if tmr == 0 else d + 1,
                                                                              '월화수목금토일'[day],
                                                                              lunch[day] if content == '중식' else
                                                                              dinner[day])
                        }
                    }
                ]
            }
        }
        
    elif content in homeBusStop01:
        busStop = ['21244','21243'][homeBusStop01.index(content)]
        busList = bus(0,busStop,1)
        bus01,bus02 = map(str,busList)
        dataSend = {
            "version": "2.0",
            "template":{
                "outputs":[
                    {
                        "simpleText":{
                            "text": "{} ( {} )\n\n이번 버스 : {} {}\n\n다음 버스 : {} {}\n".format(content,busStop,bus01,' 도착 예정' if bus01 not in ['출발대기','운행종료'] else '',bus02,' 도착 예정' if bus02 not in ['출발대기','운행종료'] else '')
                        }
                    }
                ]
            }
        }
    elif content in homeBusStop13:
        busStop = ['21244','21243'][homeBusStop13.index(content)]
        busList = bus(0,busStop,13)
        bus01,bus02 = map(str,busList)
        dataSend = {
            "version": "2.0",
            "template":{
                "outputs":[
                    {
                        "simpleText":{
                            "text": "{} ( {} )\n\n이번 버스 : {} {}\n\n다음 버스 : {} {}\n".format(content,busStop,bus01,' 도착 예정' if bus01 not in ['출발대기','운행종료'] else '',bus02,' 도착 예정' if bus02 not in ['출발대기','운행종료'] else '')
                        }
                    }
                ]
            }
        }
    elif content in homeBusStop5513:
        busStop = ['21244','21243'][homeBusStop5513.index(content)]
        busList = bus(0,busStop,5513)
        bus01,bus02 = map(str,busList)
        dataSend = {
            "version": "2.0",
            "template":{
                "outputs":[
                    {
                        "simpleText":{
                            "text": "{} ( {} )\n\n이번 버스 : {} {}\n\n다음 버스 : {} {}\n".format(content,busStop,bus01,' 도착 예정' if bus01 not in ['출발대기','운행종료'] else '',bus02,' 도착 예정' if bus02 not in ['출발대기','운행종료'] else '')
                        }
                    }
                ]
            }
        }
    elif content in bus_stn_dict_01.keys():
        busStop, n = map(str,bus_stn_dict_01.get(content))
        busList = bus(int(n),busStop,1)
        bus01,bus02 = map(str, busList)
        dataSend = {
            "version": "2.0",
            "template":{
                "outputs":[
                    {
                        "simpleText":{
                            "text": "{} ( {} )\n\n이번 버스 : {} {}\n\n다음 버스 : {} {}\n".format(content,busStop,bus01,' 도착 예정' if bus01 not in ['출발대기','운행종료'] else '',bus02,' 도착 예정' if bus02 not in ['출발대기','운행종료'] else '')
                        }
                    }
                ]
            }
        }
    elif content in bus_stn_dict_5513.keys():
        busStop, n = map(str,bus_stn_dict_5513.get(content))
        busList = bus(int(n),busStop,5513)
        bus01,bus02 = map(str, busList)
        dataSend = {
            "version": "2.0",
            "template":{
                "outputs":[
                    {
                        "simpleText":{
                            "text": "{} ( {} )\n\n이번 버스 : {} {}\n\n다음 버스 : {} {}\n".format(content,busStop,bus01,' 도착 예정' if bus01 not in ['출발대기','운행종료'] else '',bus02,' 도착 예정' if bus02 not in ['출발대기','운행종료'] else '')
                        }
                    }
                ]
            }
        }
    elif content in bus_stn_dict_13.keys():
        busStop, n = map(str,bus_stn_dict_13.get(content))
        busList = bus(int(n),busStop,13)
        bus01,bus02 = map(str, busList)
        dataSend = {
            "version": "2.0",
            "template":{
                "outputs":[
                    {
                        "simpleText":{
                            "text": "{} ( {} )\n\n이번 버스 : {} {}\n\n다음 버스 : {} {}\n".format(content,busStop,bus01,' 도착 예정' if bus01 not in ['출발대기','운행종료'] else '',bus02,' 도착 예정' if bus02 not in ['출발대기','운행종료'] else '')
                        }
                    }
                ]
            }
        }
    elif content=="!도움말":
        dataSend = {
            "version": "2.0",
            "template":{
                "outputs":[
                    {
                        "simpleTextext":{
                            "text": "안녕하세요 구암고등학교 정보를 알려주는 알렉스봇입니다.\n 자신이 등하교하는 정류장이 존재하지 않는다면 문의해주세요.\n 채팅 오류나 시스템 오류가 발생할경우 20105 김동우 에게 문의해주세요.\n 피드백이나 더 추가했으면 좋겠는 것들이 있다면 문의해주세요.\n \n==============\n 자료제공 : 서울특별시교육청, 서울특별시버스정보시스템\n 플러스친구 개발 :  구암고등학교 2학년 1반 김동우 \n Github : https://github.com/kimdongwoo0930/guamchat\n 이용해 주셔서 고맙습니다 :)"
                        }
                    }
                ]
            }
        }
    else :
        dataSend = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText":{
                            "text" : "===coming soon==="
                        }
                    }
                ]
            }
        }
    
    return jsonify(dataSend)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
