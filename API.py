import requests
import json
from flask import Flask, request, jsonify, Response, render_template, make_response
from werkzeug.utils import secure_filename
import logging
import os
import glob
from slugify import slugify
import wsgiserver
from PIL import Image
from io import BytesIO
import base64
import pothole
import predict_days
import predict_material_cost
import predict_other_cost
import demo_api_call
from numpyencoder import NumpyEncoder

#configuration
#this api
api_host = '0.0.0.0'
api_port = 1234
current_image = 'current.jpg'
uploads_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)),"static","uploads")
#end configuration

logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))
log = logging.getLogger(__name__)
app = Flask(__name__)
app.debug = True

@app.route('/', methods=['GET'])
def index():
    return render_template("index.html")

@app.route('/estimate/<width>/<height>', methods=['GET'])
def estimate(width,height):
    return render_template("estimator.html",width=width,height=height)

@app.route('/detect', methods=['POST'])
def detect():
    data = json.loads(request.data)
    im = Image.open(BytesIO(base64.b64decode(data['image'].split(',')[1])))
    rgb_im = im.convert('RGB')
    rgb_im.save(current_image)

    detected = pothole.detect_and_color_splash(current_image)

    with open("current_masked.jpg", "rb") as image_file:
        detected['size'] = rgb_im.size
        detected['image'] = base64.b64encode(image_file.read()).decode('utf-8')
    
    json_str = json.dumps(detected, cls=NumpyEncoder, indent=4)
    return json_str, 200

@app.route('/predictCosts', methods=['POST'])
def predictCosts():
    data = json.loads(request.data)
    grade = data['grade']
    year = data['year']
    month = data['month']
    volume = data['volume']
    
    result = {
        'material': 'error',
        'other': 'error',
        'days': 'error'
    }

    result['material'] = predict_material_cost.materialCostPredict(grade,year,month,volume)
    result['other'] = predict_other_cost.otherCostPredict(grade,year,month,volume)
    result['days'] = predict_days.unskilledWorkerDaysPredict(year,month,volume)
    result['video_test'] = demo_api_call.demoApiCall(grade,year,month,volume)

    json_str = json.dumps(result, cls=NumpyEncoder, indent=4)
    return json_str, 200

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']

    save_path = os.path.join(uploads_folder, secure_filename(file.filename))
    current_chunk = int(request.form['dzchunkindex'])

    # If the file already exists it's ok if we are appending to it,
    # but not if it's new file that would overwrite the existing one
    if os.path.exists(save_path) and current_chunk == 0:
        # 400 and 500s will tell dropzone that an error occurred and show an error
        return make_response(('File already exists', 400))

    try:
        with open(save_path, 'ab') as f:
            f.seek(int(request.form['dzchunkbyteoffset']))
            f.write(file.stream.read())
    except OSError:
        # log.exception will include the traceback so we can see what's wrong 
        log.exception('Could not write to file')
        return make_response(("Not sure why,"
                              " but we couldn't write the file to disk", 500))

    total_chunks = int(request.form['dztotalchunkcount'])

    if current_chunk + 1 == total_chunks:
        # This was the last chunk, the file should be complete and the size we expect
        if os.path.getsize(save_path) != int(request.form['dztotalfilesize']):
            log.error(f"File {file.filename} was completed, "
                      f"but has a size mismatch."
                      f"Was {os.path.getsize(save_path)} but we"
                      f" expected {request.form['dztotalfilesize']} ")
            return make_response(('Size mismatch', 500))
        else:
            log.info(f'File {file.filename} has been uploaded successfully')
    else:
        log.debug(f'Chunk {current_chunk + 1} of {total_chunks} '
                  f'for file {file.filename} complete')

    return make_response(("Chunk upload successful", 200))

@app.route('/videos', methods=['GET'])
def videos():
    files = glob.glob(os.path.join(uploads_folder, '*.mp4'))
    files = [f.replace(f, os.path.basename(f)) for f in files]
    json_str = json.dumps(files, cls=NumpyEncoder, indent=4)
    return json_str, 200

@app.route('/workers', methods=['GET'])
def workers():
    workers_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),"workers.json")
    f = open(workers_file_path)
    data = json.load(f) 
    json_str = json.dumps(data, cls=NumpyEncoder, indent=4)
    return json_str, 200

#app.run(api_host,api_port)
if __name__ == '__main__':
    # Debug/Development
    app.run(debug=True, host=api_host, port=api_port)
    # Production
    # http_server = wsgiserver.WSGIServer(app, host=api_host, port=api_port)
    # http_server.start()