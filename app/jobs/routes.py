from flask import Blueprint, jsonify, request

from app.jobs import service

job_router_blueprint = Blueprint('job_router', __name__, url_prefix="/job")
service = service.JobService()

@job_router_blueprint.route("/", methods=["GET"])
def list_jobs():
    jobs = service.get_all()
    return jsonify(jobs), 200 # TODO error handling

@job_router_blueprint.route("/<string:job_id>", methods=["GET", "PATCH", "DELETE"])
def list_job(job_id):
    job = None

    if request.method == "GET":
        job = service.get(job_id)
    elif request.method == "PATCH":
        data = request.json
        frequency = data.get('frequency')

        job = service.update(job_id, frequency)
    elif request.method == "DELETE":
        job = service.cancel(job_id)
        if job:
            return jsonify({'message': 'Job deleted successfully'}), 200
        else:
            return jsonify({'error': 'Job not found'}), 404

    return jsonify(job), 200 # TODO error handling

@job_router_blueprint.route('/', methods=["POST"])
def add_job():
    data = request.json
    script_name = data.get('script_name')
    frequency = data.get('frequency')

    job = service.add(script_name, frequency)
    
    return jsonify(job), 201 # TODO error handling