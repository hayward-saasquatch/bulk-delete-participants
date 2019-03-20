import sys, argparse, os, re, requests, json, csv
from requests.auth import HTTPBasicAuth
from urllib.error import HTTPError

#parse input arguments
parser = argparse.ArgumentParser()
parser.add_argument('-i','--inputFile', help='The file containing the list of participants to delete', required=True)
parser.add_argument('-t','--tenantAlias', help='The tenant alias to use', required=True)
parser.add_argument('-a','--apiKey', help='the API key for the tenant', required=True)
parser.add_argument('-m','--method', help='the delete API method to use', choices=['account','user'])
parser.add_argument('-d','--doNotTrack', help='configuration for whether or not to block the users from being tracked again. Options are `all` to mark true for all (overriding in-file preferences) or only mark true when included as true in the file as `doNotTrack` column', choices=['all','file'])
args = parser.parse_args()

#default to deleting the full account
APIMethod = "account"
#set the default option for which do nottrack config to what is in the file
doNotTrack = 'file'

if args.apiKey: apiKey = args.apiKey
if args.tenantAlias: tenantAlias = args.tenantAlias
if args.method: APIMethod = args.method
if args.doNotTrack: doNotTrack = args.doNotTrack
if args.inputFile: inputFile = args.inputFile
else:
    rootdir = '.'

# create an output file as a inputfilename_errors.csv
tempOutputFile = inputFile.rstrip(".csv")
outputFile = tempOutputFile + "_errors.csv"

# set the default for what number to add to the output file name if the default value is already taken
fileNameCount = 2

# loop through till a file name is found for 
while True:
    print(outputFile)
    
    # if the selected filename doesnt already exist, then we have our output file name and can exit this loop
    if not os.path.isfile(outputFile):
        break
    # if the file name is already taken, add the next number to the end of the name, and loop back through
    else:
        outputFile = tempOutputFile + "_errors_" + str(fileNameCount) + ".csv"
        fileNameCount += 1

cleanDir = re.compile(r"[./]")

# initially empty list of user deletion errors
deletionErrors = []

# function for making the request to saasquatch to delete the user. Default value for do not track (if not passed in) is false
def sendDelete(accountId, userId, thisUserdoNotTrack=False):
    
    # configure which endpoint to use (whether to delete just the user, or the user and the underlying account)
    if APIMethod == "user":
        url = 'https://app.referralsaasquatch.com/api/v1/'+ tenantAlias +'/open/account/'+ accountId +'/user/' + userId
    else:
        url = 'https://app.referralsaasquatch.com/api/v1/'+ tenantAlias +'/open/account/'+ accountId

    #if the user has been marked to not be tracked
    if thisUserdoNotTrack:
        url += "?doNotTrack=true"
        print("adding `doNotTrack` to query")

    headers = {'Content-Type' : 'application/json'}

    response = None
    try:
        response = requests.delete(url, auth=('', apiKey), headers = headers)
        #if r.status_code != requests.codes.ok:

        print(type(response))
        print(response)
        #print(response.json())
        response.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        print ("Http Error:",errh)
        return errh
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:",errc)
        return errc
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:",errt)
        return errt
    except requests.exceptions.RequestException as err:
        print ("OOps: Something Else",err)
        return err

        #print("Unable to delete participant: {}".format(e))

    # except:
    #     print("Unexpected error:", sys.exc_info()[0])
    
    # if there were no errors, return None
    return None


# add users to a list of participants that were unable to be deleted
def markDeleted(row, response):
    #if there are already entries in the dictionary
    #if deletionErrors:
    tempErrDict = {}
    tempErrDict = {"id": row['id'], "accountId": row['accountId'], "error": str(response)}
    
    # append the entry for the participant that was unable to be deleted to the list 
    deletionErrors.append(tempErrDict)

def main():

    try:
        #read in the list of participants to be deleted
        with open(inputFile, newline='') as f:
            #reader = csv.reader(f)
            # for row in reader:
            #     print(row)

            reader = csv.DictReader(f)

            #print(reader)
            
            # look through each entry in the file of participants to delete
            for row in reader:
                #print(row['id'], row['firstName'])

                #print(row)

                #try:
                print("Deleting participant - accountId:`{}` userId:`{}`".format(row['accountId'], row['id']))

                #TODO: remove reliance on having a `doNotTrack` column
                
                response = None
                
                # if the `doNotTrack` parameter was set when running the script. Override choice in csv and mark all as do not track
                if doNotTrack == "all":
                    response = sendDelete(row['accountId'], row['id'], True)
                
                # if `doNotTrack` is set to take the value from the file (the default if not passed in as an arguement)
                elif doNotTrack == "file":
                    #if row['doNotTrack']: 
                    
                    # check if `doNotTrack` is one of the column headers
                    if 'doNotTrack' in row.keys():
                        
                        # if there is a `doNotTrack` column, and that column one of the values of `True`, `TRUE`, or `true`, then include the do not track flag in the request 
                        if row['doNotTrack'] == "true" or row['doNotTrack'] == "TRUE" or row['doNotTrack'] == "True":
                            response = sendDelete(row['accountId'], row['id'], True)
                    
                    # if there is no `doNotTrack` column, assume the user should not be marked do not track
                    else: response = sendDelete(row['accountId'], row['id'])
                
                # if, somehow, do not track is not set to `all` or `file`, then do not include the flag
                else:
                    response = sendDelete(row['accountId'], row['id'])

                #TODO: pass back the HTTP error to include in the output

                #print(type(response))
                #if type(response) == "JSON":


                # if the response from the `sendDelete` function was not `None`, this means there was an error and the usr was unable to be deleted ('requests.exceptions.HTTPError') etc
                if response:
                    print(response)

                    markDeleted(row, response)

                    print("Unable to delete participant: accountId:`{}` userId:`{}`, adding to error output file".format(row['accountId'], row['id']))

                #else:
                    #print("printing repsponse: ", response)




    except IOError:
        print("Could not read file:", inputFile)


    try:
        #write the list of participants, with errors, that couldn't be deleted
        #with open(outputFile, 'wb', newline='') as f:
            #reader = csv.DictReader(f)

        with open(outputFile, 'w') as csv_file:
            fieldnames = ['id', 'accountId', 'error']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for row in deletionErrors:
               writer.writerow(row)

    except IOError:
        print("Could not write errors to file:", inputFile)


if __name__ == '__main__':
  main()
