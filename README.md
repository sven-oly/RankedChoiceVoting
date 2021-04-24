# RankedChoiceVoting
A simulation for voting using ranked choice with multiple candidates and multiple elected posts. Based on information at this site: https://www.fairvote.org/how_rcv_works

This runs with python3 rcv.py.

Optional command line parameters include
* number of candidates
* number of voters
* number of positions to be filled

Another option paramter 'test' may be included which sets a specific random number seed for reproducing a configuration.

Example:
  python3 rcv.py 6 2500 3

creates 6 candidates for 3 positions. 2500 voters are simulated.

Note: candidates and voters are generated with a "liberality" value. This uses normal distributions to label each candidate and voter. Each voter choose rankings for candidates based on the distance between the candidate's liberality and that of the voter.
