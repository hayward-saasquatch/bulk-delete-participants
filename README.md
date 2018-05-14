# Bulk Delete Participants

Script for bulk deleting participants in a SaaSquatch project

### Usage
`python3 deleteUsers.py -t test_alu125hh1si9w -a TEST_BHASKh5125Las5hL125oh3VbLmPxUSs -i User_Delete_Example.csv -d all`

#### Options:
- `-t`,`--tenantAlias`: The tenant alias to use. Required.
- `-a`,`--apiKey`: The API key for the tenant. Required.
- `-i`, `--inputFile`: The file containing the list of participants to delete. Required.
- `-m`,`--method`: the delete API method to use (account or user). Defaults to account.
- `-d`,`--doNotTrack`: configuration for whether or not to block the users from being tracked again. Options are `all` to mark true for all (overriding in-file preferences) or only mark true when included as true in the file as `doNotTrack` column. Defaults to false.
