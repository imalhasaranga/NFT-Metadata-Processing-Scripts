import glob
import json
import csv
import re
import os
import sys
import json
import hashlib
import time
import shutil
import random
import hashlib # hashlib module

root = "./parent"
dest = "./destination"


collection_name = "TWNFT"
extension = "gif"
pre_defined = ["tokenId","name","description","image","edition"]

def create_csv():
    headers = []
    for p in pre_defined:
        headers.append(p)
    for file in glob.glob(dest+"/metadata/*.json"):
        json_ob = json.load(open(file))
        for i in json_ob["attributes"]:
            headers.append(i["trait_type"])
    headers = list(dict.fromkeys(headers))

    if not os.path.exists(dest+"/csv_metadata"):
        os.makedirs(dest+"/csv_metadata")
    with open(dest+"/csv_metadata/metadata.csv", 'w',newline="",encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for file in sorted(glob.glob(dest+"/metadata/*.json"),  key=lambda x: float(re.findall("(\d+)", x)[0])):
            row = [""] * len(headers)
            json1 = json.load(open(file))
            row[headers.index("tokenId")] = json1["tokenId"]
            row[headers.index("name")] = collection_name + " #"+str(json1["tokenId"])
            row[headers.index("description")] = ""
            row[headers.index("image")] = ""
            row[headers.index("edition")] = ""
            for i in json1["attributes"]:
                trtype = i["trait_type"]
                index = headers.index(trtype)
                row[index] = i["value"]
            writer.writerow(row)

def private_index(arr,index):
    try:
        arr.index(index)
        return True
    except ValueError:
        return False

def private_make_attriubte_array(headers, row):
    arr = []
    for h in headers:
        if not private_index(pre_defined,h):
            if row[headers.index(h)].strip():
                attr = {}
                attr["trait_type"] = h
                attr["value"] = row[headers.index(h)]
                arr.append(attr)
    return arr


def csv_to_metadata():
    jsons = []
    with open(dest+"/csv_metadata/metadata.csv", 'r') as file:
        csvreader = csv.reader(file, delimiter=',')
        headers = next(csvreader, None)
        for row in csvreader:
            map = {}
            for p in pre_defined:
               map[p] = row[headers.index(p)]
            map["attributes"] = private_make_attriubte_array(headers,row)
            jsons.append(map)
    with open(dest+"/csv_metadata/metadata.json", 'w+') as f:
        json.dump(jsons, f, indent=4)

def private_empty(path):
    shutil.rmtree(path)
    os.mkdir(path)


def hash_file(filename):
    # h = hashlib.sha1()
    # with open(filename, 'rb') as file:
    #     chunk = 0
    #     while chunk != b'':
    #         chunk = file.read(1024)
    #         h.update(chunk)
    # return h.hexdigest()
    return str(os.path.getsize(filename))

def hash_str(strx):
    return hashlib.md5(strx.encode("utf-8")).hexdigest()

def private_KMOrder(attributes) :
    return sorted(attributes, key=lambda d: d['trait_type'])

def rootToHashMap():
    all_data = {}
    for file in glob.glob(root+"/*"):
        if os.path.isdir(file):
            jsons = file+"/metadata"
            for file_2 in glob.glob(jsons+"/*.json"):
                json_ob = json.load(open(file_2))
                key = str(hash_str(json.dumps(private_KMOrder(json_ob["attributes"]))))
                value = hash_file(os.path.splitext(file+"/"+os.path.basename(file_2))[0]+"."+extension)
                all_data[str(key)] = value
    return all_data

def destCSVJsonToHashMap():
    all_data = {}
    for json_ob in json.load(open(dest+"/csv_metadata/metadata.json")):
        key = str(hash_str(json.dumps(private_KMOrder(json_ob["attributes"]))))
        value = hash_file(dest+"/"+json_ob["tokenId"]+"."+extension)
        all_data[str(key)] = value
        
    return all_data

def destToHashMap():
    all_data = {}
    jsons = dest+"/metadata"
    for file_2 in glob.glob(jsons+"/*.json"):
        json_ob = json.load(open(file_2))
        key = str(hash_str(private_KMOrder(json.dumps(json_ob["attributes"]))))
        value = hash_file(os.path.splitext(dest+"/"+os.path.basename(file_2))[0]+"."+extension)
        all_data[str(key)] = value
    return all_data


def parent_validation():
    for file in glob.glob(root+"/*"):
        if os.path.isdir(file):
            jsons = file+"/metadata"
            if os.path.isdir(jsons):
                for file_2 in glob.glob(jsons+"/*.json"):
                    json_ob = json.load(open(file_2))
                    tokenId = json_ob["tokenId"]
                    nft = file+"/"+str(tokenId)+"."+extension
                    if not (os.path.exists(nft)):
                        sys.exit("Please Fix, Path not found: "+nft)
            else:
                sys.exit("Path not found: "+jsons)
    print("all Good!")

def copy():
    private_empty(dest)
    if not os.path.exists(dest+"/metadata"):
        os.makedirs(dest+"/metadata")

    for file in glob.glob(root+"/*"):
        if os.path.isdir(file):
            jsons = file+"/metadata"
            if os.path.isdir(jsons):
                for file_2 in glob.glob(jsons+"/*.json"):
                    json_ob = json.load(open(file_2))
                    nft = file+"/"+str(json_ob["tokenId"])+"."+extension
                    uid = time.time_ns()
                    new_name = dest+"/"+str(uid)+"."+extension
                    json_ob["tokenId"] = uid
                    shutil.copy(nft, new_name)
                    with open(dest+"/metadata/"+str(uid)+".json", 'w+') as f:
                        json.dump(json_ob, f, indent=4)


def randomize():
    file_count = len(glob.glob1(dest+"/metadata", "*.json"))
    arr = []
    for i in range(1, file_count+1):
        arr.append(i)
    random.shuffle(arr)
    for file_2 in glob.glob(dest+"/metadata/*.json"):
        json_ob = json.load(open(file_2))
        uid = arr.pop()
        nft = dest+"/"+str(json_ob["tokenId"])+"."+extension
        new_name = dest+"/"+str(uid)+"."+extension
        os.rename(nft, new_name)
        json_ob["tokenId"] = uid
        json_ob["name"] = collection_name+" #" + \
            str(json_ob["tokenId"])  # remove if you have unique name
        with open(dest+"/metadata/"+str(uid)+".json", 'w+') as f:
            json.dump(json_ob, f, indent=4)
        os.remove(file_2)

def private_concat(list):
    arr = []
    for x,y in list.items():
        arr.append(x+""+y)
    return arr

def all_good(normal = True):
    if normal:
        rH = rootToHashMap()
        with open("root.json", 'w+') as f:
            json.dump(rH, f, indent=4)
        dH = destToHashMap()
        with open("dest.json", 'w+') as f:
            json.dump(dH, f, indent=4)
        if not rH == dH:
            print("---------ERROR-----------")
            print("Diff "+str(len(set(private_concat(rH)) ^ set(private_concat(dH)))/2))
            sys.exit("Validation Failed, Destiantion Collection not match with Root Collection")
        else:
            print("Yup, All good")
    else:
        print("Checking final set")
        rH = rootToHashMap()
        with open("root.json", 'w+') as f:
            json.dump(rH, f, indent=4)
        dCH = destCSVJsonToHashMap()
        with open("dest_CSV_json.json", 'w+') as f:
            json.dump(dCH, f, indent=4)
        if not rH == dCH:
            print("---------ERROR-----------")
            print("Diff "+str(len(set(private_concat(rH)) ^ set(private_concat(dCH)))/2))
            sys.exit("Validation Failed, Destiantion Collection not match with Root Collection")
        else:
            print("Yup, All good")



parent_validation()
copy()
print("validation started")
all_good()
print("randomization started")
randomize()
print("validation started after randomization")
all_good()
print("creating csv")
create_csv()
print("csv to metadata")
csv_to_metadata()
print("matadata json against destination validation started")
all_good(False)
