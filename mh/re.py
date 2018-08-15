import re
pattern = re.compile(r'^((https|http|ftp|rtsp|mms)?:\/\/)[^\s]+')
str = u'http://www.jb51.net'
print(pattern.search(str))