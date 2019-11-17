import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import random
import chat_db
import requests
import re
import socket
import time
import threading
import queue
import recomendation_system 
sock = socket.socket()
sock.connect(('35.204.44.141', 2003))



cnt = 0
q = queue.Queue()

def send(q):
    while True:
        time.sleep(2)
        cnt = q.qsize()
        sock.send(f"hackathon.team6.backend.cnt {cnt} -1\n".encode('utf-8'))
        while not q.empty():
            q.get()



sender = threading.Thread(target=send, args=(q,))
sender.start()

token = "265069d4cb2304f8c3a02c93ebeef56056602f87f28a4942afb3ef2b4cf2427b3777997863d3f05e289ec"

def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id':random.randint(0, 1000000)})

def try_auth(request, user_id):
    if request.find("vk_bot_token_") >= 0:
        if request == "vk_bot_token_"+"d22d9059-b4a3-48ee-bc06-035f7d035ef1":
            chat_db.auth_user(user_id)
            return "Уcпешная авторизация!"
        return "Некорректный токен!"
    return "Неавторизованный пользователь!"
        


vk = vk_api.VkApi(token=token)

longpoll = VkLongPoll(vk)
print("ready")
for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        request = event.text
        ans = ""
        q.put(1)
        if event.to_me:
            if chat_db.user_exists(event.user_id):
                req = requests.request(url='https://vk.com/id'+str(event.user_id), method='GET')
                current_name = re.findall(r"<title>(.*)</title>", req.text)[0].split()[0]
                write_msg(event.user_id, "Добрейший вечерочек, "+ current_name)
                write_msg(event.user_id, "Братишка, я тебе добра принес:")
                # print(request)
                res_list = recomendation_system.result(str(request))
                print(res_list)
                # res_list = result("плвтье")
                for answ in res_list:
                    ans += str(answ) + ", "
                    write_msg(event.user_id, answ)
            else:
                write_msg(event.user_id, try_auth(request, event.user_id))
        chat_db.story(event.user_id, request, ans)