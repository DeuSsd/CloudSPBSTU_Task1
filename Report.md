# Выполнение домашнего задания

1. Устанавливаю три виртуальные машины в VirtualBox

![](./assets/screens/Screenshot_1.png)

---

2. Далее произвожу переименование *hostname*

Для этого открываем нужный файл

```shell 
$ sudo vim /etc/hostname 
```

И переименовываем на нужный: ognevserver затем перезагружаем машину

---

3. Создаем нового пользователя ognev_1

```shell 
$ sudo adduser ognev_1 
```

```Full Name: Denis Ognev```

```Password: ####```

---

4. Проделываем тоже самое с другими линукс системами

**Debian**

![](./assets/screens/Screenshot_2.png)

```shell 
$ sudo hostnamectl set-hostname ognev_gatevay 
$ sudo vim /etc/hosts 
```

Встречаю следующую ошибку

![](./assets/screens/Screenshot_3.png)

Пробую с root правами 

```shell
$ su
```

И получаю ещё  одну ошибку

![](./assets/screens/Screenshot_4.png)

Выполняю следующие команды

![](./assets/screens/Screenshot_5.png)

---

5. Создаем нового пользователя ognev_1

```shell
$ sudo adduser ognev_2
 ```

```Full Name: Denis Ognev```

```Password: ####```


![](./assets/screens/Screenshot_6.png)

---

6. fedora

```shell
$ sudo hostnamectl set-hostname ognevclient 
$ sudo nano /etc/hostname 
$ sudo adduser ognev_3
$ sudo passwd ognev_3
Password: ####
```
Третий пользователь:

![](./assets/screens/Screenshot_7.png)

---

7. Настраиваем SSH соединение с машинами

Обновляем репозиторий командой:

```shell
$ sudo apt update
```

Устанавливаем SSH с помощью команды:

```shell
$ sudo apt-get install ssh
```

Устанавливаем OpenSSH

```shell
$ sudo apt install openssh-server
```

Добавим пакет SSH-сервера в автозагрузку


```shell
$ sudo systemctl enable sshd
$ apt install openssh-server -y
$ systemctl enable ssh
$ systemctl start ssh
$ system status ssh
```

![](./assets/screens/Screenshot_8.png)

Повторяем для других систем

**Debian**

![](./assets/screens/Screenshot_9.png)

**Fedora**

```shell
$ sudo dnf install openssh-server
```

![](./assets/screens/Screenshot_10.png)

---

8. Выполним проброс портов для SSH, так как работаем с виртуальными машинами

![](./assets/screens/Screenshot_11.png)

![](./assets/screens/Screenshot_12.png)

Логин и порт:
- ```ognev_1 порт 20001```

- ```ognev_2 порт 20002```

- ```ognev_3 порт 20003```

---

9. Подключаемся по SSH 

![](./assets/screens/Screenshot_13.png)

---

10. Настройка linux сети

**Ubuntu(Debian)**
```shell
$ sudo apt-get install netplan.io
```

**Fedora**
```shell
$ sudo dnf install snapd
```

---

Окей... У меня проблема...

... В виду того, что я ещё недостаточно разбираюсь в работе на разных линукс системах, то решил на этом этапе работать на 3-х ubuntu-server линукс дистрибутивах.

Создал пользователья, имя хоста и поднял ssh серверы на новых VM машинах

![](./assets/screens/Screenshot_16.png)

---

Конфигурируем в *netplan* сеть

**ognev_server**

Заполняем конфигурационный файл

```shell
$ sudo vim /etc/netplan/00-installer-config.yaml
```
```yaml
network:
  ethernets:
    enp0s3:
      dhcp4: true
    enp0s8:
      dhcp4: false
      addresses: [192.168.6.10/24]
      gateway4: 192.168.6.1
  version: 2
```
Проверяем синтаксис на корректность

```shell
$ sudo netplan --debug generate
```

![](./assets/screens/Screenshot_28.png)

Применяем конфигурацию 

```shell
$ sudo netplan apple
```

**ognev_gateway**

Конфигурация сетевого шлюза

```yaml
network:
  ethernets:
    enp0s3:
      dhcp4: true
    enp0s8:
      dhcp4: false
      addresses: [192.168.6.1/24]
    enp0s9:
      dhcp4: false
      addresses: [192.168.7.1/24]
  version: 2
```

**ognev_client**

Конфигурация клиента

```yaml
network:
  ethernets:
    enp0s3:
      dhcp4: true
    enp0s8:
      dhcp4: false
      addresses: [192.168.7.100/24]
      gateway4: 192.168.7.1
  version: 2
```

Выведем содержимое плучившихся конфиг-файлов в консоль

```shell
$ cat /etc/netplan/00-installer-config.yaml
```

![](./assets/screens/Screenshot_17.png)

---

Выполним связывание интерфейсов enp0s8 и enp0s9 на шлюзе

```shell
$ sudo echo 1 | sudo tee /proc/sys/net/ipv4/ip_forward 1
```
Теперь Server и Client видят друг друга через шлюз

А чтобы при перезапуске машин шлюз восстанавливал видимость, раскомментируем данную строку

```#net.ipv4.ip_forward=1```

в файле 

```shell
$  sudo vim /etc/sysctl.conf 
```

![](./assets/screens/Screenshot_19.png)

Получим в ```tcpdump``` следующий результат

```$ sudo tcpdump -i enp0s8 icmp```

![](./assets/screens/Screenshot_25.png)


Выполним фильтрацию пакетов с помощью ```iptables```

![](./assets/screens/Screenshot_20.png)

```shell
$ sudo iptables -A FORWARD -i enp0s9 -o enp0s8 -p tcp --syn --dport 5000 -m conntrack --ctstate NEW -j ACCEPT
$ sudo iptables -A FORWARD -i enp0s8 -o enp0s9 -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
$ sudo iptables -A FORWARD -i enp0s9 -o enp0s8 -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
$ sudo iptables -P FORWARD DROP
```
Поличился следующий набор правил

![](./assets/screens/Screenshot_26.png)

Сохраним правила

```shell
$ sudo apt-get install iptables-persistent
```


```shell
$ sudo su
root# sudo iptables-save > /etc/iptables/rules.v4
root# sudo ip6tables-save > /etc/iptables/rules.v6
root# exit
```

![](./assets/screens/Screenshot_28.png)

---

**Текущая конфигурация сети выглядит теперь следующим образом**

![](./assets/scheme.png)


---

10. Создание HTTP-сервера

Копируем на ```ognev_server``` сервер

```shell
$ scp -P 20001 Server.py ognev_1@localhost:Server.py
```
Настраиваем службу ```web-server``` для автозапуска

```shell
$ sudo vim /lib/systemd/system/web-server.service
```

![](./assets/screens/Screenshot_21.png)


```
$ sudo systemctl daemon-reload
$ sudo systemctl start web-server
$ sudo systemctl enable web-server
$ sudo systemctl status web-server
```

![](./assets/screens/Screenshot_22.png)


Выполним проверку работы Сервера командой ```curl```

![](./assets/screens/Screenshot_23.png)

```shell
$ curl -X GET 192.168.6.10:5000/

$ curl -X POST -d 'username=linuxize' http://192.168.6.10:5000/login

$ curl -X PUT -d password=0000 192.168.6.10:5000/change_password
```

![](./assets/screens/Screenshot_24.png)

Посмотрим на *tcpdump*

```shell
$ sudo tcpdump -i enp0s8 tcp
```

![](./assets/screens/Screenshot_27.png)

---
Изменим порт на котором работает сервер и проверим работу правил на шлюзе

![](./assets/screens/Screenshot_29.png)

Посмотрим при помощи инструмента ```tshark``` на поступление с интерфейса ```enp0s8``` c хоста ```192.168.7.100```

```shell
$ sudo tshark -i enp0s8 dst host 192.168.7.100
```

Видим, что проходят только пакеты на порт: **5000**, но так как сервер работает на порту **5010**, то никакого ответа клиент не получает. А по порту **5010** сервер не достижим.

![](./assets/screens/Screenshot_14.png)

Изменив порт на тот, что разрешён в правилах - **5000**, получаем, что пакеты также проходят только по этому порту, но видно при этом, что сервер отвечает.

![](./assets/screens/Screenshot_15.png)

Создадм ***bash*** скрипт с запросами

```bash
#!/usr/bin/env bash
curl -X GET 192.168.6.10:5000/
curl -X POST -d 'username=linuxize' http://192.168.6.10:5000/login
curl -X PUT -d password=0000 192.168.6.10:5000/change_password
```

Выполним вызов команд при помощи ***bash***  скрипта 

```shell
$ bash ./client_test.sh
```

![](./assets/screens/Screenshot_30.png) 

# Заключение

Таким образом, была выполнена работа по натройке сетевого соединения между устройствами, конфигурирования сети, настройка правил для пропуска пакетов на шлюзе, разворачиванию простенького HTTP-сервера, с методами GET, POST, PUT. Полученный сервер и сеть были протестированы. Задача выполнена корректно. 
