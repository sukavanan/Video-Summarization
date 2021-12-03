'''
 # @ Author: Shivesh M M
 # @ Create Time: 2020-05-02 07:53:20
 # @ Modified by: Shivesh M M
 # @ Description:
 '''

from subprocess import check_output
a = str(check_output('ffprobe -i  "'+file_name+'" 2>&1 |grep "Duration"',shell=True)) 
a = a.split(",")[0].split("Duration:")[1].strip()
h, m, s = a.split(':')
duration = int(h) * 3600 + int(m) * 60 + float(s)

print(int(duration))

