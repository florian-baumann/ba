#from antigravity import geohash
from django.shortcuts import redirect, render, HttpResponse
from .forms import UserForm
from .models import Users
from datetime import datetime, timedelta
from dateutil import parser

# from importlib.machinery import SourceFileLoader
# geohash = SourceFileLoader('geohash', '.geohash.py').load_module()

from .geohash import *
from .config import *



# #filters all users with same location-Fields
# def simil(form):
#     curr_loc = form.data['location'] #https://stackoverflow.com/questions/43014771/django-form-object-has-no-attribute-error
#     # # print(curr_loc)
#     # # print(type(curr_loc))
#     # # curr_loc = "berlin"
#     # print(curr_loc)
#     # print(type(curr_loc))
#     temp = Users.objects.filter(location=curr_loc)
#     # print(temp)
#     #temp = Users.objects.filter(location=form.data['location'])
#     return temp

# renders index.html & receive form input & redirection to answers.html with values from the form 
# def index(request):
    
#     form = UserForm()
#     if request.method == "POST":
#         form = UserForm(request.POST)
#         if form.is_valid():
#             form.save()
            
#             return render(request, "answer.html", {"users": simil(form)})

#     all_users = Users.objects.all()
#     return render(request, "index.html", {"user_form": form, "all_users": all_users})


# #renders answers.html
# def answer(request):

#     return render(request, "answer.html")

# -------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------



def latlongToGeohash(latitude, longitude, precicion):
    return encode(latitude,longitude, precicion)


#   https://stackabuse.com/python-how-to-flatten-list-of-lists/
def flattenList(list_of_lists):
    if len(list_of_lists) == 0:
        return list_of_lists
    if isinstance(list_of_lists[0], list):
        return flattenList(list_of_lists[0]) + flattenList(list_of_lists[1:])
    return list_of_lists[:1] + flattenList(list_of_lists[1:])
#   print("---------- faltlist")
#   print(flattenList(["hello", ["abcd"],["edf"]]))


def filterDiplicates(List):
    return list(set(List))
#   print("---------- filterDuplicates")
#   print(filterDiplicates(["hello", "hello", "hash", "hello"]))
    

#   input1: Geohash                initialer geohash" "in der Mitte"
#   input2: neighberhood_layers    Anzahl an Geohash Schichten um Geohash
#   output:                        List aller Geohashes um input1 Geohash herum ohne Duplicate
#   achtung! bisher nur maximal neighberhood_layers = 3
def calculate_Area(geohash, neighberhood_layers):
    geohashList = []
    geohashList.append(geohash)     #initialen Geohash hinzufügen
    index = 0
    # if index == 1:
    #     geohashList.append(neighbors(geohash))
    #     geohashList = flattenList(geohashList)
    #     #geohashList.append(geohash)
    #     index = index+1
    #     #print("tets", geohashList)
    #   enn keine Layers dann gib initialen geohash wieder zurück
    if neighberhood_layers == 0:
        return geohashList
    #   iteriere sooft wie neighberhood_Layers gefordert werden   
    while index <= neighberhood_layers:
        index = index + 1
        tempList = []
        
        #   berechne für jeden geohash in geohahsList die Neighbours und füge sie der Teporären geohashList hinzu
        for hash in geohashList:
            tempHash = neighbors(hash)
            tempList.append(tempHash)

        #   füge tempöräre geohashListe der finalen hinzu, und "entferne" eckige Klammern in der temporären Liste
        geohashList.append(flattenList(tempList))
        
        #   wenn mehr als ein Geohash, entferne eckige klammern in finale geohashListe (die der kürzlich hinzugefügten TemporärenListe)
        if index > 0:
            geohashList = flattenList(geohashList)

        #   wenn alle Layers hinzugefügt = index hochgezählt, breche while-Schleife ab
        if index == neighberhood_layers:
            break
    # filtere alle Duplikate aus GeohashListe 
    geohashListFiltered = filterDiplicates(geohashList)

    print("final calculated inner area of request:")
    print(geohashListFiltered)
    print("size of calculated geohash array:", len(geohashListFiltered))
    return geohashListFiltered

#   calculate_Area("7gxyru", 2)
#   -->
#---------- final:
# ['7gxyrq', 'k58n2n', 'k58n27', '7gxyrs', 'k58n2k', '7gxyru', 'k58n2m', '7gxyrv', '7gxyry', '7gxyrf',
#  'k58n24', '7gxyrt', 'k58n25', '7gxyr6', '7gxyrg', '7gxyrm', '7gxyrk', '7gxyr7', 'k58n2q', 'k58n26',
#  'k58n2j', '7gxyrw', 'k58n2h', '7gxyre', '7gxyrd']
# länge: 25


#   input1&2:      List of Geohashes, smae Length & Geohash length
#   return:        Prozentsatz(0-100) Integer der gleichen Elemente in geohashListe1&2 
def calculateOverlap(geohashList1, geohashList2):
    overlapNumber = 0

    #überprüfe ob Länge der Listen und Länge der Geohashes gleich ist, wenn nicht gebe Error
    if len(geohashList1) == len(geohashList2) and len(geohashList1[0]) == len(geohashList2[0]):
        
        for geohash in geohashList1:
            overlapNumber += geohashList2.count(geohash)
            #print("for: ", overlapNumber)      

        overlapPercentage = int(overlapNumber/len(geohashList1) * 100)
        print(">>> final coverage:", overlapPercentage)

        return overlapPercentage
    else:
        return -1

#   calculateOverlap(['7gxyrs', '7gxyrv', '7gxyru', 'k58n24', 'k58n2j', 'helo'], ['k58n2j', 'k58n2m', '7gxyrv', '7gxyrk', 'k58n25', 'hello'])
#   --> 
#   33


# checks if db entry is expired
def checkExpiration(user):
    print("check expiration:", user)
    if user.expire_at.timestamp() < datetime.now().timestamp():
        print("expired user deleted: ", user)
        user.delete()




# renders index.html & receive form input & redirection to answers.html with values from the form 
def index(request):
    request.POST._mutable = True
    form = UserForm()
    all_users = Users.objects.all()
    neighbors = []

    print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< new request >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

    if request.method == "POST":
        form = UserForm(request.POST)

        #print POSt request
        #print(request.POST)

        #check if entered geohash is the correct length. If not shorten it or None
        if geohash_length <= len(form.data['geohash']):
            form.data['geohash'] = form.data['geohash'][0:(geohash_length)]
        else :
            form.data['geohash'] = None


        # berechne und speichere Geohash List in DB
        form.data['geohashList'] = calculate_Area(form.data['geohash'], neighberhood_layers) 

        # berechne expire time point
        form.data['expire_at'] = datetime.now() + timedelta(hours= int(form.data['expire']))
        print("new user entry expire_at", form.data['expire_at']) 

        if form.is_valid():
            
            
            #https://stackoverflow.com/questions/49275868/how-to-filter-json-array-in-django-jsonfield
            #neighbors = Users.objects.filter(calculateOverlap(form.data['geohashList'], [self.geohashList]))

            for curr_user in Users.objects.all():
                print(">>>>>>>>>>> compare to user:", curr_user)

                checkExpiration(curr_user)

                print(curr_user.geohashList)
                if calculateOverlap(curr_user.geohashList, form.cleaned_data['geohashList']) > 33 :
                    #nutzer nict sich selbst zurückgeben
                    if curr_user.mail != form.data['mail']: 
                        neighbors.append(curr_user)

                # remove duplicates with same mail - only one entry per mail adress allowed
                if curr_user.mail == form.data['mail'] :
                    curr_user.delete()

                

            form.save()
            print('<<<< form saved')



            #print(all_users)
            print(">>>>>>>>>>> final neighbours: ", neighbors)


            return render(request, "answer.html", {"users": neighbors})
        else:
            print(">>>> Form invalid")
            print(form.errors)

    all_users = Users.objects.all()
    return render(request, "index.html", {"user_form": form, "all_users": all_users})


#renders answers.html
def answer(request):
    return render(request, "answer.html")

