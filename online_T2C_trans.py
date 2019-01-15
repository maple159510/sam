import re
import os


def translation_selection(cword,candidate_list):
    twcandidate=[]
    best_count=0
    best_translation=""
    twcandidate=re.split(r'/',candidate_list)
    for tword in twcandidate:
        tword_count=word_count(cword,tword)
        
        if(tword_count>=best_count):
            best_count=tword_count
            best_translation=tword                 
    return best_translation
   
def word_count(cword,tword):
    count=0
    #with open('output/all_tn_tl.trn','r',encoding='UTF-8-sig') as textfile:
    #for line in textfile:
    for line in open('all_tn_tl.trn', 'r', encoding='UTF-8'):
        tn_sequence=re.split(':',line)[0]
        cn_sequence=re.split(':',line)[2]
        if ((cword in cn_sequence) and (tword in tn_sequence)):
            count=count+1
            #print(cn_sequence,":",tn_sequence)
    #print(tword+':'+str(count))
    #textfile.close()
    return count

    
def t2c_trans(sentence):
    CN2TW_dict={}

    #sentence=input("請輸入句子:")
    cn_list=[]


    for line in open('medical_t2c_dict.txt', 'r', encoding='UTF-8'):
        #print(line)
        value,cn_key,lr=re.split(r'/|\n',line)
        if(cn_key in CN2TW_dict.keys()):
            CN2TW_dict[cn_key]=CN2TW_dict[cn_key]+'/'+value
        else:
            CN2TW_dict[cn_key]=value



    new_sentence=sentence + "。。。"
    i=0
    tl_sentence=''
    while(i<len(new_sentence)-3):
        gram4=new_sentence[i]+new_sentence[i+1]+new_sentence[i+2]+new_sentence[i+3]
        gram3=new_sentence[i]+new_sentence[i+1]+new_sentence[i+2]
        gram2=new_sentence[i]+new_sentence[i+1]
        gram1=new_sentence[i]
        if (gram4 in CN2TW_dict.keys()):
            i = i+4
            #print(gram4,":",CN2TW_dict[gram4])
            tl_sentence=tl_sentence+translation_selection(gram4,CN2TW_dict[gram4])
        elif (gram3 in CN2TW_dict.keys()):
            i=i+3
            #print(gram3,":",CN2TW_dict[gram3])
            tl_sentence=tl_sentence+translation_selection(gram3,CN2TW_dict[gram3])
        elif (gram2 in CN2TW_dict.keys()):
            i=i+2
            #print(gram2,":",CN2TW_dict[gram2])
            tl_sentence=tl_sentence+translation_selection(gram2,CN2TW_dict[gram2])        
        else:
            if (gram1 in CN2TW_dict.keys()):
                #print(gram1,":",CN2TW_dict[gram1])
                tl_sentence=tl_sentence+translation_selection(gram1,CN2TW_dict[gram1])            
            else:
                tl_sentence=tl_sentence + '(' + gram1 + ')'
            i=i+1      
    #print(sentence+":"+tl_sentence)    
    print(tl_sentence,end='\n')
    return tl_sentence

#sentence=input("請輸入句子:")
#t2c_trans(sentence)