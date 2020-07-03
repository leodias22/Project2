# Project 1

Web Programming with Python and JavaScript

This project containt:
 - 3 sql files, each used to create a table in the Heroku Database. The 3 tables are Books, Users and Reviews, the later has forein keys to both previous tables.
 - 6 html files
  . A layout page, used to kke the standard and to import bootstrap styles
  . A login page
  . A user registration page, to create user accounts
  . A Welcome page, responsable for the search aspect of the webpage
  . A results page, that shows the list of book in a given search made
  . A details page, that shows more information from the books, from Goodreads, and allows for user feedback regarding the Books
  - 1 Application file, responsable for running all the functions of the webpage. Interfacing the front end with the database and the goodreads api

  Beyond the above, a test with Goodreads API was made using the APITEST.py file. The import.py was created to import the books.csv file.
  At the requirements page, I have added the follwoing imports:
  - jsonify - to deliver the API for the project
  - sqlalchemy.orm - to keep the command line "db = scoped_session(sessionmaker(bind=engine))" functioning
  - requests  - to deal with the request for the Goodreads API

  
