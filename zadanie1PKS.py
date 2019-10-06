import socket

def pusti_ako_server():
    ip_servera = '192.168.56.1'
    port = 30000
    velkost_fragmentu = 512
    moj_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    moj_socket.bind((ip_servera,port))

    print("Server spusteny.")

    while True:
        sprava, klient = moj_socket.recvfrom(velkost_fragmentu)
        if sprava.decode() == "K":
            print("Koniec")
            break
        elif sprava.decode() == "REQUESTING CONNECT":
            moj_socket.sendto("YOU MAY CONNECT".encode(), klient)
        else:
            print("Klient s adresou "+ str(klient) + "poslal toto:" + sprava.decode())
            odpoved = sprava.decode().upper()
            moj_socket.sendto(odpoved.encode(), klient)
    moj_socket.close()


def pusti_ako_klient():
     ip_servera = '192.168.56.1'
     port = 30000
     server = (ip_servera,port)
     velkost_fragmentu = 512
     print("Defaulna ip servera je: " + ip_servera)
     print("Defaultny port je:" + str(port))
     print("Defaultna maximalne velkost fragmentu je: "+str(velkost_fragmentu))
     moj_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
     moj_socket.connect((ip_servera,port))

     prikaz = input("Zadajte Z pre nastavenie ip adresy alebo portu,\nP pre pripojenie na server,\n F pre nastavenie maximalnej velkosti fragmentu,\n M pre poslanie spravy,\n K pre ukoncienie\n")
     while True:
        if prikaz == 'Z':
            ip_servera = input("Zadajte novu ip:  ")
            port = int(input("Zadajte novy port:  "))

        elif prikaz == 'P':
            moj_socket.sendto("REQUESTING CONNECT".encode(), server)
            odpoved, ip_servera = moj_socket.recvfrom(velkost_fragmentu)
            if odpoved.decode() == "YOU MAY CONNECT":
                moj_socket.connect(server)
                moj_socket.sendto("I AM CONNECTED".encode(), server)
                print("Som pripojeny na server")

        elif prikaz == 'F':
            velkost_fragmentu = int(input("Zadajte maximalnu velkost fragmentu:  "))
            if (velkost_fragmentu > 512):
                print("najviac moze byt 512 ,nastavime ju na tolko")
                velkost_fragmentu = 512

        elif prikaz == 'K':
            print("Koniec")
            moj_socket.sendto(prikaz.encode(), server)
            break

        elif prikaz == 'M':
            sprava = input("Napiste spravu:  ")
            moj_socket.sendto(sprava.encode(), server)
            odpoved, server = moj_socket.recvfrom(velkost_fragmentu)
            print("zo servera prislo toto: " + odpoved.decode())

        else:
            print("Neplatny prikaz")
        prikaz = input("Napiste vas dalsi prikaz:  ")
     moj_socket.close()


def nacitaj_subor(nazov):
    f = open("nazov", "rb")
    retazec = []
    try:
        byte = f.read(1)
        while byte != b"":
            retazec.append(byte)
            byte = f.read(1)
    finally:
        f.close()
        print("nacitane")
        return retazec

def uloz_subor(nazov,retazec):
    f = open("nazov", "wb")
    for i in range(len(retazec)):
        f.write(retazec[i])
    print("ulozene")


moznost = input("Ak sa ma tento PC spravat ako server, zadajte 1, ak sa ma spravat ako klient,zadajte 2\n")

if moznost == "1":
    pusti_ako_server()
elif moznost == "2":
    pusti_ako_klient()
elif moznost == "3":
    uloz_subor("output.jpg",nacitaj_subor("pokus.jpg"))
else:
    print("Zadali ste zly vstup")

