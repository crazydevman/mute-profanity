"""
Created on July 13, 2013

@author: Scott Brown
"""

import urllib
import os
import sys
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs

Addon = xbmcaddon.Addon()
__addon_path__ = Addon.getAddonInfo('path')
__scriptid__ = Addon.getAddonInfo('id')
__scriptname__ = Addon.getAddonInfo('name')
__cwd__ = Addon.getAddonInfo('path')
__version__ = Addon.getAddonInfo('version')


BASE_RESOURCE_PATH = xbmc.translatePath(os.path.join(__addon_path__, 'resources'))
MEDIA_PATH = os.path.join(BASE_RESOURCE_PATH, 'media')
BACKGROUND_FILE = os.path.join(MEDIA_PATH, 'BackgroundPanel.png')

from EDLManager import EDLManager
import JSONUtils as data
import SubFinder as subf
import filter

# magic; id of this plugin's instance - cast to integer
_thisPlugin = int(sys.argv[1])

#setup loggers
subf.log = xbmc.log


def showSimpleListing(listing, isDir=True):
    # send each item to xbmc
    for item in listing:
        print "adding item: %s" % item[0]
        print "url will go to %s" % item[1]
        listItem = xbmcgui.ListItem(item[0])
        xbmcplugin.addDirectoryItem(_thisPlugin,item[1],listItem, isDir)

    # tell xbmc we have finished creating
    xbmcplugin.endOfDirectory(_thisPlugin)


def showThumbnailListing(listing, isDir=False):
    for item in listing:
        listItem = xbmcgui.ListItem(label=item[0], thumbnailImage=item[1])
        xbmcplugin.addDirectoryItem(_thisPlugin,item[2],listItem, isDir)

    # tell xbmc we have finished creating
    xbmcplugin.endOfDirectory(_thisPlugin)


def get_categories():
    filterLoc = os.path.join(BASE_RESOURCE_PATH, "filter.txt")
    return filter.parse_file(filterLoc)


def get_severities():
    mapping = {'None': None, 'Low': 10, 'Medium': 8, 'High': 6, 'Very High': 1}
    xbmc.log('Cat1: ' + Addon.getSetting("blockcat1"))
    xbmc.log('Cat2: ' + Addon.getSetting("blockcat2"))
    xbmc.log('Cat3: ' + Addon.getSetting("blockcat3"))
    xbmc.log('Cat4: ' + Addon.getSetting("blockcat4"))
    severities = {'Expletives': mapping[Addon.getSetting("blockcat1")],
                  'Religious': mapping[Addon.getSetting("blockcat2")],
                  'Sexual': mapping[Addon.getSetting("blockcat3")],
                  'Derogatory Terms': mapping[Addon.getSetting("blockcat4")]}
    return severities


def getInitialListing():
    listing = list()
    listing.append(['Edit Movies', sys.argv[0] + "?mode=movies"])
    listing.append(['Edit TV Shows', sys.argv[0] + "?mode=tv"])
    listing.append(['View Active Blocked List', sys.argv[0] + "?mode=view-active"])
    listing.append(['View All Words', sys.argv[0] + "?mode=show-all"])
    return listing


def getWordsListing(show_all=False):
    listing = list()
    categories = get_categories()
    severities = get_severities()

    catId = 0
    for name, tuples in categories.iteritems():
        wordId = 0
        for word, severity in tuples:
            if show_all or filter.is_blocked(severity, name, severities):
                params = {'mode': 'word-details',
                          'wordId': wordId,
                          'categoryId': catId}
                listing.append([word, sys.argv[0] + '?' + urllib.urlencode(params)])
            wordId += 1
        catId += 1
    return listing


def get_params():
    param = []
    paramstring = sys.argv[2]
    if len(paramstring) >= 2:
        params = sys.argv[2]
        cleanedparams = params.replace('?', '')
        if params[len(params) - 1] == '/':
            params = params[0:len(params) - 2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]
    return param


def get_blocked_words():
    tuples = filter.get_blocked_tuples(get_categories(), get_severities())
    return [word for word, severity in tuples]


def createEDL(srtLoc, fileLoc):
    try:
        safety = Addon.getSetting("safety")
        safety = float(safety) / 1000
        edl = EDLManager(srtLoc, fileLoc, get_blocked_words(), safety)
        edl.open_file = lambda x,y : xbmcvfs.File(x, y)
        edl.rename = lambda x,y : xbmcvfs.rename(x,y)
        if Addon.getSetting("editsrt") == "true":
            # Tell the edl manager to replace blocked works on SRT file too
            edl.modify_srt = True

        # Does all work to update / create EDL, update SRT
        edl.updateEDL()
        return True
    except:
        print "Unexpected error:", sys.exc_info()[0]
        return False


def handle(params):
    try:
        mode = urllib.unquote_plus(params["mode"])
    except:
        mode = None

    dialog = xbmcgui.Dialog()

    if mode == 'mute-movie':
        movieid = urllib.unquote_plus(params["id"])
        xbmc.log("movieid: %s" % str(movieid))
        details = data.getMovieDetails(movieid)
        xbmc.log('details: %s' % details)

        ret = dialog.yesno(details['label'], Addon.getLocalizedString(30302))
        if not ret:
            sys.exit()

        fileLoc = details['file']
        finder = subf.SubFinder(Addon)
        srtLoc = finder.getSRT(fileLoc)
        if srtLoc:
            xbmc.log("Using srt file: %s" % srtLoc)
            if createEDL(srtLoc, fileLoc):
                dialog.ok(details['label'], Addon.getLocalizedString(30303))
            else:
                dialog.ok(details['label'], Addon.getLocalizedString(30307))
    elif mode == 'mute-episode':
        episodeId = urllib.unquote_plus(params["id"])
        xbmc.log("episodeId: %s" % str(episodeId))
        details = data.getEpisodeDetails(episodeId)
        xbmc.log('details: %s' % details)

        ret = dialog.yesno(details['showtitle'], Addon.getLocalizedString(30308))
        if not ret:
            sys.exit()

        fileLoc = details['file']
        finder = subf.SubFinder(Addon)
        srtLoc = finder.getSRT(fileLoc)
        if srtLoc:
            xbmc.log("Using srt file: %s" % srtLoc)
            if createEDL(srtLoc, fileLoc):
                dialog.ok(details['showtitle'], Addon.getLocalizedString(30309))
            else:
                dialog.ok(details['showtitle'], Addon.getLocalizedString(30307))
    elif mode == 'movies':
        movieDict = data.GetAllMovies()
        xbmc.log("movieDict: %s" % movieDict)
        listing = []
        for movie in movieDict:
            url = sys.argv[0] + "?mode=mute-movie&id=" + str(movie['movieid'])
            listing.append([movie['label'], movie['thumbnail'], url])
        showThumbnailListing(listing)
    elif mode == 'tv':
        shows = data.GetAllTVShows()
        xbmc.log('tv shows: %s' % shows)
        listing = []
        for show in shows:
            url = sys.argv[0] + "?mode=tvshow-details&id=" + str(show['tvshowid'])
            listing.append([show['label'], show['thumbnail'], url])
        showThumbnailListing(listing, True)
    elif mode == 'tvshow-details':
        showId = urllib.unquote_plus(params["id"])
        episodes = data.GetTVShowEpisodes(showId)
        xbmc.log('episodes: %s' % episodes)
        listing = []
        for episode in episodes:
            url = sys.argv[0] + "?mode=mute-episode&id=" + str(episode['episodeid'])
            listing.append([episode['label'], episode['thumbnail'], url])
        showThumbnailListing(listing, True)
    elif mode == 'view-active':
        show = dialog.yesno("WARNING", "This will show offensive words on screen.\nAre you sure you want to view it now?")
        if show:
            showSimpleListing(getWordsListing())
    elif mode == 'show-all':
        show = dialog.yesno("WARNING", "This will show offensive words on screen.\nAre you sure you want to view it now?")
        if show:
            dialog.ok('XBMC', "To edit this list, modify 'filter.txt' in the script's directory" )
            showSimpleListing(getWordsListing(True))
    elif mode == 'word-details':
        categoryId = int(urllib.unquote_plus(params["categoryId"]))
        wordId = int(urllib.unquote_plus(params["wordId"]))

        categories = get_categories()
        prefs = get_severities()

        category = categories.keys()[categoryId]
        word, severity = categories[category][wordId]
        isFiltered = filter.is_blocked(severity, category, prefs)
        blockNum = None
        if category in prefs:
            blockNum = prefs[category]

        title = 'Blocking This Word' if isFiltered else 'Not Actively Blocking'
        line0 = 'Category: %s' % category
        line1 = "Severity (1 is lowest, 10 is most offensive): %d" % severity

        if blockNum:
            line2 = 'Current category setting blocks words with severity >= %d' % blockNum
        else:
            line2 = 'No setting for this category, cannot block it'

        dialog.ok(title, line0, line1, line2)

    else:
        xbmc.log("Running %s v%s. Using default listing." % (__scriptid__, __version__))
        xbmc.log(" %s " % str(sys.argv[:]))
        showSimpleListing(getInitialListing())
