
import http.server
import socketserver
from urllib.parse import urlparse, parse_qs, unquote
import sqlite3
import json


conn = sqlite3.connect('pays.db')

table = ["wp", "name", "capital", "language", "flag", "head_of_state_name", "head_of_state_title", "population", "surface", "gdp", "lat", "long", "continent", 'hymne']
continent_carte = {"oceania" : [-22.294851, 166.451406, 3],  "south_america" : [-12.089175, -55.409274, 2]  }



class RequestHandler(http.server.SimpleHTTPRequestHandler): #classe principale du programme
    static_dir = '/client'   
    server_version = 'Server v0'  #on versionne le serveur
    
    # Pour gérer les requetes de types GET
    def do_GET(self): #do_get classique
        self.init_params()
        
        if self.chem_info[0] == "service" and self.chem_info[1] == "country":
            self.met_info(self.chem_info[2])   
                 
        elif self.chem_info[0] == "service" and self.chem_info[1] == "continent":
            self.met_carte(self.chem_info[2])
        else:
            self.met_statique()
    
    # Pour gérer les requetes de types HEAD
    def do_HEAD(self): #do_head classique
        self.met_statique()

    # méthode qui véhicule les info à l'utilisateur : 
    def met_info(self,country):
        req=conn.cursor() #correspond à la requete dans la base de données
        req.execute("SELECT * FROM countries WHERE name = '"+country+"'") #requete type SQL
        result = req.fetchall() #renvoie toutes les lignes de la requête 
        print(result)  #print la requete en question
        if result==[]:
            print("Ce pays n'est pas dans la base de données")
        else : 
            data = result[0] 
      # puis il faut mettre les données sous forme de dictionnaire
            compteur=0
            dict = {}
            for row in data :
                dict[table[compteur]]=row
                compteur+=1
            print(dict)
        #mettre ces données sous forme json :
        self.send_json(dict)
        
    def met_carte(self, continent):
        req = conn.cursor()
        req.execute("SELECT name, lat, long FROM countries WHERE continent = '"+continent+"'") #requete type SQL
        result = req.fetchall()
        dicts = []
        if result == []:
            print("Ce continent n'est pas dans la base de donnée")
        else :
            dicts = []
            for (name, lat, lon) in result:
                dicts.append({"name":name, "lat":lat, "lon":lon})
            
        # On envoie les données sous forme de fichier json :
        self.send_json([continent_carte[continent]] +dicts)


    #méthode pour envoyer l'objet statique voulu : 
    def met_statique(self):
        self.path = self.static_dir + self.path #on met le répertoire en préfixe pour changer le chemin d'accès
    #puis avec la methode parent : 
        if (self.command=='HEAD'):
            http.server.SimpleHTTPRequestHandler.do_HEAD(self) # avec HEAD 
        else : 
            http.server.SimpleHTTPRequestHandler.do_GET(self) # avec GET 



    #méthode pour mettre les données sous forme json    
    def send_json(self,data,headers=[]):
        bodytex = bytes(json.dumps(data),'utf-8') #codage du corps du texte
        self.send_response(200) #pour rendre la réponse avec les propriétés correctes
        self.send_header('Content-Type','application/json')
        self.send_header('Content-Length',int(len(bodytex)))
        [self.send_header(*t) for t in headers]
        self.end_headers()
        self.wfile.write(bodytex)     

  

    def send(self,body,headers=[]):
        codage = bytes(body, 'UTF-8') #on choisit ici de coder en UTF8 c'est la norme
        self.send_response(200) #pour rendre la réponse avec les propriétés correctes
    
        [self.send_header(*t) for t in headers]
        self.send_header('Content-Length',int(len(codage)))
        self.end_headers()
    
        self.wfile.write(codage)
        
    #on initialise les paramètres de la requête            
    def init_params(self):
        info = urlparse(self.path)
        self.chem_info = [unquote(v) for v in info.path.split('/')[1:]]
        self.query_string = info.query
        self.params = parse_qs(info.query)

        leng = self.headers.get('Content-Length')
        typee = self.headers.get('Content-Type')
        if leng:
            self.body = str(self.rfile.read(int(leng)),'utf-8')
            if typee == 'application/x-www-form-urlencoded' : 
                self.params = parse_qs(self.body)
        else:
            self.body = ''
    
        print('chem_info =',self.chem_info)
        print('body =',leng,typee,self.body)
        print('params =', self.params)

#
#--------------------------
#On lance le serveur
#--------------------
httpd = socketserver.TCPServer(("", 8080), RequestHandler)
httpd.serve_forever()







#
