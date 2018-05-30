#-----------------------------------------------------------------------------#
# Imports
#-----------------------------------------------------------------------------#
import re
import os
import numpy as np

#-----------------------------------------------------------------------------#
# NJOY input template
#-----------------------------------------------------------------------------#
njoy_template = \
"""
moder /
20 -21
reconr /
-21 -22
'PENDF tape' /
{0} 0 0/
0.001 0.0 0.005/
0/
broadr /
-21 -22 -23
{0} 1 0 0 0/
0.001 1 0.02/
300/
0/
unresr /
-21 -23 -24/
{0} 1 1 0/
300/
infinity/
0/
groupr /
-21 -24 0 25/
{0} 3 0 5/
''/
300
infinity
3 {1}/
0/
0/
stop
"""

#-----------------------------------------------------------------------------#
# Cross Section Library
#-----------------------------------------------------------------------------#
def make_library(MAT_MT, path = '/home/keith/opt/NJOY2016/bin/njoy') :
    """ Process nuclide output.
    
        Args:
            MAT_MT: tuple containing material number and reaction number 
                    ex. (9228, 102) represents the (n,gamma) xs for u235 
            path: path to njoy
    """ 
    if type(MAT_MT) == tuple:
        MAT_MT = [MAT_MT]
    elif type(MAT_MT) != list:
        print('BAD INPUT, input must be a tuple or a list of tuples')
        return
    if type(MAT_MT[0][0]) != str:
        print('BAD INPUT, tuple elements must be strings') 
        return
    library = []
    for foil in MAT_MT:
        MAT = str(foil[0])
        MT = str(foil[1])
        s = njoy_template.format(MAT, MT)
        f = open('njoy.inp', 'w')
        f.write(s)
        f.close()
        os.system('cp ' + MAT + '.endf tape20')
        os.system(path + ' < njoy.inp')
        file = open('output', 'r').read()
        p0 = '\s*(\d+\s{4}\S+)\n\s+'
        # Get group and cross section
        data = re.findall(p0, file) 
        p1 = r'(\d+)\sgroup'
        # Get number of groups
        group_num = int(re.findall(p1, file)[0]) 
        entry = np.zeros(group_num)
        for i in data:
            group = i.split()[0]
            cross_section = i.split()[1]
            entry[int(group)-1] = clean_value(cross_section)
        library.append(entry)
    return(library)

def clean_value(v) :
    """ Clean a formatted value and return as a float.
    
        Args:
            s: string of value to clean
        Returns:
            v: float value
    """
    # from 1-1 to 1e-1
    v = re.sub('(?<=\d)-', 'e-', v)
    # from 1+1 to 1e1
    return float(v.replace('+', 'e'))

def throwaway(trash):
    for garbage in trash:
        os.remove(garbage)
    return

#-----------------------------------------------------------------------------#
# Final stuff
#-----------------------------------------------------------------------------#
if __name__ == "__main__":
    outfile = make_library([
                            ('4931', '102'), ('4931', '4')  , ('7925', '4'),  \
                            ('7925', '16') , ('7925', '102'), ('4525', '4'),  \
                            ('4525', '102'), ('1325', '103'), ('1325', '103'),\
                            ('1325', '107')
                          ])
    np.save('njoy_cross_sections', outfile)
    trash = ['tape20', 'tape21', 'tape22', 'tape23', \
             'tape24', 'tape25', 'output', 'njoy.inp']
    throwaway(trash)






