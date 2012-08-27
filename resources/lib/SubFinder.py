'''
Created August 26, 2012

@author: Scott Brown
'''
import os
import time
import traceback

import MKVSubExtract as mkv
import MP4SubExtract as mp4
import SubDownloader as dl

import xbmcgui

def log(*args):
    for arg in args:
        print arg

class SubFinder():
    '''Used to find SRT subtitles'''
    def __init__(self, Addon, plugin):
        self.Addon = Addon
        self.plugin = plugin
        
        #copy our log function to the modules
        mkv.log = log
        mp4.log = log
        dl.log = log
        
    def getSRT(self, fileLoc):
        head, ext = os.path.splitext(fileLoc)
        log("head: %s" % head)
        
        srtFile = head + ".SRT"
        if os.path.isfile(srtFile):
            log("Found existing SRT file: %s" % srtFile)
            return srtFile
        
        srtFile = head + ".srt"
        if os.path.isfile(srtFile):
            log("Found existing SRT file: %s" % srtFile)
            return srtFile
        
        log("No external srt file was found")
        
        extractor = None
        if ext.lower() == '.mkv' and self.Addon.getSetting("usemkvextract") == "true":
            log("Will attempt to use mkvextract to extract subtitle")
            extractor = mkv.MKVExtractor() #Addon.getSetting("mkvextractpath"))
        elif (ext.lower() == ".m4v" or ext.lower() == '.mp4') and self.Addon.getSetting("usemp4box") == "true":
            log("Will attempt to use mp4box to extract subtitle")
            extractor = mp4.MP4Extractor()
        
        if extractor:
            subTrack = None
            try:
                subTrack = extractor.getSubTrack(fileLoc)
            except:
                log(traceback.format_exc())
                log('Error attempting to get the subtitle track')
            
            if not subTrack:
                log("No subtitle track found in the file")
                
            else:
                pDialog = xbmcgui.DialogProgress()
                pDialog.create('XBMC', self.plugin.get_string(30320))
                extractor.startExtract(fileLoc, subTrack)
                while extractor.isRunning():
                    if pDialog.iscanceled():
                        extractor.cancelExtract()
                        log("User cancelled the extraction progress; returning")
                        return None
                    pDialog.update(extractor.progress)
                    time.sleep(.1)
                    
                srtFile = extractor.getSubFile()
                if srtFile:
                    return srtFile
                else:
                    log("Unable to extract subtitle from file")
                    xbmcgui.Dialog().ok('XBMC', self.plugin.get_string(30321))
                    
        dialog = xbmcgui.Dialog()
        download = True
        if not self.Addon.getSetting("autodownload"):
            download = dialog.yesno("XBMC", self.plugin.get_string(30304))
            
        if download:
            pDialog = xbmcgui.DialogProgress()
            pDialog.create('XBMC', self.plugin.get_string(30305))
            log('Attempting to download subtitle file from the internet')
            srtFile = None
            try:
                srtFile = dl.FindSubtitles(fileLoc,"eng")
            except:
                log(traceback.format_exc())
            
            if (pDialog.iscanceled()): 
                log("TODO: Dialog was cancelled, we should have stopped")
                pDialog.close()
                return None
                
            pDialog.close()
            if srtFile:
                log("Successfully downloaded subtitle file: %s" % srtFile)
                return srtFile
            else:
                log("Could not download subtitle file")
                dialog.ok('XBMC', self.plugin.get_string(30306))
        
        #Any other options to create SRT file, put them here
        log("Could not use any means available to find the subtitle file")
        return None