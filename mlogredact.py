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
    file = '/var/log/mongod.log'

    opts, args = getopt.getopt(sys.argv[1:],":f:")
    for opt, arg in opts:
      if opt == '-f':
        self.file = arg
      else:
        self.printUsage()
        exit(0)

  def parseLine(self, line):
    line = line.strip('\n').strip('\r')
    cmdIndex = line.index(']') + 2

    return line[0:cmdIndex], line[cmdIndex:]


  def flattenJson(self, jsonString):
    jsonString = re.sub('ObjectId\([\'"]([a-zA-Z0-9]*)[\'"]\)', r'"\1"', jsonString)
    jsonString = re.sub('ISODate\(([\'"][a-zA-Z0-9-_ ]*[[\'"])\)', r'"\1"', jsonString)
    jsonString = re.sub('new Date\(([0-9]*)\)', r'"\1"', jsonString)

    return jsonString


  def findJson(self, line):
    counter = 0
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
    line    = line.decode('UTF-8', 'ignore')
    resLine = line

    try:
      for begin, end in jsons:
        jsonString = line[begin:end]
        jsonString = self.flattenJson(jsonString)
        jsonData  = demjson.decode(jsonString)
        obfJson   = self.obfuscateJson(jsonData)
        resLine   = resLine.replace(line[begin:end], demjson.encode(obfJson))
    except demjson.JSONDecodeError, e:
      return 'ERROR Reading the original JSON value'
    except demjson.JSONEncodeError, e:
      return 'ERROR Obfuscating JSON'

    return resLine


  def run(self):
    with open(self.file) as f:
      for line in f:
        time, message = self.parseLine(line)
        message = self.obfuscateJsonLine(message)

        print('%s %s' % (time, message))

def main():
  mlogredact = MLogReactTool()
  mlogredact.run()

if __name__ == '__main__':
  sys.exit(main())
