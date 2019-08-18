#!/usr/bin/python3
# -*- coding: utf-8 -*-
import urllib, json
import requests
import time
import datetime
import speech_recognition as sr
import random
import threading
import re


######VARIABLES
nom = "Arthur" #Le nom par default est Arthur

jourSemaine=["lundi","mardi","mercredi","jeudi","vendredi","samedi","dimanche"]



"""
https://api.navitia.io/v1/journeys?from=2.2934000000000196;48.8859&to=2.358100000000036;48.8099&datetime=20190209T174740
https://api.navitia.io/v1/journeys?from=2.2934000000000196;48.8859&to=2.330436;48.864244&datetime=20190209T190040&forbidden_uris[]=physical_mode:Bus

https://api.darksky.net/forecast/7e947064852bbae07dea882d4412ce93/42.3601,-71.0589,255657600?lang=fr
https://api.darksky.net/forecast/7e947064852bbae07dea882d4412ce93/48.856614,%202.3522219?lang=fr&units=si
^Paris

"""

#Fonctions
def getTimeAndDay():
    date = datetime.datetime.now()
    a = [((datetime.datetime.today().weekday() ) % 7 ), (date.hour), (date.minute) ]
    return a

def urltoJsonMeteo(url= "https://api.darksky.net/forecast/7e947064852bbae07dea882d4412ce93/48.856614,%202.3522219?lang=fr&units=si" ):
    requ= urllib.request.urlopen(url)         
    data = json.loads(requ.read().decode())
    #print(data)
    return data
data = ""
def Meteo(ville="Paris", quand=0, Infos=0):
    """
    calcul coordonées géographiques"
    """
    
    url= "https://api.opencagedata.com/geocode/v1/json?q="+ville+"&key=a4078987eaeb4bb7b9ba8eb46950032f"
    requ= urllib.request.urlopen(url)         
    data = json.loads(requ.read().decode())
    
    lat = (data["results"][0]["bounds"]["northeast"]["lat"])
    lng =  (data["results"][0]["bounds"]["northeast"]["lng"])
    #return data    
    
    if quand>1:
        jourdemandé = jourSemaine[getTimeAndDay()[0]-1+quand]
    elif quand==0:
        jourdemandé = "aujourd'hui"
    else:
        jourdemandé = "demain"
        
    unités = ""
        
    """
    Infos:
        0-Summary
        1-Temp
        2-windSpeed
        3-Pression
        4-Humidity 
        5-pluie           
    """
    info = ''
    data = urltoJsonMeteo("https://api.darksky.net/forecast/7e947064852bbae07dea882d4412ce93/"+str(lat)+",%20"+str(lng)+"?lang=fr&units=si")
    if Infos == 0:
       info = 'summary' 
    elif Infos == 1:
        temp = (data["currently"]["temperature"])
        return (str(  round(temp, 1))+ " degrés")
       
    elif Infos == 2:
        info = 'windSpeed'
        unités = " m.s-1"
    elif Infos == 3:
        info = 'pressure'
        unités = " Pascals"
    elif Infos == 4:
        info = 'humidity'
        unités = " %"
    elif Infos == 5:
        info = 'precipIntensity'
        pluie = (data["daily"]["data"][quand][info])
        
        if pluie<0.1:
            print("Non, il ne va pas pleuvoir "+ jourdemandé)
        elif pluie<0.3:
            print("il  va légèrement pleuvoir "+ jourdemandé)
        elif pluie<0.5:
            print("Oui, il  va pleuvoir "+ jourdemandé)
        elif pluie>0.5:
            print("Oui, il va y avoir une averse! "+ jourdemandé)
        return pluie        
    
    return (str(data["daily"]["data"][quand][info])  + unités)
    
   


    

def textToList(phrase):
    i=0
    liste=[]
    while i < (len(phrase)):
        mot = ""
        while i < (len(phrase)) and (phrase[i] != ' '):            
            mot+= phrase[i]
            i+=1
        liste.append(mot)#.encode("utf-8"))
        i+=1
    liste[0] = liste[0].lower()
    return liste

def listeContain(liste, mot, motcomplet=False, afterIndex=0):
    for i in range (afterIndex, len(liste)):
        if mot == liste[i] or (mot in liste[i] and not motcomplet):
            return i          
    return -1


def indexMot(i, mot, liste, motcomplet=False):
    try:
        if mot == liste[i] or (mot in liste[i] and not motcomplet):
                return True
        return False 
    except:
        return False

def jourDeLaSemaine(nbr):
    return jourSemaine[nbr] 


class Time(threading.Thread):
        """Gestion de l'heure et de la date"""
        def __init__(self,interval=10.0):
                threading.Thread.__init__(self)
                self.interval=interval
                self.finished=threading.Event()
        def run(self):
                while not self.finished.isSet():                        
                        jour = getTimeAndDay()[0]
                        heure = getTimeAndDay()[1]
                        minute = getTimeAndDay()[2]
                                                
                        fichier = open("C:/Users/matth/OneDrive/Bureau/Reveil_Connecte/Reveil-Connecte/assistant_vocal/donnes/listeReveils.txt", "r")        
                        rep = fichier.readlines()
                        for i in range (len(rep)):
                             donnesReveil = (re.split("[ h]",rep[i]))  # On Transforme la ligne en liste splité aux espaces et au h
                             #print(donnesReveil)
                             if len(donnesReveil) == 5 and heure == int(donnesReveil[1]) and minute == int(donnesReveil[2]) and -1 !=  (donnesReveil[3]).find(str(jour)) and bool(donnesReveil[0]) == True:
                                 print("Réveil")
                                 #MUSIQUE REVEIL
                        fichier.close()
                                 
                        #print("jour: "+str(jourDeLaSemaine(jour-1))+". Il est: "+str(heure)+"heures et "+str(minute) + " minutes")                        
                        self.finished.wait(self.interval) 
                self.finished.set()
        def arret(self):
                self.finished.set()
a = Time()
a.start()

#synonymes
def enchante():
    l = ["Enchante ", "Content de vous revoir ", "Bien le bonjour ", "Salutation ", "Bonjour "]
    return l[random.randint(0, len(l)-1)]

def entendu():
    l = ["Entendu" , "C'est entendu ", "C'est noté ", "Je retiens ca ", "Très bien ", "Je note ça", "Je prend note"]
    return l[random.randint(0, len(l)-1)]

def alphred(phrase="", _respond=0):
    
######VARIABLES
    jour = -1
    jours = []
    repeat = False
    global nom
    zero = ""
    
    
    
# Record Audio
    if phrase == "":
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Dites quelque chose!")
            audio = r.listen(source, phrase_time_limit=5)
    
    
        
    # Speech recognition using Google Speech Recognition
    try:       
   
        # for testing purposes, we're just using the default API key
        # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
        # instead of `r.recognize_google(audio)`
        if phrase == "":
            phrase = r.recognize_google(audio, language='fr-FR', key="AIzaSyCiqFKX59tNMUeykCksuCXyZZtA5opXF20")    
      
        listeMots = textToList(phrase)
        
        print("Vous avez dit: " + phrase + "\n")
       
        #Réponse for the return of the recursive call
        if _respond != 0:
            if _respond == 1 and len(listeMots) == 1:
                return listeMots[0]
                
                
        
        
        #apprentisage du nom
        elif (listeContain(listeMots, "m'appelle") != -1 and listeContain(listeMots, "ne", True) == -1) :
            i = listeContain(listeMots, "m'appelle")
            nom = listeMots[i+1]
            print(entendu() + " " + nom)
        elif listeContain(listeMots, "mon")+1 ==  listeContain(listeMots, "nom") == listeContain(listeMots, "est")-1:
            i = listeContain(listeMots, "est")
            nom= listeMots[i+1]
            print(entendu() + " "+ nom)
            
         #Mauvais nom
        elif listeContain(listeMots, "ne")+1 == listeContain(listeMots, "m'appelle")  :
            print("Comment vous-appelez vous donc?")
            respond = alphred("", 1)
            if respond != None:
                nom = respond
                print(entendu() + ""+ nom)
            
        
        #Heure
        elif ((listeContain(listeMots, "heure") != -1 )and (listeContain(listeMots, "quelle") != -1)):
            date = datetime.datetime.now()
            if date.minute < 10:
                zero = "0"
            print("Il est " + str(date.hour) + "h" + zero+ str(date.minute) )
            zero=""
            
         #Jour
        elif ((listeContain(listeMots, "jour") != -1 )and (listeContain(listeMots, "quel") != -1)):
            jour = getTimeAndDay()[0]            
            print("On est un " + jourDeLaSemaine(jour))
            
            
        # reveil
        elif (listeContain(listeMots, "réveil") != -1 )and ((indexMot((listeContain(listeMots, "réveil")+1), "à", listeMots)) or (indexMot((listeContain(listeMots, "réveil")+2), "à", listeMots)) or (indexMot((listeContain(listeMots, "réveil")+3), "à", listeMots)) or (indexMot((listeContain(listeMots, "réveil")+4), "à", listeMots)) or (indexMot((listeContain(listeMots, "réveil")+5), "à", listeMots)) or (indexMot((listeContain(listeMots, "réveil")+6), "à", listeMots)) or (indexMot((listeContain(listeMots, "réveil")+7), "à", listeMots))):
            jour = ((datetime.datetime.today().weekday() ) % 7 )
            #print("jour:" + str(jour))
            if listeContain(listeMots, "chaque") != -1 or (listeContain(listeMots, "tous") != -1 and listeContain(listeMots, "les") != -1):
                repeat = True
            if  listeContain(listeMots, "après-demain") != -1 or (listeContain(listeMots, "après") != -1 and listeContain(listeMots, "demain") != -1):
                jour = ((datetime.datetime.today().weekday() ) % 7 )
                jour= (jour+2)%7
                jours.append(str(jour))
            if  listeContain(listeMots, "demain") != -1 and listeContain(listeMots, "après") == -1:
                jour = ((datetime.datetime.today().weekday() ) % 7 )
                jour= (jour+1)%7
                jours.append(str(jour))
            if  listeContain(listeMots, "aujourd'hui") != -1:
                jour = ((datetime.datetime.today().weekday() ) % 7 )
                jours.append(str(jour))
            if  listeContain(listeMots, "lundi") != -1:
                jour= 0
                jours.append(str(jour))
            if  listeContain(listeMots, "mardi") != -1:
                jour= 1
                jours.append(str(jour))
            if  listeContain(listeMots, "mercredi") != -1:
                jour= 2
                jours.append(str(jour))
            if  listeContain(listeMots, "jeudi") != -1:
                jour= 3
                jours.append(str(jour))
            if  listeContain(listeMots, "vendredi") != -1:
                jour= 4
                jours.append(str(jour))
            if  listeContain(listeMots, "samedi") != -1:
                jour= 5
                jours.append(str(jour))
            if  listeContain(listeMots, "dimanche") != -1:
                jour= 6
                jours.append(str(jour))
            elif len(jours) == 0 and (datetime.datetime.today().hour>=20 or datetime.datetime.today().hour<6):
                jour = ((datetime.datetime.today().weekday() +1) % 7 )
                jours.append(str(jour)) # Si on ne précise pas le jours  et qu'il est > 20h on met le reveil à demain
            elif len(jours) == 0:
                jour = ((datetime.datetime.today().weekday()) % 7 )
                jours.append(str(jour-1)) # Sinon on le met à aujourd'hui
            indexMotReveil = listeContain(listeMots, "réveil")
            indexReveil = listeContain(listeMots, "à", True, indexMotReveil) +1
            reveil = listeMots[indexReveil]
            print(entendu() + "! Je mets un reveil à " + reveil +"!" )
            fichier = open("donnes/listeReveils.txt", "a")        
            fichier.write("True " + reveil+ " " + ''.join(jours) + " " + str(repeat) + "\n")
            fichier.close()            
           
            fichier = open("donnes/listeReveils.txt", "r")        


        elif not (listeContain(listeMots, "salut") == listeContain(listeMots, "bonjour") == listeContain(listeMots, "hello") == listeContain(listeMots, "yo")):
            print(enchante() +nom)            
        
        
        else:
            if(_respond ==0):
                print ("Je n'ai pas compris! :(" )
        
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))
   # except:
    #    print "Je n'ai pas compris! :( \nEt je suis blindé!"

alphred()