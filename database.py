import mysql.connector
import datetime
from flask import Flask, request, redirect

class db:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host="your_host",
            user="username",
            password="database_password",
            database="database_name",
            auth_plugin=''
        )
        self.cursor = self.conn.cursor()
        #self.conn.commit()
        # TODO make  one for checking if the membership is finished
        # TODO make a delete check if the membership is due
        #so the reader is either existing or current and if he existing he can make either a month or a year membership or none, ref id is student id
    def RegisterReader(self,id:int,name:str,phone:int,address:str,membership:int): #TODO membership is either 1 or 12 or 0
        self.cursor.execute('INSERT INTO Reader (Name,PhoneNumber) VALUES (%s,%s)',
                            (name,phone))
        self.cursor.execute('INSERT INTO Member (id,Name,PhoneNumber,Address) VALUES (%s,%s,%s,%s)',
                            (id,name,phone,address))

        if membership:
            current_date = datetime.date.today()
            if membership == 1:  # 1 month
                renewal_date = current_date + datetime.timedelta(days=30)
            elif membership == 12:  # 12 months
                renewal_date = current_date + datetime.timedelta(days=365)
            self.cursor.execute('INSERT INTO Membership (ExpiryDate, MembershipDate, MemberID) VALUES (%s, %s, %s)',
                            (renewal_date, current_date, id))
        self.conn.commit()
    
    def RenewMembership(self, member_id:int, membership_duration:int):
        current_renewal_date = None
        self.cursor.execute('SELECT ExpiryDate FROM Membership WHERE MemberID = %s', (member_id,)) 
        
        # Fetch the current renewal date
        current_renewal_date_row = self.cursor.fetchone()
        
        if current_renewal_date_row:
            current_renewal_date = current_renewal_date_row[0]
            
        if current_renewal_date is None:
            # If no current renewal date is found, use the current date
            current_renewal_date = datetime.date.today()
            
        if membership_duration == 1:  # 1 month
            new_renewal_date = current_renewal_date + datetime.timedelta(days=30)
            
        elif membership_duration == 12:  # 12 months
            new_renewal_date = current_renewal_date + datetime.timedelta(days=365)
            
        else:
            # invalid membership duration
            return "Invalid membership duration"
        
        try:
            # Check if membership record exists
            self.cursor.execute('SELECT COUNT(*) FROM Membership WHERE MemberID = %s', (member_id,))
            membership_exists = self.cursor.fetchone()[0]
            
            if membership_exists:
                # Update existing membership
                self.cursor.execute('UPDATE Membership SET ExpiryDate = %s WHERE MemberID = %s',
                                    (new_renewal_date, member_id))
            else:
                # Create new membership
                self.cursor.execute('INSERT INTO Membership (MemberID, ExpiryDate) VALUES (%s, %s)',
                                    (member_id, new_renewal_date))
            
            self.conn.commit()
            return "Membership renewed successfully"
        except Exception as e:
            # Handle any exceptions
            print("Error:", e)
            self.conn.rollback()
            return "Failed to renew membership: " + str(e)


    def RetrieveReader(self, reader_id:int):
        self.cursor.execute('SELECT * FROM Member WHERE ID = %s', (reader_id,))
        member_data = self.cursor.fetchone()
        return member_data  # Assuming only one reader is returned

    def RetrieveMembership(self, member_id:int):
        self.cursor.execute('SELECT * FROM Membership WHERE MemberID = %s', (member_id,))
        membership_data = self.cursor.fetchone()
        return membership_data  # Assuming only one membership record is returned
        
    def RetrieveReadersWithRenewalDate(self):
        self.cursor.execute('''
            SELECT M.*, MEM.ExpiryDate
            FROM Member M
            LEFT JOIN Membership MEM ON M.ID = MEM.MemberID
        ''')
        reader_data = self.cursor.fetchall()
        return reader_data
    
    def SearchReadersByID(self, reader_id: int):
        try:
            # Execute SQL query to search for readers by partial ID and retrieve renewal date
            self.cursor.execute('''
                SELECT M.*, MEM.ExpiryDate
                FROM Member M
                LEFT JOIN Membership MEM ON M.ID = MEM.MemberID
                WHERE M.ID LIKE %s
            ''', ('%' + str(reader_id) + '%',))
            reader_data = self.cursor.fetchall()
            return reader_data
        except Exception as e:
            # Handle any exceptions
            print("Error:", e)
            return None

    def AddBook(self, book_id: int, name: str, publisher: str, quantity: int, book_code: int, vendor_id: int):
        try:
            self.cursor.execute('''
                INSERT INTO Book (BookID, Name, Publisher, Quantity, BookCode, VendorID)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (book_id, name, publisher, quantity, book_code, vendor_id))
            self.conn.commit()
            return "Book added successfully"
        except Exception as e:
            print("Error:", e)
            self.conn.rollback()
            return "Failed to add book: " + str(e)
    


    def ListBooksOnly(self):
        try:
            self.cursor.execute('SELECT * FROM Book')
            book_data = self.cursor.fetchall()
            return book_data
        except Exception as e:
            print("Error:", e)
            return None
    
    def listbookgenre(self,book_id):
        self.cursor.execute('SELECT GenreID FROM BookGenre WHERE BookID = ?', (book_id,))
        book_data = self.cursor.fetchall()
        return book_data

    def ListBooks(self):
        try:
            query = """
                SELECT b.*, GROUP_CONCAT(DISTINCT bg.GenreID) AS GenreIDs, GROUP_CONCAT(DISTINCT ba.Author) AS Authors
                FROM Book b
                LEFT JOIN BookGenre bg ON b.BookID = bg.BookID
                LEFT JOIN BookAuthor ba ON b.BookID = ba.BookID
                GROUP BY b.BookID
            """
            self.cursor.execute(query)
            book_data = self.cursor.fetchall()

            return book_data
        except Exception as e:
            print("Error:", e)
            return None



    def RetrieveBooks(self):
        try:
            # Execute SQL query to retrieve books along with their genres
            self.cursor.execute('''
                SELECT B.BookID, B.Name, B.Publisher, B.Quantity, B.BookCode, V.Name AS VendorName, GROUP_CONCAT(G.GenreName) AS Genres
                FROM Book B
                LEFT JOIN Vendor V ON B.VendorID = V.VendorID
                LEFT JOIN BookGenre BG ON B.BookID = BG.BookID
                LEFT JOIN Genre G ON BG.GenreID = G.GenreID
                GROUP BY B.BookID
            ''')
            book_data = self.cursor.fetchall()
            return book_data
        except Exception as e:
            # Handle any exceptions
            print("Error:", e)
            return None
        
    def AddVendor(self, vendor_id: int, name: str, phone_number: str):
        try:
            self.cursor.execute('''
                INSERT INTO Vendor (VendorID, Name, PhoneNumber)
                VALUES (%s, %s, %s)
            ''', (vendor_id, name, phone_number))
            self.conn.commit()
            return "Vendor added successfully"
        except Exception as e:
            print("Error:", e)
            self.conn.rollback()
            return "Failed to add vendor: " + str(e)

    def ListVendors(self):
        try:
            self.cursor.execute('SELECT * FROM Vendor')
            vendor_data = self.cursor.fetchall()
            return vendor_data
        except Exception as e:
            print("Error:", e)
            return None
        
        
    def AddGenre(self, genre_name: str):
        try:
            self.cursor.execute('''
                INSERT INTO Genre (GenreName)
                VALUES (%s)
            ''', (genre_name,))
            self.conn.commit()
            return "Genre added successfully"
        except Exception as e:
            print("Error:", e)
            self.conn.rollback()
            return "Failed to add genre: " + str(e)
        
    def AddBookGenre(self, BookID: int, GenreID:int):
        try:
            self.cursor.execute('''
                INSERT INTO BookGenre (BookID,GenreID)
                VALUES (%s,%s)
            ''', (BookID,GenreID))
            self.conn.commit()
            return f"Book genre added of book id: {BookID}"
        except Exception as e:
            print("Error:", e)
            self.conn.rollback()
            return "Failed to add book genre: " + str(e)
    
    
    def ListGenres(self):
        try:
            self.cursor.execute('SELECT * FROM Genre')
            genre_data = self.cursor.fetchall()
            return genre_data
        except Exception as e:
            print("Error:", e)
            return None
        
    def AddAuthor(self, book_id: int, author: str):
        try:
            self.cursor.execute('''
                INSERT INTO BookAuthor (BookID, Author)
                VALUES (%s, %s)
            ''', (book_id, author))
            self.conn.commit()
            return "Author added successfully"
        except Exception as e:
            print("Error:", e)
            self.conn.rollback()
            return "Failed to add author: " + str(e)

    def ListAuthors(self):
        try:
            self.cursor.execute('SELECT DISTINCT Author FROM BookAuthor')
            author_data = self.cursor.fetchall()
            return author_data
        except Exception as e:
            print("Error:", e)
            return None
    
    
    def DeleteReader(self, reader_id: int):
        

        try:
            # Check if there are any membership records associated with the reader
            self.cursor.execute('SELECT COUNT(*) FROM Membership WHERE MemberID = %s', (reader_id,))
            membership_exists = self.cursor.fetchone()[0]
            
            if membership_exists:
                # Delete associated membership records first
                self.cursor.execute('DELETE FROM Membership WHERE MemberID = %s', (reader_id,))
            
            # Now, delete the reader record
            self.cursor.execute('DELETE FROM Member WHERE ID = %s', (reader_id,))
            self.conn.commit()
            return f"Reader with ID {reader_id} deleted successfully"
        except Exception as e:
            print("Error:", e)
            self.conn.rollback()
            return "Failed to delete reader: " + str(e)

    def delete_book(self, book_id: int):
        try:
            # Delete associated book authors first
            self.cursor.execute('DELETE FROM BookAuthor WHERE BookID = %s', (book_id,))
            
            # Now, delete associated book genres
            self.cursor.execute('DELETE FROM BookGenre WHERE BookID = %s', (book_id,))
            
            # Finally, delete the book from the Book table
            self.cursor.execute('DELETE FROM Book WHERE BookID = %s', (book_id,))
            
            self.conn.commit()
            return f"Book with ID {book_id} deleted successfully"
        except Exception as e:
            print("Error:", e)
            self.conn.rollback()
            return "Failed to delete book: " + str(e)

    def DeleteMembership(self, member_id: int):
        try:
            # Delete membership record
            self.cursor.execute('DELETE FROM Membership WHERE MemberID = %s', (member_id,))
            self.conn.commit()
            return f"Membership for member with ID {member_id} deleted successfully"
        except Exception as e:
            print("Error:", e)
            self.conn.rollback()
            return "Failed to delete membership: " + str(e)

    def UpdateBook(self, book_id: int, title: str, publisher: str, quantity: int, book_code: int, vendor_id: int, genre_id: int, author: str):
        try:

            # Update book information
            self.cursor.execute('''
                UPDATE Book
                SET Name = %s, Publisher = %s, Quantity = %s, BookCode = %s, VendorID = %s
                WHERE BookID = %s
            ''', (title, publisher, quantity, book_code, vendor_id, book_id))

            # Update book genre
            self.cursor.execute('''
                UPDATE BookGenre
                SET GenreID = %s
                WHERE BookID = %s
            ''', (genre_id, book_id))

            # Update book author
            self.cursor.execute('''
                UPDATE BookAuthor
                SET Author = %s
                WHERE BookID = %s
            ''', (author, book_id))

            # Commit changes
            self.conn.commit()
            
            return f"Book with ID {book_id} updated successfully"
        except Exception as e:
            print("Error:", e)
            self.conn.rollback()
            return "Failed to update book: " + str(e)
    def DeleteVendor(self, vendor_id: int):
        try:
            # Check if any books are associated with the vendor
            self.cursor.execute('SELECT COUNT(*) FROM Book WHERE VendorID = %s', (vendor_id,))
            books_exist = self.cursor.fetchone()[0]
            
            # Check if any authors are associated with the books from this vendor
            self.cursor.execute('''
                SELECT COUNT(*)
                FROM BookAuthor BA
                INNER JOIN Book B ON BA.BookID = B.BookID
                WHERE B.VendorID = %s
            ''', (vendor_id,))
            authors_exist = self.cursor.fetchone()[0]
            
            if books_exist:
                # If books are associated with the vendor, prevent deletion
                return "Cannot delete vendor. Books are associated with this vendor."
            elif authors_exist:
                # If authors are associated with books from this vendor, prevent deletion
                return "Cannot delete vendor. Authors are associated with books from this vendor."
            
            # If no books or authors are associated, proceed with deletion
            self.cursor.execute('DELETE FROM Vendor WHERE VendorID = %s', (vendor_id,))
            self.conn.commit()
            return f"Vendor with ID {vendor_id} deleted successfully"
        except Exception as e:
            print("Error:", e)
            self.conn.rollback()
            return "Failed to delete vendor: " + str(e)



    def UpdateGenre(self, genre_id: int, genre_name: str):
        try:
            self.cursor.execute('''
                UPDATE Genre
                SET GenreName = %s
                WHERE GenreID = %s
            ''', (genre_name, genre_id))
            self.conn.commit()
            return f"Genre with ID {genre_id} updated successfully"
        except Exception as e:
            print("Error:", e)
            self.conn.rollback()
            return "Failed to update genre: " + str(e)

    def DeleteVendor(self, vendor_id: int):
        try:
            # Check if there are any books associated with the vendor
            self.cursor.execute('SELECT COUNT(*) FROM Book WHERE VendorID = %s', (vendor_id,))
            books_exist = self.cursor.fetchone()[0]

            if books_exist:
                # Delete associated books first
                self.cursor.execute('DELETE FROM Book WHERE VendorID = %s', (vendor_id,))
            
            # Now, delete the vendor record
            self.cursor.execute('DELETE FROM Vendor WHERE VendorID = %s', (vendor_id,))
            self.conn.commit()
            return f"Vendor with ID {vendor_id} deleted successfully"
        except Exception as e:
            print("Error:", e)
            self.conn.rollback()
            return "Failed to delete vendor: " + str(e)

    def DeleteGenre(self, genre_id: int):
        try:
            self.cursor.execute('''DELETE FROM Genre WHERE GenreID = %s''', (genre_id,))
            self.conn.commit()
            return f"Genre with ID {genre_id} deleted successfully"
        except Exception as e:
            print("Error:", e)
            self.conn.rollback()
            return "Failed to delete genre: " + str(e)
    
database = db()
