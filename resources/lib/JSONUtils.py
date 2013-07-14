"""
Created on Apr 9, 2012
Updated July 13, 2013

@author: Scott Brown
"""
import xbmc

def __get_result(query, logit=False):
    response = xbmc.executeJSONRPC(query)

    if logit:
        xbmc.log('response from query %s\n%s' %(query, response))

    if response.startswith( "{" ):
        response = eval( response )
    return response['result']

def GetAllMovies():
    query = '{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": {"properties": ["thumbnail", "file", "mpaa"]}, "id": 1}'
    
    result = __get_result(query, True)
    if 'movies' not in result:
        return []
    return result['movies']

def getMovieDetails(movieid):
    query = '{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovieDetails", "params": {"movieid": %s, "properties" : ["title", "file"]}, "id": 1}' % movieid
    
    result = __get_result(query)
    return result['moviedetails']

def GetAllTVShows():
    query = '{"jsonrpc": "2.0", "method": "VideoLibrary.GetTVShows", "params": {"properties": ["studio", "thumbnail"]}, "id": 1}'

    result = __get_result(query, True)
    if 'tvshows' not in result:
        return []
    return result['tvshows']

def GetTVShowEpisodes(showId):
    query = '{"jsonrpc": "2.0", "method": "VideoLibrary.GetEpisodes", "params": {"properties": ["showtitle", "thumbnail", "file"], "sort": {"method": "episode"}, "tvshowid":%s}, "id": 1}' % showId

    result = __get_result(query, True)
    if 'episodes' not in result:
        return []
    return result['episodes']

def getEpisodeDetails(episodeId):
    query = '{"jsonrpc": "2.0", "method": "VideoLibrary.GetEpisodeDetails", "params": {"episodeid": %s, "properties" : ["showtitle", "file"]}, "id": 1}' % episodeId

    result = __get_result(query, True)
    return result['episodedetails']
