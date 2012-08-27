
import struct
import os
import string

from zipfile import *
from xmlrpclib import ServerProxy
from urllib2 import Request, urlopen

text_characters = "".join(map(chr, range(32, 127)) + list("\n\r\t\b"))
_null_trans = string.maketrans("", "")

server = ServerProxy("http://api.opensubtitles.org/xml-rpc")
token = ""
           
def FindSubtitles(videoname, lang):
        print "Contacting www.opensubtitles.org (" + videoname + ")"
        filename = os.path.join (os.path.dirname(videoname), os.path.splitext(os.path.basename(videoname))[0] + ".srt")
        print filename
        
        langs = lang.split(",")
        
        data = GetSubtitles(videoname);
        if data:
                for l in langs:
                        for item in data:
                                if item['SubLanguageID'] == l:
                                        print "Found", item['LanguageName'], "subtitle ..."
                                        fullFile = os.path.join (os.path.dirname(videoname), item['SubFileName'])
                                        zipname = Download(item['ZipDownloadLink'], fullFile)
                                        print "Extracting subtitle ", filename
                                        Unzip(zipname, filename, item['SubFileName'])
                                        os.remove(zipname)
                                        return filename
        print "No Subtitles found"
        return None
        
                                
def GetSubtitles(moviepath):
        #print server.LogIn("","","","SubIt")['status']
        token = server.LogIn("", "", "", "SubIt")['token']
                
        moviebytesize = os.path.getsize(moviepath) 
        hash = Compute(moviepath)
        movieInfo = {'sublanguageid' : 'eng', 'moviehash' : hash, 'moviebytesize' : str(moviebytesize)}
        movies = [movieInfo]
        data = server.SearchSubtitles(token, movies)['data']
        
        # if the hash fails, try searching by title of movie (assuming file is named after its title)
        if (data == False):
                basename = os.path.basename(moviepath)
                name = os.path.splitext(basename)[0]
                print "Could not find by hash ..." 
                print "Searching by name: \"" + name + "\"" 
                movieInfo = {'sublanguageid' : 'eng', 'query' : name}
                movies = [movieInfo]
                data = server.SearchSubtitles(token, movies)['data']
                
        server.LogOut()
        
        return data
        
        

def Compute(name): 
        try:
                longlongformat = 'q'  # long long 
                bytesize = struct.calcsize(longlongformat) 
                f = file(name, "rb") 
                filesize = os.path.getsize(name) 
                hash = filesize 
                
                if filesize < 65536 * 2: 
                        return "SizeError" 

                for x in range(65536 / bytesize): 
                        buffer = f.read(bytesize) 
                        (l_value,) = struct.unpack(longlongformat, buffer)  
                        hash += l_value 
                        hash = hash & 0xFFFFFFFFFFFFFFFF #to remain as 64bit number  


                f.seek(max(0, filesize - 65536), 0) 
                for x in range(65536 / bytesize): 
                        buffer = f.read(bytesize) 
                        (l_value,) = struct.unpack(longlongformat, buffer)  
                        hash += l_value 
                        hash = hash & 0xFFFFFFFFFFFFFFFF 

                f.close() 
                returnedhash = "%016x" % hash 
                return returnedhash 

        except(IOError):
                return "IOError"

def Unzip(zipname, unzipname, subname=None):
        z = ZipFile(zipname)
        if not subname:
            for filename in z.namelist():
                if os.path.splitext(os.path.basename(filename))[1] == ".srt":
                    outfile = file(unzipname, "w")
                    outfile.write(z.read(filename))
                    outfile.close()
                    break
        else:
            #Subtitle file specified, just use that one
            outfile = file(unzipname, "w")
            outfile.write(z.read(subname))
            outfile.close()

def istext(s):
    if "\0" in s:
        return 0
    
    if not s:  # Empty files are considered text
        return 1

    # Get the non-text characters (maps a character to itself then
    # use the 'remove' option to get rid of the text characters.)
    t = s.translate(_null_trans, text_characters)

    # If more than 30% non-text characters, then
    # this is considered a binary file
    return float(len(t)) / len(s) <= 0.30
 
def Download(url, filename):
        req = Request(url)
        f = urlopen(req)
        print "downloading " + url
        print "save to " + filename + ".zip"
        # Open our local file for writing
        local_file = open(filename + ".zip", "w" + "b")
        #Write to our local file
        local_file.write(f.read())
        local_file.close()
        print "file " + filename + ".zip created"
        return filename + ".zip"
