# trello2status
Scrapes Trello Data into Splunk Dashboard for emailing status and meeting notes

https://trello.com/app-key

Version 0.0.0.0.0.1

Fill in the API KEY and API TOKEN in local/trello.conf. You can also specify them in the |gettrello command args

Update the TrelloEmail.csv lookup to include your specific email groups for each account/board.

[BASIC] The Meeting Notes function looks for a list "Sync Meeting Notes" and pulls the latest card.

Feel free to update the email text in the XML to suit your needs.

Data is pulled in live, so refreshing the Dashboard will pull an updated data set from Trello

[BASIC] You MUST select at least one email group for the dashboard to start showing sample email

[BASIC] SEND EMAIL will use mailto: to open your preferred email tool. From there you can review and make any changes. You can also update the trello board with changes and refresh to get the change.

[BASIC] If you put a ! at the beginning of a line in a card comment, it will be removed from the email as a comment for you

There is a company slack channel for this. Reach out to me for access

[BASIC] SEND EMAIL has a max char limit, and will alert you if you simply need to copy the email text over to the new email.

Still ironing out some token logic. If a token is not resolving, toggle it between Status and Meeting Notes and back, usually fixes it

|gettrello

--token=XYZ #Optional if trello.conf used

--key=ABC # Optional if tello.conf used

--creds=DEF #Optional if default stanza used in trello.conf used

--command=boards,cards,labels,memberships,members,actions,lists,custom,plugins,checklists #only one allowed. defaults to cards
