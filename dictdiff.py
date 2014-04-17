# encoding: utf-8
"""
dictdiff.py - Python diff / merge of simple dictionaries / lists

Author: Jure Erznožnik, 4.2014

Important classes / functions:
  dictdiff: Creates the shortest possible diff dictionary
  dictmerge: applies a diff dictionary to base
  
© Jure Erznožnik 2013-
This file is subject to modified BSD license

All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the <organization> nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

TODO: currently nothing
"""

from collections import OrderedDict
from pprint import pprint


class izipDestinationMatching(object):
    __slots__ = ("attr", "value", "index")

    def __init__(self, attr, value, index):
        self.attr, self.value, self.index = attr, value, index

    def __repr__(self):
        return "izip_destination_matching: found match by '%s' = '%s' @ %d" % (self.attr, self.value, self.index)


def izip_destination(a, b, attrs, addMarker=True):
    """
    Returns zipped lists, but final size is equal to b with (if shorter) a padded with nulls
    Additionally also tries to find item reallocations by searching child dicts (if they are dicts) for attribute, listed in attrs)
    When addMarker == False (patching), final size will be the longer of a, b
    """
    for idx, item in enumerate(b):
        try:
            attr = next((x for x in attrs if x in item), None)  # See if the item has any of the ID attributes
            match, matchIdx = next(((orgItm, idx) for idx, orgItm in enumerate(a) if attr in orgItm and orgItm[attr] == item[attr]), (None, None)) if attr else (None, None)
            if match and matchIdx != idx and addMarker: item[izipDestinationMatching] = izipDestinationMatching(attr, item[attr], matchIdx)
        except:
            match = None
        yield (match if match else a[idx] if len(a) > idx else None), item
    if not addMarker and len(a) > len(b):
        for item in a[len(b) - len(a):]:
            yield item, item


def dictdiff(a, b, searchAttrs=[]):
    """
    returns a dictionary which represents difference from a to b
    the return dict is as short as possible:
      equal items are removed
      added / changed items are listed
      removed items are listed with value=None
    Also processes list values where the resulting list size will match that of b.
    It can also search said list items (that are dicts) for identity values to detect changed positions.
      In case such identity value is found, it is kept so that it can be re-found during the merge phase
    @param a: original dict
    @param b: new dict
    @param searchAttrs: list of strings (keys to search for in sub-dicts)
    @return: dict / list / whatever input is
    """
    if not (isinstance(a, dict) and isinstance(b, dict)):
        if isinstance(a, list) and isinstance(b, list):
            return [dictdiff(v1, v2, searchAttrs) for v1, v2 in izip_destination(a, b, searchAttrs)]
        return b
    res = OrderedDict()
    if izipDestinationMatching in b:
        keepKey = b[izipDestinationMatching].attr
        del b[izipDestinationMatching]
    else:
        keepKey = izipDestinationMatching
    for key in sorted(set(a.keys() + b.keys())):
        v1 = a.get(key, None)
        v2 = b.get(key, None)
        if keepKey == key or v1 != v2: res[key] = dictdiff(v1, v2, searchAttrs)
    if len(res) <= 1: res = dict(res)  # This is only here for pretty print (OrderedDict doesn't pprint nicely)
    return res


def dictmerge(a, b, searchAttrs=[]):
    """
    Returns a dictionary which merges differences recorded in b to base dictionary a
    Also processes list values where the resulting list size will match that of a
    It can also search said list items (that are dicts) for identity values to detect changed positions
    @param a: original dict
    @param b: diff dict to patch into a
    @param searchAttrs: list of strings (keys to search for in sub-dicts)
    @return: dict / list / whatever input is
    """
    if not (isinstance(a, dict) and isinstance(b, dict)):
        if isinstance(a, list) and isinstance(b, list):
            return [dictmerge(v1, v2, searchAttrs) for v1, v2 in izip_destination(a, b, searchAttrs, False)]
        return b
    res = OrderedDict()
    for key in sorted(set(a.keys() + b.keys())):
        v1 = a.get(key, None)
        v2 = b.get(key, None)
        #print "processing", key, v1, v2, key not in b, dictmerge(v1, v2)
        if v2 is not None: res[key] = dictmerge(v1, v2, searchAttrs)
        elif key not in b: res[key] = v1
    if len(res) <= 1: res = dict(res)  # This is only here for pretty print (OrderedDict doesn't pprint nicely)
    return res
