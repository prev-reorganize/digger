#! /usr/bin/env python3
# -*- coding: utf-8 -*-
########    #######    ########    #######    ########    ########
##     / / / /    License    \ \ \ \ 
##    Copyleft culture, Copyright (C) is prohibited here
##    This work is licensed under a CC BY-SA 4.0
##    Creative Commons Attribution-ShareAlike 4.0 License
##    Refer to the http://creativecommons.org/licenses/by-sa/4.0/
########    #######    ########    #######    ########    ########
##    / / / /    Code Climate    \ \ \ \ 
##    Language = python3
##    Indent = space;    2 chars;
########    #######    ########    #######    ########    ########

## ## ## ## ## python 3 only ## ## ## ## ## 

### SYS
import sys
import argparse
import importlib
import hashlib
import gc
from os import listdir, path
from collections import OrderedDict
###

### LOCAL
from  lib.func import get_runPath, dumpInits
import lib.static
###

### ACTIONS
#S - Sentence, F - Facts, A - Annotation, AS - Annotation Schema, ES - ElasticSearch

actionsArray = ['digS', 'digF', 'sendF', 'convF2A', 'digA', 'digAS']
actions = OrderedDict()
actions['digS']    = {'digS':1}
actions['digF']    = {**actions['digS'], 'digF':2}
actions['sendF']   = {**actions['digF'], 'convF2ES':3, 'esSend':4}
actions['convF2A'] = {**actions['digF'], 'annotateAsDigestXML':3}
actions['digA']    = ['extractM']
actions['digAS']   = ['extractAnnSchema']

actions

digA_modes = ['all','my', 'by']
digA_by_modes = ['author','scheme','viewpoint', 'date']

digS_modes = ['simple', 'semantic']
preAction = ['cp', 'genPDF', 'download'] 
###


### Pre-Actions
p = argparse.ArgumentParser(description='Digger')
gc.enable()
dirIsTemplate = {"_tmpl"}
###

### Argument constructor
if not sys.argv[1]:
  p.add_argument('--action', dest="action", type=str, required=True, help='Digger action', choices=actionsArray)
else:
  action = sys.argv[1]
p.add_argument('action', choices=actionsArray)    
p.add_argument('-s', dest="src",  type=str, required=True, help='Source to dig')

p.add_argument('--debug', dest="debug",  action='store_true', default=0, help='Debug mode')
args = p.parse_known_args()[0]
session = lib.static.session()
session['srcHash'] = hashlib.sha1(args.src.encode('utf-8')).hexdigest()

### Source choose
if path.isfile(args.src) and args.src.endswith('.pdf'):
  session['preAction'] = 'cp'  
  session['srcType'] = 'file'
  session['docFilename'] = path.basename(args.src)
  
elif path.isfile(args.src) and (args.src.endswith('.doc') or args.src.endswith('.docx')):
  session['preAction'] = 'genPDF'
  session['srcType'] = 'file'
  session['docFilename'] = path.basename(args.src)  
else:
  from urllib.parse import urlparse
  url = urlparse(args.src)
  if (url.scheme == 'http' or url.scheme == 'https') and len(url.netloc) > 1 and url.path.endswith('.pdf'):
    session['preAction'] = 'download'
    session['srcType'] = 'url'
    session['docFilename'] = path.basename(url.path)
    
  elif (url.scheme == 'http' or url.scheme == 'https') and len(url.netloc) > 1:
    session['preAction'] = 'genPDF'
    session['srcType'] = 'url'
    
  elif args.src == 'telegram':
    print('Boilerplate for' + args.src)
  ##
if 'preAction' in session:
  from  lib.preaction import preaction
  if args.debug == 1: dumpInits(args, session, '### before preAction')  
  preaction(args, session)
  if args.debug == 1: dumpInits(args, session, '### after preAction')  
###

### Action-dependent args
if 'digS' in actions[args.action]:
  p.add_argument('--repdfreader', dest="repdfreader", action='store_true', default=0, help='Recreate a pdf_dig pdfreader structure if cached')
  p.add_argument('--resentence',  dest="resentence",  action='store_true', default=0, help='Recreate a pdf_dig sentence structure if cached')

if 'digF' in actions[args.action]:
  p.add_argument('--refacts', dest="refacts", action='store_true', default=0, help='Recreate a facts structure if cached')  
  p.add_argument('--cognitions', dest="cognitions", type=str, help='Cognitions to dig')
  args = p.parse_known_args()[0]

  if str(args.cognitions) == 'None':
    session['cognitions'] = [x for x in listdir(get_runPath() + "/../cognitions/") if x not in dirIsTemplate]
  else:
    session['cognitions'] = args.cognitions.split()    

if 'sendF' in actions[args.action]:
  p.add_argument('--es_host', dest="refacts", type=str, required=True, default=0, help='ES hostname') 
  
###

### TO DO
p.add_argument('--annselftest', dest="annselftest", action='store_true', default=0, help='Create annotation for reader self-test')
  #p.add_argument('--expdf', dest="exPDF", type=int, default=1, help='Export annotations to PDF')
  #p.add_argument('--exes', dest="exES", type=int, default=1, help='Export annotations to ES')    
###

### Call digger
args = p.parse_args()
for action in actions[args.action]:
  diggerAction = importlib.import_module('lib.action_' + action) #.lower()
  diggerAction.init(args,session)
###
