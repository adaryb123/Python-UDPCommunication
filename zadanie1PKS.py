import socket
import time
import binascii

#--------------------------------------------------------------------------------------------------------------------------------------------------------
max_velkost = 1500

def pustim_sa_pri_starte_servera():
    ip_servera = '147.175.181.30'
    port = 30000
    print("Server spusteny.")
    print("Server ma ip " + ip_servera + " a port " + str(port))
    print("Defaultna maximalne velkost fragmentu je: "+str(max_velkost))
    print("")
    return ip_servera,port,max_velkost

def server_potvrdi_pripojenie_klienta(moj_socket,klient,velkost_fragmentu):
    moj_socket.sendto("Y".encode(), klient)
    sprava, klient = moj_socket.recvfrom(1)
    if sprava == "Y":
       print("Klient sa uspesne pripojil")

def server_chce_prijat_velkost_fragmentu(moj_socket,klient):
    sprava,klient = moj_socket.recvfrom(max_velkost)
    velkost_fragmentu = int(sprava.decode())
    print("nastavena velkost fragmentu na " + str(velkost_fragmentu))
    return velkost_fragmentu

def rozdel_fragment(fragment,velkost_fragmentu):                  
        hlavicka = fragment[:-velkost_fragmentu]
        data = fragment[-velkost_fragmentu:]
        dekodovana_hlavicka = hlavicka.decode()
        i = 0
        poradie_fragmentu = ""
        prijaty_checksum = ""
        while dekodovana_hlavicka[i] != '/':
            poradie_fragmentu += dekodovana_hlavicka[i]
            i += 1
        i += 1

        while  dekodovana_hlavicka[i] != '#':
             prijaty_checksum += dekodovana_hlavicka[i]
             i += 1
        i += 1

        return poradie_fragmentu,prijaty_checksum,data



def server_chce_prijat_obrazok(moj_socket,klient,velkost_fragmentu):
    buffer = b""
    poradie_fragmentu = ""
    while (1):
        fragment, klient = moj_socket.recvfrom(max_velkost)
        if (len(fragment) == 1):
            break
        poradie_fragmentu,prijaty_checksum,data = rozdel_fragment(fragment,velkost_fragmentu)
        vypocitany_checksum = binascii.crc32(data)
   
        if (str(prijaty_checksum) == str(vypocitany_checksum)):
           moj_socket.sendto(("Y" + poradie_fragmentu).encode(), klient)        
           buffer += data
        else:
           moj_socket.sendto(("N" + poradie_fragmentu).encode(), klient)

    with open("output.jpg","wb") as file:
        file.write(buffer)
    print("Obrazok prijaty")
       
def server_chce_prijat_spravu(moj_socket,klient,velkost_fragmentu):
    buffer = ""
    poradie_fragmentu = ""
    while (1):
        fragment, klient = moj_socket.recvfrom(max_velkost)
        if (len(fragment) == 1):
            break
        poradie_fragmentu,prijaty_checksum,data = rozdel_fragment(fragment,velkost_fragmentu)
        vypocitany_checksum = binascii.crc32(data)
   
        if (str(prijaty_checksum) == str(vypocitany_checksum)):
           moj_socket.sendto(("Y" + poradie_fragmentu).encode(), klient)        
           buffer += data.decode()
        else:
           moj_socket.sendto(("N" + poradie_fragmentu).encode(), klient)            #skus poslat corruptnuty subor

    print("Sprava od klienta :" + buffer)











def pusti_ako_server():
    ip_servera,port,velkost_fragmentu = pustim_sa_pri_starte_servera()
    moj_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    moj_socket.bind((ip_servera,port))

    while True:
  #      starting_time = time.time()
 #       while time.time() < starting_time + 10:
  #         if (moj_socket.recvfrom(1)):
    #          print("poslal ho")
  #      print("neposlal ho")

        prikaz, klient = moj_socket.recvfrom(1)
        prikaz = prikaz.decode()

        if prikaz == "K":
             print("Koniec")
             break

        elif prikaz == "P":
             server_potvrdi_pripojenie_klienta(moj_socket,klient,velkost_fragmentu)

        elif prikaz == "F":
             velkost_fragmentu = server_chce_prijat_velkost_fragmentu(moj_socket,klient)

        elif prikaz == 'O':
             server_chce_prijat_obrazok(moj_socket,klient,velkost_fragmentu)

        elif prikaz == 'S':
              server_chce_prijat_spravu(moj_socket,klient,velkost_fragmentu)

        moj_socket.sendto("H".encode(), klient)
    moj_socket.close()

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------

def pustim_sa_pri_starte_klienta():
     ip_servera = '147.175.181.30'
     port = 30000
     server = (ip_servera,port)
     print("Defaulna ip servera je: " + ip_servera)
     print("Defaultny port je:" + str(port))
     print("Defaultna maximalne velkost fragmentu je: "+str(max_velkost))
     print("")
     print("Zadajte N pre nastavenie ip adresy alebo portu")
     print("Zadajte P pre pripojenie na server")
     print("Zadajte F pre nastavenie maximalnej velkosti fragmentu")
     print("Zadajte S pre poslanie spravy")
     print("Zadajte O pre poslanie obrazku")
     print("Zadajte K pre ukoncienie\n")
     return ip_servera,port,server,max_velkost

def klient_sa_chce_pripojit(moj_socket,server,velkost_fragmentu):
    moj_socket.sendto("P".encode(), server)
    odpoved, ip_servera = moj_socket.recvfrom(velkost_fragmentu)
    if odpoved.decode() == "Y":
       moj_socket.connect(server)
       moj_socket.sendto("Y".encode(), server)
       print("Som pripojeny na server")
       return True                      #tu treba vyriesit co ked server neposle suhlas

def klient_chce_nastavit_velkost_fragmentu(moj_socket,server):
    moj_socket.sendto("F".encode(), server)
    velkost_fragmentu = input("Zadajte maximalnu velkost fragmentu:  ")        
    if (int(velkost_fragmentu) > max_velkost - 100):                                                 #- velkost_hlavicky - velkost udp a ip hlaviciek)
        velkost_fragmentu = str(max_velkost - 100)
    print("Velkost fragmentu nastavena na : "+ velkost_fragmentu)
    moj_socket.sendto(velkost_fragmentu.encode(), server)
    return int(velkost_fragmentu)

def vytvor_hlavicku(poradie_fragmentu,cast_obsahu):
    hlavicka = str(poradie_fragmentu) +"/" + str(binascii.crc32(cast_obsahu)) + "#"              #zistit velkost hlavicky
    return hlavicka.encode()


def klient_chce_poslat_obrazok(moj_socket,server,velkost_fragmentu):          # tu treba vyriesit ked packety budu chybat, cakanie na acknowledgement
    nazov = input("Zadajte nazov obrazku:  ")
    reakcia = ""
    moj_socket.sendto("O".encode(), server)
    with open(nazov,"rb") as file:
        obsah = file.read()

    poradie_fragmentu = 1
    while (obsah != b""):              
        cast_obsahu = obsah[:velkost_fragmentu]
        if (len(cast_obsahu) < velkost_fragmentu):
             cast_obsahu += (velkost_fragmentu - len(cast_obsahu))*b" "
        obsah = obsah[velkost_fragmentu:]

        hlavicka = vytvor_hlavicku(poradie_fragmentu,cast_obsahu)
        moj_socket.sendto(hlavicka + cast_obsahu, server)   

        reakcia, server = moj_socket.recvfrom(max_velkost)
        if (reakcia.decode() == "N"+str(poradie_fragmentu)):
            while (reakcia.decode() != "Y" + str(poradie_fragmentu)):
                moj_socket.sendto(hlavicka + cast_obsahu, server)    
                reakcia, server = moj_socket.recvfrom(max_velkost)
        poradie_fragmentu += 1

    print("Obrazok poslany")
    moj_socket.sendto("E".encode(), server)

def klient_chce_poslat_spravu(moj_socket,server,velkost_fragmentu):            # tu treba vyriesit ked packety budu chybat, cakanie na acknowledgement
     sprava = input("Napiste spravu:  ")
     reakcia = ""
     moj_socket.sendto("S".encode(), server)
     poradie_fragmentu = 1
     while (sprava != ""):
         cast_spravy = sprava[:velkost_fragmentu]
         if (len(cast_spravy) < velkost_fragmentu):
             cast_spravy += (velkost_fragmentu - len(cast_spravy))*" "
         sprava = sprava[velkost_fragmentu:]
        
         hlavicka = vytvor_hlavicku(poradie_fragmentu,cast_spravy.encode())
         moj_socket.sendto(hlavicka + cast_spravy.encode(), server)   

         reakcia, server = moj_socket.recvfrom(max_velkost)
         if (reakcia.decode() == "N"+str(poradie_fragmentu)):
            while (reakcia.decode() != "Y" + str(poradie_fragmentu)):
                moj_socket.sendto(hlavicka + cast_obsahu, server)    
                reakcia, server = moj_socket.recvfrom(max_velkost)
         poradie_fragmentu += 1

     print("Sprava poslana")
     moj_socket.sendto("E".encode(), server)







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
            som_pripojeny = klient_sa_chce_pripojit(moj_socket,server,velkost_fragmentu)

        elif prikaz == 'F' and som_pripojeny == True:
            velkost_fragmentu = klient_chce_nastavit_velkost_fragmentu(moj_socket,server)
            
        elif prikaz == 'K' and som_pripojeny == True:
            print("Koniec")
            moj_socket.sendto("K".encode(), server)
            break

        elif prikaz == 'S' and som_pripojeny == True:
            klient_chce_poslat_spravu(moj_socket,server,velkost_fragmentu)

        elif prikaz == 'O' and som_pripojeny == True:
            klient_chce_poslat_obrazok(moj_socket,server,velkost_fragmentu)

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