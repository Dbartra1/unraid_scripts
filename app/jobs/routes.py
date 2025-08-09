from flask import jsonify, request, current_app
from werkzeug.exceptions import BadRequest, NotFound, InternalServerError

from app.jobs import bp
from app.jobs import service

# Get the db instance from the current app context
def get_job_service():
    from flask import current_app
    return service.JobService(current_app.extensions['sqlalchemy'])

@bp.route("/", methods=["GET"])
def list_jobs():
    """Get all jobs."""
    try:
        job_service = get_job_service()
        jobs = job_service.get_all()
        return jsonify({
            'success': True,
            'data': jobs,
            'count': len(jobs)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route("/<string:job_id>", methods=["GET", "PATCH", "DELETE"])
def manage_job(job_id):
    """Get, update, or delete a specific job."""
    try:
        job_service = get_job_service()
        
        if request.method == "GET":
            job = job_service.get(job_id)
            if not job:
                raise NotFound(f"Job '{job_id}' not found")
            
            return jsonify({
                'success': True,
                'data': job
            }), 200
            
        elif request.method == "PATCH":
            data = request.get_json()
            if not data:
                raise BadRequest("No data provided")
            
            frequency = data.get('frequency')
            description = data.get('description')
            
            if not frequency and description is None:
                raise BadRequest("At least one field (frequency or description) must be provided")
            
            job = job_service.update(job_id, frequency, description)
            if not job:
                raise NotFound(f"Job '{job_id}' not found")
            
            return jsonify({
                'success': True,
                'data': job,
                'message': 'Job updated successfully'
            }), 200
            
        elif request.method == "DELETE":
            success = job_service.cancel(job_id)
            if not success:
                raise NotFound(f"Job '{job_id}' not found")
            
            return jsonify({
                'success': True,
                'message': 'Job cancelled successfully'
            }), 200
            
    except NotFound as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
    except BadRequest as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/', methods=["POST"])
def add_job():
    """Add a new job."""
    try:
        job_service = get_job_service()
        data = request.get_json()
        if not data:
            raise BadRequest("No data provided")
        
        script_name = data.get('script_name')
        frequency = data.get('frequency')
        description = data.get('description')
        
        if not script_name or not frequency:
            raise BadRequest("Script name and frequency are required")
        
        job = job_service.add(script_name, frequency, description)
        
        return jsonify({
            'success': True,
            'data': job,
            'message': 'Job created and scheduled successfully'
        }), 201
        
    except BadRequest as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route("/<string:job_id>/activate", methods=["POST"])
def activate_job(job_id):
    """Activate a previously cancelled job."""
    try:
        job_service = get_job_service()
        success = job_service.activate(job_id)
        if not success:
            raise NotFound(f"Job '{job_id}' not found")
        
        return jsonify({
            'success': True,
            'message': 'Job activated successfully'
        }), 200
        
    except NotFound as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route("/<string:job_id>/run", methods=["POST"])
def run_job_now(job_id):
    """Run a job immediately."""
    try:
        job_service = get_job_service()
        result = job_service.run_now(job_id)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': 'Job executed successfully'
        }), 200
        
    except NotFound as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route("/scheduler/status", methods=["GET"])
def get_scheduler_status():
    """Get the overall scheduler status."""
    try:
        job_service = get_job_service()
        status = job_service.get_scheduler_status()
        
        return jsonify({
            'success': True,
            'data': status
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500