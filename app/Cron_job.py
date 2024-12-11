from crontab import CronTab

def setup_cron_job(script_name, cron_expression):
    try:
        # Initialize the current user's crontab
        cron = CronTab(user=True)

        # Remove any existing job for the script
        cron.remove_all(comment=script_name)

        job = cron.new(command=f"python /path/to/scripts/{script_name}", comment=script_name)
        job.setall(cron_expression)

        # Write the updated cron jobs back to the crontab
        cron.write()

        print(f"Cron job for {script_name} set up successfully: {cron_expression}")
    except Exception as e:
        print(f"Failed to set up cron job for {script_name}: {e}")

def remove_cron_job(script_name):
    try:
        cron = CronTab(user=True)

        cron.remove_all(comment=script_name)

        cron.write()

        print(f"Cron job for {script_name} removed successfully.")
    except Exception as e:
        print(f"Failed to remove cron job for {script_name}: {e}")

if __name__ == "__main__":
    setup_cron_job("example_script.py", "0 5 * * *")
    # remove_cron_job("example_script.py")
