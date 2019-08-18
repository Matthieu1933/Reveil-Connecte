# -*- coding: iso8859-15 -*-

from Tkinter import*
import tkFileDialog,tkMessageBox
import threading
import os.path
import time
import sys

#Problème: L'angelus prend environ 15s max de retard avant de démarrer lorsque le réveil est activé.Merci pour les solutions.
t_angelus=['06:00:00','12:00:00','18:00:00']
dic_jour={'Mon':'Lundi','Tue':'Mardi','Wed':'Mercredi','Thu':'Jeudi','Fri':'Vendredi','Sat':'Samedi','Sun':'Dimanche'}
dic_mois={'Jan':'Janvier','Feb':'Février','Mar':'Mars','Apr':'Avril','May':'Mai',
          'Jun':'Juin','Jul':'Juillet','Aug':'Août','Sep':'Septembre','Oct':'Octobre',
          'Nov':'Novembre','Dec':'Décembre'}

def get_time():
        d=time.asctime()
        d=d.split()
        date=dic_jour[d[0]]+" "+d[2]+" "+dic_mois[d[1]]+" "+d[4]
        heure=d[3]
        return date,heure
                
class Angelus(threading.Thread):
        """juste pour la récitation de l'angelus"""
        def __init__(self,function,interval=1.0):
                threading.Thread.__init__(self)
                self.function=function
                self.interval=interval
                self.ange=threading.Event()
                
        def run(self):
                while not self.ange.isSet():
                        self.function()
                        self.ange.wait(self.interval)

        def bye(self):
                self.ange.set()
                
class Reveil(threading.Thread):
        """Gestion du reveil"""
        def __init__(self,time="",function=""):
                threading.Thread.__init__(self)
                self.time=time
                self.function=function
                self.go=threading.Event()

        def run(self):
                while not self.go.isSet():
                        b=get_time()
                        b=b[1]
                        if b==self.time:
                                print "c'est l'heure"
                                self.function()
                        else:   pass
                        
        def arret(self):
                self.go.set()
                        
class Time(threading.Thread):
        """Gestion de l'heure et de la date"""
        def __init__(self,canev,interval=1.0):
                threading.Thread.__init__(self)
                self.canev=canev
                self.interval=interval
                self.finished=threading.Event()
                self.dic={}
                
        def run(self):
                while not self.finished.isSet():
                        self.canev.delete(ALL)
                        b=get_time()
                        print(b)
                        x=self.canev.winfo_width()
                        y=self.canev.winfo_height()
                        self.canev.create_text(x/2,y/3,text=b[0],font='arial 12 bold',fill='red')
                        self.canev.create_text(x/2,y/2,text=b[1],font='arial 14 bold',fill='red')
                        self.finished.wait(self.interval)
                self.finished.set()
                
        def cancel(self):
                """Arrête mon Timer"""
                self.finished.set()
                
class Application(Frame):
        """Mise en place de l'interface"""
        def __init__(self):
                Frame.__init__(self)
                self.master.title("::.Reveil II.::-By Lasm Oscar Landry")
                self.configure(bg="grey40",bd=0,relief=FLAT)
                self.master.resizable(width=False, height=False)
                self.pack(padx =8, pady =8)
                self.option=['Activer','Désactiver']
                self.choixOption=StringVar()
                self.path_odio=""
                self.img={}
                self.liste=[]
                self.thread=[]
                self.arret=0
                self.build()
                self.Marie=Angelus(self.angelus)
                self.thread.append(self.Marie)
                self.Marie.start()

        def build(self):
                Label(self,text="Reveil: ",relief=FLAT,font='arial 8 bold').grid(row=0,column=0,padx=2,pady=5)
                self.ent_reveil=Entry(self,width=10,font='arial 10 bold',relief=FLAT,fg='black')
                self.ent_reveil.grid(row=0,column=1,padx=4,pady=5)
                self.bout1 = Radiobutton(self,text = self.option[0],variable = self.choixOption,value = self.option[0],
                                         relief=FLAT,command = self.optionReveil)
                self.bout1.grid(row=0,column=2,pady=5,padx=1)
                self.bout = Radiobutton(self,text = self.option[1],variable = self.choixOption,value = self.option[1],
                                         relief=FLAT,command = self.optionReveil)
                self.bout.grid(row=0,column=3,pady=5,padx=1)
                self.bout.invoke()     
                Button(self,text="Stop reveil",relief=FLAT,font='arial 6',
                       command= lambda r=1: self.zikquit(r)).grid(row=4,column=3)
                self.b=Button(self,text="Fichier Audio",relief=FLAT,font='arial 6',
                       command= lambda o=1: self.choix(o))
                self.b.grid(row=4,column=0)
                self.t_can=Canvas(self,bg='black',height=80)
                self.t_can.grid(row=5,column=0,columnspan=4)
                self.master.protocol("WM_DELETE_WINDOW",self.quitter)
                self.a=Time(self.t_can)
                self.thread.append(self.a)
                self.a.start()
                
        def optionReveil(self):
                if self.choixOption.get()=='Activer':
                        self.ent_reveil.configure(state=DISABLED)
                        if self.controle(self.ent_reveil.get()):
                                self.re=Reveil(self.ent_reveil.get(),self.zikselect)
                                self.thread.append(self.re)
                                self.re.start()
                                self.reveil=1
                                self.bout1.configure(state=DISABLED)
                        else:
                                tkMessageBox.showerror("::.For you.::","Format d'heure accepté: hh:mn:ss\n hh=heure(<=23)\nmn=minutes(<=60)\nss=sécondes(<=60)")
                                self.bout.invoke()
                                self.reveil=0
                                self.ent_reveil.delete(0,END)
                if self.choixOption.get()=='Désactiver':
                        self.ent_reveil.configure(state=NORMAL)
                        self.bout1.configure(state=NORMAL)
                        self.zikquit(1)
                        self.reveil=0
                        try:
                                self.re.arret()
                        except: pass
                
                        
        def controle(self,txt=""):
                lst=txt.split(":")
                if len(lst)==3:
                        if int(lst[0])>23 or int(lst[1])>60 or int(lst[2])>60:  return 0
                        else:   return 1
                else:
                        return 0
                

        def choix(self,o=0):
                if o:
                        self.liste=[]
                        self.path_odio=tkFileDialog.askopenfilename(filetypes=[("Fichier audio",".mp3")])
                        if self.path_odio:
                                self.liste.append(self.path_odio)
                else:   pass

        def zikselect(self):
                """Lecture du fichier audio.Ici lecture en boucle jusqu'a ce que zikquit(1)"""
                if len(self.liste):
                        v=os.path.split(self.liste[0])
                        d=v[1]
                        d=os.path.splitext(d)
                        s=d[0]
                        d=d[1]
                        if d=='.mp3':
                                import pymedia
                                self.player= pymedia.Player()
                                print self.player
                                self.player.setVolume(65000)
                                self.player.start()
                                while 1:
                                        self.player.startPlayback(v[0]+'/'+v[1])
                                        while self.player.isPlaying():
                                                if not self.player.isPlaying(): break
                                                time.sleep( 0.01 )
                                        self.arret=1
                else:
                        import pymedia
                        self.player= pymedia.Player()
                        self.player.setVolume(65000)
                        self.player.start()
                        while 1:
                                self.player.startPlayback("Maggie.mp3")                 #Utiliser un fichier .mp3 par defaut
                                while self.player.isPlaying():
                                        time.sleep( 0.01 )
                                        if not self.player.isPlaying(): break
                                self.arret=1

        def zikquit(self,r=1):
                """Pour arrêter la lecture du fichier audio"""
                if r:
                        try:
                                self.player.stop()
                        except: pass
                else:   pass
                
        def angelus(self,f1="Marie_ste.txt",f2="angelus.txt"):
                b=get_time()
                b=b[1]
                if b in t_angelus:
                        import pyTTS
                        self.tts=pyTTS.Create()
                        self.tts.SetRate(-2)
                        self.tts.SetVolume(100)
                        try:    self.bout1.configure(state=DISABLED)
                        except: pass
                        ange=open(f2,'r')
                        if self.arret:    pass
                        else:   self.zikquit(1)
                        while 1:
                                d=ange.readline()
                                d=d[:-1]
                                self.zikquit(1)
                                if d!="":
                                        if d!="amen..":
                                                if self.arret:    pass
                                                else:   self.zikquit(1)
                                                self.tts.Speak(d,0)
                                        else:
                                                if self.arret:    pass
                                                else:   self.zikquit(1)
                                                self.tts.Speak(d,0)
                                                break
                                else:
                                        ave=open(f1,'r')
                                        av=ave.readline()[:-1]
                                        while av!="":
                                                if self.arret:    pass
                                                else:   self.zikquit(1)
                                                self.tts.Speak(av,0)
                                                av=ave.readline()[:-1]
                                        ave.close()
                        ange.close()
                        self.bout1.configure(state=NORMAL)
                else:   pass
                
        def quitter(self):
                self.a.cancel()
                try:    self.re.arret()
                except: pass
                try:    self.Marie.bye()
                except: pass
                try:
                        self.tts.SetVolume(0)
                        self.tts.Stop()
                except: pass
                self.zikquit(1)
                self.master.destroy()
                sys.exit()

                
###--------------------------------------------------------------##############
if __name__=='__main__':
        app=Application()
        app.mainloop()