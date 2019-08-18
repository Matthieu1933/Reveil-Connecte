#!/usr/bin/python3
# -*- coding: utf-8 -*-

import datetime
import speech_recognition as sr
import random

######VARIABLES
jour = -1
jours = []
repeat = False
jourSemaine=["lundi","mardi","mercredi","jeudi","vendredi","samedi","dimanche"]

#Le nom par default est Arthur
try:
   nom
except NameError:
  nom = "Arthur"





#Fonctions
def textToList(phrase):
    i=0
    liste=[]
    while i < (len(phrase)):
        mot = ""
        while i < (len(phrase)) and (phrase[i] != ' '):            
            mot+= phrase[i]
            i+=1
        liste.append(mot.encode("utf-8"))
        i+=1
    return liste

def listeContain(liste, mot, motcomplet=False, afterIndex=0):
    for i in range (afterIndex, len(liste)):
        if mot == liste[i] or (mot in liste[i] and not motcomplet):
            return i          
    return -1


def indexMot(i, mot, liste, motcomplet=False):
    if mot == liste[i] or (mot in liste[i] and not motcomplet):
            return True
    return False          

def jourDeLaSemaine(nbr):
    return jourSemaine[nbr] 

#synonymes
def enchante():
    l = ["Enchante ", "Content de vous revoir ", "Bien le bonjour ", "Salutation ", "Bonjour "]
    return l[random.randint(0, len(l)-1)]

def entendu():
    l = ["Entendu" , "C'est entendu ", "C'est noté ", "Je retiens ca ", " Très bien ", "Je note ça", "Je prend note"]
    return l[random.randint(0, len(l)-1)]

# Record Audio
r = sr.Recognizer()
with sr.Microphone() as source:
    print("Say something!")
    audio = r.listen(source, phrase_time_limit=5)


    
# Speech recognition using Google Speech Recognition
try:
   
    # for testing purposes, we're just using the default API key
    # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
    # instead of `r.recognize_google(audio)`
    
    phrase = r.recognize_google(audio, language='fr-FR', key="AIzaSyCiqFKX59tNMUeykCksuCXyZZtA5opXF20")    
  
    listeMots = textToList(phrase)
    
    print("You said: " + phrase + "\n")
    
    
    #apprentisage du nom
    if listeContain(listeMots, "m'appelle") != -1 and listeContain(listeMots, "ne", True) == -1:
        i = listeContain(listeMots, "m'appelle")
        nom = listeMots[i+1]
        print(entendu() + " " + nom)
    elif listeContain(listeMots, "mon")+1 ==  listeContain(listeMots, "nom") == listeContain(listeMots, "est")-1:
        i = listeContain(listeMots, "est")
        nom= listeMots[i+1]
        print(entendu() + " "+ nom)
        
    #Heure
    elif ((listeContain(listeMots, "heure") != -1 )and (listeContain(listeMots, "quelle") != -1)):
        date = datetime.datetime.now()
        print("Il est " + str(date.hour) + "h" + str(date.minute) )
        
    # reveil
    elif (listeContain(listeMots, "réveil") != -1 )and ((indexMot((listeContain(listeMots, "réveil")+1), "à", listeMots)) or (indexMot((listeContain(listeMots, "réveil")+2), "à", listeMots)) or (indexMot((listeContain(listeMots, "réveil")+3), "à", listeMots)) or (indexMot((listeContain(listeMots, "réveil")+4), "à", listeMots)) or (indexMot((listeContain(listeMots, "réveil")+5), "à", listeMots)) or (indexMot((listeContain(listeMots, "réveil")+6), "à", listeMots)) or (indexMot((listeContain(listeMots, "réveil")+7), "à", listeMots))):
        jour = ((datetime.datetime.today().weekday() + 1) % 7 )
        
        if listeContain(listeMots, "chaque") != -1 or (listeContain(listeMots, "tous") != -1 and listeContain(listeMots, "les") != -1):
            repeat = True
        if  listeContain(listeMots, "après-demain") != -1 or (listeContain(listeMots, "après") != -1 and listeContain(listeMots, "demain") != -1):
            jour= (jour+1)%7
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
        if len(jours) == 0:
            jours.append(str(jour)) # Si on ne précise pas le jours on met le reveil a demain
        indexMotReveil = listeContain(listeMots, "réveil")
        indexReveil = listeContain(listeMots, "à", True, indexMotReveil) +1
        reveil = listeMots[indexReveil]
        print(entendu() + "! Je mets un reveil à " + reveil +"!")
        fichier = open("donnes/listeReveils.txt", "a")        
        fichier.write(reveil+ " " + ''.join(jours) + " " + str(repeat) + "\n")
        fichier.close()
        
        
        fichier = open("donnes/listeReveils.txt", "r")        
        rep = fichier.readlines()
        for i in range (len(rep)):
            rep[i] = rep[i].strip().split(' ')
        fichier.close()
        
        
        
        
    #presentation
    elif(listeContain(listeMots, "t'appelles")!=-1) or (listeContain(listeMots, "es-tu")!=-1 and listeContain(listeMots, "qui")!=-1):
        print("Je suis Alfred, votre assistant vocal")
    
    
    #salutation
    elif not (listeContain(listeMots, "alut") == listeContain(listeMots, "onjour") == listeContain(listeMots, "ello") == listeContain(listeMots, "Yo")):
        print(enchante() +nom)
          
    else:
        print "Je n'ai pas compris! :(" 
    
except sr.UnknownValueError:
    print("Google Speech Recognition could not understand audio")
except sr.RequestError as e:
    print("Could not request results from Google Speech Recognition service; {0}".format(e))
except:
    print "Je n'ai pas compris! :( \nEt je suis blindé!"
