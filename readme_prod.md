# Library System
Staff account: imstaff - imstaff
User account: imuser - imuser


### Description:
This project is web application.
This application was made to simulate library behaviour. In this program you can keep track of books you have in library and history of book borrows. 
You can also of course add new book. User can borrow books and return them. For al
You can log in as a user, staff or a superuser.
The system has it's own account to store books held in library.

## CURRENT TODOS 
Priority in stars (*)
- add Google Books API for adding books
- add requesting books that should be added to library by User 
- add fees by adding user balance to user model and by determining the amount of days   book can be held
- add automatic canceling of a reservation after 3 days of not retrieving the book (adding a type of event or altering reservation function)
- desing and implement tests for the whole system

## STRUCTURE

User
atributes:
- First Name
- Last Name
- Email
- Is Active
- Is Staff
- Is Superuser
- Last Login
- Password
- Username

methods:
- getSession()
- login()
- logout()
- resetPassword()

Book
atributes:
- Title
- Subtitle
- Authors
- Description
- pageCount
- Release Date
- Cover URL image - generated randomly

Copy
- Book - Foreign Key
- Reserved - Foreign Key
- Holder - Foreign Key
- State description

    methods:
    - reserveCopy()
    - addBook()
    - removeCopy()
    - borrowCopy()
    - returnCopy()

Event
- Copy - Foreign Key
- User - Foreign Key
- Start Date - datefield
- End Date - datefield