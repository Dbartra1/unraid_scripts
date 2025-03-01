# API Reference
Information related to the REST API provided by the UNRAID scripts app.

## Jobs Endpoints
**TODO
When we are properly handling errors we need to update this doc to reflect possible errors**

### Get all jobs
Provides a list of all `Job` objects stored in the app DB

**Protocol:** `GET`

**URL:** `/job`

**Returns:**

    [
        {
            id: string
            script_name: string
            frequency: string
            status: string
        },
        ...
    ]

### Get a job
Provides a `Job` objects for a given job ID

**Protocol:** `GET`

**URL:** `/job/<job_id>`

**Returns:**

    {
        id: string
        script_name: string
        frequency: string
        status: string
    }

### Add a job
Create a new Job to be scheduled and executed

**Protocol:** `POST`

**URL:** `/job`

**Body:**

    {
        script_name: string
        frequency: string
    }

**Returns:**

    {
        id: string
        script_name: string
        frequency: string
        status: string
    }

### Update a job
Update job schedule.

**Protocol:** `PATCH`

**URL:** `/job/<job_id>`

**Body:**

    {
        frequency: string
    }

**Returns:**

    {
        id: string
        script_name: string
        frequency: string
        status: string
    }

### Delete a job
Unschedule job and remove it from list of active jobs in DB.

**Protocol:** `DELETE`

**URL:** `/job/<job_id>`

**Returns:**

    {
        id: string
        script_name: string
        frequency: string
        status: string
    }