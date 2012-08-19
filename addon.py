'''
Created on Apr 5, 2012

@author: Scott Brown
'''

import urllib
import os
import sys
import xbmc
import xbmcaddon
import xbmcplugin
import xbmcgui
import traceback

ADDON_ID = 'plugin.video.mute-profanity'
Addon = xbmcaddon.Addon(id=ADDON_ID)
ADDON_TITLE = Addon.getAddonInfo('name')

__addon_path__ = Addon.getAddonInfo('path')
BASE_RESOURCE_PATH = xbmc.translatePath( os.path.join( __addon_path__, 'resources' ) )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ))

from UIManager import UIManager
from EDLCreator import EDLCreator
from config import plugin
import JSONUtils as data
import SubDownloader as dl
import MKVSubExtract as mkv

# magic; id of this plugin's instance - cast to integer
_thisPlugin = int(sys.argv[1])

#create helper classes
ui = UIManager(_thisPlugin)

def getInitialListing():
    """
    Creates a listing that XBMC can display as a directory
    listing
    @return list
    """
    listing = []
    listing.append(['Movies', sys.argv[0]+"?mode=movies"])
    listing.append(['TV Shows', sys.argv[0]+"?mode=tv"])
    return listing

def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
            params=sys.argv[2]
            cleanedparams=params.replace('?','')
            if (params[len(params)-1]=='/'):
                params=params[0:len(params)-2]
            pairsofparams=cleanedparams.split('&')
            param={}
            for i in range(len(pairsofparams)):
                splitparams={}
                splitparams=pairsofparams[i].split('=')
                if (len(splitparams))==2:
                    param[splitparams[0]]=splitparams[1]
        return param

params=get_params()

def existsEDL(srtLoc):
    try:
        edlLoc = srtLoc[:-3] + "edl"
        return os.path.isfile(edlLoc)
    except:
        return False

def getSRT(fileLoc):
    head, ext = os.path.splitext(fileLoc)
    xbmc.log("head: %s" % head)
    srtFile = head + ".srt"
    if os.path.isfile(srtFile):
        return srtFile
    if ext.lower() == 'mkv':
        toolsDir = ?
        subTrack = mkv.getSubTrack(fileLoc, toolsDir)
        if subTrack:
            if mkv.extractFromMKV(fileLoc, toolsDir, subTrack) == 0:
                return srtFile
            else:
                xbmc.log("Unable to extract subtitle from MKV file")
        else:
            xbmc.log("No subtitle track in the MKV file")
    #TODO: Could do more here to find a sub file
    return None

def createEDL():
    try:
        filterLoc = os.path.join( BASE_RESOURCE_PATH, "filter.txt" )
        safety = Addon.getSetting("safety")
        safety = float(safety) / 1000
        edl = EDLCreator(srtLoc, filterLoc, safety)
        if existsEDL(srtLoc):
            ret = dialog.yesno(details['label'], plugin.get_string(30301))
            if not ret:
                return False
        edl.createEDL()
        return True
    except:
        return False

try:
    mode=urllib.unquote_plus(params["mode"])
except:
    mode = None

if mode == 'movie-details':
    movieid=urllib.unquote_plus(params["id"])
    xbmc.log("movieid: %s" % str(movieid))
    details = data.getMovieDetails(movieid)
    xbmc.log('details: %s' % details)
    
    dialog = xbmcgui.Dialog()
    ret = dialog.yesno(details['label'], plugin.get_string(30302))
    if not ret:
        sys.exit()
    
    fileLoc = details['file']
    srtLoc = getSRT(fileLoc)
    if srtLoc:
        xbmc.log("Found srt file: %s" % srtLoc)
        if createEDL():
            dialog.ok(details['label'], plugin.get_string(30303))
    else:
        xbmc.log("No srt file!")
        ret = dialog.yesno(details['label'], plugin.get_string(30304))
        if ret:
            pDialog = xbmcgui.DialogProgress()
            ret = pDialog.create('XBMC', plugin.get_string(30305))
            xbmc.log('Downloading')
            try:
                dl.FindSubtitles(fileLoc,"eng")
                srtLoc = getSRT(fileLoc)
            except:
                print traceback.format_exc()
                dialog.ok('XBMC', plugin.get_string(30306))
            
            if (pDialog.iscanceled()): 
                sys.exit()
            pDialog.close()
            
            if srtLoc:
                if createEDL():
                    dialog.ok(details['label'], plugin.get_string(30303))
            else:
                dialog.ok('XBMC', plugin.get_string(30306))
else:
    xbmc.log("Running %s v0.1. Using default listing." % ADDON_ID)
    movieDict = data.GetAllMovies()
    xbmc.log("movieDict: %s" % movieDict)
    win = xbmcgui.WindowDialog()
    listing = []
    for movie in movieDict:
        url = sys.argv[0]+"?mode=movie-details&id="+str(movie['movieid'])
        listing.append([movie['label'],movie['thumbnail'],url])
    ui.showThumbnailListing(listing)