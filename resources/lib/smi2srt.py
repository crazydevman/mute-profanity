#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@package smi2srt
@brief this module is for convert .smi subtitle file into .srt subtitle 
	(Request by Alfred Chae)

Started : 2011/08/08
license: GPL

@version: 1.0.0
@author: Moonchang Chae <mcchae@gmail.com>

Modifications by Scott Brown

SMI have this format!
===================================================================================================

SRT have this format!
===================================================================================================
1
00:00:12,000 --> 00:00:15,123
This is the first subtitle

2
00:00:16,000 --> 00:00:18,000
Another subtitle demonstrating tags:
<b>bold</b>, <i>italic</i>, <u>underlined</u>
<font color="#ff0000">red text</font>

3
00:00:20,000 --> 00:00:22,000  X1:40 X2:600 Y1:20 Y2:50
Another subtitle demonstrating position.
"""
__author__ = "MoonChang Chae <mcchae@gmail.com>"
__date__ = "2011/08/08"
__version__ = "1.0.0"
__version_info__ = (1, 0, 0)
__license__ = "GCQVista's NDA"

###################################################################################################
import os
import sys
import re

###################################################################################################
def usage(msg=None, exit_code=1):
    print_msg = """
usage %s smifile.smi [...]
	convert smi into srt subtitle file with same filename.
""" % os.path.basename(
        sys.argv[0]
    )
    if msg:
        print_msg += "%s\n" % msg
    print(print_msg)
    sys.exit(exit_code)


###################################################################################################
class smiItem(object):
    def __init__(self):
        self.start_ms = 0L
        self.start_ts = "00:00:00,000"
        self.end_ms = 0L
        self.end_ts = "00:00:00,000"
        self.contents = None
        self.linecount = 0

    @staticmethod
    def ms2ts(ms):
        hours = ms / 3600000L
        ms -= hours * 3600000L
        minutes = ms / 60000L
        ms -= minutes * 60000L
        seconds = ms / 1000L
        ms -= seconds * 1000L
        s = "%02d:%02d:%02d,%03d" % (hours, minutes, seconds, ms)
        return s

    def convertSrt(self):
        if self.linecount == 4:
            i = 1  # @UnusedVariable
        # 1) convert timestamp
        self.start_ts = smiItem.ms2ts(self.start_ms)
        self.end_ts = smiItem.ms2ts(self.end_ms - 10)
        # 2) remove new-line
        self.contents = re.sub(r"\s+", " ", self.contents)
        # 3) remove web string like "&nbsp";
        self.contents = re.sub(r"&[a-z]{2,5};", "", self.contents)
        # 4) replace "<br>" with '\n';
        # self.contents = re.sub(r'(<br>)+', '\n', self.contents, flags=re.IGNORECASE)
        self.contents = re.sub(r"(<br>)+", "\n", self.contents)
        # 5) find all tags
        fndx = self.contents.find("<")
        if fndx >= 0:
            contents = self.contents
            sb = self.contents[0:fndx]
            contents = contents[fndx:]
            while True:
                m = re.match(
                    r"</?([a-z]+)[^>]*>([^<>]*)", contents, flags=re.IGNORECASE
                )
                if m == None:
                    break
                contents = contents[m.end(2) :]
                # if m.group(1).lower() in ['font', 'b', 'i', 'u']:
                if m.group(1).lower() in ["b", "i", "u"]:
                    sb += m.string[0 : m.start(2)]
                sb += m.group(2)
            self.contents = sb
        self.contents = self.contents.strip()
        self.contents = self.contents.strip("\n")

    def __repr__(self):
        s = "%d:%d:<%s>:%d" % (
            self.start_ms,
            self.end_ms,
            self.contents,
            self.linecount,
        )
        return s


###################################################################################################
def convertSMI(smi_file):
    if not os.path.exists(smi_file):
        sys.stderr.write("Cannot find smi file <%s>\n" % smi_file)
        return False
    rndx = smi_file.rfind(".")
    srt_file = "%s.srt" % smi_file[0:rndx]

    ifp = open(smi_file)
    smi_sgml = ifp.read()  # .upper()
    ifp.close()

    # skip to first starting tag (skip first 0xff 0xfe ...)
    try:
        fndx = smi_sgml.find("<SYNC")
    except Exception as e:
        print(chdt)
        raise e
    if fndx < 0:
        return None
    smi_sgml = smi_sgml[fndx:]
    lines = smi_sgml.split("\n")

    srt_list = []
    sync_cont = ""
    si = None
    last_si = None
    linecnt = 0
    for line in lines:
        linecnt += 1
        sndx = line.upper().find("<SYNC")
        if sndx >= 0:
            m = re.search(r"<sync\s+start\s*=\s*(\d+)>(.*)$", line, flags=re.IGNORECASE)
            if not m:
                raise Exception(
                    'Invalid format tag of <Sync start=nnnn> with "%s"' % line
                )
            sync_cont += line[0:sndx]
            last_si = si
            if last_si != None:
                last_si.end_ms = long(m.group(1))
                last_si.contents = sync_cont
                srt_list.append(last_si)
                last_si.linecount = linecnt
                # print '[%06d] %s' % (linecnt, last_si)
            sync_cont = m.group(2)
            si = smiItem()
            si.start_ms = long(m.group(1))
        else:
            sync_cont += line

    ofp = open(srt_file, "w")
    ndx = 1
    for si in srt_list:
        si.convertSrt()
        if si.contents == None or len(si.contents) <= 0:
            continue
        # print si
        sistr = "%d\n%s --> %s\n%s\n\n" % (ndx, si.start_ts, si.end_ts, si.contents)
        # sistr = unicode(sistr, 'utf-8').encode('euc-kr')
        ofp.write(sistr)
        ndx += 1
    ofp.close()
    return srt_file


###################################################################################################
def doConvert():
    if len(sys.argv) <= 1:
        usage()
    for smi_file in sys.argv[1:]:
        if convertSMI(smi_file):
            print("Converting <%s> OK!" % smi_file)
        else:
            print("Converting <%s> Failture!" % smi_file)


###################################################################################################
if __name__ == "__main__":
    doConvert()
