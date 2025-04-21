import os
from openai import OpenAI
import argparse
import math
import json
import pandas
import openpyxl
import re
import ast
from pydantic import BaseModel
from timeit import default_timer as timer

# Refer below for the API Base; Any one in the Openshift should be able to invoke the API
client = OpenAI(api_key="API Key", base_url="http://172.30.232.180:8000/v1")

def title_summary_generator(acn,prompt, args):
    ''' 
       Get the Prompt and provide the title and abstract
       This function calls another function
       This function is all the integrator should be using
       I could have used the response API but had some challenges
    '''
    prompt.replace("[",'')
    prompt.replace("]",'')
    prompt.replace("{",'')
    prompt.replace("}",'')
    def single_request():
        ''' Tweak the assistant as needed
            have not changed the model parameters as the default one performs well
        '''
        model=args
        start = timer()
        completion = client.chat.completions.create(
            model = model,
            messages=[
                {"role": "assistant","content": " Generate Title and Abstract for the input; Generate output in strict json format without nesting; json attribute names will be title and abstract"},
                {
                    "role": "user",
                    "content":   prompt
                }
            ],
        )
        start_pattern="{"
        end_pattern="}"
        pattern =  start_pattern + r'(.*?)' + end_pattern

        # Find all matches using the regex pattern
        matches = re.findall(pattern, completion.choices[0].message.content, re.DOTALL)
        patstr="\n{" +''.join(matches)+"\n}"
        try:
            jsondata = json.loads(patstr)
        except Exception as e:
            return {}
        return jsondata
    jsond = single_request()
    return jsond


def xstr(s):
    '''
       single liner to convert any nonstring to string
    '''
    return '' if s is None else str(s)

def main():
    # Input provided
    asrwb = openpyxl.load_workbook('asr_input.xlsx')
    asrsh = asrwb['Source Data']
    # Model that be used for the accelerator made available
    models = "meta/llama-3.1-8b-instruct"
    acn,column_values_narrative1,column_values_narrative2 = [cell.value for cell in asrsh['A']],[cell.value for cell in asrsh['DR']],[cell.value for cell in asrsh['DT']]
    i=0
    while i < (len(acn)-1):
      i +=1
      acnseq=acn[i]
      #if acnseq == 1: # Debug purposes only
      if acnseq != None: # Skip empty excel lines
         prompt=xstr(column_values_narrative1[i])+xstr(column_values_narrative2[i])
         if prompt =="":
            continue
         jsond=title_summary_generator(acnseq,prompt,models) 
         jsond["acn"]=acnseq
         jsond.setdefault('title',"None Given")
         jsond.setdefault('abstract',"None Given")
         pretty_json = json.dumps(jsond, indent=4)
         print(pretty_json)

if __name__ == "__main__":
    main()

