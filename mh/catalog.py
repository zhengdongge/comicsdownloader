import os


document = '/media/gzd/本地磁盘H/漫画/18h/'
fobj = open(document + 'catalog.txt', 'a')
fobj.write('Catalog' + '\n')  # 保存漫画页面url
for folder1 in os.listdir(document):
    os.chdir(document)
    for folder2 in os.listdir(folder1):
        fobj.write(folder2 + '\n')
fobj.close()

