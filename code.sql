CREATE TABLE Reader (
    Name VARCHAR(100),
    PhoneNumber VARCHAR(15) PRIMARY KEY
);

CREATE TABLE Guest (
    Name VARCHAR(100),
    PhoneNumber VARCHAR(15),
    VisitRate INT,
    PRIMARY KEY (PhoneNumber, Name),
    FOREIGN KEY (PhoneNumber) REFERENCES Reader(PhoneNumber)
);

CREATE TABLE Member (
    Name VARCHAR(100),
    ID INT PRIMARY KEY,
    Address VARCHAR(255),
    PhoneNumber VARCHAR(15),
    FOREIGN KEY (PhoneNumber) REFERENCES Reader(PhoneNumber)
);

CREATE TABLE Membership (
    RenewalDate DATE,
    MembershipDate DATE,
    MemberID INT NOT NULL,
    PRIMARY KEY (MemberID),
    FOREIGN KEY (MemberID) REFERENCES Member(ID)
);

CREATE TABLE Book (
    BookID INT PRIMARY KEY,
    Name VARCHAR(255),
    Publisher VARCHAR(100),
    Quantity INT,
    BookCode INT
);

CREATE TABLE Vendor (
    VendorID INT PRIMARY KEY,
    Name VARCHAR(100),
    PhoneNumber VARCHAR(15)
);

CREATE TABLE Vendor_Book (
    VendorID INT,
    BookID INT,
    PRIMARY KEY (VendorID, BookID),
    FOREIGN KEY (VendorID) REFERENCES Vendor(VendorID),
    FOREIGN KEY (BookID) REFERENCES Book(BookID)
);

CREATE TABLE Genre (
    GenreID INT AUTO_INCREMENT PRIMARY KEY,
    GenreName VARCHAR(15),
    BookID INT,
    FOREIGN KEY (BookID) REFERENCES Book(BookID)
);

CREATE TABLE BookAuthor (
    BookID INT,
    Author VARCHAR(100),
    PRIMARY KEY (BookID, Author),
    FOREIGN KEY (BookID) REFERENCES Book(BookID)
);

CREATE TABLE Employee (
    EmployeeID INT PRIMARY KEY,
    Name VARCHAR(100),
    PhoneNumber VARCHAR(15), 
    Address VARCHAR(255),
    Password VARCHAR(255)
);

CREATE TABLE Borrow (
    DueDate DATE,
    BorrowedDate DATE,
    RefNumber INT PRIMARY KEY,
    BookID INT,
    MemberID INT,
    EmployeeID INT,
    FOREIGN KEY (BookID) REFERENCES Book(BookID),
    FOREIGN KEY (MemberID) REFERENCES Member(ID),
    FOREIGN KEY (EmployeeID) REFERENCES Employee(EmployeeID)
);
