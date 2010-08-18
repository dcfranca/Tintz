# -*- coding: iso-8859-1 -*-
import string

def get_profile_path(instance, filename):
    dir = "publications/"+instance.author.__unicode__()+"/"+filename
    return dir
