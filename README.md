# Quantified-Self-Tracking-app
1.Create a virtual environment.
Use the following commands to create and activate a virtual environment:
   
  python -m venv venv_name
  
  /.venv_name/Scripts/activate

2. Install the applications in the venv using commands:
   
  pip install flask
  
  pip install flask-SQLAlchemy
  
  pip install matplotlib

  OR 
  You can create a file 'requirements.txt' and list the required libraries.
  In the terminal run : pip install -r requirements.txt
  
3. Create instance for database files:
   On the terminal type the following commands-

   python

   from app import app,db

   app.app_context().push()

   db.create_all()

   exit()
   
5. Run the main file and click on the link of the server to open the web page.
  
  python app.py

5. Now the website is ready to use.
