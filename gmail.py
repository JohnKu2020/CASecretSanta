"""
File: gmail.py
--------------
Author:  Yevhen K
Date:    16/08/2024

"""
import os.path
import base64
from email.message import EmailMessage
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class Gmail:
    """
    The Gmail class which is dedicated to work with the Gmail service via API.

    """
    def __init__(self, tokenFile, credentialsFile, verbose = False):
        """
        Init Gmail class

        Args:
            tokenFile (string): a string wich file with token to be saved.
            credentialsFile (string): a file with credentials
            verbose (boolean): is used to debug
            
        Returns:
            None

        """         
        self.tokenFile = tokenFile
        self.credentialsFile = credentialsFile
        self.verbose = verbose
        

    def send(self, form, to, subject, text):
        """
        Sends an email.

        Args:
            form (string): The email address the message is being sent from.
            to (string): The email address the message is being sent to.
            subject (string): The subject line of the email.
            text (string): The content of the email.
            
        Returns:
            Message object

        Raises:
            googleapiclient.errors.HttpError: There was an error executing the
                HTTP request.

        """
        # Before sending, get new credentials if needed
        creds = self.getCreds()
        
        try:
            service = build("gmail", "v1", credentials=creds)
            message = EmailMessage()
            message.set_content(text)
            message["To"] = to
            message["From"] = form
            message["Subject"] = subject
        
            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            create_message = {"raw": encoded_message}

            send_message = (
                service.users()
                .messages()
                .send(userId="me", body=create_message)
                .execute()
            )
            if (self.verbose):
                print(f'Message Id: {send_message["id"]}')
        except HttpError as error:
            print(f"An error occurred: {error}")
            send_message = None
        return send_message
        
    def getCreds(self):
        """
        Gets current actual credentials
            
        Returns:
            Credentials
        """     
        SCOPES = ["https://www.googleapis.com/auth/gmail.modify", "https://www.googleapis.com/auth/gmail.send"]
        creds = None
        
        if os.path.exists(self.tokenFile):
            creds = Credentials.from_authorized_user_file(self.tokenFile, SCOPES)
            if (self.verbose):
                print("Have tokens!")
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                if (self.verbose):
                    print("Refreshed token!")
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                self.credentialsFile, SCOPES
                )
                creds = flow.run_local_server(port=0)
                if (self.verbose):
                    print("Got new token")
        # Save the credentials for the next run
        with open(self.tokenFile, "w") as token:
              token.write(creds.to_json())
        return creds