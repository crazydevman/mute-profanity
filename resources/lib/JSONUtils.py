'''
Created on Apr 9, 2012

@author: Scott Brown
'''
import xbmc

def GetAllMovies():
    query = '{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": {"properties": ["thumbnail", "file", "mpaa"]}, "id": 1}'
    
    response = xbmc.executeJSONRPC(query)
    if response.startswith( "{" ):
        response = eval( response )
    result = response['result']
    return result['movies']

def getMovieDetails(movieid):
    query = '{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovieDetails", "params": {"movieid": %s, "properties" : ["title", "file"]}, "id": 1}' % movieid
    
    response = xbmc.executeJSONRPC(query)
    xbmc.log("movie details call response: %s" % response)
    
    if response.startswith( "{" ):
        response = eval( response )
    
    result = response['result']
    return result['moviedetails']
