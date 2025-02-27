import schedule
import subprocess
import time

def run_main_script():
    subprocess.run(["tmux", "send-keys", "-t", "my_session:0", "python3 update_house.py", "C-m"])

# Create a new tmux session named "my_session" if it doesn't exist
subprocess.run(["tmux", "new-session", "-d", "-s", "my_session"])

# Schedule the execution of the main script every 6 hours
schedule.every(6).hours.do(run_main_script)

run_main_script()

# Run an infinite loop to check the time and run scheduled tasks
while True:
    schedule.run_pending()
    time.sleep(1)
