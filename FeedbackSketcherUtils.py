#*******************************************************************************
#* FeedbackSketcherUtils                                                       *
#*                                                                             *
#* Copyright (c) 2017                                                          *
#* <monograff76@gmail.com>                                                     *
#*                                                                             *
#* A series of utilis to augment the feedback sketcher class                   *
#*                                                                             *
#* GNU Lesser General Public License (LGPL)                                    *
#*******************************************************************************

import feedbacksketch
import FreeCAD

def _addGroup (fbs,grpname):

    #construct the property group for the supplied property

    if hasattr (fbs,'active'+grpname):
        return

    fbs.addProperty ("App::PropertyBool",'active'+grpname, grpname, )
    fbs.addProperty ("App::PropertyLink",'base'+grpname, grpname, )
    fbs.addProperty ("App::PropertyStringList",'get'+grpname, grpname, )
    fbs.addProperty ("App::PropertyStringList",'set'+grpname, grpname, )
    fbs.addProperty ("App::PropertyStringList",'seton'+grpname, grpname, )
    fbs.addProperty ("App::PropertyStringList",'setoff'+grpname, grpname, )


def _buildFbs (name):

    #construct feedback sketch

    fbs = FreeCAD.ActiveDocument.addObject ("Sketcher::SketchObjectPython",name)

    feedbacksketch.FeedbackSketch (fbs)

    return fbs


def _addProperties (fbs, clients):

    #add base and client properties to feedback sketch

    fbs.addProperty ("App::PropertyBool",'active', 'Base', )
    fbs.addProperty ("App::PropertyStringList",'bases', 'Base', )

    fbs.bases = clients

    for b in fbs.bases:
        _addGroup (fbs,b)
        setattr(fbs, "active"+b, True)

    return fbs

def _createClients (clientList):

    clients=[]

    for client in clientList:
        clients.append (FreeCAD.ActiveDocument.addObject (
            "Sketcher::SketchObjectPython", client))

    return clients

def _assignClients (fbs, clients):

    for client in clients:
        setattr (fbs, "base"+client.Label, client)

def buildFeedbackSketch (sketchName, clientList):

    #construct a feedback sketch using the supplied sketch name
    #with clients in the supplied client list

    fbs = _buildFbs (sketchName)
    fbs = _addProperties (fbs, clientList)
    clients = _createClients (clientList)
    _assignClients (fbs, clients)    

    result = [fbs]
    result.extend (clients)

    return result
