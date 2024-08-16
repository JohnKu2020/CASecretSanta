"""
File: santa.py
--------------
Author:  Yevhen K
Date:    16/08/2024

"""

import random
import csv
import re
import os
from gmail import Gmail
from datetime import datetime

class Santa:

    def __init__(self, mailSender, verbal = True):
        """
        Init 'Secret Santa' class
        Handles user's input, make random assignments and send emails to members

        Args:
            mailSender (string): an email address on behalf of which to send messages
            verbal (boolean): for debug needs 
            
        Returns:
            None

        """         
        self.previousDirectory = os.getcwd()  # Save last path to restore if needed
        self.verbal = verbal
        self.mailSender = mailSender
        
    patterns = [
        re.compile(r'(\d{2})_(\d{2})_(\d{4})'),  # MM_DD_YYYY [0]
        re.compile(r'(\d{2})-(\d{2})-(\d{4})'),  # MM-DD-YYYY [1]
        re.compile(r'(\d{2})\.(\d{2})\.(\d{4})'),# MM.DD.YYYY [2]
        re.compile(r'(\d{2})(\d{2})(\d{4})'),    # MMDDYYYY [3]
        re.compile(r'(\d{2})([A-Za-z]{3})(\d{4})'),  # DDMonYYYY (e.g., 20Oct2023) [4]
        re.compile(r'(\d{2})-([A-Za-z]{3})-(\d{4})'),  # DD-Mon-YYYY (e.g., 20-Oct-2023) [5]
        re.compile(r'(\d{2})_([A-Za-z]{3})_(\d{4})'),  # DD_Mon_YYYY (e.g., 20_Oct_2023) [6]
        re.compile(r'(\d{2})\.([A-Za-z]{3})\.(\d{4})')  # DD.Mon.YYYY (e.g., 20.Oct.2023) [7]
    ]

    def fileMove(self, fromPath, toPath) -> bool:
        """
        Renames and moves a file from one path to another.

        Parameters:
        fromPath (str): The path to the source file
        toPath (str):   The path to the destination file

        Returns:
        bool: Returns True if there were no errors, otherwise returns False.
        """ 
        try:
            os.rename(fromPath, toPath)
            return True
        except:
            return False
    
    def sortDirectory(self, baseDirectory, destDirectory, miscDirectory) -> bool:
        """
        Renames all files in the input directory, so that instead of month/day/year the file name goes year/month/day.
        Moves the renamed files to the destination directory. Any file that is not renamed is instead moved to the misc directoy.
    
        Parameters:
        baseDirectory (str): The path to the directory containing the files that need to be sorted.
        destDirectory (str): The path to the directory where sorted files will be moved based on their categories.
        miscDirectory (str): The path to the directory where files that do not match any predefined categories will be moved.
    
        @Returns:
        bool: Returns True if the sorting operation completes successfully, otherwise returns False.
        """      
        self.baseDirectory = baseDirectory
        self.destDirectory = destDirectory
        self.miscDurectory = miscDirectory
        
        try:
            # Add to list only files
            files = [f for f in os.listdir(self.baseDirectory) if os.path.isfile(os.path.join(self.baseDirectory, f))]
        except:
            if (self.verbal):
                print('Error: Base directory not found')
                return False

        if (len(files) == 0 ):
            if (self.verbal):
                    print('No files found')
            return False
        
        for file in files:

            fMatched = False
            for index, pattern in enumerate(self.patterns):    
                matchDate = pattern.search(file)
           
                if matchDate:
                    fMatched = True
                    dateParts = matchDate.groups()
                    fileParts = file.split('.')

                    newName = ''
                    match index: # -> year/month/day
                        case 0: # MM_DD_YYYY (e.g., 07_24_2024)
                            newName = f"{dateParts[2]}_{dateParts[1]}_{dateParts[0]}"
                        case 1: # MM-DD-YYYY (e.g., 07-24-2024)
                            newName = f"{dateParts[2]}-{dateParts[1]}-{dateParts[0]}"                            
                        case 2: # MM.DD.YYYY (e.g., 07.24.2024)
                            newName = f"{dateParts[2]}.{dateParts[1]}.{dateParts[0]}" 
                        case 3: # MMDDYYYY (e.g., 07242024)
                            newName = f"{dateParts[2]}{dateParts[1]}{dateParts[0]}"                            
                        case 4: # DDMonYYYY (e.g., 20Oct2023)
                            newName = f"{dateParts[2]}{dateParts[1]}{dateParts[0]}"
                        case 5: # DD-Mon-YYYY (e.g., 20-Oct-2023)
                           newName = f"{dateParts[2]}-{dateParts[1]}-{dateParts[0]}"
                        case 6: # DD_Mon_YYYY (e.g., 20_Oct_2023) 
                           newName = f"{dateParts[2]}_{dateParts[1]}_{dateParts[0]}"
                        case 7: # DD.Mon.YYYY (e.g., 20.Oct.2023)
                           newName = f"{dateParts[2]}.{dateParts[1]}.{dateParts[0]}"                          

                    if newName != '':
                        newName += f'.{fileParts[-1]}'
                        if(self.fileMove(self.baseDirectory + '\\' + file, self.destDirectory + '\\' + newName)):
                            print( f'[{index}]: ' +file + '-> ' + newName +f' -> moving to {self.destDirectory}' )
                    break # Exit the second loop (patterns)

            if fMatched == False:
                if (self.fileMove(self.baseDirectory + '\\' + file, self.miscDurectory + '\\' + file)):
                    print(f'{file} -> no match -> moving to {self.miscDurectory}')
                
        return True    
    
    def getMembers(self):
        """
        Obtains input from user in format: the first line - Name, the next Email

        Returns:
        list: Returns list of users in format [{name},{email}, ...]
        """         
        users = []
        print("Enter participant names and emails ('done' to finish):")
        while True:
            name = input("name: ")
            if name.lower() == 'done':
                break
            email = input("email: ")
            users.append({"name": name, "email": email})
        return users
    
    def randomAssignment(self, participants):
        """
        Ramdomizes list of participants so that each participant is assigned to other

        Parameters:
        participants (list): contains list in format [{name},{email}\n ...]

        Returns:
        list: Returns list of users in format [{email}{name}, ...]
        """    
        while True:
            # Shuffle the list of participants
            shuffled_participants = participants[:]
            random.shuffle(shuffled_participants)
        
            # Check if any participant would be assigned to themselves
            if all(participant['name'] != shuffled_participants[i]['name'] for i, participant in enumerate(participants)):
                break
        
        assignments = []
        for i, participant in enumerate(participants):
            recipient = shuffled_participants[i]
            assignments.append({
                'giver_name': participant['name'],
                'giver_email': participant['email'],
                'recipient_name': recipient['name'],
                'recipient_email': recipient['email']
            })
        
        return assignments
    
    def save2File(self, participants, suffix = ''):
        """
        Saves list of users in a file with name in format mm-dd-yy.csv

        Parameters:
        participants (list): contains list of users
        suffix (string): a suffix for file name [optional]

        Returns:
        filename (string) a file name to which a list was saved
        """          
        date_str = datetime.now().strftime("%m-%d-%Y")
        filename = f"{date_str}{suffix}.csv"
        
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Name", "Email"])
            for participant in participants:
                writer.writerow([participant["name"], participant["email"]])

        if (self.verbal):
            print(f"Participants saved to {filename}")
        return filename

    def loadFromFile(self, filename):
        """
        Loads a list of users from a file
        
        Parameters:
        filename (string): a file name and path if file is not in the current folder

        Returns: a list in format [{name},{email}\n ...]
        """         
        users = []
        
        with open(filename, mode='r', newline='') as file:
            reader = csv.DictReader(file)

            # headers = reader.fieldnames
            # print(f"Headers found: {headers}")
            
            for row in reader:
                users.append({"name": row["Name"], "email": row["Email"]})
        
        return users   

    def sendInvitations(self, assignments, debug = False):
        """
        Sends an email for every member in a list
        
        Parameters:
        assignments (list): contains list of users in format:
            'giver_name': 'who gives a present',
            'giver_email': 'to whom email assignment',
            'recipient_name': '',
            'recipient_email': 'who is going to be presented'

        debug (boolean): 
            True - to debug proper assignments without actual emailing
            False or skip the second argument for real sending (if emails are real)

        Returns: none
        """

        mail = Gmail('token.json','credentials.json')
        
        for assignment in assignments:
           
            try:
                message  = "Hi " + assignment['giver_name'] + "!\nThis is a Secret Santa assignment\nYou need to buy a gift for " + assignment['recipient_name']
                if debug==False:
                    mail.send(self.mailSender, assignment['giver_email'], 'Secret Santa assignment', message)
                    pass
                else:
                    print('Sending from ' + self.mailSender + ' to ' ,assignment['giver_email'] , ":\n" + message + "\n-------------")
            except ValueError:
                print("Oops!  An error: " + ValueError)
            
