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
import hashlib
from pathlib import Path
import zipfile

root = "./Parent"
dest = "./dest2"
metadata_folder = "metadata"
csv_folder = "csv_metadata"
dest_CSV = "metadata.csv"
modified_CSV = ""

collection_name = "TWNFT"
extension = "gif"
ipfs_url = "ipfs://<HASH>"

pre_defined = ["tokenId","name","description","image","edition"]

def create_csv():
    headers = []
    for p in pre_defined:
        headers.append(p)
    for file in glob.glob(dest+"/"+metadata_folder+"/*.json"):
        json_ob = json.load(open(file,encoding='utf-8-sig'))
        for i in json_ob["attributes"]:
            headers.append(i["trait_type"])
    headers = list(dict.fromkeys(headers))

    if not os.path.exists(dest+"/"+csv_folder):
        os.makedirs(dest+"/"+csv_folder)
    with open(dest+"/"+csv_folder+"/"+dest_CSV, 'w',newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for file in sorted(glob.glob(dest+"/"+metadata_folder+"/*.json"),  key=lambda x: float(re.findall("(\d+)", x)[0])):
            row = [""] * len(headers)
            json1 = json.load(open(file,encoding='utf-8-sig'))
            row[headers.index("tokenId")] = int(json1["tokenId"])
            row[headers.index("name")] = collection_name + " #"+str(json1["tokenId"])
            row[headers.index("description")] = ""
            row[headers.index("image")] = ""
            row[headers.index("edition")] = ""
            for i in json1["attributes"]:
                trtype = i["trait_type"]
                index = headers.index(trtype)
                row[index] = i["value"]
            writer.writerow(row)
    print("Validating the CSV")
    print("------------------")
    print("* CSV to Json")
    csv_to_metadata(dest+"/"+csv_folder+"/"+dest_CSV)
    print("* Validating Metadata Json Against Parent")
    is_all_good(False)
    print("* Delete Temp metadata.json")
    print("------------------")
    os.remove(dest+"/"+csv_folder+"/metadata.json")

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
                attr["value"] = private_strip(row[headers.index(h)])
                arr.append(attr)
    return arr


def csv_to_metadata(path):
    private_create_folder_if_not(dest+"/"+csv_folder+"/metadata/")
    jsons = []
    attr_hash = []
    with open(path, 'r', encoding='utf-8-sig') as file:
        csvreader = csv.reader(file, delimiter=',')
        headers = next(csvreader, None)
        for row in csvreader:
            map = {}
            for p in pre_defined:
               map[p] = private_strip(row[headers.index(p)])
            map["tokenId"] = int(map["tokenId"])
            map["attributes"] = private_make_attriubte_array(headers,row)
            attr_hash.append(hash_str(json.dumps(private_KMOrder(map["attributes"]))))
            private_ob_file(dest+"/"+csv_folder+"/metadata/"+str(map["tokenId"])+".json",map)
            jsons.append(map)
    if len(set([x for x in attr_hash if attr_hash.count(x) > 1])) > 0:
        sys.exit("ERROR - Two NFTS are Equal ")
    private_ob_file(dest+"/"+csv_folder+"/metadata/metadata.json",jsons)

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

def rootToHashMap():
    all_data = {}
    for file in glob.glob(root+"/*"):
        if os.path.isdir(file):
            jsons = file+"/"+metadata_folder
            for file_2 in glob.glob(jsons+"/*.json"):
                json_ob = json.load(open(file_2))
                key = str(hash_str(json.dumps(private_KMOrder(json_ob["attributes"]))))
                value = hash_file(os.path.splitext(file+"/"+os.path.basename(file_2))[0]+"."+extension)
                all_data[str(key)] = value
    return all_data

def destCSVJsonToHashMap():
    all_data = {}
    for json_ob in json.load(open(dest+"/"+csv_folder+"/metadata.json",encoding='utf-8-sig')):
        key = str(hash_str(json.dumps(private_KMOrder(json_ob["attributes"]))))
        value = hash_file(dest+"/"+json_ob["tokenId"]+"."+extension)
        all_data[str(key)] = value
    return all_data

def destToHashMap():
    all_data = {}
    jsons = dest+"/"+metadata_folder
    for file_2 in glob.glob(jsons+"/*.json"):
        json_ob = json.load(open(file_2, encoding='utf-8-sig'))
        key = str(hash_str(json.dumps(private_KMOrder(json_ob["attributes"]))))
        value = hash_file(os.path.splitext(dest+"/"+os.path.basename(file_2))[0]+"."+extension)
        all_data[str(key)] = value
    return all_data

def updateNFTPath():
    jsons = []
    for json_ob in json.load(open(dest+"/"+csv_folder+"/metadata/metadata.json",encoding='utf-8-sig')):
        id = json_ob["tokenId"]
        del json_ob["tokenId"]
        json_ob["image"] = ipfs_url+"/"+str(id)+"."+extension
        jsons.append(json_ob)
        private_ob_file(dest+"/"+csv_folder+"/metadata/"+str(id)+".json",json_ob)
    private_ob_file(dest+"/"+csv_folder+"/metadata/metadata.json",jsons)


def parent_validation():
    attr_hash = []
    for file in glob.glob(root+"/*"):
        if os.path.isdir(file):
            jsons = file+"/"+metadata_folder
            if not os.path.isdir(jsons):
                sys.exit("Path not found: "+jsons)
            for file_2 in glob.glob(jsons+"/*.json"):
                json_ob = json.load(open(file_2))
                tokenId = json_ob["tokenId"]
                attr_hash.append(hash_str(json.dumps(private_KMOrder(json_ob["attributes"]))))
                nft = file+"/"+str(tokenId)+"."+extension
                if not Path(file_2).stem == str(tokenId):
                    sys.exit("Json file name does not match with the token Id "+file_2)
                if not (os.path.exists(nft)):
                    sys.exit("Please Fix, Path not found: "+nft)    
    if len(set([x for x in attr_hash if attr_hash.count(x) > 1])) > 0:
        sys.exit("ERROR - Two NFTS are Equal ")
    print("Parent Validation Success!!")

def copy():
    private_empty(dest)
    private_create_folder_if_not(dest+"/"+metadata_folder)
    for file in glob.glob(root+"/*"):
        if os.path.isdir(file):
            jsons = file+"/"+metadata_folder
            if os.path.isdir(jsons):
                for file_2 in glob.glob(jsons+"/*.json"):
                    json_ob = json.load(open(file_2))
                    nft = file+"/"+str(json_ob["tokenId"])+"."+extension
                    uid = time.time()
                    new_name = dest+"/"+str(uid)+"."+extension
                    json_ob["tokenId"] = uid
                    shutil.copy(nft, new_name)
                    private_ob_file(dest+"/"+metadata_folder+"/"+str(uid)+".json",json_ob)


def randomize():
    file_count = len(glob.glob1(dest+"/"+metadata_folder, "*.json"))
    arr = []
    for i in range(1, file_count+1):
        arr.append(i)
    random.shuffle(arr)
    for file_2 in glob.glob(dest+"/"+metadata_folder+"/*.json"):
        json_ob = json.load(open(file_2,encoding='utf-8-sig'))
        uid = arr.pop()
        nft = dest+"/"+str(json_ob["tokenId"])+"."+extension
        new_name = dest+"/"+str(uid)+"."+extension
        os.rename(nft, new_name)
        json_ob["tokenId"] = uid
        json_ob["name"] = collection_name+" #" + \
            str(json_ob["tokenId"])  # remove if you have unique name
        private_ob_file(dest+"/"+metadata_folder+"/"+str(uid)+".json",json_ob)
        os.remove(file_2)



def is_all_good(normal = True):
    rH = rootToHashMap()
    private_ob_file("root.json",rH)
    if normal:
        dH = destToHashMap()
        private_ob_file("dest.json",dH)
        if not rH == dH:
            print("---------ERROR-----------")
            print("Diff "+str(len(set(private_concat(rH)) ^ set(private_concat(dH)))/2))
            sys.exit("Validation Failed, Destiantion Collection not match with Root Collection")
    else:
        dCH = destCSVJsonToHashMap()
        private_ob_file("dest_CSV_json.json",dCH)
        if not rH == dCH:
            print("---------ERROR-----------")
            print("Diff "+str(len(set(private_concat(rH)) ^ set(private_concat(dCH)))/2))
            sys.exit("Validation Failed, Destiantion Collection not match with Root Collection")
    print("Yup, All good")

def make_zip(chunk_count):
    arr = []
    for f in sorted(glob.glob(dest+"/*."+extension), key=lambda el: int(Path(el).stem)):
        arr.append(f)
    chunks = private_divide_chunks(arr,chunk_count)
    for files in chunks:
        name = Path(files[0]).stem+"-"+Path(files[len(files)-1]).stem
        print("Creating... "+name+".zip")
        with zipfile.ZipFile(dest+"/"+name+".zip", 'w',zipfile.ZIP_DEFLATED) as zipMe:        
            for file in files:
                zipMe.write(file,arcname= "./"+name+"/"+os.path.basename(file))
        zipMe.close()
        for f1 in files:
            os.remove(f1)
    print("Done Making Zip")

def private_strip(text):
    if not text:
        return ""
    return text.strip() 

def private_divide_chunks(l, n):
	for i in range(0, len(l), n):
		yield l[i:i + n]

def private_empty(path):
    shutil.rmtree(path)
    os.mkdir(path)

def private_KMOrder(attributes) :    
    return sorted(attributes, key=lambda d: d['trait_type'])

def private_concat(list):
    arr = []
    for x,y in list.items():
        arr.append(x+""+y)
    return arr

def private_ob_file(json_path,ob):
    with open(json_path, 'w+',encoding='utf-8-sig') as f:
        json.dump(ob, f, indent=4, ensure_ascii=False)

def private_create_folder_if_not(path):
    if not os.path.exists(path):
        os.makedirs(path)

# print("Script Started!")
# parent_validation()
# print("Coping to Destination")
# copy()
# print("Copy Validation Started")
# is_all_good()
# print("Randomization Started")
# randomize()
# print("Validation Started After Randomization")
# is_all_good()
# print("Creating CSV from Collection")
# create_csv()
# print("CSV to Metadata Json") #do this after editing the original CSV
#csv_to_metadata(dest+"/"+csv_folder+"/final_metadata_no_space.csv")
# print("Metadata Created")
#print("Now zipping collection for upload")
#make_zip(500)
#updateNFTPath()
