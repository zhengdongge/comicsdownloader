import os

start_id = 4203#4001
end_id = 4203#5600
checklist = []
for url_num in range(start_id, end_id+1):
    dir_num = ((int(url_num) - 1) // 100 * 100) + 1
    document = '/media/gzd/本地磁盘H/漫画/18h/' + str(dir_num) + '_' + str(dir_num + 99)
    os.chdir(document)
    for folder in os.listdir(document):
        if str(url_num) in folder:
            if 'p]' in folder[-2:]:
                total_img = len([pic for pic in os.listdir(folder)]) - 1
                total_img_title = int(folder[-5:-2])
                if total_img != total_img_title:
                    checklist.append(url_num)

print (checklist)