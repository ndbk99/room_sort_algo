from random import *
from math import *
import csv

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


def find_member(Team,name):
    """
    Quick and dirty function to return a member object if it has the queried name

    Parameters
    ----------
    Team: object of class Team
        whatever team the member you're looking for belongs to
    name: string
        the name of the member you're looking for

    Returns
    -------
    member: object of class Member
        team member with name "name" inputted as parameter
    """
    members = Team.members
    for member in members:
        if member.name == name:
            return member

# CLASS: Member of robotics team
class Member:
    """
    Class to hold an individual robotics team member

    Parameters
    ----------
    data: 1 x M array
        array that holds data about the member in the format [name,[preferences in order 1 to M]]

    Methods
    -------
    happiness: calculates "happiness quotient" of self based on current room assignment and prefs list (higher index => lower happiness)

    """

    def __init__(self,data,Team):  # Read info from data array from read_csv()
        self.name = data[0]
        self.Team = Team
        self.prefs = data[1]
        self.room = []
        self.room_number = 0
        self.Team.members.append(self)  # Automatically add member to its team!
        self.Team.n_members += 1

    def happiness(self):
        f = 0  # Lower f => higher happiness
        room = self.Team.rooms[self.room_number]
        prefs = [find_member(self.Team,name) for name in self.prefs]

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

    Methods
    -------
    rand_rooms: assigns team members to n_rooms randomly
    print_rooms: prints current room arrangement in niceish format
    find_happiest: runs rand_rooms repeatedly and stores/prints progressively "happiest" room arrangements
    evolve: UNDER CONSTRUCTION - function to reach optimal arrangement more quickly
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
                print "|", member.name, member.happiness(),
            print " "
        print " "

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

    def find_happiest(self,max_iterations,print_rooms=False):
        i = 0
        optimal = 1000000000
        # Run rand_rooms() repeatedly, storing successively happier configs
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

    def evolve(self,iterations):
        seed_1 = self.rand_rooms()
        self.print_rooms()
        print self.rooms_happiness()

        seed_2 = self.rand_rooms()
        self.print_rooms()
        print self.rooms_happiness()

    def rooms_happiness(self):
        room_happiness_array = []
        for room in self.rooms:
            room_happiness = 0
            for member in room:
                room_happiness += member.happiness()
            room_happiness_array.append(room_happiness)
        return room_happiness_array

Robotics = Team("Murphy's Outlaws",4)  # Create team object
data = read_prefs("preferences.txt")  # Read in member data
members = [Member(x,Robotics) for x in data]  # Create members from data and team (automatically added to team!)
Robotics.evolve(100000)
x = raw_input("Hi")
