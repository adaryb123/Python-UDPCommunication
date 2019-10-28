import socket
import binascii             #kniznica na vypocet CRC
import os                   #kniznica na zobrazenie adresara v ktorom sa nachadzame

#--------------------------------------------------------------------------------------------------------------------------------------------------------
max_velkost = 1500

def get_ip_address():                           # tato funkcia je skopirovana zo Stack overflow, sluzi na zistenie svojej IP adresy
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

def pustim_sa_pri_starte_servera():
    ip_servera = get_ip_address() # "169.254.112.14"
    port = 30000
    server = (ip_servera, port)
    vypisy = False
    velkost_fragmentu = max_velkost - 100
    print("Server spusteny.")
    print("Server ma ip " + ip_servera + " a port " + str(port))
    print("Defaultna maximalne velkost fragmentu je: "+str(max_velkost))
    print("")
    return server,velkost_fragmentu,vypisy

def server_potvrdi_pripojenie_klienta(moj_socket,klient,velkost_fragmentu):
    moj_socket.sendto("Y".encode(), klient)
    sprava, klient = moj_socket.recvfrom(1)
    if sprava.decode() == "Y":
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

def server_chce_prijat_obrazok(moj_socket,klient,velkost_fragmentu,vypisy):
    buffer = b""
    poradie_fragmentu = "0"
    nazov,klient = moj_socket.recvfrom(max_velkost)
    celkovy_pocet_fragmentov, klient = moj_socket.recvfrom(max_velkost)
    celkovy_pocet_fragmentov = celkovy_pocet_fragmentov.decode()

    while (int(poradie_fragmentu) != int(celkovy_pocet_fragmentov)):
        fragment, klient = moj_socket.recvfrom(max_velkost)
        poradie_fragmentu,prijaty_checksum,data = rozdel_fragment(fragment,velkost_fragmentu)
        vypocitany_checksum = binascii.crc32(data)

        if (vypisy == True):
            print("Prisiel fragment cislo " + poradie_fragmentu + " z celkoveho poctu " + celkovy_pocet_fragmentov + " a s velkostou " + str(velkost_fragmentu))
   
        if (str(prijaty_checksum) == str(vypocitany_checksum)):
           moj_socket.sendto(("Y" + poradie_fragmentu).encode(), klient)        
           buffer += data
        else:
           print("Chyba vo fragmente " + poradie_fragmentu)
           moj_socket.sendto(("N" + poradie_fragmentu).encode(), klient)

    with open("OUTPUT" + nazov.decode(),"wb") as file:
        file.write(buffer)
    print("Obrazok prijaty a ulozeny do " + str(os.getcwd()))

def skrat_koniec(sprava):
    while True:
        if (sprava[-1] == " "):
            sprava = sprava[:-1]
        else:
            break
    return sprava
       
def server_chce_prijat_spravu(moj_socket,klient,velkost_fragmentu,vypisy):
    buffer = ""
    poradie_fragmentu = "0"
    celkovy_pocet_fragmentov, klient = moj_socket.recvfrom(max_velkost)
    celkovy_pocet_fragmentov = str(celkovy_pocet_fragmentov.decode())

    while (int(poradie_fragmentu) != int(celkovy_pocet_fragmentov)):
        fragment, klient = moj_socket.recvfrom(max_velkost)
        poradie_fragmentu,prijaty_checksum,data = rozdel_fragment(fragment,velkost_fragmentu)
        vypocitany_checksum = binascii.crc32(data)

        if (vypisy == True):
            print("Odoslal sa fragment cislo " + poradie_fragmentu + " z celkoveho poctu " + celkovy_pocet_fragmentov + " a s velkostou " + str(velkost_fragmentu))
   
        if (str(prijaty_checksum) == str(vypocitany_checksum)):
           moj_socket.sendto(("Y" + poradie_fragmentu).encode(), klient)        
           buffer += data.decode()
        else:
           print("Chyba vo fragmente " + poradie_fragmentu)
           moj_socket.sendto(("N" + poradie_fragmentu).encode(), klient)           

    buffer = skrat_koniec(buffer)
    print("Sprava od klienta :" + buffer)


def nastav_vypisovanie(vypisy):
    if (vypisy == False):
        print("Odteraz vypisujeme poradie fragmentov")
        return True
    else:
        print("Odteraz nevypisujeme poradie fragmentov")
        return False








def pusti_ako_server():
    server,velkost_fragmentu,vypisy = pustim_sa_pri_starte_servera()
    moj_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    moj_socket.bind(server)

    while True:
        prikaz, klient = moj_socket.recvfrom(1)
        prikaz = prikaz.decode()
        if prikaz == "K":
             print("Koniec")
             break

        elif prikaz == "V":
             vypisy = nastav_vypisovanie(vypisy) 
         
        elif prikaz == "C":
             print("Prijate subory sa nachadzaju v priecinku : " + str(os.getcwd()))

        elif prikaz == "P":
             server_potvrdi_pripojenie_klienta(moj_socket,klient,velkost_fragmentu)

        elif prikaz == "F":
             velkost_fragmentu = server_chce_prijat_velkost_fragmentu(moj_socket,klient)

        elif prikaz == 'O':
             server_chce_prijat_obrazok(moj_socket,klient,velkost_fragmentu,vypisy)

        elif prikaz == 'S':
              server_chce_prijat_spravu(moj_socket,klient,velkost_fragmentu,vypisy)

        moj_socket.sendto("H".encode(), klient)
    moj_socket.close()

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------

def pustim_sa_pri_starte_klienta():
     ip_servera = get_ip_address()
     port = 30000
     server = (ip_servera,port)
     vypisy = False
     velkost_fragmentu = max_velkost - 100
     print("Defaulna ip servera je: " + ip_servera)
     print("Defaultny port je:" + str(port))
     print("Defaultna maximalne velkost fragmentu je: "+str(max_velkost))
     print("Vypisovanie poradi fragmentov je vypnute")
     print("")
     print("Zadajte N pre nastavenie ip adresy alebo portu")
     print("Zadajte P pre pripojenie na server")
     print("Zadajte F pre nastavenie maximalnej velkosti fragmentu")
     print("Zadajte V pre nastavenie vypisovanie poradi fragmentov")
     print("Zadajte C pre zobrazenia cesty k suboru")                           
     print("Zadajte S pre poslanie spravy")
     print("Zadajte O pre poslanie obrazku")
     print("Zadajte W pre vlozenie chyby do fragmentu")
     print("Zadajte K pre ukoncienie\n")
     return server,velkost_fragmentu,vypisy

def klient_sa_chce_pripojit(moj_socket,server,velkost_fragmentu):
    moj_socket.sendto("P".encode(), server)
    odpoved, ip_servera = moj_socket.recvfrom(velkost_fragmentu)
    if odpoved.decode() == "Y":
       moj_socket.connect(server)
       moj_socket.sendto("Y".encode(), server)
       print("Som pripojeny na server")
       return True
    else:
       print("Nepodarilo sa pripojit")
       return False

def klient_chce_nastavit_velkost_fragmentu(moj_socket,server):
    moj_socket.sendto("F".encode(), server)
    velkost_fragmentu = input("Zadajte maximalnu velkost fragmentu:  ")        
    if (int(velkost_fragmentu) > max_velkost - 100):                                               
        velkost_fragmentu = str(max_velkost - 100)
    print("Velkost fragmentu nastavena na : "+ velkost_fragmentu)
    moj_socket.sendto(velkost_fragmentu.encode(), server)
    return int(velkost_fragmentu)

def vytvor_hlavicku(poradie_fragmentu,cast_obsahu,je_chyba):
    hlavicka = str(poradie_fragmentu) +"/" + str(binascii.crc32(cast_obsahu)+je_chyba) + "#"              
    return hlavicka.encode()


def klient_chce_poslat_obrazok(moj_socket,server,velkost_fragmentu,vypisy,chyba):         
    nazov = input("Zadajte nazov obrazku:  ")
    moj_socket.sendto("O".encode(), server)
    moj_socket.sendto(nazov.encode(), server)
    with open(nazov,"rb") as file:
        obsah = file.read()

    poradie_fragmentu = 1
    celkovy_pocet_fragmentov = int(len(obsah)/velkost_fragmentu) + 1
    moj_socket.sendto(str(celkovy_pocet_fragmentov).encode(), server)
    while (poradie_fragmentu <= celkovy_pocet_fragmentov):              
        cast_obsahu = obsah[:velkost_fragmentu]
        if (len(cast_obsahu) < velkost_fragmentu):
             cast_obsahu += (velkost_fragmentu - len(cast_obsahu))*b" "

        je_chyba = 0
        if (poradie_fragmentu == chyba):
              je_chyba = 99
              chyba = 0
        hlavicka = vytvor_hlavicku(poradie_fragmentu,cast_obsahu,je_chyba)

        moj_socket.sendto(hlavicka + cast_obsahu, server)  

        if (vypisy == True):
            print("Odoslal sa fragment cislo " + str(poradie_fragmentu) + " z celkoveho poctu " + str(celkovy_pocet_fragmentov) + " a s velkostou " + str(velkost_fragmentu))

        moj_socket.settimeout(20)
        try:
            reakcia, server = moj_socket.recvfrom(max_velkost)
            moj_socket.settimeout(None)
            if (reakcia.decode() == "N"+str(poradie_fragmentu)):
                 continue
            elif (reakcia.decode() == "Y"+str(poradie_fragmentu)):
                 obsah = obsah[velkost_fragmentu:] 
                 poradie_fragmentu += 1
            else:
                continue

        except:
            moj_socket.settimeout(None)
            continue

    print("Obrazok poslany")

def klient_chce_poslat_spravu(moj_socket,server,velkost_fragmentu,vypisy,chyba):           
     sprava = input("Napiste spravu:  ")
     moj_socket.sendto("S".encode(), server)
     poradie_fragmentu = 1
     celkovy_pocet_fragmentov = int(len(sprava)/velkost_fragmentu) + 1
     moj_socket.sendto(str(celkovy_pocet_fragmentov).encode(), server)
     while (poradie_fragmentu <= celkovy_pocet_fragmentov):
         cast_spravy = sprava[:velkost_fragmentu]
         if (len(cast_spravy) < velkost_fragmentu):
             cast_spravy += (velkost_fragmentu - len(cast_spravy))*" "
           
         je_chyba = 0
         if (poradie_fragmentu == chyba):
              je_chyba = 99
              chyba = 0
         hlavicka = vytvor_hlavicku(poradie_fragmentu,cast_spravy.encode(),je_chyba)

         moj_socket.sendto(hlavicka + cast_spravy.encode(), server)   

         if (vypisy == True):
             print("Odoslal sa fragment cislo " + str(poradie_fragmentu) + " z celkoveho poctu " + str(celkovy_pocet_fragmentov) + " a s velkostou " + str(velkost_fragmentu))

         moj_socket.settimeout(20)
         try:
            reakcia, server = moj_socket.recvfrom(max_velkost)
            moj_socket.settimeout(None)
            if (reakcia.decode() == "N"+str(poradie_fragmentu)):
                 continue
            elif (reakcia.decode() == "Y"+str(poradie_fragmentu)):
                 sprava = sprava[velkost_fragmentu:] 
                 poradie_fragmentu += 1
            else:
                continue

         except:
            moj_socket.settimeout(None)
            continue

     print("Sprava poslana")







def pusti_ako_klient():
     server,velkost_fragmentu,vypisy = pustim_sa_pri_starte_klienta()
     moj_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
     som_pripojeny = False
     prikaz = input("Sem napiste prikaz:  ")
     chyba = 0
     while True:
        if prikaz == 'N':
            ip_servera = input("Zadajte novu ip:  ")
            port = int(input("Zadajte novy port:  "))
            server = (ip_servera,port)

        elif prikaz == 'P':
            som_pripojeny = klient_sa_chce_pripojit(moj_socket,server,velkost_fragmentu)

        elif prikaz == 'F' and som_pripojeny == True:
            velkost_fragmentu = klient_chce_nastavit_velkost_fragmentu(moj_socket,server)

        elif prikaz == "V" and som_pripojeny == True:
            vypisy = nastav_vypisovanie(vypisy)
            moj_socket.sendto("V".encode(), server)

        elif prikaz == "C" and som_pripojeny == True:
            print("Subory na odosielanie sa nachadzaju v priecinku : " + str(os.getcwd()))
            moj_socket.sendto("C".encode(), server)            

        elif prikaz == 'K' and som_pripojeny == True:
            print("Koniec")
            moj_socket.sendto("K".encode(), server)
            break

        elif prikaz == 'W':
            chyba = int(input("Zadajte cislo fragmentu v ktorom bude chyba, alebo 0 ak chcete chybu vypnut : "))  
            prikaz = input("Napiste vas dalsi prikaz:  ")
            continue

        elif prikaz == 'S' and som_pripojeny == True:
            klient_chce_poslat_spravu(moj_socket,server,velkost_fragmentu,vypisy,chyba)

        elif prikaz == 'O' and som_pripojeny == True:
            klient_chce_poslat_obrazok(moj_socket,server,velkost_fragmentu,vypisy,chyba)

        else:
            print("Zadali ste zly prikaz alebo nieste pripojeny na server")
            prikaz = input("Napiste vas dalsi prikaz:  ")
            continue
        if (som_pripojeny == False):
            prikaz = input("Napiste vas dalsi prikaz:  ")
            continue

        odpoved, ip_servera = moj_socket.recvfrom(1)
        if (odpoved.decode() == "H"):
            prikaz = input("Napiste vas dalsi prikaz:  ")
        else:
            print("niekde je chyba")
     moj_socket.close()



#--------------------------------------------------------------------------------------------------------------------------------------------------------

moznost = input("Ak sa ma tento PC spravat ako server, zadajte 1, ak sa ma spravat ako klient,zadajte 2\n")

if moznost == "1":
    pusti_ako_server()
elif moznost == "2":
    pusti_ako_klient()
else:
    print("Zadali ste zly vstup")