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
        sprava, klient = moj_socket.recvfrom(velkost_fragmentu+1)
        prikaz,sprava = dekoduj_a_zisti_prikaz(sprava.decode())
        if prikaz == "K":
             print("Koniec")
             break
        elif prikaz == "P":
              moj_socket.sendto("Y".encode(), klient)
        elif prikaz == "Y":
             print("Klient sa uspesne pripojil")
        elif prikaz == "F":
             velkost_fragmentu = int(sprava)
             print("Velkost fragmentu nastavena na : "+ str(velkost_fragmentu))
            # moj_socket.sendto("H".encode(), klient)
        elif prikaz == 'O':
             sprava, klient = moj_socket.recvfrom(velkost_fragmentu)
             print("Dosiel nam subor\n");
             uloz_subor("output.jpg",sprava)
             moj_socket.sendto("SUBOR ULOZENY".encode(), klient)
        elif prikaz == 'S':
             while (prikaz != "E"):
                print("Klient: " + sprava)
                moj_socket.sendto("Y".encode(), klient)
                sprava, klient = moj_socket.recvfrom(velkost_fragmentu+1)
                prikaz,sprava = dekoduj_a_zisti_prikaz(sprava.decode())
                print(prikaz)

      #  moj_socket.sendto("H".encode(), klient)
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

     som_pripojeny = False
     while True:
        if prikaz == 'N':
            ip_servera = input("Zadajte novu ip:  ")
            port = int(input("Zadajte novy port:  "))
            server = (ip_servera,port)

        elif prikaz == 'P':
            moj_socket.sendto(prikaz.encode(), server)
            odpoved, ip_servera = moj_socket.recvfrom(velkost_fragmentu)
            if odpoved.decode() == "Y":
                moj_socket.connect(server)
                moj_socket.sendto("Y".encode(), server)
                print("Som pripojeny na server")
                som_pripojeny = True

        elif prikaz == 'F' and som_pripojeny == True:
            velkost_fragmentu = int(input("Zadajte maximalnu velkost fragmentu:  "))
            print("Velkost fragmentu nastavena na : "+ str(velkost_fragmentu))
            sprava = prikaz + velkost_fragmentu_do_retazca(velkost_fragmentu)
            moj_socket.sendto(sprava.encode(), server)
           # reakcia, server = moj_socket.recvfrom(velkost_fragmentu)

         #nie    if (velkost_fragmentu > 512):   #nie
           #     print("najviac moze byt 512 ,nastavime ju na tolko")
            #    velkost_fragmentu = 512

        elif prikaz == 'K' and som_pripojeny == True:
            print("Koniec")
            moj_socket.sendto(prikaz.encode(), server)
            break

        elif prikaz == 'S' and som_pripojeny == True:
            sprava = input("Napiste spravu:  ")
            reakcia = "Y"
            while (sprava != "" and reakcia == "Y"):
                cast_spravy = sprava[:velkost_fragmentu]
                sprava = sprava[velkost_fragmentu:]
                moj_socket.sendto(('S' + cast_spravy).encode(), server)
                reakcia, server = moj_socket.recvfrom(velkost_fragmentu)
                reakcia = reakcia.decode()
                print(reakcia)

            moj_socket.sendto("E".encode(), server)

        elif prikaz == 'O' and som_pripojeny == True:
            moj_socket.sendto('O'.encode(),server)
            nazov = input("Zadajte nazov suboru:   ")
            moj_socket.sendto(nacitaj_subor(nazov),server)
            odpoved, server = moj_socket.recvfrom(velkost_fragmentu)
            print("Server: " + odpoved.decode())
        else:
            print("Zadali ste zly prikaz alebo nieste pripojeny na server")
  #      odpoved, ip_servera = moj_socket.recvfrom(velkost_fragmentu)
  #      if (odpoved.decode() == "H"):
         prikaz = input("Napiste vas dalsi prikaz:  ")
     moj_socket.close()

def dekoduj_a_zisti_prikaz(retazec):
    prikaz= retazec[0];
    retazec = retazec[1:]
    return prikaz,retazec

def nacitaj_subor(nazov):
    with open(nazov, mode="rb") as file: 
         retazec = file.read()
    return retazec


def uloz_subor(nazov,retazec):
    with open(nazov,mode = "wb") as file:
        file.write(retazec)
    print("ulozene")

def velkost_fragmentu_do_retazca(velkost_fragmentu):
    velkost_v_retazci = str(velkost_fragmentu)
    finalny_retazec = (5- len(velkost_v_retazci))*'0' + velkost_v_retazci
    return finalny_retazec

moznost = input("Ak sa ma tento PC spravat ako server, zadajte 1, ak sa ma spravat ako klient,zadajte 2\n")

if moznost == "1":
    pusti_ako_server()
elif moznost == "2":
    pusti_ako_klient()
else:
    print("Zadali ste zly vstup")