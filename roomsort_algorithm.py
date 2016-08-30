from random import *
from math import *
import csv

print "BEGIN"
print "______________________________________"

def read_prefs(filename):
    """
    Read in CSV file containing team members' names and rooming preferences

    Parameters
    ----------
    filename: opened CSV file
        holds team member names and their list of roommate preferences

    Returns
    -------
    data: M x N array
        holds M items of processed info for each of N team members in format [name,[roommate preferences from 1 to M]]
    """
    data = []
    with open(filename) as csvfile:
        doc = csv.reader(csvfile)
        # Read each member
        for row in doc:
            n_prefs = len(row)
            member = []
            # Add member name
            member.append(row[0])
            # Add rooming preferences
            member.append([])
            for n in range(1,n_prefs):
                member[1].append(row[n])
            data.append(member)
    print "CSV data read successfully"
    return data

def members_from_name(names):
    data = []
    for name in names:
        data.append([name,[]])
    print data
    return data

# CLASS: Member of robotics team
class Member:
    """
    Class to hold an individual robotics team member

    Parameters
    ----------
    data: 1 x M array
        array that holds data about the member in the format [name,[preferences in order 1 to M]]
    Team: Team() object
        team to which the new member will automatically be added

    Attributes
    ----------
    name: string, name of the team member
    prefs: string[], array of member's rooming preferences
    Team: Team(), member's team object
    room: array holding the other Member() objects in the member's room
    room_number: index of the room that the member is in

    Methods
    -------
    happiness: calculates "happiness quotient" of self based on current room assignment and prefs list (higher index => lower happiness)
    """

    def __init__(self,data,Team):  # Data array is generated from read_csv() function
        self.name = data[0]
        self.prefs = data[1]
        self.Team = Team
        self.room_number = 0
        self.Team.members.append(self)  # Automatically add member to its team!
        self.Team.n_members += 1  # Increase number of members on the team to account for this new member

    def happiness(self):
        f = 0  # Lower f => higher happiness
        room = self.Team.rooms[self.room_number]
        prefs = [self.Team.find_member(name) for name in self.prefs]

        for member in room:
            if member in prefs:  # Add index for members in prefs
                f += prefs.index(member)
                # print self.name, "prefs", member.name
            elif member.name == self.name:  # Add n/2 for members not in prefs
                f += 0
                # print self.name, "is", member.name
            else:
                f += len(self.prefs)*2
                # print self.name, "nonprefs", member.name
            # Could add cases for "nopes" / other levels
        return f

    def move_room(self,room_number):
        old_number = self.room_number
        self.Team.rooms[old_number].remove(self)  # Remove Member from old room

        self.room_number = room_number  # Update Member's room number

        new_room = self.Team.rooms[room_number]  # Get current target room from Member's Team
        new_room.append(self)  # Add Member to target room array

        self.Team.rooms[room_number] = new_room  # Update the room in self.Team with the Member


class Team:
    """
    Class to hold a robotics team

    Parameters
    ----------
    name: string
        gives team a name
    n_rooms: integer
        number of rooms to be generated
    members: array of Member objects
        holds all the members on the team

    Attributes
    ----------
    members: array of Members() that are on the team
    n_members: number of members on the team (i.e. length of members array)
    n_rooms: number of rooms available to the team
    rooms: array of arrays of Member() objects, representing the current room arrangements

    Methods
    -------
    rand_rooms: assigns team members to n_rooms randomly
    print_rooms: prints current room arrangement in niceish format
    find_happiest: DEPRECATED brute-force search; runs rand_rooms() repeatedly and stores progressively "happier" room arrangements
    members_happiness: returns happiness of each member on the team
    evolve: single step where one pair of members are switched to create happier configuration
    run_sort_algorithm: runs evolve_step repeatedly to work towards the happiest config
    algorithm_iterate: iterates evolve_iterate however many times and returns the "happiest" configuration out of all of those
    """

    def __init__(self,name,n_rooms,members=[]):
        self.members = members
        self.n_members = len(self.members)
        self.n_rooms = n_rooms
        # Make empty array of appropriate number of rooms.
        self.rooms = []
        for x in range(n_rooms):
            self.rooms.append([])

    def print_rooms(self):
        for room in self.rooms:
            for member in room:
                print "|", member.name,
            print " "
        print " "

    def find_member(self,name):
        """
        Quick and dirty function to return a member object if it has the queried name

        Parameters
        ----------
        Team: Team() object
            team that the member you're looking for belongs to
        name: string
            the name of the member you're looking for

        Returns
        -------
        member: Member() object
            team member with name "name" inputted as parameter
        """
        members = self.members
        for member in members:
            if member.name == name:
                return member

    def rand_rooms(self,print_rooms=False):

        # Empty out current rooms array
        self.rooms = []
        for x in range(self.n_rooms):
            self.rooms.append([])

        # Shuffle members list
        members = self.members
        shuffle(members)

        # Assign rooms
        for member_index in range(self.n_members):
            room_index = member_index % self.n_rooms  # set room number to mod of member index by # of rooms
            self.rooms[room_index].append(self.members[member_index])  # append current member to correct room
            self.members[member_index].room_number = room_index  # set room index of current member

        # Print rooms if asked to
        if print_rooms:
            self.print_rooms()

        # Find total happiness index
        sum_happiness = 0
        for member in self.members:
            sum_happiness += member.happiness()
        return self.rooms, sum_happiness

    # DEPRECATED; brute-force search method
    def find_happiest(self,max_iterations,print_rooms=False):
        i = 0
        optimal = 1000000000

        # Randomize rooms repeatedly, storing successively happier configs
        while i < max_iterations:
            current = self.rand_rooms()[0]
            if i % (max_iterations/10) == 0:
                print "*"
            if current < optimal:
                optimal = current
                print optimal
                if print_rooms:
                    self.print_rooms()
            i += 1
        return self.rooms

    def members_happiness(self):
        members_happiness_array = []
        for member in self.members:
            members_happiness_array.append(member.happiness())
        return members_happiness_array

    def evolve(self):
        start_happiness = sum(self.members_happiness())

        # Order members by happinesses
        happiest = 10000
        saddest = 0
        index = 0
        ordered = [[h,m] for h,m in sorted(zip(self.members_happiness(),self.members),reverse=True)]  # THIS IS WHERE THE PROBLEM IS

        i = 0
        j = 0
        while i < self.n_members - 1:
            # Switch saddest member until new arrangement is happier (until we run out of pairs)
            member_A = ordered[i][1]
            room_A = member_A.room_number
            member_B = ordered[i+1][1]
            room_B = member_B.room_number
            member_A.move_room(room_B)
            member_B.move_room(room_A)
            # Recalculate overall happiness
            end_happiness = sum(self.members_happiness())
            if end_happiness < start_happiness:
                # Happier arrangement finally found, so break out
                print end_happiness
                self.print_rooms()
                return sum(self.members_happiness())
            else:
                # Undo switch if it isn't happier and we still have more switches to try
                if i < self.n_members - 2:
                    member_A.move_room(room_A)
                    member_B.move_room(room_B)
                # End of list reached; switch saddest members anyway to keep program from stalling at local minimum
                else:
                    # Unclear if this code is helpful; still leads to stalls. See below #### section for better ideas. May delete this later.
                    saddest_member = ordered[0][1]
                    second_member = ordered[1][1]
                    saddest_member_room = saddest_member.room_number
                    second_member_room = second_member.room_number
                    saddest_member.move_room(second_member_room)
                    second_member.move_room(saddest_member_room)
                    print "reached list limit... execute switch of saddest anyway. happiness =", sum(self.members_happiness())
                    self.print_rooms()

            ### NEXT STEP: write code to detect and terminate stalls.

            j += 1
            if j > self.n_members - 1:
                i += 1
                j = 0
        print sum(self.members_happiness())
        return sum(self.members_happiness())

    def run_sort_algorithm(self):
        self.rand_rooms()  # Set random initial conditions for the iterations
        prev_happiness = self.evolve()
        current_happiness = 0
        # Run algorithm until it stalls! More efficient this way
        while prev_happiness > current_happiness:
            current_happiness = self.evolve()
            prev_happiness = current_happiness
        print "End happiness =", sum(self.members_happiness())
        self.print_rooms()
        return sum(self.members_happiness())

    def algorithm_iterate(self,iteration_counts):
        best_happiness = 100000
        best_rooms = []
        counter = 0
        while counter < iteration_counts:
            current_happiness = self.run_sort_algorithm()
            if current_happiness < best_happiness:  # Check if the value returned from the current algorithm run is less than the one before
                # If so, set stored "best values" to current ones
                best_happiness = current_happiness
                best_rooms = []
                for room in self.rooms:
                    best_rooms.append(room)
            counter += 1
            print "Algorithm run #", counter

        # Print best rooms and best happiness found
        names = []
        for room in best_rooms:
            names.append([m.name for m in room])
        print best_happiness, names

    def best_switch(self):
        self.rooms = [\
        [self.find_member("Ali"),self.find_member("Allison"),self.find_member("Tala"),self.find_member("Sage")],\
        [self.find_member("Tara"),self.find_member("Suchita"),self.find_member("Arlyvia"),self.find_member("Evelyn")],\
        [self.find_member("Alex"),self.find_member("Sav"),self.find_member("Hailey"),self.find_member("Kim")],\
        [self.find_member("Emma"),self.find_member("Sophia"),self.find_member("Lilli"),self.find_member("Sarah")]]
        print sum(self.members_happiness())
        self.evolve()
        print sum(self.members_happiness())
        self.print_rooms()

Robotics = Team("Murphy's Outlaws",4)  # Create team object
data = read_prefs("preferences.txt")  # Read in member data from CSV
# data = members_from_name(["Ali","Allison","Tala","Sage","Tara","Suchita","Arlyvia","Evelyn","Alex","Sav","Hailey","Kim","Emma","Sophia","Lilli","Sarah"])
members = [Member(x,Robotics) for x in data]  # Create members from CSV data and automatically add them to the team
Robotics.algorithm_iterate(1000)
# Robotics.best_switch()

print "_______________________________________"
x = raw_input("END")
