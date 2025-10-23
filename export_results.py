import csv
from app import app, db, Response # Corrected: Use Response instead of SurveyResponse
from datetime import datetime

def export_to_csv(output_filename='survey_results.csv'):
    """
    Queries the database for all survey responses and exports them to a CSV file.
    """
    print("Starting the export process...")
    
    # Use the application context to access the database
    with app.app_context():
        # Query all responses from the database, ordering by timestamp
        # Corrected: Use Response model
        responses = Response.query.order_by(Response.timestamp).all()
        
        if not responses:
            print("No survey responses found in the database.")
            return

        print(f"Found {len(responses)} responses. Writing to '{output_filename}'...")

        # Define the CSV headers
        headers = ['participant_id', 'participant_uniquename', 'ranking', 'reason', 'timestamp']
        
        # Open the CSV file for writing
        with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write the header row
            writer.writerow(headers)
            
            # Write the data for each response
            for response in responses:
                writer.writerow([
                    response.participant_id,
                    response.participant_uniquename,
                    response.ranking,
                    response.reason,
                    response.timestamp.strftime('%Y-%m-%d %H:%M:%S') if response.timestamp else 'N/A'
                ])
    
    print(f"Successfully exported all responses to '{output_filename}'.")

if __name__ == '__main__':
    export_to_csv()