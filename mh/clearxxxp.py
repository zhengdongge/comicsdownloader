import os

start_id = 4301
end_id = 4400
for url_num in range(start_id, end_id+1):
    dir_num = ((int(url_num) - 1) // 100 * 100) + 1
    document = '/media/gzd/本地磁盘H/漫画/18h/' + str(dir_num) + '_' + str(dir_num + 99)
    os.chdir(document)
    for folder in os.listdir(document):
        if 'p]' in folder:
            comics_path_old = os.path.relpath(folder, start=document)
            comics_path_new = comics_path_old[:-6]
            os.rename(comics_path_old, comics_path_new)
