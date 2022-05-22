import csv
from ctypes import pointer
import datetime
import json
from lib2to3.pgen2 import driver
from urllib import response
from django import views

import requests
from django.contrib import messages
from django.db import connection
from django.http import HttpResponse
from django.shortcuts import render, redirect

from .models import AuditLog, Sponsor
from .models import Catalog
from .models import GeneralUser, Order
from .models import OrgConnections
from .models import SponsorOrg
from .models import PointHistory


# Create your views here.


def getUserInfo(request):
    userID = request.session.get('username')
    userEmail = ''
    userPassword = ''
    userType = ''
    for p in GeneralUser.objects.raw('SELECT * FROM GENERAL_USER WHERE USER_ID = %s', [userID]):
        userEmail = p.email
        userPassword = p.password
        userType = p.user_type
        userScore = p.points

    return userID, userEmail, userPassword, userType, userScore


def getCatalog(request, id):
    catalog = []
    for p in Catalog.objects.raw('SELECT * FROM CATALOG WHERE CATALOG_ID = %s', [id]):
        catalog.append(p)
    return catalog


def getOrganizations(userID):
    orgs = []
    temp = []
    i = 0
    for p in OrgConnections.objects.raw('SELECT * FROM ORG_CONNECTIONS WHERE USER_ID = %s', [userID]):
        temp.append(p)

    for p in SponsorOrg.objects.raw(
            'SELECT * FROM ORG_CONNECTIONS RIGHT JOIN SPONSOR_ORG ON ORG_CONNECTIONS.ORG_ID = SPONSOR_ORG.ORG_ID WHERE USER_ID = %s',
            [userID]):
        if (temp[i].pending_app == 0):
            orgs.append(p)
        i += 1
    return orgs


def getItems(items):
    list = []
    for i in items:
        for p in Catalog.objects.raw('SELECT * FROM CATALOG WHERE ROW_ID = %s', [i]):
            list.append(p)
    return list


def getScore(orgID, userID):
    scores = []
    for p in OrgConnections.objects.raw('SELECT * FROM ORG_CONNECTIONS WHERE USER_ID = %s AND ORG_ID = %s',
                                        [userID, orgID]):
        scores.append(p)
    return scores


def getSubtotals(itemList):
    subtotals = {}
    for i in itemList:
        # Get the org_id from the catalog_id
        # If catalog ID is not unique, this will break.
        id = 0
        for p in SponsorOrg.objects.raw('SELECT * FROM SPONSOR_ORG WHERE CATALOG_ID = %s', [i.catalog_id]):
            id = p.org_name
        if id not in subtotals:
            subtotals[id] = i.price
        else:
            subtotals[id] += i.price
    return subtotals


def user(request):
    userInfo = []
    userInfo = getUserInfo(request)
 
    return render(request, 'user.html',
                  {'userInfo': userInfo, 'username': userInfo[1].split('@')[0], 'email': userInfo[1],
                   'points': userInfo[4]})


def admin(request):
    userInfo = []
    userInfo = getUserInfo(request)
 
    if (userInfo[3] != 0):
        return error(request)
    return render(request, 'admin.html',
                  {'userInfo': userInfo, 'username': userInfo[1].split('@')[0], 'email': userInfo[1],
                   'points': userInfo[4]})


def sponsor(request):
    userInfo = []
    userInfo = getUserInfo(request)
 
    if (userInfo[3] == 2):
        return error(request)
    return render(request, 'sponsor.html',
                  {'userInfo': userInfo, 'username': userInfo[1].split('@')[0], 'email': userInfo[1],
                   'points': userInfo[4]})


def sponsorfind(request):
    userInfo = []
    userInfo = getUserInfo(request)
 
    # need the list of sponsors to display in drop down box
    sponsorList = []
    sponsorList = SponsorOrg.objects.all()
    # need to display orgs the driver/sponsor is already connected to
    connectedList = []
    connectedList = OrgConnections.objects.all()

    # This is for adding the info to the database
    if request.method == "POST":
        orgId = request.POST['spons_id']

        # add to audit log
        strToAdd = "Added " + userInfo[1] + " to org " + orgId
        date = datetime.datetime.now().date()
        AuditLog.objects.create(date=date, event=strToAdd)

        conExists = 0
        # check if the connection already exists
        # for p in GeneralUser.objects.raw('SELECT * FROM ORG_CONNECTIONS WHERE USER_ID = %s and ORG_ID = %s',[userInfo[0],orgId]):
        if (OrgConnections.objects.filter(org_id=orgId, user_id=userInfo[0]).exists()):
            conExists = 1

        if (userInfo[3] == 2 and conExists == 0):  # this is for drivers
            OrgConnections.objects.create(
                org_id=orgId, user_id=userInfo[0], pending_app=1, points=0)

        # if sponsor exists just update the organization, if not it is created
        elif (userInfo[3] == 1):
            OrgConnections.objects.update_or_create(user_id=userInfo[0], defaults={"org_id": orgId, "pending_app": 0,
                                                                                   "user_id": userInfo[0], "points": 0})

    return render(request, 'selectSponsor.html',
                  {'userInfo': userInfo, 'username': userInfo[1].split('@')[0], 'email': userInfo[1],
                   'points': userInfo[4],
                   'sponsors': sponsorList, 'connections': connectedList})


def viewApplications(request):
    userInfo = []
    userInfo = getUserInfo(request)
 
    if (userInfo[3] == 2):
        return error(request)
    # need the list of sponsors to display in drop down box
    sponsorList = []
    sponsorList = SponsorOrg.objects.all()
    # need to display drivers (and sponsors?) in the org
    connectedList = []
    connectedList = OrgConnections.objects.all()
    # need generalUser to get emails
    userEmails = []
    userEmails = GeneralUser.objects.all()
    # current user org info
    userOrg = []
    try:
        userOrg = OrgConnections.objects.get(user_id=userInfo[0])
    except Exception:
        pass

    # change the pendingApp value to 0. I don't think this gets used?
    #    if request.method == "accept":
    #        #add to audit log
    #        strToAdd = "Aplication for accepted."
    #        date = datetime.datetime.now().date()
    #        AuditLog.objects.create(date=date, event=strToAdd)

    #        conId = request.accept.value
    #        OrgConnections.objects.update_or_create(connection_id=conId, defaults={"pending_app": 0})

    return render(request, 'viewApps.html',
                  {'userInfo': userInfo, 'username': userInfo[1].split('@')[0], 'email': userInfo[1],
                   'points': userInfo[4],
                   'sponsors': sponsorList, 'connections': connectedList, 'allUsers': userEmails, 'currUser': userOrg})


# This isn't needed?, can probably delete?
def userLogout(request):
    if request.method == "LOGOUT":
        del request.session['username']
        return redirect('/login/base')


def acceptApp(request):
    if "pid" in request.GET:
        pid = request.GET['pid']
        OrgConnections.objects.update_or_create(
            connection_id=pid, defaults={"pending_app": 0})

        # add to audit log
        theCon = OrgConnections.objects.get(connection_id=pid)
        strToAdd = "App accepted for user " + \
                   str(theCon.user_id) + " to org " + str(theCon.org_id)
        date = datetime.datetime.now().date()
        AuditLog.objects.create(date=date, event=strToAdd)

    return viewApplications(request)


def denyApp(request):
    if "pid" in request.GET:
        pid = request.GET['pid']
        obToDelete = OrgConnections.objects.get(connection_id=pid)

        # add to audit log
        theCon = OrgConnections.objects.get(connection_id=pid)
        strToAdd = "User " + str(theCon.user_id) + \
                   " removed from org " + str(theCon.org_id)
        date = datetime.datetime.now().date()
        AuditLog.objects.create(date=date, event=strToAdd)

        obToDelete.delete()

        userInfo = getUserInfo(request)
 
        if userInfo[3] == 0:
            return viewSponsor(request)

    return viewApplications(request)


def accountInfo(request):
    userInfo = []
    userInfo = getUserInfo(request)
 

    # if user wants to change the info, get the new info
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        # update the user table with the new credentials
        GeneralUser.objects.update_or_create(email=userInfo[1], defaults={
            "email": username, "password": password})

        # add to audit log
        strToAdd = "User " + str(userInfo[0]) + " updated account info."
        date = datetime.datetime.now().date()
        AuditLog.objects.create(date=date, event=strToAdd)

    return render(request, 'accountInfo.html',
                  {'userInfo': userInfo, 'username': userInfo[1].split('@')[0], 'email': userInfo[1],
                   'points': userInfo[4]})


def updatePoints(request):
    points = request.POST.get('points')
    try:
        reason = request.POST.get('reason')
    except Exception:
        reason = "MISC"
    id = request.POST.get('score')
    orgid = request.POST.get('org')
    score = 0
    userInfo = getUserInfo(request)
 

    if (points):
        # add to audit log
        strToAdd = "Added points to " + str(id) + "."
        date = datetime.datetime.now().date()

        for p in OrgConnections.objects.raw('SELECT * FROM ORG_CONNECTIONS WHERE USER_ID = %s AND ORG_ID = %s',
                                            [id, orgid]):
            score = p.points

        if (request.POST.get('b1') == "subtract"):
            points = int(points)
            points *= -1

            # change string if points negative
            strToAdd = "Removed points from " + str(id) + "."

        connection.cursor().execute('INSERT INTO POINT_HISTORY (driver_id, reason, POINT_HISTORY.change, org_id, newBalance, date) VALUES (%s, %s, %s, %s, %s, %s);',
                                    [id, reason, points, orgid, score+int(points), date])
        connection.cursor().execute('UPDATE ORG_CONNECTIONS SET POINTS = %s WHERE USER_ID = %s AND ORG_ID = %s',
                                    [score + int(points), id, orgid])

        # place in log
        AuditLog.objects.create(date=date, event=strToAdd)

    # if admin use viewapps2
    if userInfo[3] == 0:
        return viewApplications2(request, id)

    return viewApplications(request)


# Similar to viewApplications, but needed for admin tools, since there is not a user connection for them.
# Make sure to pass the id in the return statement while calling this, like viewApplications2(request, id)
def viewApplications2(request, id):
    sponsorList = []
    sponsorList = SponsorOrg.objects.all()
    # need to display drivers (and sponsors?) in the org
    connectedList = []
    connectedList = OrgConnections.objects.all()
    # need generalUser to get emails
    userEmails = []
    userEmails = GeneralUser.objects.all()

    userOrg = connectedList.filter(user_id=id)
    userOrg = userOrg[0]
    userInfo = getUserInfo(request)
 
    if (userInfo[3] == 2):
        return error(request)

    return render(request, 'viewApps.html',
                  {'userInfo': userInfo, 'username': userInfo[1].split('@')[0], 'email': userInfo[1],
                   'sponsors': sponsorList, 'connections': connectedList, 'allUsers': userEmails, 'currUser': userOrg})


def viewSponsor(request):
    userInfo = []
    userInfo = getUserInfo(request)
 

    sponsorList = []
    sponsorList = SponsorOrg.objects.all()
    # need to display drivers (and sponsors?) in the org
    connectedList = []
    connectedList = OrgConnections.objects.all()
    # need generalUser to get emails
    userEmails = []
    userEmails = GeneralUser.objects.all()

    if request.method == "POST":
        orgId = request.POST['spons_id']
        userOrgs = []
        userOrgs = OrgConnections.objects.filter(org_id=orgId)
        userOrg = userOrgs[0]

        return render(request, 'viewApps.html',
                      {'userInfo': userInfo, 'username': userInfo[1].split('@')[0], 'email': userInfo[1],
                       'points': userInfo[4],
                       'sponsors': sponsorList, 'connections': connectedList, 'allUsers': userEmails,
                       'currUser': userOrg, 'orgid': orgId})

    return render(request, 'viewSponsor.html',
                  {'userInfo': userInfo, 'username': userInfo[1].split('@')[0], 'email': userInfo[1],
                   'points': userInfo[4],
                   'sponsors': sponsorList, 'connections': connectedList})


def adminDelete(request):
    sponsorList = []
    sponsorList = SponsorOrg.objects.all()
    # need to display drivers (and sponsors?) in the org
    connectedList = []
    connectedList = OrgConnections.objects.all()
    # need generalUser to get emails
    userEmails = []
    userEmails = GeneralUser.objects.all()

    userOrg = connectedList[0]
    userInfo = getUserInfo(request)
 
    orgId = userOrg.org_id

    if "pid" in request.GET:
        pid = request.GET['pid']
        obToDelete = OrgConnections.objects.get(connection_id=pid)
        orgId = obToDelete.org_id
        # add to audit log
        strToAdd = "User " + str(obToDelete.user_id) + \
                   " removed from org " + str(orgId)
        date = datetime.datetime.now().date()
        AuditLog.objects.create(date=date, event=strToAdd)

        obToDelete.delete()

    for cons in connectedList:
        if cons.org_id == orgId:
            userOrg = cons
            break

    return render(request, 'viewApps.html',
                  {'userInfo': userInfo, 'username': userInfo[1].split('@')[0], 'email': userInfo[1],
                   'sponsors': sponsorList, 'connections': connectedList, 'allUsers': userEmails, 'currUser': userOrg})


def updateEmail(request):
    newEmail = request.POST.get('newem')
    id = request.POST.get('score')
    GeneralUser.objects.update_or_create(
        user_id=id, defaults={"email": newEmail})

    # add to audit log
    strToAdd = "Admin update email for user " + id
    date = datetime.datetime.now().date()
    AuditLog.objects.create(date=date, event=strToAdd)

    return viewApplications2(request, id)


def updatePassword(request):
    newPass = request.POST.get('newpa')
    id = request.POST.get('score')
    GeneralUser.objects.update_or_create(
        user_id=id, defaults={"password": newPass})

    # add to audit log
    strToAdd = "Admin update password for user " + id
    date = datetime.datetime.now().date()
    AuditLog.objects.create(date=date, event=strToAdd)

    return viewApplications2(request, id)


def viewDrivers(request):
    userInfo = getUserInfo(request)
 
    if (userInfo[3] != 0):
        return error(request)
    # need generalUser to get emails
    userEmails = []
    userEmails = GeneralUser.objects.all()
    userList = []

    connectedList = []
    connectedList = OrgConnections.objects.all()

    sponsorsList = SponsorOrg.objects.all()

    # neededInfo = []

    if request.method == "POST":
        try:
            orgId = request.POST['spons_id']
            userId = request.POST.get('the_user')
            theUser = userEmails[0]
            conExists = 0

            # add to audit log
            strToAdd = "User " + str(userId) + " added to org " + str(orgId)
            date = datetime.datetime.now().date()
            AuditLog.objects.create(date=date, event=strToAdd)

            for users in userEmails:
                if users.user_type == 1 and users.user_id == userId:
                    theUser = users

            if theUser.user_type == 1:  # if sponsor exists just update the organization, if not it is created
                OrgConnections.objects.update_or_create(user_id=userId,
                                                        defaults={"org_id": orgId, "pending_app": 0, "user_id": userId})
            else:
                if (OrgConnections.objects.filter(org_id=orgId, user_id=userId).exists()):
                    conExists = 1

                if conExists == 0:
                    OrgConnections.objects.create(
                        org_id=orgId, pending_app=0, user_id=userId)
        except Exception:
            pass

    # build list of driver objects, displaying just drivers
    for ac in userEmails:
        if ac.user_type == 2:
            userList.append(ac)

    return render(request, 'viewDrivers.html',
                  {'userInfo': userInfo, 'connections': connectedList, 'allUsers': userEmails,
                   'sponsors': sponsorsList, 'username': userInfo[1].split('@')[0], 'email': userInfo[1]})


def removeAccount(request):
    pid = request.GET['pid']
    obToDelete = GeneralUser.objects.get(user_id=pid)
    obToDelete.delete()

    # add to audit log
    strToAdd = "User " + str(pid) + " deleted"
    date = datetime.datetime.now().date()
    AuditLog.objects.create(date=date, event=strToAdd)

    return viewDrivers(request)


def updateEmail2(request):
    newEmail = request.POST.get('newem')
    id = request.POST.get('score')
    GeneralUser.objects.update_or_create(
        user_id=id, defaults={"email": newEmail})

    # add to audit log
    strToAdd = "Admin updated user " + str(id) + " email."
    date = datetime.datetime.now().date()
    AuditLog.objects.create(date=date, event=strToAdd)

    return viewDrivers(request)


def updatePassword2(request):
    newPass = request.POST.get('newpa')
    id = request.POST.get('score')
    GeneralUser.objects.update_or_create(
        user_id=id, defaults={"password": newPass})

    # add to audit log
    strToAdd = "Admin updated user " + str(id) + " password."
    date = datetime.datetime.now().date()
    AuditLog.objects.create(date=date, event=strToAdd)

    return viewDrivers(request)


ratioList = [1] * 10


def catalog(request, items=[], itemList=[], org=None):
    global ratioList
    renderEnd = False
    userInfo = []
    userInfo = getUserInfo(request)
 
    itemList = getItems(items)

    cartOpen = 0
    # need the list of sponsors to display in drop down box
    sponsorList = []
    sponsorList = SponsorOrg.objects.all()
    # need to display orgs the driver/sponsor is already connected to
    connectedList = []
    connectedList = OrgConnections.objects.all()

    organizations = getOrganizations(userInfo[0])

    catalog = 1
    catalogList = []

    score = 0

    try:
        # Grab the current sponsor if sponsor
        if (userInfo[3] == 1):
            org = organizations[0]
            org = org.org_id
            buildCatalog(org)
            # Add all items from that catalog to a list, which will create the objects later :)
            catalogList = getCatalog(request, org)
    except Exception:
        pass

    # When the user selects the sponsor they want, update the catalog to match that
    # if request.method == "POST":
    #     catalogID = request.POST['spons_id']

    if request.method == "POST":
        if (request.POST.get("b1") == "add"):
            org = (request.POST.get('org'))
            itemList = getItems(items)
            if request.POST.get('ITEM') and request.POST.get('DESC') and request.POST.get('URL') and request.POST.get(
                    'PRICE') and request.POST.get('CAT'):
                connection.cursor().execute(
                    "INSERT INTO CATALOG (CATALOG_ID,ITEMS,DESCRIPTION,IMAGE,PRICE) VALUES (%s, %s, %s, %s, %s)", [
                        request.POST.get('CAT'), request.POST.get(
                            'ITEM'), request.POST.get('DESC'),
                        request.POST.get('URL'), request.POST.get('PRICE')])
                # return redirect('/dashboard/catalog')
        elif (request.POST.get("b1") == "buy"):
            items.append(request.POST.get('ROW'))
            itemList = getItems(items)
            # Find a way to maintain current organization
            org = (request.POST.get('org'))
        elif (request.POST.get("b1") == "up"):
            org = (request.POST.get('org'))
            itemList = getItems(items)
            if request.POST.get('ITEM') and request.POST.get('DESC') and request.POST.get('URL') and request.POST.get(
                    'PRICE') and request.POST.get('CAT'):
                connection.cursor().execute(
                    "UPDATE CATALOG SET CATALOG_ID = %s, ITEMS = %s, IMAGE = %s, DESCRIPTION = %s, PRICE = %s WHERE ROW_ID = %s",
                    [
                        request.POST.get('CAT'), request.POST.get(
                            'ITEM'), request.POST.get('DESC'),
                        request.POST.get('URL'), request.POST.get('PRICE'), request.POST.get("ROW")])
                # return redirect('/dashboard/catalog')
        elif (request.POST.get("b1") == "del"):
            org = (request.POST.get('org'))
            itemList = getItems(items)
            connection.cursor().execute(
                "DELETE FROM CATALOG WHERE ROW_ID = %s", [request.POST.get("ROW")])
            # return redirect('/dashboard/catalog')
        elif (request.POST.get('b1') == "cartTrash"):
            cartOpen = 1
            org = (request.POST.get('org'))
            rowID = request.POST.get('row')
            index = items.index(rowID)
            items.pop(index)
            itemList = getItems(items)
        elif (request.POST.get('b1') == "clear"):
            cartOpen = 1
            org = (request.POST.get('org'))
            items.clear()
            itemList.clear()
        elif (request.POST.get('b1') == "checkOut"):
            # Remove everything from the list

            if (request.POST.get('Address') and request.POST.get('ZipCode') and request.POST.get('State')):
                items.clear()
                RawSubtotals = getSubtotals(itemList)
                itemList.clear()

                # Remove points (Also assumes unique organization names)
                for key in RawSubtotals:
                    org_id = 1
                    for p in SponsorOrg.objects.raw('SELECT * FROM SPONSOR_ORG WHERE ORG_NAME = %s', [key]):
                        org_id = p.org_id
                    # Update points
                    pastScore = 0
                    for p in OrgConnections.objects.raw(
                            'SELECT * FROM ORG_CONNECTIONS WHERE USER_ID = %s AND ORG_ID = %s', [userInfo[0], org_id]):
                        pastScore = p.points
                    newScore = pastScore - RawSubtotals.get(key)
                    if newScore >= 0:
                        connection.cursor().execute('INSERT INTO POINT_HISTORY (driver_id, reason, POINT_HISTORY.change, org_id, newBalance, date) VALUES (%s, %s, %s, %s, %s, now());',
                                                    [userInfo[0], "Item Purchase", -1*RawSubtotals.get(key), org_id, newScore])
                        connection.cursor().execute(
                            'UPDATE ORG_CONNECTIONS SET POINTS = %s WHERE USER_ID = %s AND ORG_ID = %s',
                            [newScore, userInfo[0], org_id])
                        # test new daniel, puts order in, should move to where there are enough points

                        Address = request.POST.get('Address')
                        ZipCode = request.POST.get('ZipCode')
                        State = request.POST.get('State')
                        date = datetime.datetime.now().date()

                        order = Order.objects.create(address=Address, zipcode=ZipCode, state=State,
                                                     purchase_time=date, driver_id=userInfo[0],
                                                     total_cost=RawSubtotals.get(key), status='Order Received', org_id=org_id)
                        # add to order log instead?
                        # strToAdd = "Driver " + str(userInfo[0]) + " made an order worth " + str(RawSubtotals.get(key)) + " points."
                        # date = datetime.datetime.now().date()
                        # AuditLog.objects.create(date=date, event=strToAdd)

                        renderEnd = True

                    # if(renderEnd):
                    #     return render(request, 'orderConfirm.html',
                    #         {'ord': order, 'userInfo': userInfo, 'username': userInfo[1].split('@')[0],
                    #         'nScore': newScore, 'sTotal': RawSubtotals.get(key)})

                    else:
                        messages.error(
                            request, 'Error: You do not have enough points to complete purchase')
                        # connection.cursor().execute('INSERT INTO ORDER (ADDRESS, ZIPCODE, STATE, PURCHASE_TIME, DRIVER_ID, TOTAL_COST) VALUES (%s %s %s %s %s %s)', [Address, ZipCode, State, date, userInfo[0], RawSubtotals.get(key)])
            else:
                cartOpen = 1
                org = (request.POST.get('org'))

        else:
            try:
                org = request.POST['spons_id']
                itemList = getItems(items)

            except Exception:
                pass

        try:
            buildCatalog(org)
        except Exception:
            pass

    for p in OrgConnections.objects.raw('SELECT * FROM ORG_CONNECTIONS WHERE USER_ID = %s AND ORG_ID = %s',
                                        [userInfo[0], org]):
        score = p.points

    RawSubtotals = getSubtotals(itemList)
    subtotals = []

    for key in RawSubtotals:
        subtotals.append(str(key) + ": " + str(RawSubtotals.get(key)))

    subtotals = sorted(subtotals)

    # Get all necessary scores
    scores = []
    for key in RawSubtotals:
        org_id = 1
        for p in SponsorOrg.objects.raw('SELECT * FROM SPONSOR_ORG WHERE ORG_NAME = %s', [key]):
            org_id = p.org_id
        # Update points
        pastScore = 0
        for p in OrgConnections.objects.raw('SELECT * FROM ORG_CONNECTIONS WHERE USER_ID = %s AND ORG_ID = %s',
                                            [userInfo[0], org_id]):
            scores.append(str(key) + ": " + str(p.points))

    try:
        catalog = SponsorOrg.objects.get(org_id=org.org_id)
        catalogList = getCatalog(request, org.org_id)
    except Exception:
        try:
            catalog = SponsorOrg.objects.get(org_id=org)
            catalogList = getCatalog(request, org)
        except Exception:
            pass

    return render(request, 'catalog.html',
                  {'userInfo': userInfo, 'username': userInfo[1].split('@')[0], 'email': userInfo[1],
                   'points': userInfo[4],
                   'sponsors': sponsorList, 'connections': connectedList, 'organizations': organizations,
                   'catalogName': catalog, 'catalog': catalogList, 'org': org, 'items': itemList,
                   'itemCount': len(items), 'cartOpen': cartOpen, 'points': score, 'subtotal': subtotals,
                   'scores': scores})


def nums(first_number, last_number, step=1):
    print(first_number)
    return range(first_number, last_number + 1, step)

def pointsRatio(request):
    try:
        points = request.POST['pr']
        org_id = (request.GET['oid'])
        SponsorOrg.objects.update_or_create(org_id = org_id, defaults={'rate':points})

        #delete items in the catalog
        obToDelete = Catalog.objects.filter(catalog_id=org_id)
        obToDelete.delete()

    except Exception:
        pass

    return catalog(request)


def buildCatalog(orgId):
    base_url = 'https://openapi.etsy.com/v2'
    key = "h7ctibmsc63qthr5ozej14i4"

    #get the point ration from SPONSOR_ORG FXIME
    pointRatio = SponsorOrg.objects.get(org_id = orgId).rate

    # access api and get a list of listings
    url = base_url + '/listings/active/?api_key={}'.format(key)
    response = requests.get(url)
    response = json.loads(response.text)
    with open('dashboard/nsfwIndex.txt') as f:  # opens the file in read mode
        li = f.readlines()  # puts the file into an array
        nonoWords = [x.strip() for x in li]

    # loop through JSON data and add to table one item at a time.
    startP = 10 * (int(orgId) - 1)
    endP = 10 * int(orgId)
    flag = False

    for x in range(startP, endP):
        # print(x)
        for w in nonoWords:
            if w in response:
                print("sussy")
                flag = True
            else:
                continue
        if flag == True:
            continue
        else:
            itName = response['results'][x]['title']
            desc = response['results'][x]['description']
            itPrice = response['results'][x]['price']
            # FIXME FIXME FIXME
            itPrice = float(itPrice) * pointRatio
            itemId = response['results'][x]['listing_id']

            imgIds = base_url + \
                '/listings/{}/images/?api_key={}'.format(itemId, key)

            imgIds = requests.get(imgIds)
            imgIds = json.loads(imgIds.text)

            firstImg = imgIds['results'][0]['listing_image_id']

            firstImg = base_url + \
                '/listings/{}/images/{}/?api_key={}'.format(
                    itemId, firstImg, key)
            firstImg = requests.get(firstImg)
            firstImg = json.loads(firstImg.text)

            imageUrl = firstImg['results'][0]['url_fullxfull']
            try:
                connection.cursor().execute(
                    "DELETE FROM CATALOG WHERE CATALOG_ID = %s AND ITEMS = %s", [orgId, itName[:50]])
            except Exception:
                pass

            try:
                connection.cursor().execute(
                    "INSERT INTO CATALOG (CATALOG_ID, ITEMS, DESCRIPTION, IMAGE, PRICE) VALUES (%s, %s, %s, %s, %s)",
                    [orgId, itName[:50], desc[:50], imageUrl, str(itPrice)])
            except Exception:
                pass


def history(request):
    userInfo = getUserInfo(request)
 
    # Driver orders page
    hist = PointHistory.objects.filter(driver_id=userInfo[0])

    return render(request, 'pointHistory.html',
                  {'hist': hist, 'userInfo': userInfo, 'username': userInfo[1].split('@')[0]})


def orders(request):
    userInfo = getUserInfo(request)
 
    # Driver orders page
    if userInfo[3] == 2:
        ords = Order.objects.filter(driver_id=userInfo[0])

        if request.method == "POST":
            # create csv of the table and download it
            response = HttpResponse(
                content_type='text/csv',
                headers={
                    'Content-Disposition': 'attachment; filename="orderLog.csv"'},
            )
            writer = csv.writer(response)
            writer.writerow(['Order ID', 'Address', 'ZipCode',
                            'State', 'Time', 'Cost', 'Status'])

            it = 50
            curr = 0
            for logs in ords:
                writer.writerow([logs.order_id, logs.address, logs.zipcode, logs.state, logs.purchase_time,
                                logs.total_cost, logs.status])
                curr += 1
                if curr >= it:
                    break

            return response

        return render(request, 'orders.html',
                      {'ords': ords, 'userInfo': userInfo, 'username': userInfo[1].split('@')[0]})

    # Sponsor orders page
    elif userInfo[3] == 1:

        # Get logged in sponsor OrgConnection and org_id
        org = OrgConnections.objects.get(user_id=userInfo[0])
        org_id = getattr(org, 'org_id')
        # Get all users in the org
        orgs = OrgConnections.objects.filter(org_id=org_id)
        # Creates flat list to filter the driver orders under a sponsor
        idlist = OrgConnections.objects.filter(
            org_id=org_id).values_list('user_id', flat=True)
        ords = Order.objects.filter(driver_id__in=idlist)
        users = GeneralUser.objects.filter(user_id__in=idlist, user_type=2)

        if request.method == "POST":
            # create csv of the table and download it
            response = HttpResponse(
                content_type='text/csv',
                headers={
                    'Content-Disposition': 'attachment; filename="orderLog.csv"'},
            )
            writer = csv.writer(response)
            writer.writerow(['Order ID', 'Address', 'ZipCode',
                            'State', 'Time', 'Cost', 'Driver ID', 'Status'])

            it = 50
            curr = 0
            for logs in ords:
                writer.writerow([logs.order_id, logs.address, logs.zipcode, logs.state, logs.purchase_time,
                                logs.total_cost, logs.driver_id, logs.status])
                curr += 1
                if curr >= it:
                    break

            return response

        return render(request, 'orders.html',
                      {'ords': ords, 'userInfo': userInfo, 'usrs': users,
                       'username': userInfo[1].split('@')[0]})

    else:
        ords = Order.objects.all()
        ords = reversed(ords)

        if request.method == "POST":
            # create csv of the table and download it
            response = HttpResponse(
                content_type='text/csv',
                headers={
                    'Content-Disposition': 'attachment; filename="orderLog.csv"'},
            )
            writer = csv.writer(response)
            writer.writerow(['Order ID', 'Address', 'ZipCode',
                            'State', 'Time', 'Cost', 'Driver ID', 'Status'])

            it = 50
            curr = 0
            for logs in ords:
                writer.writerow([logs.order_id, logs.address, logs.zipcode, logs.state, logs.purchase_time,
                                logs.total_cost, logs.driver_id, logs.status])
                curr += 1
                if curr >= it:
                    break

            return response

        return render(request, 'orders.html',
                      {'ords': ords, 'userInfo': userInfo, 'username': userInfo[1].split('@')[0]})


def removeOrgs(request):
    userInfo = []
    userInfo = getUserInfo(request)
 

    sponsorList = []
    sponsorList = SponsorOrg.objects.all()

    connectedList = []
    connectedList = OrgConnections.objects.all()

    if request.method == "POST":
        orgId = request.POST['spons_id']

        # remove the organization
        obToDelete = SponsorOrg.objects.get(org_id=orgId)
        obToDelete.delete()

        # add to audit log
        strToAdd = "Organization " + str(orgId) + " deleted."
        date = datetime.datetime.now().date()
        AuditLog.objects.create(date=date, event=strToAdd)

        print(orgId)

        # remove connections with that sponsor
        try:
            obToDelete = OrgConnections.objects.get(org_id=orgId)
            obToDelete.delete()
        except Exception:
            pass

    return render(request, 'removeOrgs.html',
                  {'userInfo': userInfo, 'username': userInfo[1].split('@')[0], 'email': userInfo[1],
                   'points': userInfo[4],
                   'sponsors': sponsorList, 'connections': connectedList})


def addOrg(request):
    userInfo = []
    userInfo = getUserInfo(request)
 

    sponsorList = []
    sponsorList = SponsorOrg.objects.all()

    connectedList = []
    connectedList = OrgConnections.objects.all()

    if request.method == 'POST':
        orgName = request.POST.get('orgname')
        idNum = len(SponsorOrg.objects.all()) + 1
        # make sure unique id
        taken = 1
        for org in sponsorList:
            if org.catalog_id == idNum:
                idNum += 1
        # add to audit log
        strToAdd = "Organization " + str(orgName) + " created."
        date = datetime.datetime.now().date()
        AuditLog.objects.create(date=date, event=strToAdd)

        SponsorOrg.objects.update_or_create(org_name=orgName, defaults={
            'org_name': orgName, 'catalog_id': idNum, 'rate': 100})

    return render(request, "addOrg.html",
                  {'userInfo': userInfo, 'username': userInfo[1].split('@')[0], 'email': userInfo[1]})


def auditLog(request):
    userInfo = []
    userInfo = getUserInfo(request)
 
    if (userInfo[3] != 0):
        return error(request)
    aLog = []
    aLog = AuditLog.objects.all()
    aLog = reversed(aLog)
    print(aLog)

    if request.method == "POST":
        # create csv of the table and download it
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="auditLog.csv"'},
        )
        writer = csv.writer(response)
        writer.writerow(['Date', 'Event'])

        it = 50
        curr = 0
        for logs in aLog:
            writer.writerow([logs.date, logs.event])
            curr += 1
            if curr >= it:
                break

        return response

    return render(request, "auditLog.html",
                  {'logs': aLog, 'userInfo': userInfo, 'username': userInfo[1].split('@')[0], 'email': userInfo[1]})


def error(request):
    return render(request, "error.html")


def sponsorSales(request):
    if "pid" in request.GET:
        org_id = request.GET['pid']

        # build list of driver orders for sponsor
        orgs = OrgConnections.objects.filter(org_id=org_id)
        # Creates flat list to filter the driver orders under a sponsor
        idlist = OrgConnections.objects.filter(
            org_id=org_id).values_list('user_id', flat=True)
        ords = Order.objects.filter(driver_id__in=idlist)
        users = GeneralUser.objects.filter(user_id__in=idlist, user_type=2)

        response = HttpResponse(
            content_type='text/csv',
            headers={
                'Content-Disposition': 'attachment; filename="SponsorSalesReport.csv"'},
        )
        writer = csv.writer(response)
        writer.writerow(['Order ID', 'Address', 'ZipCode',
                        'State', 'Time', 'Cost', 'Driver ID', 'Status'])

        it = 50
        curr = 0
        for logs in ords:
            writer.writerow([logs.order_id, logs.address, logs.zipcode, logs.state, logs.purchase_time,
                            logs.total_cost, logs.driver_id, logs.status])
            curr += 1
            if curr >= it:
                break

    return response


def sponsorInvoice(request):
    if "pid" in request.GET:
        org_id = request.GET['pid']

        # build list of driver orders for sponsor
        orgs = OrgConnections.objects.filter(org_id=org_id)
        # Creates flat list to filter the driver orders under a sponsor
        idlist = OrgConnections.objects.filter(
            org_id=org_id).values_list('user_id', flat=True)
        ords = Order.objects.filter(driver_id__in=idlist)
        users = GeneralUser.objects.filter(user_id__in=idlist, user_type=2)
        totalAmount = 0

        response = HttpResponse(
            content_type='text/csv',
            headers={
                'Content-Disposition': 'attachment; filename="SponsorInvoice.csv"'},
        )
        writer = csv.writer(response)
        writer.writerow(['Order ID', 'Time', 'Cost', 'Driver ID'])

        it = 50
        curr = 0
        for logs in ords:
            writer.writerow([logs.order_id, logs.purchase_time,
                            logs.total_cost, logs.driver_id])
            curr += 1
            totalAmount += logs.total_cost
            if curr >= it:
                break

        writer.writerow(['Total:', totalAmount])

    return response


def driverReportAll(request):
    if "pid" in request.GET:
        driver_id = request.GET['pid']
        print(driver_id)

        ords = Order.objects.filter(driver_id=driver_id)

        response = HttpResponse(
            content_type='text/csv',
            headers={
                'Content-Disposition': 'attachment; filename="SponsorInvoice.csv"'},
        )
        writer = csv.writer(response)
        writer.writerow(['Order ID', 'Address', 'ZipCode',
                        'State', 'Time', 'Cost', 'Driver ID', 'Status'])

        it = 50
        curr = 0
        for logs in ords:
            writer.writerow([logs.order_id, logs.address, logs.zipcode, logs.state, logs.purchase_time,
                            logs.total_cost, logs.driver_id, logs.status])
            curr += 1
            if curr >= it:
                break

    return response


def driverReportSponsor(request):
    if "pid" in request.GET:
        driver_id = request.GET['pid']
        print("driver" + driver_id)
        org_id = request.GET['oid']
        print("org" + org_id)

        # build list of driver orders for sponsor
        orgs = OrgConnections.objects.filter(org_id=org_id)
        # Creates flat list to filter the driver orders under a sponsor
        # FIXME need to have which org order is for
        ords = Order.objects.filter(driver_id=driver_id, org_id=org_id)
        # ords = Order.objects.filter(driver_id = driver_id)

        response = HttpResponse(
            content_type='text/csv',
            headers={
                'Content-Disposition': 'attachment; filename="SponsorSalesReport.csv"'},
        )
        writer = csv.writer(response)
        writer.writerow(['Order ID', 'Address', 'ZipCode',
                        'State', 'Time', 'Cost', 'Driver ID', 'Status'])

        it = 50
        curr = 0
        for logs in ords:
            writer.writerow([logs.order_id, logs.address, logs.zipcode, logs.state, logs.purchase_time,
                            logs.total_cost, logs.driver_id, logs.status])
            curr += 1
            if curr >= it:
                break

    return response
