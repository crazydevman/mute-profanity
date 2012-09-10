import sys, os, re

def frametoseconds(frame, framerate):
    return float(1/float(framerate)*int(frame))
    
def formattime(time):
    duration = int(time) 
    hours = duration / 3600
    minutes = (duration - hours * 3600) / 60
    seconds = duration % 60
    return "%02d:%02d:%02d,%s" % (hours, minutes, seconds, str(time).split(".")[1].ljust(3,"0"))

def convert(fname):
    file = open(fname)
    linecount = 0
    framerate = 0
    srtname = os.path.splitext(os.path.split(fname)[1])[0]+".srt"
    outfile = open(srtname, "w")
    for line in file.readlines():
        if linecount == 0:
            framerate = re.findall("\{\d+\}\{\d+\}(.*)$", line)[0].rstrip("\r")
        else:
            startframe, endframe, subtitle = re.findall("\{(\d+)\}\{(\d+)\}(.*)$", line)[0]
            starttime = formattime(round(float(frametoseconds(startframe, framerate)), 3))
            endtime = formattime(round(float(frametoseconds(endframe, framerate)), 3))
            subtitle.rstrip("\r")
            outfile.write("%d\n%s --> %s\n%s\n\n"%(linecount, starttime, endtime, subtitle.replace("|", "\n")))
        linecount = linecount + 1
        outfile.flush()
    outfile.close()    
    file.close()
    return srtname
