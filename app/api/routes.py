from flask import Blueprint, jsonify, request

from app.services import job_service

job_router_blueprint = Blueprint('job_router', __name__, url_prefix="/job")
job_service = job_service.JobService()

@job_router_blueprint.route("/", methods=["GET"])
def list_jobs():
    jobs = job_service.get_jobs()
    return jsonify(jobs), 200 # TODO error handling

@job_router_blueprint.route("/<int:job_id>", methods=["GET"])
def list_jobs():
    job = job_service.get_job()
    return jsonify(job), 200 # TODO error handling

@job_router_blueprint.route('/', methods=["POST", "PATCH"])
def add_job():
    data = request.json
    script_name = data.get('script_name')
    frequency = data.get('frequency')

    job = None
    if request.method == "POST":
        job = job_service.add_job(script_name, frequency)
    elif request.method == "PATCH":
        job = job_service.update_job(script_name, frequency)
    else:
        return jsonify("the fuck you doin?"), 400

    
    return jsonify(job), 200 # TODO error handling

@job_router_blueprint.route('/job/<int:job_id>', methods=['DELETE'])
def cancel_job(job_id):
    job = job_service.cancel_job(job_id)
    if job:
        return jsonify({'message': 'Job deleted successfully'}), 200
    else:
        return jsonify({'error': 'Job not found'}), 404





# TODO Dillon do we need this?
# Scripts Route
# @job_router.route('/<script_name>', methods=['POST'])
# def run_script(script_name):
#     try:

        # SCRIPTS_FOLDER = "./app/scripts/"
#         script_path = os.path.join(SCRIPTS_FOLDER, f"{script_name}")

#         if not os.path.exists(script_path):
#             return jsonify({"error": "Script not found"}), 404

#         # Run the script
#         result = subprocess.run(
#             ["python", script_path],
#             capture_output=True,
#             text=True
#         )

#         if result.returncode == 0:
#             return jsonify({"message": result.stdout.strip()}), 200
#         else:
#             return jsonify({"error": result.stderr.strip()}), 500
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500