# app.py
import tempfile
from flask import Flask, render_template, request, send_file, redirect, url_for
from config import Config
from models import db, Parameter, UploadSession
from utils.dxf_parser import extract_parameters_from_dxf
from utils.excel_exporter import generate_excel
import os
from sqlalchemy import text, create_engine
from sqlalchemy.exc import OperationalError

app = Flask(__name__)
app.config.from_object(Config)



engine = create_engine('mysql+pymysql://root:Yuvisingh%401810@localhost:3306/')

try:
    # Create the database if it doesn't exist
    with engine.connect() as conn:
        conn.execute(text("CREATE DATABASE IF NOT EXISTS python_task"))  # Make sure to use the correct database name 'parameters'
        print("Database 'python_task' is ready.")
except OperationalError as e:
    print(f"Error while connecting to MySQL: {e}")
    exit()

# Now initialize the database for your Flask app
db.init_app(app)

with app.app_context():
    db.create_all()  # Create tables if they do not exist
    
# Define a permanent location for the Excel file
PERMANENT_EXCEL_PATH = os.path.join(app.root_path, 'static/uploads', 'dxf_parameters.xlsx')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'dxf_file' not in request.files:
        return 'No file part', 400

    file = request.files['dxf_file']
    if file.filename == '':
        return 'No selected file', 400

    # Ensure file extension is DXF
    if not file.filename.lower().endswith('.dxf'):
        return 'Invalid file format. Please upload a DXF file.', 400

    if file:
        # Create a temporary directory for saving the DXF file
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, file.filename)
            file.save(file_path)  

            parameters = extract_parameters_from_dxf(file_path)

            if not parameters:
                return "No parameters extracted from DXF file.", 400
            
          
            upload_session = UploadSession(filename=file.filename)
            db.session.add(upload_session)
            db.session.commit()

            
            for param in parameters:
                new_param = Parameter(
                    session_id=upload_session.id,
                    parameter_name=param['name'],
                    parameter_value=param['value']
                )
                db.session.add(new_param)
            db.session.commit()

            # Generate Excel file in a permanent location
            generate_excel(parameters, PERMANENT_EXCEL_PATH)

            # Redirect to results page with download link
            return redirect(url_for('results', session_id=upload_session.id))

        
@app.route('/results')
def results():
    session_id = request.args.get('session_id')
    if not session_id:
        return "Session ID missing", 400

    # Fetch parameters for the specific session
    parameters = Parameter.query.filter_by(session_id=session_id).all()

    # Group parameters by unique names
    parameter_dict = {}
    for param in parameters:
        if param.parameter_name not in parameter_dict:
            parameter_dict[param.parameter_name] = []
        parameter_dict[param.parameter_name].append(param.parameter_value)

    # Find the maximum length of parameter values
    max_rows = max(len(values) for values in parameter_dict.values())

    # Ensure each list in parameter_dict has the same number of values (fill missing values with an empty string)
    for values in parameter_dict.values():
        values.extend([''] * (max_rows - len(values)))

    return render_template('result.html', parameter_dict=parameter_dict, max_rows=max_rows)



@app.route('/download')
def download():
    # Send the Excel file as a download
    return send_file(PERMANENT_EXCEL_PATH, as_attachment=True, download_name='dxf_parameters.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

if __name__ == '__main__':
    app.run(debug=True)
