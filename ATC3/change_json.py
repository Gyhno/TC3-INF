import re
from zipfile import ZipFile
import json


def get_info(country,continent):  #prend en argument le pays
                                   #et le contient(océanie ou amérique du sud)
    with ZipFile('{}.zip'.format(continent),'r') as z:
        return json.loads(z.read('{}.json'.format(country)))


a= get_info('Australia','oceania')
v=get_info('Vanuatu','oceania')
f=get_info('Fiji','oceania')
m=get_info('Federated_States_of_Micronesia','oceania')
p=get_info('Papua_New_Guinea','oceania')
nz=get_info('New_Zealand','oceania')
ar=get_info('Argentina','south_america')
bo=get_info('Bolivia','south_america')
br=get_info('Brazil','south_america')
u=get_info('Uruguay','south_america')
ch=get_info('Chile','south_america')
co=get_info('Colombia','south_america')
per=get_info('Peru','south_america')
s=get_info('Suriname','south_america')
nau=get_info('Nauru','oceania')
pau=get_info('Palau','oceania')
k=get_info('Kiribati','oceania')
mai=get_info('Marshall_Islands','oceania')
ven=get_info('Venezuela','south_america')
sam=get_info('Samoa','oceania')
sal=get_info('Solomon_Islands','oceania')
ton = get_info('Tonga','oceania')
tuv = get_info('Tuvalu','oceania')
ec = get_info('Ecuador','south_america')
gu = get_info('Guyana','south_america')
pa = get_info('Paraguay','south_america')

def print_capital(info): #pour obtenir les info correspondantes
  nom_pays = info.get('commun_name') #nom commun du pays
  capital = info.get('capital') #capitale du pays
  coord = info.get('coordinates') #coordonnées
  return nom_pays, capital, coord
  
def get_name(info): #Pour avoir le nom commun du pays
    name=info['conventional_long_name']
    if "Argentine" in name:  #problème inexplicable avec l'argentine
        return "Argentine"
    elif '[[' in name:
        new_name = re.match("\[\[(\w+)\]\]", name) 
        new_name=new_name.group(1)
    elif '[' in name:
        new_name=re.match("\[(\w+)\]", name) 
        new_name=new_name.group(1)
    else:
        new_name=name
    return new_name

def get_capital(info): #Pour avoir l'info sur la capitale du pays
    capital = info['capital']
    if 'common_name' in info:
        if info['common_name'] =='Bolivia': # cas particulier à traiter
            return 'Sucre is the constitutional capital, but the government seats at La Paz'
    if '[[' in capital: 
        capital=capital[2:-2]
    return capital
    
def get_population(info): #renvoie info sur la population
    if 'common_name' in info:
        if info['common_name']=='Venezuela': # cas particulier pour que ça fonctionne
            return '28,067,000' #info trouvée à coté
    if 'population_census' in info:
        return info['population_census']
    elif "population_estimate" in info:
        pop=info['population_estimate']
        if "(2019)" in pop:
            pop=pop[:-7]
        if "{{increase}}" in pop:
            pop=pop[13:]
        return pop
    return "not found" # le cas échéant

def get_head_of_state(info):    #renvoie le nom du leader
                                #et son titre (ex : President, Roi..)
    if 'leader_title1' in info:
        if 'common_name' in info:
            if info['common_name']=='Chile':   #pour le chili ca ne marche pas
                                                #alors on le fait manuellement
                return('Sebastián Piñera','President')
            if info['common_name']=='Venezuela':
                return('Nicolas Maduro','President') #idem pour Venezuela
        title=info['leader_title1'] #certain leader ne sont pas président
        name=info['leader_name1']
        if '[[' in name:
            t=re.match("\[\[([\w ]+)",name) #on enleve les '['
            if t is None:
                return "Erreur sur la page wikipédia"
            name = t.group(1)   #sinon on a le nom
        if '[[' in title:
            t=re.match("\[\[([\w ]+)",title) #on enleve les '['
            if t is None:
                return "Erreur sur la page wikipédia"
            title = t.group(1)
        if "Monarch" in title:  
            title="Monarch"
        if "President" in title:
            title="President"
        return (name,title)
    return "Erreur sur la page wikipédia"



def get_coords(info):  #récupération des coordonnées du pays
    """ne fonctionne que pour les formats Nbre|nbre|lettre|nb|nb|lettre|qqchose, il faut traiter à part ceux qui on des secondes NB|nb|nb|lettre"""
    lat=None #initialisation des coordonnées
    long=None
    if 'common_name' in info: #on traite le cas particulier du Vanuatu
        if info['common_name']=='Vanuatu':
            return{'lat':'17°43'+"'"+'48"S','long':'163°19'+"'"+'00"E'}
    if "coordinates" in info: #on cherche les coordonnées dans les informations
        coo=info['coordinates']
        if '{{' in coo: #on récupère les coordonnées et on les met en forme
            m = re.match("(?i).*{{coord\s*\|([^}]*)}}", coo)
            coo = m.group(1)
            
            m=re.match('(\w+)\|(\w+)\|(\w+)\|(\w+)\|(\w+)\|(\w+)',coo)
            if m.group(3) in ['N','S']: #on continue à mettre en forme les coordonnées
                lat=m.group(1)+"°"+m.group(2)+"' "+m.group(3)
                long=m.group(4)+"°"+m.group(5)+"' "+m.group(6)
            else:
                m=re.match('(\w+)\|(\w+)\|(\w+)\|(\w+)\|(\w+)\|(\w+)\|(\w+)\|(\w+)',coo)
                lat=m.group(1)+"°"+m.group(2)+"' "+m.group(3)+'"'+m.group(4)
                long=m.group(5)+"°"+m.group(6)+"' "+m.group(7)+'"'+m.group(8)
        co={'lat':lat , 'long':long} #on choisit un format d'affichage des coordonnées
        return co
    return {'lat':'???','long':'???'} #cas terminal que l'on ne doit pas rencontrer

#récupération de la surface du pays

def get_surface(info): 
    """on cherche la surface dans les informations du pays et on la retourne"""
    return info['area_km2']

#récupération du PIB du pays 

def nettoie(str): 
    """fonction qui enlève des blocs inutiles de type '-----&' dans les chaînes de caractère """
    i=0
    while str[i] != '&':
        i=i+1
    return str[:i-1]+" "+str[i+6:]
            
def get_gdp(info):
    if 'common_name' in info: #on traite les cas particuliers de l'Australie et du Venezuela
        if info['common_name']=='Australia':
            return '$1.313 trillion'
        if info['common_name']=='Venezuela':
            return '$70,14 billion'
    if 'GDP_PPP' in info: #on cherche le PIB dans les informations du pays pour les autres cas
        pib=info['GDP_PPP']
        if "&nbsp;" in pib: #on nettoie la chaîne de caractères correspondant au PIB si besoin
            pib=nettoie(pib)
        return pib
    return "beaucoup?" #cas terminal si il n'y a pas d'informations sur le PIB du pays : on ne doit pas s'y retrouver
    
    #récupération de la langue officielle du pays (ou de la première langue officielle quand il y en a plusieurs)
    
def get_languages(info):
    if "common_name" in info:#pays ne pouvant pas être traité avec le même appel que les autres
        if info["common_name"]=="Bolivia":
            return "Spanish" 
        if info["common_name"]=="New Zealand":
            return "English" 
        if info["common_name"]=="Suriname":
            return "Dutch" 
    if "languages" in info:#cas où la langue est répertorié comme 'language'
        language=info['languages']
        if "{{unbulleted" in language:#on élimine la ponctuation
            m=re.match("\{\{unbulleted list\|\[\[(\w+)",language)
            language=m.group(1)
        elif "{{hlist" in language:
            m=re.match("\{\{hlist \|\[\[([\w ]+)",language)
            language=m.group(1)
        else:
            m=re.match("\[\[([\w ]+)",language)
            language=m.group(1)
        if 'English' in language:#on trouve la langue du pays considéré
            language= 'English'
        if "Portuguese" in language:
            language="Portuguese"
        if "Spanish" in language:
            language="Spanish"
        
        return language
    elif "official_languages" in info:#cas où la langue est répertoriée comme 'official_languages'"
        language=info['official_languages']
        if "{{unbulleted" in language:#on élimine la ponctuation
            m=re.match("\{\{unbulleted list[ ]*\|[ ]*\[\[(\w+)",language)
            language=m.group(1)
        elif "{{hlist" in language:
            m=re.match("\{\{hlist[ ]*\|\[\[([\w ]+)",language)
            language=m.group(1)
        else:
            m=re.match("\[\[([\w ]+)",language)
            language=m.group(1)
        if 'English' in language:#on trouve la langue du pays considéré
            language= 'English'
        if "Portuguese" in language:
            language="Portuguese"
        if "Spanish" in language:
            language="Spanish"
        
        return language
        
#récupération de toutes les infos précédentes 
      
def get_infos(info):
  return [get_capital(info),get_name(info),get_language(info),get_head_of_state(info),get_population(info),get_surface(info),get_gdp(info),get_coords(info)]

#récupération d'une photo du pays

def get_image(country):
    return country+'.png'
    
