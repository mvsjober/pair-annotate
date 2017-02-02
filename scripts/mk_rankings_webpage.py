#!/usr/bin/env python3

import sys
import numpy as np
import matplotlib.pyplot as plt

#------------------------------------------------------------------------------

wanted_video = sys.argv[1]
rankings_txt = sys.argv[2]
#threshold = sys.argv[3]
threshold = float(sys.argv[3])
outputdir = sys.argv[4]

items = []

#------------------------------------------------------------------------------

with open(rankings_txt, 'r') as fp:
    for line in fp:
        parts = line.split(',')
        if parts[0] != wanted_video:
            continue
        items.append((parts[0], parts[1], float(parts[2])))

sorted_items = sorted(items, key=lambda x:x[2])
values = np.array([t[2] for t in sorted_items])
vsum = np.sum(values)
vmax = np.max(values)
values_norm = values/vmax

#values_diff = np.diff(values_norm)
#values_diff2 = np.abs(np.diff(values_norm, n=2))

#values_diff2 = np.gradient(values_norm)

dd = np.array([1, 1, 1, -1,  -1, -1])/6.0
values_diff = np.convolve(values_norm, dd, mode='same')
lenn = len(values_norm)
values_diff[0:3] = 0.0
values_diff[lenn-1] = values_diff[lenn-2] = values_diff[lenn-3]

values_diff2 = np.convolve(values_diff, dd, mode='same')
#values_diff2 = np.diff(values_diff)

#am=np.argmax(values_norm>0.5)
half=lenn//2
am=np.argmax(values_diff2[half:]>threshold)+half
if am == 0:
    am = np.argmax(values_diff2)

values_threshold = values_norm[am]
#print(values_threshold, file=sys.stderr)

#print(am, values_diff2, file=sys.stderr)


print("%s %0.1f%%" % (wanted_video, 100.0*am/len(values_norm)), file=sys.stderr)
x=np.linspace(0.0, 1.0, len(values_norm))

#fig = plt.figure()
plt.plot(x, values_norm)
plt.plot(np.linspace(0.0, 1.0, len(values_diff)), 10.0*values_diff, 'r')
plt.plot(np.linspace(0.0, 1.0, len(values_diff2)), 10.0*values_diff2, 'y')

plt.annotate('threshold', xy=(x[am], values_threshold), xycoords='data',
             arrowprops=dict(facecolor='black', shrink=0.05),
             xytext=(x[am]-0.1, values_threshold+0.1))
figfile='threshold_'+wanted_video+'_' + str(threshold) + '.jpg'
plt.savefig(outputdir+'/'+figfile)
#plt.show()

i=1
print('<img src="'+figfile+'"/>')

print("<table>")
print("<tr>")
for t in sorted_items:
    (video_name, image_name, value) = t
    print('<td><img width=300 src="https://annotate.hiit.fi/static/annotate/videos/links/'+video_name+'/images/midframe/'+image_name+'" />')
    print('<br /><font')
    vv = value/vmax
    if vv >= values_threshold:
        print('color="red"')
    print('>' + str(value/vmax) + '</font></td>')

    if i % 5 == 0:
        print('</tr><tr>')
    i += 1


print("</tr>")
print("</table>")
