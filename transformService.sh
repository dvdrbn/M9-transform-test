#!/bin/sh
json=$1
url='https://us-east-1.model9api.io/transform'
export PATH=/usr/bin:/bin
export _EDC_ADD_ERRNO2=1
cnvto="$(locale time-codeset)"
headers="Content-Type:application/json"
echo "Running Model9 transform service"
output=$(curl -H "$headers" -s -k -X POST --data "$json" $url)
if ! [ -z "$output" ]; then
   echo "Transform ended with the following output:"   
   # If the answer is in ASCII then convert to EBCDIC            
   firstChar=$(echo $output | cut -c1)                           
   if [ "$firstChar" = "#" ]; then                               
      convOutput="$(echo $output | iconv -f ISO8859-1 -t $cnvto)"
   else                                                          
      convOutput=$output                                         
   fi                                                            
   echo "$convOutput"                                            
fi
status=$(echo $convOutput | tr -s " " | cut -d, -f1 | cut -d" " -f3)
   echo "Transform ended with status: $status"
if [ "$status" = '"OK"' ];then
   exit 0
else if [ "$status" = '"WARNING"' ]; then
   exit 4
else
   exit 8
fi
fi