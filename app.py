from flask import Flask, request, render_template, jsonify, redirect, url_for
import pandas as pd
import os
from werkzeug.utils import secure_filename
from flask_wtf.csrf import CSRFProtect
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback_secret_key')
csrf = CSRFProtect(app)

# 使用环境变量或默认路径
data_file = os.environ.get('DATA_FILE', '/tmp/survey_data.xlsx')

# 确保数据文件存在
if not os.path.exists(os.path.dirname(data_file)):
    os.makedirs(os.path.dirname(data_file))

if not os.path.exists(data_file):
    df = pd.DataFrame(columns=[
        'ID', 'First Name', 'Last Name', 'Email', 'Organization',
        'Job Responsibilities', 'Location', 'Coding', 'Requirements',
        'Testing', 'UI Design', 'Project Management', 'Experience'
    ])
    df.to_excel(data_file, index=False)

@app.route('/')
def survey_form():
    logger.info("Survey form page accessed")
    return render_template('survey_form.html')

@app.route('/submit', methods=['POST'])
def submit_response():
    try:
        form_data = {
            'First Name': secure_filename(request.form.get('first_name')),
            'Last Name': secure_filename(request.form.get('last_name')),
            'Email': request.form.get('email'),
            'Organization': secure_filename(request.form.get('organization')),
            'Job Responsibilities': secure_filename(request.form.get('responsibilities')),
            'Location': secure_filename(request.form.get('location')),
            'Coding': request.form.get('coding'),
            'Requirements': request.form.get('requirements'),
            'Testing': request.form.get('testing'),
            'UI Design': request.form.get('ui_design'),
            'Project Management': request.form.get('project_management'),
            'Experience': secure_filename(request.form.get('experience')),
        }
        
        logger.info(f"Form submitted with data: {form_data}")

        try:
            df = pd.read_excel(data_file)
            new_id = df['ID'].max() + 1 if len(df) > 0 else 1
            form_data['ID'] = new_id
            df = pd.concat([df, pd.DataFrame([form_data])], ignore_index=True)
            df.to_excel(data_file, index=False)
            logger.info("Data successfully saved to Excel file")
        except Exception as e:
            logger.error(f"Error saving to Excel: {str(e)}")
            return jsonify({'message': 'Error saving data', 'error': str(e)}), 500

        return redirect(url_for('show_data'))
    
    except Exception as e:
        logger.error(f"Error processing form submission: {str(e)}")
        return jsonify({'message': 'Error processing submission', 'error': str(e)}), 500

@app.route('/data')
def show_data():
    try:
        df = pd.read_excel(data_file)
        data = df.to_dict('records')
        return render_template('data.html', data=data)
    except Exception as e:
        logger.error(f"Error reading data: {str(e)}")
        return jsonify({'message': 'Error reading data', 'error': str(e)}), 500

@app.route('/delete/<int:id>', methods=['POST'])
def delete_record(id):
    try:
        df = pd.read_excel(data_file)
        df = df[df['ID'] != id]
        df.to_excel(data_file, index=False)
        logger.info(f"Record with ID {id} deleted successfully")
        return redirect(url_for('show_data'))
    except Exception as e:
        logger.error(f"Error deleting record: {str(e)}")
        return jsonify({'message': 'Error deleting record', 'error': str(e)}), 500

@app.route('/favicon.ico')
def favicon():
    return '', 204  # Return no content for favicon requests

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


