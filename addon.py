"""
Created on Apr 5, 2012

@author: Scott Brown
"""

import os
import sys

import xbmc
import xbmcaddon

Addon = xbmcaddon.Addon()
__addon_path__ = Addon.getAddonInfo('path')
BASE_RESOURCE_PATH = xbmc.translatePath(os.path.join(__addon_path__, 'resources'))
sys.path.append(os.path.join(BASE_RESOURCE_PATH, "lib"))

import nav

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


params = get_params()
nav.handle(params)