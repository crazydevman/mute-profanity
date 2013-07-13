"""
Created August 26, 2012

@author: Scott Brown
"""
import os
import time
import traceback

import MKVSubExtract as mkv
import MP4SubExtract as mp4
import SubDownloader as sdl
import sub2srt
import ssatool
import smi2srt

import xbmcgui

def log(*args):
    for arg in args:
        print arg

class SubFinder():
    '''Used to find SRT subtitles'''
    def __init__(self, Addon):
        self.Addon = Addon
        
        #copy our log function to the modules
        mkv.log = log
        mp4.log = log
        sdl.log = log
        
    def getSRT(self, fileLoc):
        head, ext = os.path.splitext(os.path.basename(fileLoc))
        log("head: %s" % head)
        
        #First check existing subtitle files, especially existing SRT backups
        for fname in os.listdir(os.path.dirname(fileLoc)):
            log("Checking fname: %s" % fname)
            if fname.startswith(head) and os.path.splitext(fname)[1].lower() == ".srt":
                fname = os.path.join(os.path.dirname(fileLoc), fname)
                if os.path.isfile(fname + ".bck"):
                    os.rename(fname + ".bck", fname)
                log("Found existing SRT file: %s" % fname)
                return fname
                
        log("No existing SRT file was found")
        
        #Check other subtitle formats, converting them to SRT, starting with SubStation Alpha
        extensions = ['.ssa', '.ass']
        for fname in os.listdir(os.path.dirname(fileLoc)):
            if fname.startswith(head) and os.path.splitext(fname)[1].lower() in extensions:
                fname = os.path.join(os.path.dirname(fileLoc), fname)
                log("Found existing Substation Alpha file: %s" % fname)
                try:
                    return ssatool.main(fname)
                except:
                    log("Error attempting to convert SubStation Alpha file")
                    
        #Check for SMI files
        for fname in os.listdir(os.path.dirname(fileLoc)):
            if fname.startswith(head) and os.path.splitext(fname)[1].lower() == ".smi":
                fname = os.path.join(os.path.dirname(fileLoc), fname)
                log("Found existing SMI file: %s" % fname)
                try:
                    srtFile = smi2srt.convertSMI(fname)
                    if srtFile:
                        return srtFile
                except:
                    log("Error attempting to convert SubStation Alpha file")
        
        #Check for sub files last
        for fname in os.listdir(os.path.dirname(fileLoc)):
            if fname.startswith(head) and os.path.splitext(fname)[1].lower() == ".sub":
                fname = os.path.join(os.path.dirname(fileLoc), fname)
                log("Found existing SUB file: %s, converting to SRT" % fname)
                try:
                    return sub2srt.convert(fname)
                except:
                    log("Error attempting to convert sub file")
        
        extractor = None
        if ext.lower() == '.mkv' and self.Addon.getSetting("usemkvextract") == "true":
            log("Will attempt to use mkvextract to extract subtitle")
            toolsDir = self.Addon.getSetting("mkvextractpath")
            if toolsDir:
                extractor = mkv.MKVExtractor(toolsDir)
            else:
                extractor = mkv.MKVExtractor()
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
                pDialog.create('XBMC', self.Addon.getLocalizedString(30320))
                extractor.startExtract(fileLoc, subTrack)
                while extractor.isRunning():
                    if pDialog.iscanceled():
                        extractor.cancelExtract()
                        log("User cancelled the extraction progress; returning")
                        return None
                    pDialog.update(extractor.progress)
                    time.sleep(.1)
                
                pDialog.close()    
                srtFile = extractor.getSubFile()
                if srtFile:
                    return srtFile
                else:
                    log("Unable to extract subtitle from file")
                    xbmcgui.Dialog().ok('XBMC', self.Addon.getLocalizedString(30321))
                    
        dialog = xbmcgui.Dialog()
        download = True
        if not self.Addon.getSetting("autodownload"):
            download = dialog.yesno("XBMC", self.Addon.getLocalizedString(30304))
            
        if download:
            pDialog = xbmcgui.DialogProgress()
            pDialog.create('XBMC', self.Addon.getLocalizedString(30305))
            log('Attempting to download subtitle file from the internet')
            extractor = sdl.StartThreaded(fileLoc, "eng")
            while extractor.isAlive():
                if pDialog.iscanceled():
                    log("Dialog was cancelled, Stopping download")
                    extractor.join(.01)
                    pDialog.close()
                    return None
                time.sleep(.1)
            
            pDialog.close()
            srtFile = extractor.join()
            if srtFile:
                log("Successfully downloaded subtitle file: %s" % srtFile)
                return srtFile
            else:
                log("Could not download subtitle file")
                dialog.ok('XBMC', self.Addon.getLocalizedString(30306))
        
        #Any other options to create SRT file, put them here
        log("Could not use any means available to find the subtitle file")
        return None