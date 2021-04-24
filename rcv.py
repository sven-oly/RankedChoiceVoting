# Rank Choice Voting simulation
# https://www.fairvote.org/how_rcv_works

import random
import sys

def generateNames(num_samples):
    nums = random.sample(range(1000), k=num_samples)
    return nums

class Candidate():
    def __init__(self, name, index, liberality=0.5):
        self.name = name
        self.index = index
        self.one_votes = 0
        self.liberality = liberality
        self.viable = True
        self.elected = False



def distanceSort(a):
    return a[1]  # The distance from the candidate's position.

class Voter():
    def __init__(self, id, lib_rank):
        self.id = id
        self.liberality = lib_rank;
        self.votes = []

    def genVotes(self, slate):
        # self.genVotesRandom(slate)
        self.genVotesBiasedOnLiberality(slate)

    def genVotesRandom(self, slate):
        # Generate v votes for 0 to num_candidates
        num_candidates = len(slate)
        self.votes = [0] * num_candidates
        # 0 indicates no ranking for this candidate by this voter
        num_votes = random.randint(0, num_candidates)
        # This should use the liberality of the voter and that
        # of the candidate
        votes = random.sample(range(num_candidates), k=num_votes)
        for k in range(len(votes)):
            self.votes[votes[k]] = k + 1

    def genVotesBiasedOnLiberality(self, slate):
        # Generate v votes for 0 to num_candidates
        mu = 0.5
        sigma = 0.2
        max_voter_can_tolerate = 1.0 + random.gauss(mu, sigma)
        num_candidates = len(slate)
        self.votes = [0] * num_candidates
        # 0 indicates no ranking for this candidate by this voter
        num_votes = random.randint(0, num_candidates)
        voter_lib_rank = self.liberality

        # This should use the liberality of the voter and that
        # of the candidate
        distances = []
        for c in slate:
            distance_from_candidate = abs(c.liberality - voter_lib_rank)
            if distance_from_candidate <= max_voter_can_tolerate:
                distances.append((c.index, distance_from_candidate))
        distances.sort(key=distanceSort)
        for k in range(len(distances)):
            self.votes[distances[k][0]] = k + 1

def sortByFirstRank(a):
    return a.one_votes

class TestData():
    def __init__(self):
        self.sim = None

    def setFirstSecondVotes(self, first, seconds):
        voter_index = 0
        for i in range(self.sim.num_candidates):
            num1 = first[i]
            num2 = second[i]
            v = self.sim.voters
            count2 = 0  # How many seconds have been assigned
            index2 = 0
            for j in range(num1):
                v[j].votes = [0] * self.sim.num_candidates
                v[j].votes[i] = 1
                if count2 < num2[index2] and index2 < self.sim.num_candidates:
                    v[j].votes[index2] = 2
                    count2 += 1
                else:
                    index2 += 1
        # TODO: Check if this is correct, and if we need third choices, etc.


    # https://www.fairvote.org/multi_winner_rcv_example
    def rvcSample(self):
        self.sim = RankSim(num_candidates=6, num_voters=9200, num_winners=3)
        names = ["Armando Perez", "Cathy Chan", "Hannah Murphy",
                 'Charles Lorenzo', 'Brad Jackson', 'June Smith']
        for i in range(self.sim.num_candidates):
            self.sim.ccandidates[i].name = names[i]
        # Next, set up first and second votes
        first_votes = [2500, 1750, 1300, 1300, 1350, 1000]
        # Second votes for each candidate for handling excess
        seconds = [[0, 1250, 250, 0, 1000, 0],
                   [640, 0, 1600, 320, 640, 0],
                   [0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0],
                   [0, 1250, 150, 50, 0, 0],
                   [0, 100, 580, 300, 20, 0]]

class RankSim():
    def __init__(self, num_candidates, num_voters, num_winners=1):
        self.num_candidates = num_candidates
        self.num_voters = num_voters
        self.num_winners = num_winners
        self.voters = []
        self.candidates = []
        # Simplifies getting those still in play
        self.active_candidates = set()
        for i in range(self.num_candidates):
            self.active_candidates.add(i)

        self.random_candidates()
        self.random_voters()
        self.genVotes()
        self.checkVotes()
        self.elected_count = 0
        self.total_votes = self.countTotalVoted()
        self.needed_to_win = round(self.total_votes / (self.num_winners + 1))

    def random_candidates(self):
        self.candidates = []
        mu = 1.0
        sigma = 1.0
        names = generateNames(self.num_candidates)
        for i in self.active_candidates:
            lib_rank = random.gauss(mu, sigma)
            c = Candidate('c%04d' % names[i], i, lib_rank)
            self.candidates.append(c)
        return

    def random_voters(self):
        mu = 1.0
        sigma = 1.0
        for i in range(self.num_voters):
            lib_rank = random.gauss(mu, sigma)
            self.voters.append(Voter(i+1, lib_rank))

    def printCandidateInfo(self):
        print('%d candidates running for %d positions' % (self.num_candidates, self.num_winners))
        for i in range(self.num_candidates):
            c = self.candidates[i]
            print('  #%d %4.2f %-20s' % (i, c.liberality, c.name))

    def printLiberalitySummary(self, items, num_slots, label='Unlabeled'):
        min = max = items[0].liberality
        for v in items:
            lib_rank = v.liberality
            if lib_rank < min:
                min = lib_rank
            elif lib_rank > max:
                max = lib_rank
        print ('%s range from %f to %f' % (label, min, max))
        slots = [0] * (num_slots + 1)
        lib_range = max - min
        lib_block_size = lib_range / num_slots
        for v in items:
            slot = int((v.liberality - min) / lib_block_size)
            slots[slot] += 1
        print('%s in %s groups: %s' % (label, num_slots, slots))
        return slots

    def printVoteStatus(self, round, remove_zeros=False):
        # Only show viable candidates in each round

        remaining_candidates = [c for c in self.candidates if c.viable]
        remaining_candidates.sort(key=sortByFirstRank, reverse=True)
        round_string = 'Round %d' % round
        print('%-10s %5s %6s : %s' %
              (round_string, 'Name ', '#1',
               "Vote summary"))
        for candidate in remaining_candidates:
            i = candidate.index
            vote_summary = [0] * (self.num_candidates + 1)
            votes = []  # Unused for now
            for j in range(self.num_voters):
                votes.append(self.voters[j].votes[i])
                vote_summary[self.voters[j].votes[i]] += 1
            note = ""
            if candidate.elected:
                note = "elected"
            summary = '%s. None = %d' % (vote_summary[1:], vote_summary[0])
            if not remove_zeros > 0:
                print(' %-9s %5s %6d : %s' %
                      (note, candidate.name, candidate.one_votes, summary))
            if len(votes) < 100:
                print('         Votes: %s' % votes)

    def genVotes(self):
        # Naive to start with
        for i in range(self.num_voters):
            self.voters[i].genVotes(self.candidates)

    def checkVotes(self):
        # Check if any preferences do not start at 1.
        for v in self.voters:
            min_vote = min(v.votes)
            max_vote = max(v.votes)
            if min_vote > 1:
                print('Strange votes for voter %d: %s' % (v.id, v.votes))

    # Returns how many people voted for any candidate
    def countTotalVoted(self):
        total_voted = 0

        for v in self.voters:
            votes = v.votes
            i = 0
            voted = False
            while not voted and i < self.num_candidates:
                voted = votes[i] > 0
                i += 1

            if voted:
                total_voted += 1
        return total_voted   # Returns total #1 votes

    # Find #1 votes for each viable candidate
    # Done once at the start
    def countOneVotes(self):
        for c in self.candidates:
            c.one_votes = 0

        for v in self.voters:
            votes = v.votes
            for i in range(self.num_candidates):
                if self.candidates[i].viable and votes[i] == 1:
                    self.candidates[i].one_votes += 1
        return

    def checkForWinner(self):
        # if any candidate has more #1 votes than the number of votes needed to win, declare as elected
        # Consider candidates with most #1 votes first
        remaining_candidates = [c for c in self.candidates if c.viable and not c.elected]
        remaining_candidates.sort(key=sortByFirstRank, reverse=True)
        # TODO !!! Must adjust win criteria for last position.
        if len(remaining_candidates) == 1:
            remaining_candidates[0].elected = True
            return remaining_candidates[0]
        for c in remaining_candidates:
            if c.one_votes >= self.needed_to_win:
                c.elected = True
                return c
        return None  # Not done yet

    def getSecondVotes(self, c):
        # Get 2nd votes by voter for this candidate for candidates
        # who are still in the running
        c_index = c.index
        candidates = self.candidates
        voters_second_choice_after_winner = [0] * self.num_candidates
        for v in self.voters:
            candidate_place = v.votes[c_index]
            if candidate_place > 0:
                # Get the next preferred after this candidate.
                next_candidate_index = self.num_candidates
                for i in self.active_candidates:
                    if v.votes[i] > candidate_place:
                        next_candidate_index = min(next_candidate_index, v.votes[i])

                if next_candidate_index < self.num_candidates:
                    voters_second_choice_after_winner[next_candidate_index] += 1
        return voters_second_choice_after_winner

    def findMinCandidate(self):
        # Find the candidate with the least number of #1 votes
        min_1_votes = len(self.voters)
        min_candidate = None
        for c in self.candidates:
            if c.viable and c.one_votes < min_1_votes:
                min_1_votes  = c.one_votes
                min_candidate = c
        return min_candidate

    def updateForRemovedCandidate(self, c):
        c.viable = False
        self.active_candidates.remove(c.index)
        second_votes = self.getSecondVotes(c)
        # And update all other votes
        for index in self.active_candidates:
            add_to_second_place_candidate = second_votes[index]
            if add_to_second_place_candidate > 0:
                self.candidates[index].one_votes += add_to_second_place_candidate
                c.one_votes =- add_to_second_place_candidate
                print('    %d votes moved from %s to %s' %
                      (add_to_second_place_candidate, c.name,
                       self.candidates[index].name))

    def updateForWinningCandidate(self, c):
        # Find excess and update all other
        self.active_candidates.remove(c.index)
        excess = c.one_votes - self.needed_to_win

        # excess_fraction = excess / c.one_votes  # This fails if there are not enough second votes
        second_place_votes = self.getSecondVotes(c)
        total_second_votes = sum(second_place_votes)
        # Try this - fraction of votes for the candidate that actually have seconds
        if total_second_votes > 0:
            excess_fraction = excess / total_second_votes

            removed_from_winner = 0
            for c_index in self.active_candidates:
                add_to_second_place_candidate = int(round(excess_fraction * second_place_votes[c_index]))
                if add_to_second_place_candidate:
                    print('    %d excess votes moved from %s to %s' %
                          (add_to_second_place_candidate, c.name,
                           self.candidates[c_index].name))
                    self.candidates[c_index].one_votes += add_to_second_place_candidate
                    c.one_votes -= add_to_second_place_candidate
        c.elected = True
        self.winning_candidates.append(c)
        self.elected_count += 1

    def run(self):
        # The algorithm for picking a single winner
        # How to extend for N winners
        winner_index = 0

        self.printLiberalitySummary(self.voters, 10, 'Voters')
        self.printLiberalitySummary(self.candidates, 10, 'Candidates')
        self.printCandidateInfo()
        self.winning_candidates = []
        viables = self.candidates
        round = 1;
        winning_candidate = None

        print('++ %d votes needed to win' % (self.needed_to_win))

        self.countOneVotes()
        complete = False
        while not winning_candidate:

            self.printVoteStatus(round)

            winning_candidate = True  # To start loop
            while winning_candidate:
                winning_candidate = self.checkForWinner()
                if winning_candidate:
                    print('  !! Candidate %s elected' % (winning_candidate.name))
                    self.updateForWinningCandidate(winning_candidate)
                else:  # No winner this time
                    winning_candidate = None
                    removed = self.findMinCandidate()
                    if removed:
                        print('  -- Removed candidate %s' % (removed.name))
                        self.updateForRemovedCandidate(removed)
                if len(self.winning_candidates) >= self.num_winners:
                    return self.winning_candidates, round
                round += 1
        return self.winning_candidates, round


def setSeed():
    # Reproducible system
    random.seed(17)

    # Press the green button in the gutter to run the script.
if __name__ == '__main__':
    args = sys.argv
    num_candidates, num_voters, num_elected = 4, 17, 1
    if len(args) > 1 and args[-1] == "test":
        setSeed()
    if len(args) > 1:
        num_candidates = int(args[1])
    if len(args) > 2:
        num_voters = int(args[2])
    if len(args) > 3:
        num_elected = int(args[3])
    print('RCV: %d candidates, %d voters, %d to be elected' % (num_candidates, num_voters, num_elected))
    sim = RankSim(num_candidates, num_voters, num_elected)
    winners, round = sim.run()
    print('%d elected by round %d' % (len(winners), round))
    for w in winners:
        print('  %d %4.2f %s' % (w.index, w.liberality, w.name))

    print('Election complete!')
