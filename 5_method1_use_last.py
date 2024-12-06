# Read DOIs from `data/metadata.json`
# write results in Compare.tsv
import json
import time
import datetime
import sys
import os
import Levenshtein
import html
import re

from unidecode import unidecode


###
# Go through a tei XML file
# Returns the nb of references and the raw last ref as a string
def Count_Bib_entries_XML(XMLFile):
    f = open(XMLFile, "r")
    Nb = 0; State="OUT"; Last = ""
    for line in f:
        if ("<listBibl" in line):
            State="IN_Bib";
        elif (State=="IN_Bib" and "<biblStruct" in line):
            Nb=Nb+1; State="IN_Rec"
        elif (State=="IN_Rec" and "type=\"raw_reference\"" in line):
            State="IN_Bib"; Last = line.strip().replace("<note type=\"raw_reference\">","").replace("</note>","")
        elif ("</listBibl" in line):
            State="OUT";
            #print("########## \n\n LAST : \n"+Last+"\n\n#########\n")
    return Nb, Last

###
# Go through the list of reference of a doi.
# Try to find the 'Last' raw ref in this list.
# The remaining ref could be considered as sneaked in.
def ParseJson(DOI,Last):
    Sneaked=[]; Sneaked_After_Last=[]; State="Before_Last"; date=""
    try:
        metadata = DOI
        dateC=metadata['created']['date-time']
        dateD=metadata['deposited']['date-time']
        if 'reference' not in metadata.keys():
            #print(" Problematic Json: '"+str(metadata)+"' has no 'reference'")
            return "No reference in Json","",dateC,dateD,State
        else:
            # All ref after last are suspect, all the ones
            for i in metadata['reference']:
                if 'unstructured' in i.keys():
                    json_ref = i['unstructured']
                else:
                    json_ref=""
                S1 = re.sub(' +','',unidecode(json_ref.strip()))
                S2 = re.sub(' +','',unidecode(html.unescape(Last).strip()))
                d=Levenshtein.distance(S2, S1)
                if (d<10):
                    Sneaked=[]; Sneaked_After_Last=[]; State="After_Last";
                elif State=="After_Last":
                    if 'DOI' in i.keys():
                        if '10.38124' in i['DOI']:
                            Sneaked.append(i['DOI'])
                        else:
                            Sneaked_After_Last.append("Suspect: "+i['DOI'])
                    elif 'unstructured' in i.keys():
                        Sneaked_After_Last.append("Suspect no DOI:"+i['unstructured'])
                    else:
                        Sneaked_After_Last.append("Suspect :")
            if Sneaked==[] and State!="After_Last":
                # This happen when Last=[] (empty XML) Or Last not in Json. In both case Grobid did fail in extracting correctly the last ref from PDF
                # Going backward because no Last was found in XML
                State="BF_L"
                for i in reversed(metadata['reference']):
                    if 'DOI' in i.keys() and State=="BF_L":
                            if '10.38124' in i['DOI']:
                                Sneaked.append(i['DOI'])
                            else:
                                State="AF_L"
                    else:
                        State="AF_L"
    except json.decoder.JSONDecodeError:
        print("Pb when reading Json file \o/")
        print("Most probably DOI could not be resolved '"+doi+"' is not a Json file")
        return "Not a Json file","","","",State
    return Sneaked,Sneaked_After_Last,dateC,dateD,State

if __name__ == '__main__':
    # Read the list of DOI
    
    data = []
    with open("data/metadata.json", "r") as f:
        data = json.load(f)
    print("Meta loaded")

    # output a 4 columns file, for each DOI the ref count in crossref, in xml and diff
    f = open("data/results_method1.tsv", "w")
    ft = open("data/method1_time.tsv", "w")
    ft.write("Cited \t Date from (Citing Paper) \t Date To (Cited Paper)\n")
    print(str(sys.argv),file=f)
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),file=f)
    f.write("DOI \t created Date \t deposited \t Crossref ReferencesNbr \t XML ReferencesNbr \t Diff \t Nb Sneaked \t Nb Sneaked List \t Nb Other After Last \t Other After Last List \t Raw Last \t State\n")
    H_Count={}
    
    for i, item in enumerate(data):
        doi = item["DOI"]
        NB_Crossreff = item["reference-count"]
        #print("i:"+str(i)+ " -- DOI:"+str(doi)+" -- ref count:"+str(NB_Crossreff)+" \n")

        if os.path.isfile("data/grobid/"+str(i)+".xml"):
            #print("data/grobid/"+str(i)+".xml")
            #Parse XML
            NB_XML,Last = Count_Bib_entries_XML("data/grobid/"+str(i)+".xml")
        else:
            #print("No xml file for: data/grobid/"+str(i)+" -> "+doi+" has nos ref")
            NB_XML=0; Last=""
                
        #Parse Json
        Sneaked_List, Others_After_Last, dateC, dateD, State = ParseJson(item,Last)
        if not isinstance(Sneaked_List, str):
            Nb_Sneaked = len(Sneaked_List)
        else:
            Nb_Sneaked = 0
       # print("NB_Cro: "+str(NB_Crossreff))
       # print("NB_XML: "+str(NB_XML))
        Diff = NB_Crossreff-NB_XML
       # print("Diff  : "+str(Diff))
        rDOI = doi;
        f.write(rDOI + "\t" +dateC+ "\t" +dateD +"\t"+ str(NB_Crossreff) + "\t" + str(NB_XML) + "\t" + str(Diff) + "\t" + str(Nb_Sneaked) + "\t" + str(Sneaked_List)  + "\t"+ str(len(Others_After_Last)) + "\t" + str(Others_After_Last).replace("\\'","") + "\t"+ Last.replace('#','-') + "\t"+ State + "\n")
        #print("Sneaked: "+str(len(Sneaked_List))+"\n"+str(Sneaked_List))
        #print("\n\n ########################## \n\n")
        
        if not isinstance(Sneaked_List, str):
            for s in Sneaked_List:
                if s.lower() in H_Count.keys():
                    H_Count[s.lower()]=H_Count[s.lower()]+1
                else:
                    H_Count[s.lower()]=1
                metadata=""
                for j in data:
                    if j['DOI']==s:
                        metadata = j
                if metadata!="":
                    dateto=metadata['created']['date-time']
                    ft.write(s.lower()+"\t"+dateC+" \t "+dateto+"\n")
                    #print(s.lower() +"\t"+dateC+" \t "+dateto)
                else:
                    ft.write(s.lower() +"\t"+dateC+" \t NA\n")
                    #print(s.lower() +"\t"+dateC+" \t NA")
    f.close()
    ft.close()
        
    f = open("data/method1_benefit.tsv", "w")
    f.write("DOI \t created Date \t Nb Undue Citations \n")
    Sorted_Sneaked = sorted(H_Count.items(), key=lambda x: x[1], reverse=True)
    for s in Sorted_Sneaked:
        DOI = s[0]
        metadata=""
        for j in data:
            if j['DOI']==DOI:
                metadata = j
        if metadata!="":
            date=metadata['created']['date-time']
            f.write(str(s[0])+" \t "+date+"\t"+str(s[1])+"\n")
            #print(str(s[0])+" : "+str(s[1]))
        else:
            f.write(str(s[0])+" \t NA \t"+str(s[1])+"\n")
    
