from flask import Flask, render_template, request, redirect,jsonify, Blueprint,flash,url_for
import datetime
from datetime import datetime as dt
from database import db 
from flask_admin import Admin,AdminIndexView
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, login_user, login_required, logout_user, current_user,UserMixin
from sqlalchemy.orm import relationship
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yoursecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'your_database_server_link'
dbs = SQLAlchemy(app)

# TODO make flash messages
# TODO change home.html and reader gui
# TODO add some gui stuff
# note: to access u need first to go /signin redirections are not adjusted yet
# /ADMIN NOW WORKS NOT FULLY TESTED


class CustomAdminIndexView(AdminIndexView):
    def is_accessible(self):
        #! make a home panel soon
        return True




admin = Admin(app, name='NMU Panel',template_mode='bootstrap4', index_view=CustomAdminIndexView())

database = db()
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_employee(employee_id):
    # Use the session.get() method instead of query.get()
    return dbs.session.get(Employee, int(employee_id))

class MyModelView(ModelView):
    def __init__(self, model, session, name=None, category=None, endpoint=None, url=None, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        
        super(MyModelView, self).__init__(model, session, name=name, category=category, endpoint=endpoint, url=url)

    def is_accessible(self):
        # Logic
        return True

class EmployeeAdminView(ModelView):
    form_rules = ('Name', 'PhoneNumber', 'Address', 'Password')  # Specify the order of form fields
    column_list = ('EmployeeID', 'Name', 'PhoneNumber', 'Address')  # Specify the columns to display in the list view

    def on_model_change(self, form, model, is_created):
        # Hash the password before saving it to the database
        if 'Password' in form and form.Password.data:
            model.Password = generate_password_hash(form.Password.data)



class Reader(dbs.Model):
    __tablename__ = 'Reader'
    column_display_pk = True
    Name = dbs.Column(dbs.String(100), primary_key=True)
    PhoneNumber = dbs.Column(dbs.String(15))

class Member(dbs.Model):
    __tablename__ = 'Member'
    column_display_pk = True
    ID = dbs.Column(dbs.Integer, primary_key=True)
    Name = dbs.Column(dbs.String(100))
    PhoneNumber = dbs.Column(dbs.String(15))
    Address = dbs.Column(dbs.String(255))
    

class Employee(dbs.Model,UserMixin):
    __tablename__ = 'Employee'
    column_display_pk = True
    EmployeeID = dbs.Column(dbs.Integer, primary_key=True)
    Name = dbs.Column(dbs.String(100))
    PhoneNumber = dbs.Column(dbs.String(15))
    Address = dbs.Column(dbs.String(255))
    Password = dbs.Column(dbs.String(255))
    

    def is_active(self):
        # Override the is_active method to always return True
        return True
    def get_id(self):
        # Return the EmployeeID as a string
        return str(self.EmployeeID)
class Membership(dbs.Model):
    __tablename__ = 'Membership'
    column_display_pk = True
    ExpiryDate = dbs.Column(dbs.DATE)
    MemberID = dbs.Column(dbs.Integer, primary_key=True)
    

class Genre(dbs.Model):
    __tablename__ = 'Genre'
    GenreID = dbs.Column(dbs.Integer, primary_key=True, autoincrement=True)
    GenreName = dbs.Column(dbs.String(50), unique=True)
    

class Vendor(dbs.Model):
    __tablename__ = 'Vendor'
    column_display_pk = True
    VendorID = dbs.Column(dbs.Integer, primary_key=True)
    Name = dbs.Column(dbs.String(100))
    PhoneNumber = dbs.Column(dbs.String(15))

class BookGenre(dbs.Model):
    __tablename__ = 'BookGenre'
    column_display_pk = True
    BookID = dbs.Column(dbs.Integer, dbs.ForeignKey('Book.BookID'), primary_key=True)
    GenreID = dbs.Column(dbs.Integer, dbs.ForeignKey('Genre.GenreID'), primary_key=True)
    book = dbs.relationship('Book', backref='book_genres')
    genre = dbs.relationship('Genre', backref='book_genres')


class BookAuthor(dbs.Model):
    __tablename__ = 'BookAuthor'
    column_display_pk = True
    BookID = dbs.Column(dbs.Integer, dbs.ForeignKey('Book.BookID'), primary_key=True)
    Author = dbs.Column(dbs.String(100), primary_key=True)
    book = dbs.relationship('Book', backref='authors')

class Book(dbs.Model):
    __tablename__ = 'Book'
    BookID = dbs.Column(dbs.Integer, primary_key=True)
    Name = dbs.Column(dbs.String(255))
    Publisher = dbs.Column(dbs.String(100))
    Quantity = dbs.Column(dbs.Integer)
    BookCode = dbs.Column(dbs.Integer)
    VendorID = dbs.Column(dbs.Integer, dbs.ForeignKey('Vendor.VendorID'))


class Borrow(dbs.Model):
    __tablename__ = 'Borrow'
    column_display_pk = True
    DueDate = dbs.Column(dbs.DATE)
    BorrowedDate = dbs.Column(dbs.DATE)
    RefNumber = dbs.Column(dbs.Integer, primary_key=True)
    BookID = dbs.Column(dbs.Integer, dbs.ForeignKey('Book.BookID'))
    MemberID = dbs.Column(dbs.Integer, dbs.ForeignKey('Member.ID'))
    EmployeeID = dbs.Column(dbs.Integer, dbs.ForeignKey('Employee.EmployeeID'))
    member = relationship('Member', backref='borrows')


    
class BookGenreAdminView(ModelView):
    column_list = ['BookID', 'GenreID']
    form_columns = ['BookID', 'GenreID']
    column_labels = {            #column_labels is a predefined variable used to customize the column names
        'BookID': 'BOOK ID',  # Capitalize column name
        'GenreID': 'GENRE ID'  # Capitalize column name
    }

class BookAuthorAdminView(MyModelView):
    column_list = ['BookID', 'Author'] 
    form_columns = ['BookID', 'Author']  
    column_labels = {
        'BookID': 'BOOK ID',
        'Author': 'AUTHOR'
    }
# Create Flask-Admin views for each model
admin.add_view(MyModelView(Reader, dbs.session,form_columns = ['Name', 'PhoneNumber']))
admin.add_view(MyModelView(Member, dbs.session,form_columns = ['ID', 'Name', 'PhoneNumber', 'Address']))
admin.add_view(EmployeeAdminView(Employee, dbs.session))
admin.add_view(MyModelView(Book, dbs.session, form_columns = ['BookID','Name', 'Publisher','Quantity','BookCode','VendorID']))
admin.add_view(MyModelView(Membership, dbs.session,form_columns = ['ExpiryDate','MemberID']))
admin.add_view(MyModelView(Genre, dbs.session,form_columns = ['GenreName']))
admin.add_view(BookGenreAdminView(BookGenre,dbs.session))
admin.add_view(BookAuthorAdminView(BookAuthor,dbs.session))
admin.add_view(MyModelView(Borrow, dbs.session,form_columns = ['RefNumber', 'DueDate', 'BorrowedDate', 'BookID', 'MemberID', 'EmployeeID']))
admin.add_view(MyModelView(Vendor, dbs.session, form_columns = ['VendorID','Name', 'PhoneNumber']))





@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        password = request.form.get('password')

        # Check if employee ID and password are correct
        employee = Employee.query.filter_by(EmployeeID=employee_id).first()
        if employee and check_password_hash(employee.Password, password):
            # Login successful
            login_user(employee)
            return redirect('/')
        else:
            # Login failed
            flash('Invalid employee ID or password', 'error')
            return redirect(url_for('login'))

    # Render the login page template
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()  # Log out the current user
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('home.html')

@app.route('/readers') 
@login_required
def readers():
    search_term = request.args.get('search', '')
    
    
    if search_term.isdigit():  # Check if search term is a number (assuming it's the reader ID)
        # If search term is a number, fetch reader data by ID
        reader_data = database.SearchReadersByID(int(search_term))
        print(reader_data)
        return render_template('readers.html', readers=reader_data)
    else:
        # If search term is not a number or empty, fetch default set of readers
        readers_data = database.RetrieveReadersWithRenewalDate()
        return render_template('readers.html', readers=readers_data)
    #! change it leater her
@app.route('/action', methods=['POST'])
def renew_membership():
    if request.method == 'POST':
        reader_id = request.form['reader_id']
        action = request.form['action']
        if action == '1':  # Renew for 1 month
            database.RenewMembership(reader_id, 1)
        elif action == '12':  # Renew for 12 months
            database.RenewMembership(reader_id, 12)
        elif action == 'delete':  # Delete membership
            database.DeleteMembership(reader_id) #make later -- done
        elif action == 'deletereader':
            database.DeleteReader(reader_id) #make later -- done
    return redirect('/readers')

@app.route('/readers/add', methods=['POST'])
def add_reader():
    if request.method == 'POST':
        # Get form data
        reader_name = request.form['reader_name']
        reader_contact = request.form['reader_contact']
        reader_id = request.form['reader_id']
        reader_address = request.form['reader_address']
        
        # Insert reader into the database
        database.RegisterReader(reader_id, reader_name, reader_contact, reader_address, None)
        
        # Redirect to the reader page
        return redirect('/readers')
    

    
@app.route('/books/add', methods=['POST'])
def add_item():
    # Handle adding new items (books, genres, vendors) here
    item_type = request.json.get('type')
    if item_type == 'book':
        # Handle book addition
        book_id = request.json['id']
        book_name = request.json['title']
        publisher = request.json['publisher']
        quantity = request.json['quantity']
        book_code = request.json['bookCode']
        vendor_id = request.json['vendorID']
        genre_id = request.json['genreID']
        author = request.json['author']
        # Add the new book to the database
        database.AddBook(book_id, book_name, publisher, quantity, book_code, vendor_id)
        database.AddBookGenre(book_id, genre_id)
        database.AddAuthor(book_id,author)

    elif item_type == 'vendor':
        # Handle vendor addition
        vendor_name = request.json['name']
        phone_number = request.json['phoneNumber']
        new_vendor_id = request.json['vendorID']
        database.AddVendor(new_vendor_id,vendor_name, phone_number)

    elif item_type == 'genre':
        # Handle genre addition
        genre_name = request.json['genreName']
        database.AddGenre(genre_name)

    # You can add more cases for other item types if needed

    # Return success response
    return jsonify({'message': 'Item added successfully'})

@app.route('/books', methods=['GET'])
@login_required
def books():
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # If AJAX request, return JSON response with books, vendors, and genres data
        books_data = database.ListBooks()
        vendors_data = database.ListVendors()
        genres_data = database.ListGenres()
        # Combine the data into a single dictionary
        response_data = {
            'books': books_data,
            'vendors': vendors_data,
            'genres': genres_data
        }
        return jsonify(response_data)
    else:
        # If regular page request, render the books.html template
        return render_template('books.html')
    
@app.route('/books/update', methods=['POST']) #! UNDER DEVELOPMENT
def update_item():
    # Handle updating items (books, genres, vendors) here
    item_type = request.json.get('type')
    if item_type == 'book':
        # Handle book update
        book_id = request.json['id'] #TODO try request.form instead of request.json (maybe will work :D)
        book_name = request.json['title']
        publisher = request.json['publisher']
        quantity = request.json['quantity']
        book_code = request.json['bookCode']
        vendor_id = request.json['vendorID']
        genre_id = request.json['genreID']
        author = request.json['author']
        
        print(book_id, book_name, publisher, quantity, book_code, vendor_id,genre_id,author) #, book_name, publisher, quantity, book_code, vendor_id,genre_id,author)
        database.UpdateBook(book_id, book_name, publisher, quantity, book_code, vendor_id,genre_id,author)
        
    elif item_type == 'vendor':
        # Handle vendor update
        vendor_id = request.json['id']
        vendor_name = request.json['name']
        phone_number = request.json['phoneNumber']
        # Update the vendor in the database
        print(vendor_id,vendor_name,phone_number)
        database.UpdateVendor(vendor_id, vendor_name, phone_number)
        
    elif item_type == 'genre':
        # Handle genre update
        genre_id = request.json['id']
        genre_name = request.json['genreName']
        # Update the genre in the database
        database.UpdateGenre(genre_id, genre_name)

    # You can add more cases for other item types if needed

    # Return success response
    return jsonify({'message': 'Item updated successfully'})

@app.route('/books/delete', methods=['POST'])
def delete_item():
    # Handle deleting items (books, genres, vendors) here
    item_type = request.json.get('type')
    item_id = request.json.get('id')
    print(item_id)
    if item_type == 'book':
        # Handle book deletion
        database.delete_book(item_id)
        
    elif item_type == 'vendor':
        # Handle vendor deletion
        database.DeleteVendor(item_id)
        print(item_id)
    elif item_type == 'genre':
        # Handle genre deletion
        database.DeleteGenre(item_id)

    # You can add more cases for other item types if needed

    # Return success response
    return jsonify({'message': 'Item deleted successfully'})


@app.route('/borrow', methods=['GET', 'POST'])
@login_required
def borrow():
    if request.method == 'POST':
        # Get data from the form
        book_id = request.form['book_id']
        member_id = request.form['member_id']
        ref_number = request.form['ref_number']
        employee_id = request.form['employee_id']
        borrowed_date = request.form['borrowed_date']
        due_date = request.form['due_date']

        # Convert dates to datetime objects
        borrowed_date = dt.strptime(borrowed_date, '%Y-%m-%d')
        due_date = dt.strptime(due_date, '%Y-%m-%d')

        # Perform any necessary validation

        # Save the borrow record to the database
        borrow_record = Borrow(
            BookID=book_id,
            MemberID=member_id,
            RefNumber=ref_number,
            EmployeeID=employee_id,
            BorrowedDate=borrowed_date,
            DueDate=due_date
        )
        dbs.session.add(borrow_record)
        dbs.session.commit()
            # Update the quantity of the book (decrease by one)
        book = Book.query.filter_by(BookID=book_id).first()
        if book:
            book.Quantity -= 1
            dbs.session.commit()
        else:
            flash('Book not found', 'error')

        flash('Book borrowed successfully', 'success')
        return redirect('/borrow')

    # Fetch borrow records from the database
    borrow_records = Borrow.query.all()

    # If it's a GET request, render the borrow form
    return render_template('borrow.html', Borrows=borrow_records)


@app.route('/borrow/return', methods=['POST'])
@login_required
def return_book():
    if request.method == 'POST':
        ref_number = request.form['return_ref_number'] # Get the reference number of the borrow record to return
        # Query the database to mark the borrow record as returned
        borrow_record = Borrow.query.filter_by(RefNumber=ref_number).first()
        if borrow_record:
            dbs.session.delete(borrow_record)  # Delete the record
            dbs.session.commit()
            flash('Book returned successfully', 'success')  # Assuming you have a column named 'returned' in your Borrow model
            # Commit the changes to the database
            dbs.session.commit()

            # Update the quantity of the book (increase by one)
            book = Book.query.filter_by(BookID=borrow_record.BookID).first()
            if book:
                book.Quantity += 1
                dbs.session.commit()
            else:
                flash('Book not found', 'error')

            flash('Book returned successfully', 'success')
        else:
            flash('Borrow record not found', 'error')

        return redirect('/borrow')

@app.route('/borrow/update', methods=['POST'])
@login_required
def update_borrow():
    if request.method == 'POST':
        # Get data from the form
        borrow_id = request.form['borrow_id']
        book_id = request.form['editBookID']
        member_id = request.form['editMemberID']
        ref_number = request.form['editRefNumber']
        employee_id = request.form['editEmployeeID']
        borrowed_date = request.form['editBorrowedDate']
        due_date = request.form['editDueDate']

        # Convert dates to datetime objects
        borrowed_date = dt.strptime(borrowed_date, '%Y-%m-%d')
        due_date = dt.strptime(due_date, '%Y-%m-%d')

        # Perform any necessary validation

        # Update the borrow record in the database
        borrow_record = Borrow.query.get(borrow_id)
        borrow_record.BookID = book_id
        borrow_record.MemberID = member_id
        borrow_record.RefNumber = ref_number
        borrow_record.EmployeeID = employee_id
        borrow_record.BorrowedDate = borrowed_date
        borrow_record.DueDate = due_date

        dbs.session.commit()

        flash('Borrow record updated successfully', 'success')
        return redirect('/borrow')


if __name__ == '__main__':
    app.run(debug=True)
 