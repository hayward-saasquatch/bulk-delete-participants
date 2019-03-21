# Bulk Delete Participants

Script for bulk deleting participants in a SaaSquatch project

### Usage
*Please note:* Make sure to run this script from within the python virtual environment outlined below.

`python3 deleteUsers.py -t test_alu125hh1si9w -a TEST_BHASKh5125Las5hL125oh3VbLmPxUSs -i User_Delete_Example.csv -d all`

#### Options:
- `-t`,`--tenantAlias`: The tenant alias to use. Required.
- `-a`,`--apiKey`: The API key for the tenant. Required.
- `-i`, `--inputFile`: The file containing the list of participants to delete. Required.
- `-m`,`--method`: the delete API method to use (account or user). Defaults to account.
- `-d`,`--doNotTrack`: configuration for whether or not to block the users from being tracked again. Options are `all` to mark true for all (overriding in-file preferences) or only mark true when included as true in the file as `doNotTrack` column. Defaults to false.

### Setup
The following steps outline how to setup a linux system to run this script (based on the information outlined in [this](https://docs.python-guide.org/dev/virtualenvs/#lower-level-virtualenv) guide)

1. Install Python 3.6+. For debian-based systems: `sudo apt-get install python3.6`
2. Install virtualenv to create an isolated python environment to run this script in `pip install virtualenv`
3. From the top level of the project folder, create a new virtual environment `virtualenv -p /usr/bin/python3.6 venv`. This example assumes the version of python you install was 3.6, so please plug in the version of python you used in step 1.
4. Activate your new virutal environment: `source venv/bin/activate`
5. Install the python packages you will need to run this script `pip install -r requirements.txt`