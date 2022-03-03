import os
from shutil import rmtree

name = input("Enter name with extension: ")
NameWithoutExt = name[:-4]
print('Please Wait.......')

comSil = 'ffmpeg -hide_banner -stats -vn -i {name} -af "silencedetect=n=-30dB:d=1"\
         -vstats -f null - 2> silence.txt'.format(name = name)
os.system (comSil)


duration = os.popen('ffmpeg -hide_banner -i "'+ name +'" 2>&1 | grep "Duration"').read()
dur = duration[12 : duration.index(',')]
h,m,s = dur.split(':')
FinalDur = round(float(h)*3600 + float(m)* 60 + float(s))

f = open('silence.txt','r')
l = []
for i in f.readlines():
    if "silence_end" in i :
        l.append(i[:-1].split('|'))
f.close()
##________________________________________##   

time =[]   # end, duration
for i in l:
    time.append([(i[0][i[0].index(':')+2:-1]),(i[1][i[1].index(':')+2:-1])])

c = []
for i in time :
    c.append ([round(float(i[0])-float(i[1]),4),float(i[0])])


if round(c[0][0]) != 0 :
    c.insert(0, [0.0,0.0])

if round(c[-1][1]) != FinalDur:
    c.append([FinalDur,FinalDur]) 


final_directory = 'temp_cuts'
try:
    os.makedirs(final_directory)
except :
    print('Directory already exists')

for i in range(len(c)-1) :
    
    # end cut of current silence
    endCur = str(float(c[i][1]))         
    
    # Duration of current cut
    durCur = str(float(c[i+1][0]) - float(c[i][1])+0.5)  # 0.5 is for fade out effect
    
    # name of the temp cut files with numbering
    newName = str(NameWithoutExt+ "_"+ str(i+1).rjust(8,'0')+".mp4")
    cutPath = str(final_directory + '\\'+ newName)
    
    
    command = "ffmpeg -hwaccel auto -loglevel quiet -ss "+\
              endCur +\
              " -i \"" \
              + name +\
              "\" -to "+\
              durCur +\
              " -c:v h264_nvenc -preset fast -c:a aac \""+\
              cutPath + '\"'
    
    os.system(command)

originalDir = os.getcwd()
os.chdir(final_directory)
parts = []
for i in os.listdir() :
    parts.append(i)

os.chdir(originalDir)
f = open('mylist.txt', 'w')
for i in parts:
    a = "file '"+ final_directory+ '\\'+i + "'\n"
    f.write(a)
f.close()


finCmd = "ffmpeg -hwaccel auto -loglevel quiet -f concat -safe 0 -i mylist.txt -c copy \"{OutName}\"".format(OutName = NameWithoutExt+ '_cut.mp4')
os.system(finCmd)

os.remove('silence.txt')
os.remove ('mylist.txt')
rmtree(final_directory)


print('\nDone !!!\n')
    