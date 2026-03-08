from flask import Flask, render_template, request
import os


from analyzer import extract_text_from_pdf, run_full_analysis

app = Flask(__name__)
# Configure a folder to temporarily store uploaded resumes
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':

        # Safely get the uploaded file and job description
        uploaded_file = request.files.get('resume')
        job_description = request.form.get('job_description', '')

        # Safety check to ensure a file was actually uploaded
        if uploaded_file and uploaded_file.filename != '':
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
            uploaded_file.save(filepath)

            # 1. Extract raw text from the PDF
            resume_text = extract_text_from_pdf(filepath)

            # 2. Run the Master Engine to get our elite data dictionary
            results = run_full_analysis(resume_text, job_description)

            # Clean up the uploaded file
            os.remove(filepath)

            # 3. Unpack the dictionary and pass the new data to the frontend
            return render_template('index.html',
                                   score=results['overall_score'],
                                   radar_scores=results['radar_scores'], # NEW: Multi-factor scores
                                   categorized_skills=results['categorized_skills'], # NEW: Skill Groups
                                   matched_skills=results['flat_skills']['matched'],
                                   missing=results['flat_skills']['missing'],
                                   suggestions=results['learning_path'],
                                   improvements=results['feedback'],
                                   warnings=results['warnings'], # NEW: ATS Warnings
                                   heatmap_html=results['heatmap_html'])

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)