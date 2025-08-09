# Job Scheduling System

The Unraid Scripts project now includes a robust job scheduling system that allows you to schedule and manage script execution automatically.

## Features

- **Flexible Scheduling**: Support for common frequencies (daily, hourly, weekly, etc.) and custom cron expressions
- **Job Management**: Create, update, activate, deactivate, and delete jobs
- **Immediate Execution**: Run jobs on-demand for testing or urgent tasks
- **Status Tracking**: Monitor job status, last run time, and next scheduled run
- **Error Handling**: Comprehensive error handling and logging
- **REST API**: Full REST API for managing jobs programmatically

## Supported Frequencies

### Predefined Frequencies
- `hourly` - Runs every hour at minute 0
- `daily` - Runs every day at midnight
- `weekly` - Runs every Sunday at midnight
- `monthly` - Runs on the 1st of every month at midnight
- `yearly` - Runs on January 1st at midnight
- `every_minute` - Runs every minute
- `every_5_minutes` - Runs every 5 minutes
- `every_15_minutes` - Runs every 15 minutes
- `every_30_minutes` - Runs every 30 minutes

### Custom Cron Expressions
You can also use standard cron expressions for more precise control:
- `0 2 * * *` - Runs daily at 2:00 AM
- `0 */6 * * *` - Runs every 6 hours
- `0 0 * * 1` - Runs every Monday at midnight

## API Endpoints

### Jobs Management

#### GET /api/jobs/
Get all jobs with their current status and scheduling information.

#### POST /api/jobs/
Create a new job.

**Request Body:**
```json
{
    "script_name": "my_script",
    "frequency": "daily",
    "description": "Optional description of the job"
}
```

#### GET /api/jobs/{job_id}
Get details of a specific job.

#### PATCH /api/jobs/{job_id}
Update a job's frequency or description.

**Request Body:**
```json
{
    "frequency": "hourly",
    "description": "Updated description"
}
```

#### DELETE /api/jobs/{job_id}
Cancel a job (marks it as inactive and unschedules it).

#### POST /api/jobs/{job_id}/activate
Activate a previously cancelled job.

#### POST /api/jobs/{job_id}/run
Run a job immediately.

#### GET /api/jobs/scheduler/status
Get the overall scheduler status and information about all scheduled jobs.

## Usage Examples

### Creating a Daily Backup Job
```bash
curl -X POST http://localhost:5000/api/jobs/ \
  -H "Content-Type: application/json" \
  -d '{
    "script_name": "backup_script",
    "frequency": "daily",
    "description": "Daily backup of important data"
  }'
```

### Running a Job Immediately
```bash
curl -X POST http://localhost:5000/api/jobs/backup_script/run
```

### Updating Job Frequency
```bash
curl -X PATCH http://localhost:5000/api/jobs/backup_script \
  -H "Content-Type: application/json" \
  -d '{
    "frequency": "every_6_hours"
  }'
```

### Cancelling a Job
```bash
curl -X DELETE http://localhost:5000/api/jobs/backup_script
```

## Job States

- **ACTIVE**: Job is scheduled and will run according to its frequency
- **INACTIVE**: Job is cancelled/disabled and won't run
- **RUNNING**: Job is currently executing
- **COMPLETED**: Job has finished successfully
- **FAILED**: Job execution failed

## Script Requirements

For a script to be executable by the scheduler:

1. **File Location**: Place scripts in the `app/scripts/` directory
2. **Executable**: Scripts should be executable Python files
3. **Exit Codes**: Return 0 for success, non-zero for failure
4. **Output**: Use print statements for logging (captured by the scheduler)

### Example Script Structure
```python
#!/usr/bin/env python3
import sys
from datetime import datetime

def main():
    print(f"[{datetime.now()}] Script started")
    # Your script logic here
    print("Script completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

## Testing

Use the provided `test_api.py` script to test the API endpoints:

```bash
# Start the Flask application
python -m app.app

# In another terminal, run the test script
python test_api.py
```

## Configuration

The scheduler can be configured through environment variables:

- `SERVER_IP`: IP address to bind to (default: 0.0.0.0)
- `PORT_NUMBER_FLASK`: Port to run on (default: 5000)
- `SEED_TEST_DATA`: Set to "true" to seed test jobs (default: false)

## Troubleshooting

### Common Issues

1. **Script Not Found**: Ensure scripts are in the correct directory and have proper permissions
2. **Scheduling Failures**: Check that the frequency format is valid
3. **Execution Timeouts**: Scripts have a 5-minute timeout by default

### Logs

The application provides comprehensive logging. Check the console output for:
- Job scheduling status
- Script execution results
- Error messages and stack traces

### Database

The system uses an in-memory SQLite database by default. For production use, consider switching to a persistent database by modifying the `SQLALCHEMY_DATABASE_URI` configuration.
