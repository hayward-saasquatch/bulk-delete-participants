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
doNotTrack = ''

if args.apiKey: apiKey = args.apiKey
if args.tenantAlias: tenantAlias = args.tenantAlias
if args.method: APIMethod = args.method
if args.doNotTrack: doNotTrack = args.doNotTrack
if args.inputFile: inputFile = args.inputFile
else:
    rootdir = '.'

#TODO: create an output file as a inputfilename_errors.csv
tempOutputFile = inputFile.rstrip(".csv")
outputFile = tempOutputFile + "_errors.csv"

fileNameCount = 2

while True:
    print(outputFile)
    if not os.path.isfile(outputFile):
        break
    else:
        outputFile = tempOutputFile + "_errors_" + str(fileNameCount) + ".csv"
        fileNameCount += 1



cleanDir = re.compile(r"[./]")

importErrors = []

def sendDelete(accountId, userId, thisUserdoNotTrack=False):

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
    return None


#add users to a list of participants that were unable to be deleted
def markDeleted(row, response):
    #if there are already entries in the dictionary
    #if importErrors:
    tempErrDict = {}
    tempErrDict = {"id": row['id'], "accountId": row['accountId'], "error": str(response)}
    importErrors.append(tempErrDict)
        #print("a")

    #if the dictionary is still empty
    # else:
    #     importErrors.append({"id": row['id'], "accountId": row['accountId'], "error": response})


    #print(importErrors)


def main():

    try:
        #read in the list of participants to be deleted
        with open(inputFile, newline='') as f:
            #reader = csv.reader(f)
            # for row in reader:
            #     print(row)

            reader = csv.DictReader(f)

            #print(reader)

            for row in reader:
                print(row['id'], row['firstName'])

                #print(row)

                #try:
                print("Deleting participant - accountId:`{}` userId:`{}`".format(row['accountId'], row['id']))

                if doNotTrack == "all":
                    response = sendDelete(row['accountId'], row['id'], True)
                elif row['doNotTrack'] == "true" or row['doNotTrack'] == "TRUE" and doNotTrack == "file":
                    response = sendDelete(row['accountId'], row['id'], True)
                else:
                    response = sendDelete(row['accountId'], row['id'])

                #TODO: pass back the HTTP error to include in the output

                #print(type(response))
                #if type(response) == "JSON":


                #means there was an error and the usr was unable to be deleted 'requests.exceptions.HTTPError' etc
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
            for row in importErrors:
               writer.writerow(row)

    except IOError:
        print("Could not read file:", inputFile)


if __name__ == '__main__':
  main()
