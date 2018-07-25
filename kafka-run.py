[root@node2 kafka]# cat run.py
#!/usr/bin/env python
# _*_ coding:utf-8 _*_


import threading
import os
import time

BASH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
hostname = os.environ.get('MY_POD_NAME')   #获取POD_NAME
pod_num = os.environ.get('KAFKA_REPLICAS_NUM')  #获取POD数量
service_name = os.environ.get('KAFKA_SERVER_NAME')  #获取Services Name
kafka_start = '/usr/local/kafka/bin/kafka-server-start.sh /usr/local/kafka/config/server.properties'   #kafka 启动命令

def start():
    time.sleep(10)  #防止run未运行完
    os.system(kafka_start)
    return True

def set_conf():
    #多线程启动，启动顺序并不固定
    # try 防止先
    try:   
        zk_list = []
        host_num = hostname.split("-")[-1]
        os.system("echo %s > /usr/local/kafka/data/myid" %(int(host_num)+1))
        os.system("sed -i 's/broker.id=0/broker.id=%s/g' %s/config/server.properties" %(host_num,BASH))

        count = 0
        while count < int(pod_num):
            s_name = "%s.%s:%s:2888:3888" %('zk',count+1,hostname[:-1]  + "%s" %count +"."+service_name)
            os.system("echo %s >> /usr/local/kafka/config/zk.properties" %s_name)
            zk_list.append("%s:2181," %(hostname[:-1]  + "%s" %count +"."+service_name))
            count += 1
        os.system("sed -i 's/zookeeper.connect=localhost:2181/zookeeper.connect=%s/g' %s/config/server.properties"  \
                  %("".join([str(i) for i in zk_list]),BASH))
        return True
    except AttributeError:
        return True

def run(cmd):
    os.system(cmd)
    
if __name__ in '__main__':
    # 先执行
    set_conf()   #修改kafka 和zookeeper配置文件
    cmd = "/usr/local/kafka/bin/zookeeper-server-start.sh /usr/local/kafka/config/zk.properties"  #zookeeper启动命令
    t = threading.Thread(target=run,args=[cmd,])  #传参
    t.start()
    t.join(5)
start()  #后启动kafka