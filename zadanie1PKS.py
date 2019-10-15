import socket

velkost_fragmentu = 65535

#--------------------------------------------------------------------------------------------------------------------------------------------------------


def pustim_sa_pri_starte_servera():
    ip_servera = '147.175.181.30'
    port = 30000
    print("Server spusteny.")
    print("Server ma ip " + ip_servera + " a port " + str(port))
    print("Defaultna maximalne velkost fragmentu je: "+str(velkost_fragmentu))
    print("")
    return ip_servera,port,velkost_fragmentu

def server_potvrdi_pripojenie_klienta(moj_socket,klient):
    moj_socket.sendto("Y".encode(), klient)
    sprava, klient = moj_socket.recvfrom(velkost_fragmentu+1)
    if sprava == "Y":
       print("Klient sa uspesne pripojil")

def server_chce_prijat_velkost_fragmentu(moj_socket,klient):
    sprava,klient = moj_socket.recvfrom(10)
    velkost_fragmentu = sprava.decode()[1:]
    print("nastavena velkost fragmentu na " + velkost_fragmentu)

def server_chce_prijat_obrazok(moj_socket,klient):
    buffer = b""
    header = ""
    while (header != "E"):
        zakodovana_sprava, klient = moj_socket.recvfrom(velkost_fragmentu)
        header = zakodovana_sprava[:1].decode()
        buffer += zakodovana_sprava[1:] 
        moj_socket.sendto("Y".encode(), klient)
    with open("output.jpg","wb") as file:
        file.write(buffer)
    print("Obrazok prijaty")
       
def server_chce_prijat_spravu(moj_socket,klient):
    sprava = ""
    prikaz = ""
    while (prikaz != "E"):
        cast_spravy, klient = moj_socket.recvfrom(velkost_fragmentu+1)
        prikaz = cast_spravy[:1].decode()
        sprava += cast_spravy[1:].decode()
        moj_socket.sendto("Y".encode(), klient)
    print("Sprava od klienta :" + sprava)











def pusti_ako_server():
    ip_servera,port,velkost_fragmentu = pustim_sa_pri_starte_servera()
    moj_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    moj_socket.bind((ip_servera,port))

    while True:
        prikaz, klient = moj_socket.recvfrom(1)
        prikaz = prikaz.decode()

        if prikaz == "K":
             print("Koniec")
             break

        elif prikaz == "P":
             server_potvrdi_pripojenie_klienta(moj_socket,klient)

        elif prikaz == "F":
             server_chce_prijat_velkost_fragmentu(moj_socket,klient)

        elif prikaz == 'O':
             server_chce_prijat_obrazok(moj_socket,klient)

        elif prikaz == 'S':
              server_chce_prijat_spravu(moj_socket,klient)

        moj_socket.sendto("H".encode(), klient)
    moj_socket.close()

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------

def pustim_sa_pri_starte_klienta():
     ip_servera = '147.175.181.30'
     port = 30000
     server = (ip_servera,port)
     print("Defaulna ip servera je: " + ip_servera)
     print("Defaultny port je:" + str(port))
     print("Defaultna maximalne velkost fragmentu je: "+str(velkost_fragmentu))
     print("")
     print("Zadajte N pre nastavenie ip adresy alebo portu")
     print("Zadajte P pre pripojenie na server")
     print("Zadajte F pre nastavenie maximalnej velkosti fragmentu")
     print("Zadajte S pre poslanie spravy")
     print("Zadajte O pre poslanie obrazku")
     print("Zadajte K pre ukoncienie\n")
     return ip_servera,port,server,velkost_fragmentu

def velkost_fragmentu_do_retazca(velkost_fragmentu):
    velkost_v_retazci = str(velkost_fragmentu)
    finalny_retazec = (5- len(velkost_v_retazci))*'0' + velkost_v_retazci
    return finalny_retazec

def klient_sa_chce_pripojit(moj_socket,server):
    moj_socket.sendto("P".encode(), server)
    odpoved, ip_servera = moj_socket.recvfrom(velkost_fragmentu)
    if odpoved.decode() == "Y":
       moj_socket.connect(server)
       moj_socket.sendto("Y".encode(), server)
       print("Som pripojeny na server")
       return True                      #tu treba vyriesit co ked server neposle suhlas

def klient_chce_nastavit_velkost_fragmentu(moj_socket,server):
    moj_socket.sendto("F".encode(), server)
    velkost_fragmentu = int(input("Zadajte maximalnu velkost fragmentu:  "))            #tu este osetrit tu maximalnu velkost fragmentu
    print("Velkost fragmentu nastavena na : "+ str(velkost_fragmentu))
    moj_socket.sendto(("F" + velkost_fragmentu_do_retazca(velkost_fragmentu)).encode(), server)

def klient_chce_poslat_obrazok(moj_socket,server):          # tu treba vyriesit ked packety budu chybat, cakanie na acknowledgement
    nazov = input("Zadajte nazov obrazku:  ")
    reakcia = b"Y"
    moj_socket.sendto("O".encode(), server)
    with open(nazov,"rb") as file:
        buffer = file.read()
    while (buffer != b""):
        buffer_part = buffer[:velkost_fragmentu]
        buffer = buffer[velkost_fragmentu:]
        moj_socket.sendto("X".encode() + buffer_part, server)
        reakcia, server = moj_socket.recvfrom(velkost_fragmentu+1)
    print("Obrazok poslany")
    moj_socket.sendto("E".encode(), server)
    reakcia, server = moj_socket.recvfrom(velkost_fragmentu+1)

def klient_chce_poslat_spravu(moj_socket,server):            # tu treba vyriesit ked packety budu chybat, cakanie na acknowledgement
     sprava = input("Napiste spravu:  ")
     reakcia = "Y"
     moj_socket.sendto("S".encode(), server)
     while (sprava != ""):
         cast_spravy = sprava[:velkost_fragmentu]
         sprava = sprava[velkost_fragmentu:]
         moj_socket.sendto(('X' + cast_spravy).encode(), server)
         reakcia, server = moj_socket.recvfrom(velkost_fragmentu)
         reakcia = reakcia.decode()

     moj_socket.sendto("E".encode(), server)
     reakcia, server = moj_socket.recvfrom(velkost_fragmentu+1)







def pusti_ako_klient():
     ip_servera,port,server,velkost_fragmentu = pustim_sa_pri_starte_klienta()
     moj_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
     moj_socket.connect((ip_servera,port))
     som_pripojeny = False
     prikaz = input("Sem napiste prikaz:  ")
     while True:
        if prikaz == 'N':
            ip_servera = input("Zadajte novu ip:  ")
            port = int(input("Zadajte novy port:  "))
            server = (ip_servera,port)

        elif prikaz == 'P':
            som_pripojeny = klient_sa_chce_pripojit(moj_socket,server)

        elif prikaz == 'F' and som_pripojeny == True:
            klient_chce_nastavit_velkost_fragmentu(moj_socket,server)
            
        elif prikaz == 'K' and som_pripojeny == True:
            print("Koniec")
            moj_socket.sendto("K".encode(), server)
            break

        elif prikaz == 'S' and som_pripojeny == True:
            klient_chce_poslat_spravu(moj_socket,server)

        elif prikaz == 'O' and som_pripojeny == True:
            klient_chce_poslat_obrazok(moj_socket,server)

        else:
            print("Zadali ste zly prikaz alebo nieste pripojeny na server")
            prikaz = input("Napiste vas dalsi prikaz:  ")
            continue

        odpoved, ip_servera = moj_socket.recvfrom(1)
        if (odpoved.decode() == "H"):
            prikaz = input("Napiste vas dalsi prikaz:  ")
     moj_socket.close()



#--------------------------------------------------------------------------------------------------------------------------------------------------------

moznost = input("Ak sa ma tento PC spravat ako server, zadajte 1, ak sa ma spravat ako klient,zadajte 2\n")

if moznost == "1":
    pusti_ako_server()
elif moznost == "2":
    pusti_ako_klient()
else:
    print("Zadali ste zly vstup")