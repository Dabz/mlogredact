from __future__ import print_function
import dateutil.parser
import re
import datetime
import string
import json
import demjson
import sys
import random
import getopt
import six

class MLogReactTool:

  def printUsage(self):
    print('python mlogredact.py -f $LOG_FILE')


  def __init__(self):
    self.file  = '/var/log/mongod.log'
    self.debug = False

    opts, args = getopt.getopt(sys.argv[1:],":f:d")
    for opt, arg in opts:
      if opt == '-f':
        self.file = arg
      elif opt == '-d':
        self.debug = True
      else:
        self.printUsage()
        exit(0)

  def parseLine(self, line):
    line  = line.strip('\n').strip('\r')
    line  = line.decode('UTF-8', 'ignore')
    if ']' in line and line.index(']') < (len(line) - 2):
      index = line.index(']') + 2
      return line[0:index], line[index:]
    else:
      msg, e = "Error: not a standard line", ""
      if self.debug:
        msg += ' (' + line + ')'
      return msg, e


  def flattenJson(self, jsonString):
    jsonString = re.sub('([,{]\s*)([a-zA-Z0-9_]+\.[a-zA-Z0-9\._]+)\s*:', r'\1"\2": ', jsonString)
    jsonString = re.sub('ObjectId\([\'"]([a-zA-Z0-9]*)[\'"]\)', r'"\1"', jsonString)
    jsonString = re.sub('ISODate\(([\'"][a-zA-Z0-9-_ ]*[[\'"])\)', r'"\1"', jsonString)
    jsonString = re.sub('new Date\(([0-9]*)\)', r'"\1"', jsonString)
    jsonString = re.sub('BinData\([a-zA-Z0-9.-_]*\)', r'"BinData"', jsonString)
    jsonString = re.sub('BinData', r'"BinData"', jsonString)

    jsonString = re.sub(r':\s*([a-zA-Z\-_/@]+[a-zA-Z\.-_/0-9@]*)', ": '\1'", jsonString)

    return jsonString


  def findJson(self, line):
    counter = 0
    beg     = 0
    res     = []

    for i, c in enumerate(line):
      if c == '{':
        if counter == 0:
          beg = i
        counter += 1
      if c == '}':
        counter -= 1
        if counter <= 0:
          res.append((beg, i + 1))

    return res

  def obfuscateJson(self, jsonData):
    for key, value in jsonData.iteritems():
      if isinstance(value, six.string_types):
        jsonData[key] = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(len(value)))
      elif isinstance(value, datetime.date):
        jsonData[key] = datetime(random.randint(2000, 2015), random.randint(1, 12), random.randint(1, 28))
      else:
        jsonData[key] = random.randint(0, 1000)

    return jsonData


  def obfuscateJsonLine(self, line):
    jsons   = self.findJson(line)
    resLine = line

    try:
      for begin, end in jsons:
        jsonString = line[begin:end]
        jsonString = self.flattenJson(jsonString)
        jsonData  = demjson.decode(jsonString)
        obfJson   = self.obfuscateJson(jsonData)
        resLine   = resLine.replace(line[begin:end], demjson.encode(obfJson))
    except demjson.JSONDecodeError, e:
      msg = 'ERROR Deconding JSON'
      if self.debug:
        msg += ' (' + jsonString + ')'
      return msg
    except demjson.JSONEncodeError, e:
      return 'ERROR Obfuscating JSON'

    return resLine

  def obfuscateIPLine(self, message):
    message = re.sub(r'[0-9]+\.[0-9]+\.[0-9]+', r'%d.%d.%d' % (random.randint(1, 254), random.randint(1, 254), random.randint(1, 254)), message)
    message = re.sub(r'[0-9]+\.[0-9]+\.[0-9]+', r'%d.%d.%d' % (random.randint(1, 254), random.randint(1, 254), random.randint(1, 254)), message)
    return message


  def run(self):
    with open(self.file) as f:
      for line in f:
        time, message = self.parseLine(line)
        if not message == "":
          message = self.obfuscateJsonLine(message)
          message = self.obfuscateIPLine(message)

        if not time.strip():
          time = ''
        if not message.strip():
          message = ''

        print('%s %s' % (time.encode('ascii'), message.encode('ascii', 'ignore')))

def main():
  mlogredact = MLogReactTool()
  mlogredact.run()

if __name__ == '__main__':
  sys.exit(main())
