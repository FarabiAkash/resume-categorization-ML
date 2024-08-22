import os
import joblib
import pandas as pd
import PyPDF2
import shutil  # For copying files
from bs4 import BeautifulSoup  # For converting to HTML

def categorize_resumes(root_dir):
    results = []

    # Load the trained model and vectorizer
    model = joblib.load(os.path.join(models_dir, 'resume_categorizer.pkl'))
    vectorizer = joblib.load(os.path.join(models_dir, 'tfidf_vectorizer.pkl'))

    # Traverse through the root directory and process each file in each subdirectory
    for category_folder in os.listdir(root_dir):
        category_path = os.path.join(root_dir, category_folder)
        print(category_folder)

        # Ensure we are processing only directories (which represent categories)
        if os.path.isdir(category_path):
            for filename in os.listdir(category_path):
                if filename.endswith(".pdf"):
                    file_path = os.path.join(category_path, filename)
                    try:
                        with open(file_path, "rb") as f:
                            pdf_reader = PyPDF2.PdfReader(f)
                            text = " ".join([page.extract_text() for page in pdf_reader.pages])

                            # Predict category using the trained model
                            text_vectorized = vectorizer.transform([text])
                            predicted_category = model.predict(text_vectorized)[0]

                            # Copy the resume to the new category folder in the categorized directory
                            new_category_folder = os.path.join(categorized_dir, predicted_category)
                            os.makedirs(new_category_folder, exist_ok=True)  # Create category folder if it doesn't exist
                            new_file_path = os.path.join(new_category_folder, filename)
                            shutil.copy2(file_path, new_file_path)  # Copy the file instead of moving it

                            # Convert resume text to HTML format using BeautifulSoup
                            soup = BeautifulSoup(text, "html.parser")
                            resume_html = str(soup)

                            # Append result to the list with the four columns
                            results.append({
                                "ID": os.path.splitext(filename)[0],  # Filename without extension
                                "Resume_str": text,  # Resume in string format
                                "Resume_html": resume_html,  # Resume in HTML format
                                "Category": predicted_category  # Predicted category
                            })
                    except Exception as e:
                        print(f"Error processing {file_path}: {e}")

    # Save the results to a CSV file with the 4 columns
    csv_path = os.path.join(csv_dir, 'categorized_resumes.csv')
    results_df = pd.DataFrame(results)
    results_df.to_csv(csv_path, index=False)



# Paths (Ensure these are set correctly)
data_dir = 'dataset/data/data'  # Root directory with subdirectories as categories
models_dir = 'dataset/task_result/models'  # Directory where the trained model is saved
categorized_dir = 'dataset/task_result/categorized_resumes'  # Directory where the categorized resumes will be saved
csv_dir = 'dataset/task_result/csv_resume'  # Directory to save the CSV file
os.makedirs(models_dir, exist_ok=True)
os.makedirs(categorized_dir, exist_ok=True)
os.makedirs(csv_dir, exist_ok=True)

# Command-line execution for testing
if __name__ == "__main__":
    import sys
    root_directory = sys.argv[1]  # Root directory containing the resume folders (categories)
    categorize_resumes(root_directory)
