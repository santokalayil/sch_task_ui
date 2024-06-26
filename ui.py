import dash
from datetime import datetime, timedelta
import pytz  # Library for handling timezones
import time  # For sleep functionality
from dash import Output, Input, html, dcc

# Replace with your specific database connection and interaction logic
import db

# Set number of retries and retry interval
MAX_RETRIES = 3
RETRY_INTERVAL = 600  # 10 minutes in seconds

def check_and_store_data(filename):
    # Replace with your logic to check for and process the file
    # If the file is found and processed successfully, return True
    # Otherwise, return False
    try:
        # Perform file processing logic here
        # ...
        return True
    except Exception as e:
        print(f"Error processing file {filename}: {e}")
        return False

app = dash.Dash(__name__)

# Define Indian Standard Time (IST) timezone
ist_timezone = pytz.timezone('Asia/Kolkata')

def get_scheduled_times():
    now = datetime.now(ist_timezone)
    # Calculate scheduled times for 10:30 AM and 10:30 PM IST
    morning_check = now.replace(hour=10, minute=30)
    evening_check = now.replace(hour=22, minute=30)

    # Adjust for past time checks (if current time is past 10.30 AM/PM)
    if now > morning_check and now > evening_check:
        # Schedule checks for tomorrow
        morning_check += timedelta(days=1)
        evening_check += timedelta(days=1)
    elif now > morning_check:
        # Schedule only evening check for today
        evening_check = now.replace(hour=22, minute=30)

    return morning_check, evening_check

# Function to store execution logs
def store_execution_log(message):
    # Replace with your logic to store the message in the database (or other storage)
    db.store_log(message, level="info")  # Example placeholder

# Function to retrieve recent logs from the database
def get_recent_logs(limit=10):
    session = db.create_database()  # Create or connect to the database
    logs = session.query(db.Log).order_by(db.Log.datetime.desc()).limit(limit).all()
    session.close()  # Close the database session
    return logs

# # Layout with hidden interval component, log display, and manual check button
# app.layout = html.Div([
#     dcc.Interval(
#         id='interval-component',
#         interval=1 * 60 * 1000,  # Check every minute
#         n_intervals=0
#     ),
#     html.Div(id='execution-logs'),  # Container for log display
#     html.Button('Run Checks Now', id='manual-check-button', n_clicks=0),
# ])

# Layout with hidden interval component, log tabs, and manual check button
app.layout = html.Div([
    dcc.Interval(
        id='interval-component',
        interval=1 * 60 * 1000,  # Check every minute
        n_intervals=0
    ),
    dcc.Tabs(
        id='logs-tabs',
        children=[
            dcc.Tab(label="Recent Logs", value="recent"),
            dcc.Tab(label="All Logs", value="all"),  # Placeholder for later implementation
        ]
    ),
    html.Div(id='log-display'),  # Container for displaying logs
    html.Button('Run Checks Now', id='manual-check-button', n_clicks=0),
])

@app.callback(
    [Output('log-display', 'children'), Output('interval-component', 'n_intervals')],
    [Input('interval-component', 'n_intervals'), Input('logs-tabs', 'value'), Input('manual-check-button', 'n_clicks')]
)
def update_interval_and_logs(n_intervals, tab_value, n_clicks):
    now = datetime.now(ist_timezone)
    scheduled_morning_check, scheduled_evening_check = get_scheduled_times()

    # Check if current time is within the scheduled window (with buffer)
    buffer = timedelta(minutes=10)  # Allow 10-minute buffer for execution
    is_morning_check_time = scheduled_morning_check - buffer <= now <= scheduled_morning_check + buffer
    is_evening_check_time = scheduled_evening_check - buffer <= now <= scheduled_evening_check + buffer
    is_manual_check = n_clicks > 0  # Check if manual button was clicked

    logs = []
    
    if tab_value == "all":
        # Retrieve recent logs using get_recent_logs
        recent_logs = get_recent_logs()
        logs = [html.Div(f"{log.datetime.strftime('%Y-%m-%d %H:%M:%S IST')}: {log.log_message}") for log in recent_logs]
    
    if is_morning_check_time or is_evening_check_time or is_manual_check:
        # Perform checks and store data (with retry logic)
        for filename in ['file1.txt', 'file2.txt']:  # Replace with your filenames
            retries = 0
            while retries < MAX_RETRIES:
                if check_and_store_data(filename):
                    message = f"Successfully processed file {filename} at {now.strftime('%H:%M:%S')}"
                    logs.append(message)
                    store_execution_log(message)  # Store log in database
                    break  # Success, exit loop
                else:
                    message = f"Failed to process file {filename} at {now.strftime('%H:%M:%S IST')}. Retrying ({retries+1}/{MAX_RETRIES})..."
                    logs.append(message)
                    time.sleep(RETRY_INTERVAL)  # Wait before retrying
                    retries += 1

        # Update log display in UI
        if logs:
            log_elements = [html.Div(log_message) for log_message in logs]
            return log_elements, n_intervals
        else:
            return None, n_intervals

    # Reset manual check button after click
    return dash.callback_context.triggered[0]['prop_id'].split('.')[0], n_intervals  # Reset n_clicks for manual button

if __name__ == '__main__':
    app.run_server(debug=True)  # Start the Dash app server