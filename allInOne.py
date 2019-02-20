from http.server import SimpleHTTPRequestHandler, BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import cgi
from cgi import parse_header, parse_multipart
import logging
import os
import re
import sqlite3
import mysql.connector
from pprint import pprint
from io import BytesIO

#####################################################
#                                                   #
# DBmanager                                         #
#                                                   #
#####################################################

REQUEST = {}
        
#####################################################
#                                                   #
# Dispatcher                                        #
#                                                   #
#####################################################

class Dispatcher:
        
    #####################################################
    #                                                   #
    # run                                               #
    #                                                   #
    #####################################################

    def run (self, path, method):
        global REQUEST
        self.action = path
        
        # choose SQLite or MySQL below
        db = DBmanager('sqlite', path)        
        #db = DBmanager('mysql', path) 

        html = self.DoHeaderMenus()
                
        if method == 'GET':
            if 'menu' in REQUEST:
                if REQUEST['menu'][0] == 'blog':
                    #with open("readme.html", 'r') as myfile:
                    #    html += myfile.read()
                    html += '''
<center><div style="width: 75%; padding: 10px 10px; display: block; text-align: left;">
<h1>Really all in one</h1>
<p>
I got peeved with all those frameworks that promise wonders and deliver much less.
<br /><br />
This is a port to Python 3.7 of a minimal web app I did in PHP some while back.
<br /><br />
It really lives up to its name of "all in one" as this readme text and the css styling are all
tucked away in the allinOne.py file!
<br /><br />
I tried to segregate my data structures from the executable code. The benefit in my view is that the data definitions exist ONLY in one place
 - the SQL statements to build the tables and views.
<br /><br />
There is a way in both MySQL and SQLite (which are both supported in this project) to interogate
the schema and iterate thru the fields of a data entry form (ie the columns of a table).
Therefore you do not polute your data manager code with knowledge of the data structures. Any changes made
to these doesn't involve any rework - especially in forms and reports.
<br /><br />
This comes at the cost of some begnin naming conventions. If you have a foreign key your your record you call it 
foreign_id and you expect the value to be displayed for this lookup field to be in a column called foreign in a 
table aptly called foreign_tb or a view called foreign_tb_view. Quite simple really.
<br /><br />
</p>
</div></center>                   
                    '''
                    
                elif REQUEST['menu'][0] == 'category':
                    html += db.Display('select * from category_tb')

                elif REQUEST['menu'][0] == 'capacity':
                    html += db.Display('select * from capacity_tb')
                    
                elif REQUEST['menu'][0] == 'person':
                    html += db.Display('select * from person_tb')
                    
                elif REQUEST['menu'][0] == 'activity':
                    html += db.Display('select * from activity_tb_view order by category')
                    
                elif REQUEST['menu'][0] == 'booking':
                    html += db.Display('select * from booking_view order by person')

            elif 'order' in REQUEST:
                if 'dir' in REQUEST:
                    html += db.Display(f"select * from {REQUEST['table'][0]} order by {REQUEST['order'][0]} {REQUEST['dir'][0]}")
                else:
                    html += db.Display(f"select * from {REQUEST['table'][0]} order by {REQUEST['order'][0]}")
                       
            elif 'row' in REQUEST:
                html += db.EditTable(REQUEST['table'][0], REQUEST['row'][0])                
                
            elif 'table' in REQUEST:
                html += db.Display(f"select * from {REQUEST['table'][0]}")

        elif method == 'POST':
            html += db.PostTable()

        else:
            html += db.Populate()
            html += db.Display('select * from activity_tb_view order by category')
            html += db.Display('select * from booking_view order by person')
            
        db.Close()
        html += self.DoFooter()

        return bytes(html, 'utf-8')
        
    #####################################################
    #                                                   #
    # DoHeaderMenus                                     #
    #                                                   #
    #####################################################

    def DoHeaderMenus (self):    
        myTitle = "Minimal web app in Python"
        myStyle = '''
<!-- <link rel="stylesheet" type="text/css" href="/Schlumpf.css" />
For the sake of "all in one" we will have inline styling rather than a css file -->
<style>
#Schlumpf {
    font-family: "Trebuchet MS", Arial, Helvetica, sans-serif;
    border-collapse: collapse;
    width: 100%;
}
#Schlumpf div {
    margin: auto;
    width: 50%;
    text-align: center;
    border: 3px solid green;
    padding: 10px;
}
#footer {
    padding-top: 12px;
    padding-bottom: 12px;
    text-align: center;
    background-color: black;
    color: white;
    font-style: italic;
    font-weight: bold;
}
#tablehead {
    margin: auto;
    width: 50%;
    text-align: center;
}
#Schlumpf table {
    margin: auto;
//    width: auto;
    padding: 10px;
} 
#Schlumpf td, #Schlumpf th {
    border: 1px solid #ddd;
    padding: 8px;
}

#Schlumpf tr:nth-child(even){background-color: #f2f2f2;}

#Schlumpf tr:hover {background-color: #ddd;}

#Schlumpf th {
    padding-top: 12px;
    padding-bottom: 12px;
    text-align: left;
    background-color: #4CAF50;
    color: white;
}

#content a, .menu a:link, .menu a:active, .menu a:visited 
{
text-decoration: none;
}
#content a:hover 
{
background-color: black;
color: white;
}

.nav 
{
align: center;
margin: 10px 10px;
padding-top: 8px;
padding-bottom: 10px;
padding-left: 8px;
background: none;
}

.nav li 
{
list-style-type: none;
display: inline;
padding: 10px 30px;
background-color: #e67e22;
margin-left: -11px;
font-size: 120%;
}

.nav li:first-child
{
margin-left: 0;
border-top-left-radius: 10px !important;
border-bottom-left-radius: 10px !important;
}

.nav li:last-child
{
margin-right: 0px;
border-top-right-radius: 10px !important;
border-bottom-right-radius: 10px !important;
}

.nav a, .menu a:link, .menu a:active, .menu a:visited 
{
text-decoration: none;
color: white;
border-bottom: 0;
padding: 10px 10px;
}

.nav a:hover 
{
text-decoration: none;
background: #9b59b6;
padding: 10px 10px;
}

ul.nav li a.current 
{
text-decoration: none;
background: #e74c3c;
padding: 10px 10px;
}

</style>
        '''
        
        retval = f'''
<html>
<head>
<title>{myTitle}</title>
{myStyle}
</head>
<body>

<center><h1>{myTitle}</h1></center>

<center><ul class="nav">
<li> <a href="{self.action}">Home</a></li>
<li> <a href="{self.action}?menu=blog">readme</a></li>
<li> <a href="{self.action}?menu=booking">booking</a></li>
<li> <a href="{self.action}?menu=activity">activity</a></li>
<li> <a href="{self.action}?menu=category">category</a></li>
<li> <a href="{self.action}?menu=capacity">capacity</a></li>
<li> <a href="{self.action}?menu=person">person</a></li>
</ul></center>
        '''
        return retval

    #####################################################
    #                                                   #
    # DoFooter                                          #
    #                                                   #
    #####################################################

    def DoFooter (self):    
        retval = f'''
<div id="footer">Say NO to bloatware</div>    
</body>
</html>    
'''
        return retval
      
#####################################################
#                                                   #
# DBmanager                                         #
#                                                   #
#####################################################

class DBmanager:
            
    def __init__(self, engine, action,):
        global REQUEST
        self.dsn = engine
        self.action = action
        self.db_name = 'db_name'
        if self.dsn == 'sqlite':
            self.cnx = sqlite3.connect('Schlumpf.db')
            print ("connecting to sqlite")
        else:
            self.cnx = mysql.connector.connect(host='localhost',
                                     user='DB_USER',
                                     password='DB_PASSWORD',
                                     db=self.db_name)
            print ("connecting to mysql")
                       
    def __exit__(self, exc_type, exc_value, traceback):
        self.cnx.close()

    #####################################################
    #                                                   #
    # Populate                                          #
    #                                                   #
    #####################################################

    def Populate(self):
        html = ''
        if os.path.isfile('Schlumpf.db') == True and self.dsn == 'sqlite':
            print ("database already exists")
            
        strings = [
        'drop table if exists activity_tb',
        "create table if not exists activity_tb ("\
        "id  integer primary key AUTO_INCREMENT,"\
        "activity text NOT NULL,"\
        "description text NULL,"\
        "category_id int NOT NULL,"\
        "venue text NOT NULL,"\
        "latitude float NULL,"\
        "longitude float NULL,"\
        "distance float NULL,"\
        "travel_time text NULL)",
        "insert into activity_tb (activity, category_id, venue, latitude, longitude) values "\
        "('spelling bee', 3, 'Hornsby',-33.868820, 151.099010)",
        "insert into activity_tb (activity, category_id, venue, latitude, longitude) values "\
        "('swimming carnival', 1, 'Mona Vale', -33.677830, 151.302290)",
        "insert into activity_tb (activity, category_id, venue, latitude, longitude) values "\
        "('zone athletics', 1, 'Castle Hill',  -33.729252, 151.004013)",
        "insert into activity_tb (activity, category_id, venue, latitude, longitude) values "\
        "('excursion at the zoo', 2, 'Taronga', -33.843548, 151.241348)",
        "insert into activity_tb (activity, category_id, venue, latitude, longitude) values "\
        "('a day in court', 2, 'Lane Cove', -33.814871, 151.166435)",
        "insert into activity_tb (activity, category_id, venue, latitude, longitude) values "\
        "('exploring the city', 3, 'Sydney', -33.868820, 151.209290)",

        'drop table if exists category_tb',
        "create table if not exists category_tb ("\
        "id integer primary key AUTO_INCREMENT,"\
        "category text NOT NULL)",
        "insert into category_tb (category) values ('sport')",
        "insert into category_tb (category) values ('visit')",
        "insert into category_tb (category) values ('academic')",
        
        'drop view if exists activity_tb_view',
        "create view activity_tb_view as "\
        "select activity_tb.id as id, "\
        "activity_tb.activity as activity, "\
        "category_tb.category as category, "\
        "activity_tb.venue as venue,"\
        "activity_tb.latitude as latitude,"\
        "activity_tb.longitude as longitude,"\
        "activity_tb.distance as distance,"\
        "activity_tb.travel_time as time "\
        "from activity_tb, category_tb "\
        "where activity_tb.category_id =  category_tb.id",

        'drop table if exists capacity_tb',
        "create table if not exists capacity_tb ("\
        "id integer primary key AUTO_INCREMENT,"\
        "capacity text NOT NULL)",
        "insert into capacity_tb (capacity) values ('organiser')",
        "insert into capacity_tb (capacity) values ('staff')",
        "insert into capacity_tb (capacity) values ('parent')",
        "insert into capacity_tb (capacity) values ('volunteer')",
        "insert into capacity_tb (capacity) values ('student')",

        'drop table if exists person_tb',
        "create table if not exists person_tb ("\
        "id integer primary key AUTO_INCREMENT,"\
        "person text NOT NULL)",
        "insert into person_tb (person) values ('Mrs Smith')",
        "insert into person_tb (person) values ('Mr Doodle')",
        "insert into person_tb (person) values ('Ms Wilson')",
        "insert into person_tb (person) values ('Lucy Sommerfield')",
        "insert into person_tb (person) values ('David Walnaugh')",
        "insert into person_tb (person) values ('Mary Ellison')",
        "insert into person_tb (person) values ('Mrs Sommerfield')",
        "insert into person_tb (person) values ('Mrs Walnaugh')",
        "insert into person_tb (person) values ('Mrs Ellison')",

        'drop table if exists booking',
        "create table if not exists booking ("\
        "id  integer primary key AUTO_INCREMENT,"\
        "activity_id int NOT NULL,"\
        "person_id int NOT NULL,"\
        "capacity_id int NOT NULL,"\
        "authority_id int NOT NULL,"\
        "paid text NULL,"\
        "attended text NULL)",
        "insert into booking (activity_id, person_id, capacity_id, authority_id) values (1, 4, 5, 7)",
        "insert into booking (activity_id, person_id, capacity_id, authority_id) values (2, 4, 5, 7)",
        "insert into booking (activity_id, person_id, capacity_id, authority_id) values (3, 4, 5, 7)",
        "insert into booking (activity_id, person_id, capacity_id, authority_id) values (4, 4, 5, 7)",
        "insert into booking (activity_id, person_id, capacity_id, authority_id) values (5, 4, 5, 7)",
        "insert into booking (activity_id, person_id, capacity_id, authority_id) values (1, 5, 5, 8)",
        "insert into booking (activity_id, person_id, capacity_id, authority_id) values (2, 5, 5, 8)",
        "insert into booking (activity_id, person_id, capacity_id, authority_id) values (3, 5, 5, 8)",
        "insert into booking (activity_id, person_id, capacity_id, authority_id) values (4, 5, 5, 8)",
        "insert into booking (activity_id, person_id, capacity_id, authority_id) values (5, 5, 5, 8)",
        "insert into booking (activity_id, person_id, capacity_id, authority_id) values (1, 6, 5, 9)",
        "insert into booking (activity_id, person_id, capacity_id, authority_id) values (2, 6, 5, 9)",
        "insert into booking (activity_id, person_id, capacity_id, authority_id) values (3, 6, 5, 9)",
        "insert into booking (activity_id, person_id, capacity_id, authority_id) values (4, 6, 5, 9)",
        "insert into booking (activity_id, person_id, capacity_id, authority_id) values (5, 6, 5, 9)",

        "insert into booking (activity_id, person_id, capacity_id, authority_id) values (1, 1, 1, 10)",
        "insert into booking (activity_id, person_id, capacity_id, authority_id) values (2, 2, 2, 10)",
        "insert into booking (activity_id, person_id, capacity_id, authority_id) values (3, 3, 4, 10)",
        "insert into booking (activity_id, person_id, capacity_id, authority_id) values (4, 1, 1, 10)",
        "insert into booking (activity_id, person_id, capacity_id, authority_id) values (5, 2, 2, 10)",
        "insert into booking (activity_id, person_id, capacity_id, authority_id) values (5, 3, 4, 10)",

        'drop view if exists booking_view',
        "create view booking_view as "\
        "select booking.id as id, activity_tb.activity as activity, "\
        "person_tb.person as person, capacity_tb.capacity as capacity, "\
        "(select person from person_tb where id = booking.authority_id) as authority "\
        "from booking, activity_tb, person_tb, capacity_tb "\
        "where booking.activity_id =  activity_tb.id "\
        "and booking.person_id = person_tb.id "\
        "and booking.capacity_id = capacity_tb.id"
        ]
        cursor = self.cnx.cursor()
        for string in strings:
            if self.dsn == 'sqlite':
                string = re.sub(r'AUTO_INCREMENT', "AUTOINCREMENT", string)
                try:
                    cursor.execute (string)
                except sqlite3.Error as e:
                    html += f'An error occurred: {e.args[0]}' 
            else:
                try:
                    cursor.execute (string)
                except mysql.connector.Error as err:
                    html += "Failed creating database: {}".format(err)

        cursor.close()
        return html

    #####################################################
    #                                                   #
    # Close                                             #
    #                                                   #
    #####################################################

    def Close(self):
        cursor = self.cnx.cursor()
        
        if self.dsn == 'mysql':
            #cursor.commit()
            cursor.close()
        else:
            self.cnx.commit()
            self.cnx.close()
            '''
            cursor.execute(f"select * from sqlite_master where type='table'")
            for row in cursor:
              print(row) 
            cursor.execute(f"select * from sqlite_master where type='view'")
            for row in cursor:
              print(row) 
            '''
    
    #####################################################
    #                                                   #
    # RowExists                                           #
    #                                                   #
    #####################################################

    def RowExists(self, sql):
        cursor = self.cnx.cursor()
        cursor.execute(sql)
        
        for row in cursor:
            return True
            
        return False

    #####################################################
    #                                                   #
    # Display                                           #
    #                                                   #
    #####################################################

    def Display(self, sql):
        global REQUEST
        html = ''#sql+'<br />'
        matches = re.search(r'from\s+(\S+)', sql)
        view = matches.group(1)
        table = re.sub(r'_view', "", matches.group(1)) #preg_replace ("/_view/i", "", $view);
        html += "<div id=\"tablehead\"><h2>"+re.sub(r'_tb$', '', table)+"</h2></div>\n"
        html += f'<a href="{self.action}?table={table}&row=-1">new item</a>'
        html += '<table id="Schlumpf">'
        colTypes = self.FetchColumnTypes (view)
        #pprint (colTypes)
        cursor = self.cnx.cursor()
        cursor.execute(sql)
        colname=[]
        html += '<tr>'
        i=0
        for column in list(map(lambda x: x[0], cursor.description)):
            if 'dir' in REQUEST:
                if REQUEST['dir'][0] == 'asc':
                    html += f'<th><a href="{self.action}?table={view}&order={column}&dir=desc">{column}</a></th>'
                else:
                    html += f'<th><a href="{self.action}?table={view}&order={column}&dir=asc">{column}</a></th>'
            else:
                html += f'<th><a href="{self.action}?table={view}&order={column}&dir=asc">{column}</a></th>'
            colname.insert(i, column)
            i = i+1
        html += '</tr>'
        
        for row in cursor:
            html += '<tr>'
            i=0
            for col in row:
                if colname[i] == 'id':
                    html += f'<td><a href="{self.action}?table={table}&row={col}">{col}</a></td>'
                else:
                    #mytype = colTypes[colname[i]]
                    html += f'<td>{col}</td>' #f'<td>{col} ({mytype})</td>'
                i = i+1
            html += '</tr>'
        
        html += '</table>'
        return html

    #####################################################
    #                                                   #
    # PostTable                                         #
    #                                                   #
    #####################################################

    def PostTable(self):
        global REQUEST
        sql = ''
        table = ''
        button = ''
        html = ''
        rowid = 0
        if 'rowid' in REQUEST:
            rowid = int(REQUEST['rowid'][0])
        if 'table' in REQUEST:
            table = REQUEST['table'][0]
        if 'button' in REQUEST:
            button = REQUEST['button'][0]

        if button == 'DELETE':
            rowid *= -1

        if button == 'NEW':
            rowid = -1

        REQUEST.pop('rowid', None)        
        REQUEST.pop('table', None)        
        REQUEST.pop('button', None)        
        
        html = f'<hr>rowid={rowid} table={table} button={button}<hr>'
        
        if (rowid == -1) and (button == 'NEW'):
            sql = f"insert into {table} ("
            j = 0;
            for field, value in REQUEST.items():
                if j != 0:
                    sql +=  ", "   
                    
                sql += field
                j=j+1
            sql += ") values ("
            
            j = 0
            for field, value in REQUEST.items():
                if j != 0:
                    sql +=  ", "   
                    
                sql += repr(value[0]).strip()
                
                j=j+1
                        
            sql += ");"
            #html += '<hr>**** INSERT PostTable ' + sql + ' All done!<br />'

        elif (button == 'SYNC'):
            sql = f"insert into {table} ("
            j = 0;
            for field, value in REQUEST.items():
                if j != 0:
                    sql +=  ", "   
                    
                sql += field
                j=j+1
            sql += ") values ("
            
            j = 0
            for field, value in REQUEST.items():
                if j != 0:
                    sql +=  ", "   
                
                sql += repr(re.sub('\n', '', str(value[0]))).strip()
                
                j=j+1
                        
            sql += ");"
            #html += '<hr>**** SYNC INSERT PostTable ' + sql + ' All done!<br />'
            
        elif (int(rowid) > 0) and (button == 'SAVE'):
            sql = f"update {table} set "
            
            j = 0
            for field, value in REQUEST.items():
                if j != 0:
                    sql +=  ", "
                    
                sql += field
                sql += " = ";
                sql += repr(re.sub('\n', '', str(value[0]))).strip()
                    
                j=j+1
                        
            sql += f" where id = {rowid};"
            #html += '<hr>**** UPDATE PostTable ' + sql + ' All done!<br />'
        elif (int(rowid) < 0) and (button == 'DELETE'):
            rowid = abs(rowid)
            sql = f"delete from {table} where id = {rowid};"
            #html += '<hr>**** DELETE PostTable ' + sql + ' All done!<br />'
            
        cursor = self.cnx.cursor()

        if self.dsn == 'sqlite':
            try:
                cursor.execute (sql)
            except sqlite3.Error as e:
                html += f'An error occurred: {e.args[0]} <br />with {sql}<hr>' 
        else:
            try:
                cursor.execute (sql)
            except mysql.connector.Error as err:
                html += "Failed sql statement: {}".format(err) + ' <br />with ' +sql + "<hr>"
        
        cursor.close()
        
        html += '<hr>PostTable '+sql+' All done!<br />'
        return html
     
     
    #####################################################
    #                                                   #
    # EditTable                                         #
    #                                                   #
    #####################################################

    def EditTable (self, table, row):
        colTypes  = self.FetchColumnTypes(table)
        colValues = self.FetchColumnValues(table, row)
        
        html = f'<form class="edittable" name="myform" action="{self.action}" method="post" enctype="multipart/form-data">'
        html += '<table id="Schlumpf">'
        for key, value in colTypes.items():
            if key.lower() != 'id':
                if re.search('\_id$', key): # a lookup field
                    lookupName = re.sub(r'\_id$', '', key) # $lookupName = preg_replace("/_id$/", "", $key);

                    lookup = re.sub(r'authority', 'person', lookupName) # bug fix 7 Feb 2019

                    html += f"<tr><td>{lookupName}</td><td>"
                    html += f'<SELECT NAME="{key}">'
                    luid = luval = ''

                    cursor = self.cnx.cursor()
                    cursor.execute(f'select id, {lookup} from {lookup}_tb order by {lookup}')
                    for lurow in cursor:
                        selected = ''
                        i=0
                        for lucol in lurow:
                            if i == 0:
                                luid = lucol
                            else:
                                luval = lucol          
                                if int(row) != -1:
                                    if colValues is True :
                                        if colValues[key] == luid:
                                            selected = "selected"
                            i=i+1
                            
                        html += f'<OPTION VALUE="{luid}" {selected}>{luval}'                   
                    html += "</td></tr>\n"
                    
                else:    
                    html += f'<tr><td>{key}</td><td>'
                    if not colValues :
                        myvalue = ''
                    else :
                        myvalue = colValues[key]
                        
                    if key in ['date', 'datetime']:
                        html += f'<input type="datetime-local" name="{key}" value="{myvalue}">'
                        
                    elif (key == 'int') or (key == 'integer') or (key == 'float'):
                        html += f'<input type="number-local" name="{key}" value="{myvalue}">'

                    elif key in ['content', 'excerpt']:
                        html += f'<textarea name="{key}" rows="4" cols="75">{myvalue}</textarea>'
                    else:
                        html += f'<input type="text" name="{key}" size=75 value="{myvalue}">'
                        
                    html += "</td></tr>\n"    
            
        html +=  f'<tr><td><input type="hidden" name="rowid" value="{row}"/>'
        html +=  f'<input type="hidden" name="table" value="{table}"/>'
        if int(row) == -1:
            html +=  f'</td><td><input type="submit" name="button" value="NEW"/></td</tr>'
        else:
            html +=  f'<input type="submit" name="button" OnClick="return confirm(\'Are you sure you want to delete this record ?\');"value="DELETE"/></td><td>\n'
            html +=  f'<input type="submit" name="button" value="SAVE"/></td</tr>\n'
            
        html +=  f'</table>\n</form>'
        return html
    
    #####################################################
    #                                                   #
    # FetchColumnTypes                                  #
    #                                                   #
    #####################################################

    def FetchColumnTypes(self, table):
        cursor = self.cnx.cursor()
        cols = {}
        if self.dsn == 'sqlite':
            cursor.execute(f"select * from sqlite_master where type='table' and name='{table}'")
            i=0
            mycol=0
            for column in list(map(lambda x: x[0], cursor.description)):
                #print (column)
                if column == 'sql':
                    mycol = i
                i = i+1

            for row in cursor:
                sql = row[mycol]
                
                matches = re.search(r'\((.+)\)', sql)
                sqldef = matches.group(1)
                fields = re.split(r',', sqldef)
                
                for field in fields:
                    matches = re.search(r'(\S+)\s+(\w+)', field)
                    name = matches.group(1)
                    attribute = matches.group(2)
                    cols[name] = attribute
                
        else:
            cursor.execute(f"select column_name, data_type from information_schema.columns where table_name = '{table}' and table_schema = '{self.db_name}'")
            for row in cursor:
                cols[row[0]] = row[1]
             
        return cols

    #####################################################
    #                                                   #
    # FetchColumnValues                                 #
    #                                                   #
    #####################################################

    def FetchColumnValues (self, table, id):    
        cursor = self.cnx.cursor()
        cols = {}
        
        if id == -1:
            idd = 1
        else:
            idd = id
        
        cursor.execute(f'select * from {table} where id = {idd}')
        colname=[]
        i=0
        for column in list(map(lambda x: x[0], cursor.description)):
            colname.insert(i, column)
            i = i+1
        
        for row in cursor:
            i=0
            for col in row:
                if id == -1:
                    cols[colname[i]] = ''
                else:
                    cols[colname[i]] = col
                i=i+1
        return cols

#####################################################
#                                                   #
# web server                                        #
#                                                   #
#####################################################

class S(SimpleHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        """Serve a GET request."""
        global REQUEST
        print ('self.path is '+self.path)
        if (self.path != '/') and (not re.search(r'^\/\?', self.path)):
            print ("serving a file..."+self.path)  # serving a file.../?menu=blog
            f = self.send_head()
            if f:
                try:
                    self.copyfile(f, self.wfile)
                finally:
                    f.close()
        else:
            print ("parsing and dispatch")
            logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
            self._set_response()
            (scheme, netloc, pathology, params, query, fragment) = urlparse (self.path)  # returns a tuple   
            #ulp = parse_qs (query)
            REQUEST.clear()
            REQUEST = parse_qs (query)
            if len(query) == 0:
                method = ''
            else:
                method = 'GET'
                
            d = Dispatcher()
            self.wfile.write(d.run(pathology, method))       

    def list_directory(self, path): #disable it
        return None

    def do_POST(self):
        global REQUEST
        REQUEST.clear()
        
        ctype, pdict = cgi.parse_header(self.headers['content-type'])
        
        boundary = pdict['boundary'].encode("utf-8") # some kludge
        pdict['boundary'] = boundary # to circumvent bugs in cgi
        pdict['CONTENT-LENGTH'] = int(self.headers['content-length'])
        
        if ctype == 'multipart/form-data':
            REQUEST = cgi.parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers['content-length'])
            REQUEST = cgi.parse_qs(
                    self.rfile.read(length), 
                    keep_blank_values=1)
        else:
            REQUEST = {}
            
        pprint (REQUEST)
        path = ''
        d = Dispatcher()
        self._set_response()
        self.wfile.write(d.run(path, 'POST'))       

#####################################################
#                                                   #
# main loop                                         #
#                                                   #
#####################################################

def run(server_class=HTTPServer, handler_class=S, port=8000):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info(f'Starting httpd on port {port}...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')

if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
