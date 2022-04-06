#from antigravity import geohash
from django.shortcuts import redirect, render, HttpResponse
from .forms import UserForm
from .models import Users
from datetime import datetime, timedelta
from dateutil import parser


# module with tools for working with geohashes (https://github.com/hkwi/python-geohash)
from .geohash import *


# config file
from .config import *



def latlongToGeohash(latitude, longitude, precicion):
# encodes longtude latitude coordinates to a Geohash with given length
# input1: latitude      string         latitude value
# input2: longitude     string         longitude value
# input3: precicion     int         geohash length
# return:               string      the corresponding geohash

    return encode(float(latitude),float(longitude), precicion)



def flattenList(list_of_lists):
# flattens a given list of lists
# input: list_of_lists      [[string]]      list of lists with a depth of maximum 4
# return:                   [string]

# example:
# flattenList(["hello", ["abcd"],["edf"]])
# --> ["hello", "abcd","edf"]


    if len(list_of_lists) == 0:
        return list_of_lists
    if isinstance(list_of_lists[0], list):
        return flattenList(list_of_lists[0]) + flattenList(list_of_lists[1:])
    return list_of_lists[:1] + flattenList(list_of_lists[1:])



def filterDiplicates(List):
#   filters removes duplicates from a list
#   input:list   [string]       the input list
#   return:      [string]       filtered list

# Example:
#filterDiplicates(["hello", "hello", "hash", "hello"])
# --> ["hello", "hello", "hash"]

    return list(set(List))



def calculate_Area(geohash, neighberhood_layers):
    #   input1: geohash                string                       inner Geohash
    #   input2: neighberhood_layers    int in the range [0, 3]      number of layers around the geohash for the number of Geohashes in the neighbourhood area(NA) (input-> number of geohashes in NA; 0->1; 1->9; 2->25; 4->36)
    #   return:                        [string]                     List aller Geohashes um input1 Geohash herum ohne Duplicate
    
    # Example:
    # calculate_Area("7gxyru", 2)
    # --> ['7gxyrq', 'k58n2n', 'k58n27', '7gxyrs', 'k58n2k', '7gxyru', 'k58n2m', '7gxyrv', '7gxyry', '7gxyrf',
    #  'k58n24', '7gxyrt', 'k58n25', '7gxyr6', '7gxyrg', '7gxyrm', '7gxyrk', '7gxyr7', 'k58n2q', 'k58n26',
    #  'k58n2j', '7gxyrw', 'k58n2h', '7gxyre', '7gxyrd']
    
    geohashList = []
    geohashList.append(geohash)     #initialen Geohash hinzufügen
    index = 0
    # if index == 1:
    #     geohashList.append(neighbors(geohash))
    #     geohashList = flattenList(geohashList)
    #     #geohashList.append(geohash)
    #     index = index+1
    #     #print("tets", geohashList)
    #   wenn keine Layers dann gib initialen geohash wieder zurück
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

 

def calculateOverlap(geohashList1, geohashList2):
#   input1&2:      [string]     List of Geohashes: same List length & Geohash length
#   return:        int          percentage of similar entries 

#   Example:
#   calculateOverlap(['7gxyrs', '7gxyrv', '7gxyru', 'k58n24', 'k58n2j', 'helo'], ['k58n2j', 'k58n2m', '7gxyrv', '7gxyrk', 'k58n25', 'hello'])
#   --> 33
 
    
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




def checkExpiration(user):
#   checks if a database entry is expired and delets it if it is expired
#   imput user:     user object

    print("check expiration:", user)
    if user.expire_at.timestamp() < datetime.now().timestamp():
        print("expired user deleted: ", user)
        user.delete()



def index(request):
#   renders index.html & receive form input & redirection to answers.html/error.html

    request.POST._mutable = True
    form = UserForm()
    all_users = Users.objects.all()
    neighbors = []

    #print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< new request >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

    if request.method == "POST":
        form = UserForm(request.POST)


        #checks if longitude and latitude coordinates are given, if yes encode it to geohash and remove values
        # if form.data['longitude']!=0 and form.data['latitude']!=0:
        #     form.data['geohash'] = latlongToGeohash(form.data['longitude'], form.data['latitude'], geohash_length)
        #     form.data['longitude'] = 0
        #     form.data['latitude'] = 0

        

        #check if entered geohash is the correct length. If not shorten it
        if geohash_length <= len(form.data['geohash']):
            form.data['geohash'] = form.data['geohash'][0:(geohash_length)]

        

        # calculate the neigbourhood area Geohash list and save it to the database
        form.data['geohashList'] = calculate_Area(form.data['geohash'], neighberhood_layers) 

        # calculate the expiration time point
        form.data['expire_at'] = datetime.now() + timedelta(hours= int(form.data['expire']))
        form.data['expire'] = 0
        #print("new user entry expire_at", form.data['expire_at']) 

   

        if form.is_valid():

            #iterate over all database entries to chack expiration and determine neighbors
            for curr_user in Users.objects.all():
                print(">>>>>>>>>>> compare to user:", curr_user)

                checkExpiration(curr_user)

                print(curr_user.geohashList)
                if calculateOverlap(curr_user.geohashList, form.cleaned_data['geohashList']) > threshold :
                    
                    #preventing users are their own neigbour
                    if curr_user.mail != form.data['mail']: 
                        neighbors.append(curr_user)

                # remove duplicates with same mail - only one entry per mail adress allowed
                if curr_user.mail == form.data['mail'] :
                    curr_user.delete()

                

            form.save()
            #print('<<<< form saved')



            #print(all_users)
            #print(">>>>>>>>>>> final neighbours: ", neighbors)


            return render(request, "answer.html", {"users": neighbors})
        else:
            #print(">>>> Form invalid")
            print(form.errors)
            error_msg = ""
            return render(request, "error.html", {"error_msg": form.errors})

    #all_users = Users.objects.all()
    #return render(request, "index.html", {"user_form": form, "all_users": all_users})
    return render(request, "index.html", {"user_form": form})



#renders answers.html
def answer(request):
    return render(request, "answer.html")

