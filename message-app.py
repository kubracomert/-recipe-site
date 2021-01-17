import sqlite3
import cryptography
from cryptography.fernet import Fernet
import random
import hashlib as hasher
import numpy as np
import cv2

def rast():#rastgele oluşturulacak metin için fonksiyon
    metin= """We take revenge during goat-yoga class.
    A herd of ladies arrive each Saturday, and
    Friday night we gorge ourselves like horses
    before a race. We watch, waiting for one moment:
    table pose. When they’re on all fours, we snap
    into action: climb up on their backs, pose for
    a picture, then release the coffee bean waterfall
    right into their highlighted hair. The group
    screams! We feign ignorance. Who else can dominate
    humans this way and go unpunished? Serving goat
    cheese with wine tonight, Brittany? Ok. But remember
    you’re about to go into downward dog, and none of
    us are housebroken."""

    x=metin.split()
    y=random.sample(x,20)
    yeni=""
    for i in y:
       yeni=yeni+" "+str(i)
    return yeni                
            
sifreleyici=hasher.sha256()#özet için

con=sqlite3.connect("KVT.db")#veri tabanı ile olan bağlantıyı açma

kullaniciAd=input("Kullanıcı Adı:")
parola=input("Parola:")

sorgu = "SELECT id FROM kullanicilar where ad='{}'". format(kullaniciAd)#giriş yapılan kullanıcı adına ait id'yi alma
cursor=con.cursor()
cursor.execute(sorgu)
id1= cursor.fetchone()

sorgu1 = "SELECT id FROM kullanicilar where parola='{}'".format(parola)#giriş yapılan parolaya ait id'yi alma
cursor1=con.cursor()
cursor1.execute(sorgu1)
id2= cursor1.fetchone()


if id1==None or id2==None:
    print('Kullanıcı adı ya da parola hatalı!')

elif id1==id2:#alınan id'lerin eşleşmesi durumunda girişe izin verme
   print("Giriş Başarılı")
   islem=input('''Yapmak istediğiniz işlemi seçiniz:
      1.Mesaj gönder
      2.Mesajlara bak\n ''')

   if(islem=="1"):
       
        alici=input("Mesaj göndermek istediğiniz kullanıcı adını giriniz:")
        key=Fernet.generate_key()#anahtar oluşturma
        f=Fernet(key)

        sorgu2="SELECT id FROM kullanicilar where ad='{}'".format(alici)#ekrandan girilen alıcının id'sini alma
        cursor2=con.cursor()
        cursor2.execute(sorgu2)
        aliciID = cursor2.fetchone()

        if aliciID==None:
            print('Böyle bir kullanıcı bulunmamaktadır!')
        else:
            a=input("Kullanıcıya mesaj göndermek için 1'e basınız.\nKullanıcıya rastgele oluşturulan metni iletmek için 2'ye basınız.")
            
            if a=='1':
                mesaj=input("Gönderilecek mesajı giriniz: ")
                sifreleyici.update(mesaj.encode("utf-8"))#mesajın özetini alma
                hashliMetin = sifreleyici.hexdigest()
                      
                token = f.encrypt(mesaj.encode("utf-8"))#mesajı şifreleme
                
                sorgu3y="""INSERT INTO anahtar(aliciId, gondericiId,anahtar) VALUES ({},{},"{}") """.format(aliciID[0],id1[0],key)#anahtar tablosuna ekleme
                cursor3y=con.cursor()
                cursor3y.execute(sorgu3y)
                
                sorgug="""SELECT anahtarId FROM anahtar where anahtar="{}" """.format(key)#anahtarın id'sini alma
                cursorg=con.cursor()
                cursorg.execute(sorgug)
                aId=cursorg.fetchone()
                
                #mesaj bilgilerinin mesajlar tablosuna eklenmesi
                sorgu3="""INSERT INTO mesajlarTbl(anahtarId,alanID, gonderenID,mesajIcerik,ozet) VALUES ({},{},{},"{}","{}")""".format(aId[0],aliciID[0],id1[0],token,hashliMetin)
                cursor3=con.cursor()
                cursor3.execute(sorgu3)
                
                print("Mesaj Gönderildi!")
      

            elif a=='2':
                x=rast()#rastgele mesaj oluşturma
                print("Oluşan mesaj:{}".format(x))
                sifreleyici.update(x.encode("utf-8"))#oluşan mesajın özetini çıkarma
                hashliMetin = sifreleyici.hexdigest()
                 
                token = f.encrypt(x.encode("utf-8"))#oluşan mesajı şifreleme
                
                sorgu3y="""INSERT INTO anahtar(aliciId, gondericiId,anahtar) VALUES ({},{},"{}") """.format(aliciID[0],id1[0],key)#anahtar tablosuna ekleme
                cursor3y=con.cursor()
                cursor3y.execute(sorgu3y)
                
                sorgug="""SELECT anahtarId FROM anahtar where anahtar="{}" """.format(key)#anahtar id
                cursorg=con.cursor()
                cursorg.execute(sorgug)
                aId=cursorg.fetchone()

                #mesaj bilgilerini mesajlar tablosuna ekleme
                sorgu3="""INSERT INTO mesajlarTbl(anahtarId,alanID, gonderenID,mesajIcerik,ozet) VALUES ({},{},{},"{}","{}")""".format(aId[0],aliciID[0],id1[0],token,hashliMetin)
                cursor3=con.cursor()
                cursor3.execute(sorgu3)
                
                print("Mesaj Gönderildi!")
       
            
   elif(islem=="2"):
       
            sorgu4="SELECT gonderenID FROM mesajlarTbl where alanID = '{}'".format(id1[0])

            cursor4=con.cursor()
            cursor4.execute(sorgu4)
            gonderenID=cursor4.fetchone()

            sorgukey="SELECT * FROM anahtar where aliciId = '{}'".format(id1[0])#gelen mesajın anahtar tablosunda ki anahtarını almak için
            cursorkey=con.cursor()
            cursorkey.execute(sorgukey)
            size=cursorkey.fetchall()
            for i in size:
                dbkey=i[3]
            dbkey=dbkey[1:]
            
            sorgu5="SELECT ad FROM kullanicilar where id='{}'".format(gonderenID[0])#mesajı gönderen kişinin adını almak için
            cursor5=con.cursor()
            cursor5.execute(sorgu5)
            for i in cursor5.fetchall():
                 gonderen=str(i[0])
            print("Gönderen Kişi:"  + gonderen)

            sorgu6="SELECT * FROM mesajlarTbl where alanID = '{}' ".format(id1[0])#mesajlar tablosunda ki mesaj bilgileri için
            cursor6=con.cursor()
            cursor6.execute(sorgu6)
            
            for i in cursor6.fetchall():
                vtgMesaj=str(i[4])
                ozetliMesaj=str(i[5])
          
            vtgMesaj=vtgMesaj[1:]
            vtgAnahtar=Fernet(dbkey)#veri tabanından gelen anahtarın Fernet ile tanımlanması
            mesajCoz=vtgAnahtar.decrypt(vtgMesaj.encode('utf-8'))#anahtar ile mesajın çözülmesi
            mesajCoz=mesajCoz.decode("utf-8")
            print("Gelen mesaj: {}".format(mesajCoz))
            
            mesajCoz=vtgAnahtar.decrypt(vtgMesaj.encode('utf-8'))
            sifreleyici.update(mesajCoz)#çözülen mesajın özetinin alınması
            hashliMetin = sifreleyici.hexdigest()
            
            if ozetliMesaj!=hashliMetin:#veri tababanından gelen özet ile burada tekrar oluşturulan özetin karşılaştırılması
                print("değiştirilmiş")
        

else:
    print('Kullanıcı adı ya da parola hatalı!')
con.commit()
con.close()#veri tabanı bağlantısının kapatılması
