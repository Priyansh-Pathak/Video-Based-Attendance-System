# import os
# import shutil
# from flask import Flask, request, render_template, send_file, jsonify, send_from_directory, redirect, url_for
# from werkzeug.utils import secure_filename
# import pandas as pd
# from datetime import datetime
# from attendance_recognition import process_video_and_mark_attendance

# app = Flask(__name__)
# UPLOAD_FOLDER = 'uploads'
# ATTENDANCE_FOLDER = 'attendance_reports'
# UNKNOWN_FOLDER = 'static/unknown_faces'
# EXTRACTED_FOLDER = 'extracted_faces'

# os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# os.makedirs(ATTENDANCE_FOLDER, exist_ok=True)
# os.makedirs(UNKNOWN_FOLDER, exist_ok=True)
# os.makedirs(EXTRACTED_FOLDER, exist_ok=True)

# attendance_cache = {}

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/upload', methods=['POST'])
# def upload_video():
#     global attendance_cache
#     video_file = request.files.get('video')
#     if video_file:
#         filename = secure_filename(video_file.filename)
#         save_path = os.path.join(UPLOAD_FOLDER, filename)
#         video_file.save(save_path)

#         # Process video attendance
#         attendance_cache = process_video_and_mark_attendance(save_path)

#         # Save attendance to Excel
#         date_str = datetime.now().strftime("%Y-%m-%d_%H-%M")
#         excel_path = os.path.join(ATTENDANCE_FOLDER, f"attendance_{date_str}.xlsx")
#         df = pd.DataFrame(list(attendance_cache.items()), columns=["Name", "Status"])
#         df.to_excel(excel_path, index=False)

#         return send_file(excel_path, as_attachment=True)

#     return "❌ Video upload failed", 400

# @app.route('/identified-names')
# def get_identified_names():
#     global attendance_cache
#     present = [name for name, status in attendance_cache.items() if status == "Present"]
#     absent = [name for name, status in attendance_cache.items() if status == "Absent"]
#     return jsonify({"present": present, "absent": absent})

# # -------- Bulk Unknown Face Labeling Dashboard -------- #

# @app.route('/label-unknowns', methods=['GET'])
# def label_unknowns():
#     files = sorted(os.listdir(UNKNOWN_FOLDER))
#     if not files:
#         return "<h3>✅ All unknown faces have been labeled!</h3>"

#     # Generate HTML dashboard with grid input form
#     html = """
#     <!DOCTYPE html>
#     <html lang="en">
#     <head>
#       <meta charset="UTF-8" />
#       <meta name="viewport" content="width=device-width, initial-scale=1" />
#       <title>Unknown Faces Labeling Dashboard</title>
#       <style>
#         body {
#           font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
#           background: #f9fafb;
#           padding: 30px 15px;
#           color: #222;
#           display: flex;
#           justify-content: center;
#           min-height: 100vh;
#           margin: 0;
#         }
#         .container {
#           max-width: 900px;
#           width: 100%;
#           background: #fff;
#           border-radius: 8px;
#           box-shadow: 0 2px 12px rgba(0,0,0,0.1);
#           padding: 25px 30px;
#           box-sizing: border-box;
#         }
#         h2 {
#           text-align: center;
#           color: #0277bd;
#           margin-bottom: 25px;
#           font-weight: 700;
#         }
#         form {
#           width: 100%;
#         }
#         .grid {
#           display: grid;
#           grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
#           gap: 18px;
#         }
#         .card {
#           border: 1px solid #ccc;
#           border-radius: 8px;
#           padding: 12px 8px 20px 8px;
#           text-align: center;
#           background: #e1f5fe;
#           box-sizing: border-box;
#           box-shadow: inset 0 0 5px #81d4fa;
#         }
#         .card img {
#           width: 140px;
#           height: auto;
#           border-radius: 6px;
#           margin-bottom: 8px;
#           border: 2px solid #81d4fa;
#         }
#         .card input {
#           width: 90%;
#           padding: 8px 10px;
#           font-size: 14px;
#           border: 2px solid #81d4fa;
#           border-radius: 6px;
#           box-sizing: border-box;
#         }
#         .card input:focus {
#           border-color: #0288d1;
#           outline: none;
#         }
#         button {
#           margin-top: 25px;
#           width: 100%;
#           background-color: #0288d1;
#           color: white;
#           font-weight: 700;
#           font-size: 16px;
#           border: none;
#           padding: 14px;
#           border-radius: 8px;
#           cursor: pointer;
#           transition: background-color 0.3s ease;
#         }
#         button:hover {
#           background-color: #0277bd;
#         }
#       </style>
#     </head>
#     <body>
#       <div class="container">
#         <h2>🆕 Unknown Faces Labeling Dashboard</h2>
#         <form method="POST" action="/submit-multiple-labels" autocomplete="off">
#           <div class="grid">
#     """

#     for file in files:
#         html += f"""
#           <div class="card">
#             <img src="/static/unknown_faces/{file}" alt="Unknown face {file}">
#             <input type="text" name="{file}" placeholder="Enter name" />
#             <small>{file}</small>
#           </div>
#         """

#     html += """
#           </div>
#           <button type="submit">✅ Save All Labels</button>
#         </form>
#       </div>
#     </body>
#     </html>
#     """
#     return html

# @app.route('/submit-multiple-labels', methods=['POST'])
# def submit_multiple_labels():
#     for filename, name in request.form.items():
#         name = name.strip()
#         if name:
#             person_dir = os.path.join(EXTRACTED_FOLDER, name)
#             os.makedirs(person_dir, exist_ok=True)

#             src = os.path.join(UNKNOWN_FOLDER, filename)
#             dst = os.path.join(person_dir, filename)
#             if os.path.exists(src):
#                 shutil.move(src, dst)
#     return redirect(url_for("label_unknowns"))

# # -------- JSON & Static File Routes -------- #

# @app.route('/unknowns')
# def list_unknown_faces():
#     return jsonify(sorted(os.listdir(UNKNOWN_FOLDER)))

# @app.route('/unknown/<filename>')
# def get_unknown_face(filename):
#     return send_from_directory(UNKNOWN_FOLDER, filename)

# if __name__ == '__main__':
#     app.run(debug=True)
# import os
# import shutil
# from flask import Flask, request, render_template, send_file, jsonify, send_from_directory, redirect, url_for
# from werkzeug.utils import secure_filename
# import pandas as pd
# from datetime import datetime
# from attendance_recognition import process_video_and_mark_attendance

# app = Flask(__name__)
# UPLOAD_FOLDER = 'uploads'
# ATTENDANCE_FOLDER = 'attendance_reports'
# UNKNOWN_FOLDER = 'static/unknown_faces'
# EXTRACTED_FOLDER = 'extracted_faces'

# os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# os.makedirs(ATTENDANCE_FOLDER, exist_ok=True)
# os.makedirs(UNKNOWN_FOLDER, exist_ok=True)
# os.makedirs(EXTRACTED_FOLDER, exist_ok=True)

# attendance_cache = {}

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/upload', methods=['POST'])
# def upload_video():
#     global attendance_cache
#     video_file = request.files.get('video')
#     if video_file:
#         filename = secure_filename(video_file.filename)
#         save_path = os.path.join(UPLOAD_FOLDER, filename)
#         video_file.save(save_path)

#         # Process video attendance
#         attendance_cache = process_video_and_mark_attendance(save_path)

#         # Save attendance to Excel
#         date_str = datetime.now().strftime("%Y-%m-%d_%H-%M")
#         excel_path = os.path.join(ATTENDANCE_FOLDER, f"attendance_{date_str}.xlsx")
#         df = pd.DataFrame(list(attendance_cache.items()), columns=["Name", "Status"])
#         df.to_excel(excel_path, index=False)

#         return send_file(excel_path, as_attachment=True)

#     return "❌ Video upload failed", 400

# @app.route('/identified-names')
# def get_identified_names():
#     global attendance_cache
#     present = [name for name, status in attendance_cache.items() if status == "Present"]
#     absent = [name for name, status in attendance_cache.items() if status == "Absent"]
#     return jsonify({"present": present, "absent": absent})

# # -------- Bulk Unknown Face Labeling Dashboard -------- #

# @app.route('/label-unknowns', methods=['GET'])
# def label_unknowns():
#     files = sorted(os.listdir(UNKNOWN_FOLDER))
#     if not files:
#         return "<h3>✅ All unknown faces have been labeled!</h3>"

#     # Generate HTML dashboard with grid input form
#     html = """
#     <!DOCTYPE html>
#     <html lang="en">
#     <head>
#       <meta charset="UTF-8" />
#       <meta name="viewport" content="width=device-width, initial-scale=1" />
#       <title>Unknown Faces Labeling Dashboard</title>
#       <style>
#         body {
#           font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
#           background: #f9fafb;
#           padding: 30px 15px;
#           color: #222;
#           display: flex;
#           justify-content: center;
#           min-height: 100vh;
#           margin: 0;
#         }
#         .container {
#           max-width: 900px;
#           width: 100%;
#           background: #fff;
#           border-radius: 8px;
#           box-shadow: 0 2px 12px rgba(0,0,0,0.1);
#           padding: 25px 30px;
#           box-sizing: border-box;
#         }
#         h2 {
#           text-align: center;
#           color: #0277bd;
#           margin-bottom: 25px;
#           font-weight: 700;
#         }
#         form {
#           width: 100%;
#         }
#         .grid {
#           display: grid;
#           grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
#           gap: 18px;
#         }
#         .card {
#           border: 1px solid #ccc;
#           border-radius: 8px;
#           padding: 12px 8px 20px 8px;
#           text-align: center;
#           background: #e1f5fe;
#           box-sizing: border-box;
#           box-shadow: inset 0 0 5px #81d4fa;
#         }
#         .card img {
#           width: 140px;
#           height: auto;
#           border-radius: 6px;
#           margin-bottom: 8px;
#           border: 2px solid #81d4fa;
#         }
#         .card input {
#           width: 90%;
#           padding: 8px 10px;
#           font-size: 14px;
#           border: 2px solid #81d4fa;
#           border-radius: 6px;
#           box-sizing: border-box;
#         }
#         .card input:focus {
#           border-color: #0288d1;
#           outline: none;
#         }
#         button {
#           margin-top: 25px;
#           width: 100%;
#           background-color: #0288d1;
#           color: white;
#           font-weight: 700;
#           font-size: 16px;
#           border: none;
#           padding: 14px;
#           border-radius: 8px;
#           cursor: pointer;
#           transition: background-color 0.3s ease;
#         }
#         button:hover {
#           background-color: #0277bd;
#         }
#         a {
#           color: #0288d1;
#           font-weight: 600;
#           text-decoration: none;
#         }
#         a:hover {
#           text-decoration: underline;
#         }
#         .nav {
#           margin-bottom: 25px;
#           text-align: center;
#         }
#       </style>
#     </head>
#     <body>
#       <div class="container">
#         <div class="nav">
#           <a href="/">← Back to Upload Video</a> |
#           <a href="/students">Manage Students</a>
#         </div>
#         <h2>🆕 Unknown Faces Labeling Dashboard</h2>
#         <form method="POST" action="/submit-multiple-labels" autocomplete="off">
#           <div class="grid">
#     """

#     for file in files:
#         html += f"""
#           <div class="card">
#             <img src="/static/unknown_faces/{file}" alt="Unknown face {file}">
#             <input type="text" name="{file}" placeholder="Enter name" />
#             <small>{file}</small>
#           </div>
#         """

#     html += """
#           </div>
#           <button type="submit">✅ Save All Labels</button>
#         </form>
#       </div>
#     </body>
#     </html>
#     """
#     return html

# @app.route('/submit-multiple-labels', methods=['POST'])
# def submit_multiple_labels():
#     for filename, name in request.form.items():
#         name = name.strip()
#         if name:
#             person_dir = os.path.join(EXTRACTED_FOLDER, name)
#             os.makedirs(person_dir, exist_ok=True)

#             src = os.path.join(UNKNOWN_FOLDER, filename)
#             dst = os.path.join(person_dir, filename)
#             if os.path.exists(src):
#                 shutil.move(src, dst)
#     return redirect(url_for("label_unknowns"))

# # -------- Students Management -------- #

# @app.route('/students')
# def list_students():
#     students = sorted(os.listdir(EXTRACTED_FOLDER))
#     student_info = []
#     for student in students:
#         path = os.path.join(EXTRACTED_FOLDER, student)
#         if os.path.isdir(path):
#             count = len([f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))])
#             student_info.append({'name': student, 'image_count': count})
#     html = """
#     <!DOCTYPE html>
#     <html lang="en">
#     <head>
#       <meta charset="UTF-8" />
#       <meta name="viewport" content="width=device-width, initial-scale=1" />
#       <title>Manage Students</title>
#       <style>
#         body {
#           font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
#           background: #f9fafb;
#           padding: 30px 15px;
#           color: #222;
#           min-height: 100vh;
#           margin: 0;
#           display: flex;
#           justify-content: center;
#         }
#         .container {
#           max-width: 700px;
#           width: 100%;
#           background: #fff;
#           border-radius: 8px;
#           box-shadow: 0 2px 12px rgba(0,0,0,0.1);
#           padding: 25px 30px;
#           box-sizing: border-box;
#         }
#         h2 {
#           text-align: center;
#           color: #0277bd;
#           margin-bottom: 25px;
#           font-weight: 700;
#         }
#         table {
#           width: 100%;
#           border-collapse: collapse;
#         }
#         th, td {
#           padding: 12px 10px;
#           border-bottom: 1px solid #ddd;
#           text-align: left;
#           font-size: 16px;
#         }
#         th {
#           background: #e1f5fe;
#           color: #0277bd;
#         }
#         button {
#           background: #f44336;
#           color: white;
#           border: none;
#           padding: 8px 14px;
#           border-radius: 6px;
#           cursor: pointer;
#           font-weight: 600;
#           transition: background-color 0.25s ease;
#         }
#         button:hover {
#           background: #d32f2f;
#         }
#         a {
#           color: #0288d1;
#           font-weight: 600;
#           text-decoration: none;
#         }
#         a:hover {
#           text-decoration: underline;
#         }
#         .nav {
#           margin-bottom: 20px;
#           text-align: center;
#         }
#       </style>
#     </head>
#     <body>
#       <div class="container">
#         <div class="nav">
#           <a href="/">← Back to Upload Video</a> |
#           <a href="/label-unknowns">Label Unknown Faces</a>
#         </div>
#         <h2>Manage Saved Students</h2>
#         <table>
#           <thead>
#             <tr><th>Name</th><th>Number of Images</th><th>Action</th></tr>
#           </thead>
#           <tbody>
#     """
#     for s in student_info:
#         html += f"""
#           <tr>
#             <td>{s['name']}</td>
#             <td>{s['image_count']}</td>
#             <td>
#               <form method="POST" action="/delete-student/{s['name']}" onsubmit="return confirm('Are you sure you want to delete this student and all their data?');">
#                 <button type="submit">Delete</button>
#               </form>
#             </td>
#           </tr>
#         """
#     html += """
#           </tbody>
#         </table>
#       </div>
#     </body>
#     </html>
#     """
#     return html

# @app.route('/delete-student/<name>', methods=['POST'])
# def delete_student(name):
#     student_dir = os.path.join(EXTRACTED_FOLDER, name)
#     if os.path.exists(student_dir) and os.path.isdir(student_dir):
#         shutil.rmtree(student_dir)
#     global attendance_cache
#     attendance_cache.pop(name, None)
#     return redirect(url_for('list_students'))

# # -------- JSON & Static File Routes -------- #

# @app.route('/unknowns')
# def list_unknown_faces():
#     return jsonify(sorted(os.listdir(UNKNOWN_FOLDER)))

# @app.route('/unknown/<filename>')
# def get_unknown_face(filename):
#     return send_from_directory(UNKNOWN_FOLDER, filename)

# if __name__ == '__main__':
#     app.run(debug=True)
import os
import shutil
from flask import Flask, request, render_template, send_file, jsonify, send_from_directory, redirect, url_for
from werkzeug.utils import secure_filename
import pandas as pd
from datetime import datetime
from attendance_recognition import process_video_and_mark_attendance

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
ATTENDANCE_FOLDER = 'attendance_reports'
UNKNOWN_FOLDER = 'static/unknown_faces'
EXTRACTED_FOLDER = 'extracted_faces'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ATTENDANCE_FOLDER, exist_ok=True)
os.makedirs(UNKNOWN_FOLDER, exist_ok=True)
os.makedirs(EXTRACTED_FOLDER, exist_ok=True)

attendance_cache = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_video():
    global attendance_cache
    video_file = request.files.get('video')
    if video_file:
        filename = secure_filename(video_file.filename)
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        video_file.save(save_path)

        # Process video attendance
        attendance_cache = process_video_and_mark_attendance(save_path)

        # Save attendance to Excel
        date_str = datetime.now().strftime("%Y-%m-%d_%H-%M")
        excel_path = os.path.join(ATTENDANCE_FOLDER, f"attendance_{date_str}.xlsx")
        df = pd.DataFrame(list(attendance_cache.items()), columns=["Name", "Status"])
        df.to_excel(excel_path, index=False)

        return send_file(excel_path, as_attachment=True)

    return "❌ Video upload failed", 400

@app.route('/identified-names')
def get_identified_names():
    global attendance_cache
    present = [name for name, status in attendance_cache.items() if status == "Present"]
    absent = [name for name, status in attendance_cache.items() if status == "Absent"]
    return jsonify({"present": present, "absent": absent})

@app.route('/label-unknowns', methods=['GET'])
def label_unknowns():
    files = sorted(os.listdir(UNKNOWN_FOLDER))
    if not files:
        return "<h3>✅ All unknown faces have been labeled!</h3><br><a href='/'>← Back to Upload Video</a>"

    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <title>Unknown Faces Labeling Dashboard</title>
      <style>
        body {
          font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
          background: #f9fafb;
          padding: 30px 15px;
          color: #222;
          display: flex;
          justify-content: center;
          min-height: 100vh;
          margin: 0;
        }
        .container {
          max-width: 900px;
          width: 100%;
          background: #fff;
          border-radius: 8px;
          box-shadow: 0 2px 12px rgba(0,0,0,0.1);
          padding: 25px 30px;
          box-sizing: border-box;
        }
        h2 {
          text-align: center;
          color: #0277bd;
          margin-bottom: 25px;
          font-weight: 700;
        }
        form {
          width: 100%;
        }
        .grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
          gap: 18px;
        }
        .card {
          border: 1px solid #ccc;
          border-radius: 8px;
          padding: 12px 8px 20px 8px;
          text-align: center;
          background: #e1f5fe;
          box-sizing: border-box;
          box-shadow: inset 0 0 5px #81d4fa;
        }
        .card img {
          width: 140px;
          height: auto;
          border-radius: 6px;
          margin-bottom: 8px;
          border: 2px solid #81d4fa;
        }
        .card input {
          width: 90%;
          padding: 8px 10px;
          font-size: 14px;
          border: 2px solid #81d4fa;
          border-radius: 6px;
          box-sizing: border-box;
        }
        .card input:focus {
          border-color: #0288d1;
          outline: none;
        }
        button {
          margin-top: 25px;
          width: 100%;
          background-color: #0288d1;
          color: white;
          font-weight: 700;
          font-size: 16px;
          border: none;
          padding: 14px;
          border-radius: 8px;
          cursor: pointer;
          transition: background-color 0.3s ease;
        }
        button:hover {
          background-color: #0277bd;
        }
        a {
          color: #0288d1;
          font-weight: 600;
          text-decoration: none;
        }
        a:hover {
          text-decoration: underline;
        }
        .nav {
          margin-bottom: 25px;
          text-align: center;
        }
      </style>
    </head>
    <body>
      <div class="container">
        <div class="nav">
          <a href="/">← Back to Upload Video</a> |
          <a href="/students">Manage Students</a>
        </div>
        <h2>🆕 Unknown Faces Labeling Dashboard</h2>
        <form method="POST" action="/submit-multiple-labels" autocomplete="off">
          <div class="grid">
    """

    for file in files:
        html += f"""
          <div class="card">
            <img src="/static/unknown_faces/{file}" alt="Unknown face {file}">
            <input type="text" name="{file}" placeholder="Enter name" />
            <small>{file}</small>
          </div>
        """

    html += """
          </div>
          <button type="submit">✅ Save All Labels</button>
        </form>
      </div>
    </body>
    </html>
    """
    return html

@app.route('/submit-multiple-labels', methods=['POST'])
def submit_multiple_labels():
    for filename, name in request.form.items():
        name = name.strip()
        if name:
            person_dir = os.path.join(EXTRACTED_FOLDER, name)
            os.makedirs(person_dir, exist_ok=True)

            src = os.path.join(UNKNOWN_FOLDER, filename)
            dst = os.path.join(person_dir, filename)
            if os.path.exists(src):
                shutil.move(src, dst)

    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <title>Labels Submitted</title>
      <style>
        body {
          font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
          background: #f9fafb;
          display: flex;
          justify-content: center;
          align-items: center;
          min-height: 100vh;
          margin: 0;
        }
        .box {
          background: #fff;
          padding: 30px 40px;
          border-radius: 10px;
          box-shadow: 0 2px 10px rgba(0,0,0,0.1);
          text-align: center;
        }
        h2 {
          color: #0288d1;
          margin-bottom: 20px;
        }
        a {
          display: inline-block;
          margin-top: 20px;
          padding: 12px 20px;
          background-color: #0288d1;
          color: white;
          text-decoration: none;
          border-radius: 6px;
          font-weight: 600;
          transition: background-color 0.3s ease;
        }
        a:hover {
          background-color: #0277bd;
        }
      </style>
    </head>
    <body>
      <div class="box">
        <h2>✅ Labels submitted successfully!</h2>
        <a href="/">← Back to Upload Video</a>
      </div>
    </body>
    </html>
    """

@app.route('/students')
def list_students():
    students = sorted(os.listdir(EXTRACTED_FOLDER))
    student_info = []
    for student in students:
        path = os.path.join(EXTRACTED_FOLDER, student)
        if os.path.isdir(path):
            count = len([f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))])
            student_info.append({'name': student, 'image_count': count})

    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <title>Manage Students</title>
      <style>
        body {
          font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
          background: #f9fafb;
          padding: 30px 15px;
          color: #222;
          min-height: 100vh;
          margin: 0;
          display: flex;
          justify-content: center;
        }
        .container {
          max-width: 700px;
          width: 100%;
          background: #fff;
          border-radius: 8px;
          box-shadow: 0 2px 12px rgba(0,0,0,0.1);
          padding: 25px 30px;
          box-sizing: border-box;
        }
        h2 {
          text-align: center;
          color: #0277bd;
          margin-bottom: 25px;
          font-weight: 700;
        }
        table {
          width: 100%;
          border-collapse: collapse;
        }
        th, td {
          padding: 12px 10px;
          border-bottom: 1px solid #ddd;
          text-align: left;
          font-size: 16px;
        }
        th {
          background: #e1f5fe;
          color: #0277bd;
        }
        button {
          background: #f44336;
          color: white;
          border: none;
          padding: 8px 14px;
          border-radius: 6px;
          cursor: pointer;
          font-weight: 600;
          transition: background-color 0.25s ease;
        }
        button:hover {
          background: #d32f2f;
        }
        a {
          color: #0288d1;
          font-weight: 600;
          text-decoration: none;
        }
        a:hover {
          text-decoration: underline;
        }
        .nav {
          margin-bottom: 20px;
          text-align: center;
        }
      </style>
    </head>
    <body>
      <div class="container">
        <div class="nav">
          <a href="/">← Back to Upload Video</a> |
          <a href="/label-unknowns">Label Unknown Faces</a>
        </div>
        <h2>Manage Saved Students</h2>
        <table>
          <thead>
            <tr><th>Name</th><th>Number of Images</th><th>Action</th></tr>
          </thead>
          <tbody>
    """
    for s in student_info:
        html += f"""
          <tr>
            <td>{s['name']}</td>
            <td>{s['image_count']}</td>
            <td>
              <form method="POST" action="/delete-student/{s['name']}" onsubmit="return confirm('Are you sure you want to delete this student and all their data?');">
                <button type="submit">Delete</button>
              </form>
            </td>
          </tr>
        """
    html += """
          </tbody>
        </table>
      </div>
    </body>
    </html>
    """
    return html

@app.route('/delete-student/<name>', methods=['POST'])
def delete_student(name):
    student_dir = os.path.join(EXTRACTED_FOLDER, name)
    if os.path.exists(student_dir) and os.path.isdir(student_dir):
        shutil.rmtree(student_dir)
    global attendance_cache
    attendance_cache.pop(name, None)
    return redirect(url_for('list_students'))

@app.route('/unknowns')
def list_unknown_faces():
    return jsonify(sorted(os.listdir(UNKNOWN_FOLDER)))

@app.route('/unknown/<filename>')
def get_unknown_face(filename):
    return send_from_directory(UNKNOWN_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)
