import socket

def pusti_ako_server():
    ip_servera = '147.175.181.30'
    port = 30000
    velkost_fragmentu = 51200
    moj_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    moj_socket.bind((ip_servera,port))

    print("Server spusteny.")
    print("Server ma ip " + ip_servera + " a port " + str(port))

    while True:
        sprava, klient = moj_socket.recvfrom(velkost_fragmentu)
        if sprava.decode() == "K":
            print("Koniec")
            break
        elif sprava.decode() == "REQUESTING CONNECT":
            moj_socket.sendto("YOU MAY CONNECT".encode(), klient)
        elif sprava.decode() == 'O':
             sprava, klient = moj_socket.recvfrom(velkost_fragmentu)
             print("Dosiel nam subor\n");
             uloz_subor("output.jpg",sprava)
             moj_socket.sendto("SUBOR ULOZENY".encode(), klient)
        else:
            print("Klient s adresou "+ str(klient) + "poslal toto:" + sprava.decode())
            odpoved = sprava.decode().upper()
            moj_socket.sendto(odpoved.encode(), klient)
    moj_socket.close()


def pusti_ako_klient():
     ip_servera = '147.175.181.30'
     port = 30000
     server = (ip_servera,port)
     velkost_fragmentu = 51200
     print("Defaulna ip servera je: " + ip_servera)
     print("Defaultny port je:" + str(port))
     print("Defaultna maximalne velkost fragmentu je: "+str(velkost_fragmentu))
     print("")
     moj_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
     moj_socket.connect((ip_servera,port))

     print("Zadajte N pre nastavenie ip adresy alebo portu")
     print("Zadajte P pre pripojenie na server")
     print("Zadajte F pre nastavenie maximalnej velkosti fragmentu")
     print("Zadajte S pre poslanie spravy")
     print("Zadajte O pre poslanie obrazku")
     print("Zadajte K pre ukoncienie\n")
     prikaz = input()

     while True:
        if prikaz == 'N':
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

        elif prikaz == 'S':
            sprava = input("Napiste spravu:  ")
            moj_socket.sendto(sprava.encode(), server)
            odpoved, server = moj_socket.recvfrom(velkost_fragmentu)
            print("zo servera prislo toto: " + odpoved.decode())

        elif prikaz == 'O':
            moj_socket.sendto('O'.encode(),server)
            nazov = input("Zadajte nazov suboru:   ")
            moj_socket.sendto(nacitaj_subor(nazov),server)
            odpoved, server = moj_socket.recvfrom(velkost_fragmentu)
            print("zo servera prislo toto: " + odpoved.decode())
        else:
            print("Neplatny prikaz")
        prikaz = input("Napiste vas dalsi prikaz:  ")
     moj_socket.close()


def nacitaj_subor(nazov):
    with open(nazov, mode="rb") as file: 
         retazec = file.read()
    return retazec


def uloz_subor(nazov,retazec):
    with open(nazov,mode = "wb") as file:
        file.write(retazec)
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
