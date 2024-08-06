from flask import Flask, request, jsonify
from flask_cors import CORS
import spacy
import pandas as pd

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

# Load your trained spaCy model
nlp_ner = spacy.load("../Semproject/trained_models/output/model-best")

@app.route('/process', methods=['POST'])
def process_text():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Read the text from the file
    text_content = file.read().decode('utf-8')

    # Process the text with the model
    doc = nlp_ner(text_content)

    # Extract entities
    entities = [{"Entity": entity.label_, "Text": entity.text} for entity in doc.ents]

    # Initialize a dictionary to hold the data for the DataFrame
    data = {}

    # Process each entity in the extracted entities list
    for entity in entities:
        entity_type = entity['Entity']
        entity_value = entity['Text']

        # If the entity type is not already in the data, add it
        if entity_type not in data:
            data[entity_type] = []

        # Append the entity value to the corresponding list in the data
        data[entity_type].append(entity_value)

    # Determine the maximum length of the lists to balance the DataFrame
    max_length = max(len(values) for values in data.values())

    # Normalize the lengths of the lists in the data dictionary
    for key in data:
        if len(data[key]) < max_length:
            data[key].extend([None] * (max_length - len(data[key])))

    # Convert the data dictionary to a Pandas DataFrame
    df = pd.DataFrame(data)

    # Convert the DataFrame to a dictionary and return as JSON
    return jsonify(df.to_dict(orient='list'))

if __name__ == '__main__':
    app.run(debug=True)
