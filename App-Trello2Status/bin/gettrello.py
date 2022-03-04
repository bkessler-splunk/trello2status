import requests
import json
import collections
import splunk.Intersplunk as si
import time
import re
import sys
from splunk import rest
import splunk.entity as entity

# The script itself is considered sys.argv[0] so we use sys.argv[1] to identify the user argument to the command.
# We're going to take the user argument and pass it as the desired URI segment to the Git API
def debug(str):
    results=[]
    row={}
    row["_time"]=time.time()
    row["source"]="DEBUG"
    row["sourcetype"]="DEBUG"
    row["host"]="DEBUG"
    row["_raw"]=str
    results.append(row)
    si.outputStreamResults(results)

args={}
api_token = "MISSING"
api_key = "MISSING"
creds="MISSING"

for arg in sys.argv[1:]:
    args[arg.split("=")[0].lower()]=arg.split("=")[1]
# TODO: Make it default to command and to creds

api_token = args['token'] if 'token' in args.keys() else "MISSING"
api_key = args['key'] if 'key' in args.keys() else "MISSING"
command = args['command'].lower() if 'command' in args.keys() else "cards"
creds = args['creds'].lower() if 'creds' in args.keys() else "MISSING"


if api_token=="MISSING" or api_key=="MISSING":
    if creds!="MISSING":
        creds=args['creds'].lower()
    else:
        creds="default"
    auth={}
    with open("../local/trello.conf", 'r') as f:
        lines = f.read().splitlines()
        for i in range (0,len(lines)):
            if lines[i].startswith('#'):
                lines[i]=""
        while("" in lines) :
            lines.remove("")
        for i in range (0,len(lines)):
            if creds in lines[i]:
                auth[lines[i+1].split("=")[0]]=lines[i+1].split("=")[1]
                auth[lines[i+2].split("=")[0]]=lines[i+2].split("=")[1]
                break
    if 'api_token' in auth.keys():
        api_token=auth['api_token']

    if 'api_key' in auth.keys():
        api_key=auth['api_key']


# here we set up our function to actually perform the API call, return events and stream them to Splunk
def getdata(api_token,api_key,command):
    url = "https://api.trello.com/1/"
    pw = "key="+api_key+"&token="+api_token
    b_json = restget(url + "members/me/boards?"+pw)
    #b_json = convert(b_json)
    if command=='boards':
        operation={"funct":dump,"run":url+"boards/_BID_?fields=all&"+pw,"source":"Trello:Boards:Details"}
    elif command=='cards':
        operation={"funct":cycledump,"run":url+"boards/_BID_/cards?board=1&fields=all&actions=all&"+pw,"source":"Trello:Boards:Cards"}
    elif command=='labels':
        operation={"funct":cycledump,"run":url+"boards/_BID_/labels?fields=all&"+pw,"source":"Trello:Boards:Labels"}
    elif command=='memberships':
        operation={"funct":cycledump,"run":url+"boards/_BID_/memberships?fields=all&"+pw,"source":"Trello:Boards:Membership"}
    elif command=='members':
        operation={"funct":cycledump,"run":url+"boards/_BID_/members?fields=all&"+pw,"source":"Trello:Boards:Members"}
    elif command=='actions':
        operation={"funct":cycledump,"run":url+"boards/_BID_/actions?fields=all&"+pw,"source":"Trello:Boards:Actions"}
    elif command=='lists':
        operation={"funct":cycledump,"run":url+"boards/_BID_/lists?fields=all&"+pw,"source":"Trello:Boards:Lists"}
    elif command=='custom':
        operation={"funct":cycledump,"run":url+"boards/_BID_/customFields?fields=all&"+pw,"source":"Trello:Boards:CustomFields"}
    elif command=='plugins':
        operation={"funct":cycledump,"run":url+"boards/_BID_/plugins?fields=all&"+pw,"source":"Trello:Boards:Plugins"}
    elif command=='checklists':
        operation={"funct":cycledump,"run":url+"boards/_BID_/checklists?fields=all&"+pw,"source":"Trello:Boards:Checklists"}
    else:
        debug("Command Failure")
        sys.exit()


    for bid in b_json:
        si.outputStreamResults(operation["funct"](operation["run"].replace("_BID_",bid["id"]),operation["source"],bid["name"]))
        #operation["funct"](operation["run"].replace("_BID_",bid["id"]),operation["source"],bid["name"])

def dump(run,source,boardname):
    results=[]
    results.append(process(restget(run),source, boardname))
    return results
def cycledump(run,source,boardname):
    results=[]
    l_json=restget(run)
    #debug(run)
    if source=="Trello:Boards:Cards":
        lists=restget(run.replace("cards", "lists", 1))
    for cid in l_json:

        cid['boardname']=boardname
        if source=="Trello:Boards:Cards":
            for lid in lists:
                if lid['id'] == cid['idList']:
                    cid['listname']=lid['name']
                    break
        results.append(process(cid,source, boardname))

    return results
def restget(run):
    try:
        response = requests.get(url=run,headers=None, verify=False, timeout=None)
        if response.status_code>299 or response.status_code<200:
            debug("HTTP Failure: url="+run+" status="+str(response.status_code))
            sys.exit()
            return 0
        l_json = response.json()
    except:
        debug("REST Failure: url="+run)
        sys.exit()
        return 0
    return l_json



def spitdict(k,v,r):
    for i,j in v.items():
        if isinstance(j,dict):
            spitdict(k+"."+i,j,r)
        elif isinstance(j,list):
            spitlist(k+"."+i,j,r)
        else:
            spitstr(k+"."+i,j,r)

def spitlist(k,v,r):
    if len(v)==0:
        spitstr(k,v,r)
        return
    for i in v:
        if isinstance(i,dict):
            spitdict(k,i,r)
        elif isinstance(i,list):
            spitlist(k,i,r)
        else:
            spitstr(k,i,r)

def spitstr(k,v,r):
    k=k.replace("base.","")
    if k not in r:
        r[k] = str(v)
    elif isinstance(r[k], list):
        r[k].append(str(v))
    else:
        r[k] = [r[k], str(v)]


def process(l_json, source, boardname):
    try:
        row={}
        row["_time"]=time.time()
        row["source"]=source
        row["sourcetype"]="Trello:Data"
        row["host"]=boardname
        row["_raw"]=json.dumps(l_json)
        spitdict("base",l_json,row)
        return row
    except:
        debug("JSON Unpack Failure: board="+boardname+" source="+source)
        sys.exit()
# begin with endpoint being our user given argument


getdata(api_token,api_key, command)
