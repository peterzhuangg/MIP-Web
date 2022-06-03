from flask import Flask,render_template, send_from_directory,session
from flask import redirect
from flask import url_for
from flask import request
from model.check_login import is_existed,exist_user,is_null
from model.check_regist import add_user
from werkzeug.utils import secure_filename
from flask import jsonify, make_response, send_file
from datetime import timedelta
from model.process_image import process_nifiti_image_1
from model.FeTS2021_main.inference import run_model
from flask_dropzone import Dropzone
from io import BytesIO
import base64,zipfile,concurrent.futures,os,win32api, win32con, time


executor1 = concurrent.futures.ThreadPoolExecutor()#thread pool
executor2 = concurrent.futures.ThreadPoolExecutor(2)
app = Flask(__name__)
dropzone = Dropzone(app) #innitialization
path = './users/' # toplevel path
app.config['SECRET_KEY'] = os.urandom(24)   
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2) #session setup,expired after 2 hours and random key

@app.route('/')
def welcome():
    session['username'] = 'Stranger'
    return redirect( url_for('index') ) # welcome page redirect to login

@app.route('/user_login',methods=['GET','POST'])
def user_login():
    if request.method=='POST':  # post request for register
        username = request.form['username']
        password = request.form['password'] # get user input
        if is_null(username,password):
            login_massage = "username and password is necessary" #if no input
            return render_template('login.html', message=login_massage)
        elif is_existed(username, password):
            session['username'] = username
            print ('session set')
            isExists = os.path.exists(path+username)
            isExistsOutput = os.path.exists(path+username+'_result') 
            if not isExists:
                os.makedirs(path+username)
            if not isExistsOutput:
                os.makedirs(path+username+'_result') #if successfullty login check if their folder is exist
            return render_template('index.html', username=username)
        elif exist_user(username):
            login_massage = "wrong password"
            return render_template('login.html', message=login_massage)# wrong password
        else:
            login_massage = "username not exist"
            return render_template('login.html', message=login_massage)# user not exist
    return render_template('login.html')


@app.route("/regiser",methods=["GET", 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']# get user input
        if is_null(username,password):
            login_massage = "username and password is necessary"
            return render_template('register.html', message=login_massage) #if no input
        elif exist_user(username):
            return redirect(url_for('user_login'))
        else:
            add_user(request.form['username'], request.form['password'] ) #successfully register
            return render_template('login.html')
    return render_template('register.html')

@app.route("/index",methods=["GET", 'POST'])
def index():
    User = session.get('username')
    if User =='Stranger':
        message = 'Login to unlock more functions'
    else:
        message=''
    return render_template('index.html', username=User, message=message)

#allowed extension for file uploader
ALLOWED_EXTENSIONS = set(['gz'])
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
 

app.send_file_max_age_default = timedelta(seconds=1) # set cache time as 1 second
 
@app.route('/upload', methods=['POST', 'GET'])  # add route
def upload():
    User = session.get('username')
    if User =='Stranger':
        return  redirect(url_for('user_login'))
    if request.method == 'POST':
        for f in request.files.getlist('file'):
                                       
            if not (f and allowed_file(f.filename)):
                return 'NIFTI format only!', 400  # return the error message, with a proper 4XX code
                #return jsonify({"error": 1001, "msg": "please check the file format:png、PNG、jpg、JPG、bmp"})
            user_input = request.form.get("name")
            basepath = os.path.dirname(__file__)  
            upload_path = os.path.join(basepath, 'users/'+User ,secure_filename(f.filename))  
            f.save(upload_path)
        image_data = open(upload_path, "rb").read()
        response = make_response(image_data)
        response.headers['Content-Type'] = 'image/png'
        return redirect(url_for('manage'))
    return render_template('upload.html', username=User)


# @app.route('/index',methods=['POST', 'GET'])
# def userfiles():
@app.route('/manage', methods=['POST', 'GET'])
def manage():
    User = session.get('username')
    if User =='Stranger':
        return  redirect(url_for('user_login'))
    files_list = os.listdir(path + User)
    outputs_list = os.listdir(path + User +'_result')
    fileinfo = {}
    outputinfo = {}
    for filename in files_list:
        file_url = ('./users/' + User + '/'+filename)
        statinfo = os.stat(file_url)
        file_size=('%.2f'%(statinfo.st_size/1024/1024)) 
        fileinfo.update({str(filename): file_size})
    for filename in outputs_list:
        file_url = ('./users/' + User +  '_result/'+filename)
        statinfo = os.stat(file_url)
        output_size=('%.3f'%(statinfo.st_size/1024/1024)) 
        outputinfo.update({str(filename):output_size})
    return render_template('manage.html', fileinfo=fileinfo, outputinfo=outputinfo, username=User,file_list=files_list,output_list=outputs_list)

@app.route('/browser',methods=['POST', 'GET'])
def browser():
    User = session.get('username')
    
    file_url = session.get('imgdir')
    if User =='Stranger':
        message = 'Login to unlock more functions'
    else:
        message = ''
    if file_url:
        with open(file_url, 'rb') as f1:
            base64_str = base64.b64encode(f1.read())  # base64类型
            src = base64_str.decode('utf-8')  # str
            return render_template('browser.html',username=User,file_url = src)
    return render_template('browser.html',username=User, message=message)


@app.route('/open_file/<filename>')
def open_file(filename):
    User = session.get('username')
    file_url = ('./users/' + User + '/'+filename)
    #file_url = str(file_url).replace('/','\\')
    session['imgdir'] = file_url
    return  redirect(url_for('browser'))

@app.route('/open_result/<filename>')
def open_result(filename):
    User = session.get('username')
    file_url = ('./users/' + User + '_result/'+filename)
    #file_url = str(file_url).replace('/','\\')
    session['imgdir'] = file_url
    return  redirect(url_for('browser'))

@app.route('/delete/<filename>')
def delete_file(filename):
    User = session.get('username')
    file_path = ('./users/' + User + '/'+filename)
    os.remove(file_path)
    return redirect(url_for('manage'))
@app.route('/delete_result/<filename>')
def delete_result(filename):
    User = session.get('username')
    file_path = ('./users/' + User + '_result/'+filename)
    os.remove(file_path)
    return redirect(url_for('manage'))
@app.route('/download/<filename>')
def download_file(filename):
    User = session.get('username')
    file_path = ('./users/' + User + '/')
    #(file_path)
    return send_from_directory(file_path, filename, as_attachment=True)
    return render_template('manage.html')
@app.route('/download_result/<filename>')
def download_result(filename):
    User = session.get('username')
    file_path = ('./users/' + User + '_result/')
    #print(file_path)
    return send_from_directory(file_path, filename, as_attachment=True)
    return render_template('manage.html')

@app.route('/process/<filename>',methods=['POST', 'GET'])
def process_file(filename):       
    User = session.get('username')
    filepath = ('./users/' + User + '/'+ filename)
    outputpath = ('./users/' + User + '_result/'+ filename)
    if filename.rsplit('.', 1)[1] == 'gz':
        f_new = os.path.join('./users/' + User + '_result/', filename.split('/')[-1].split('.')[0] + '_Procssing_test.txt')
        f= open(f_new, mode='w', encoding='utf-8').close()
        tasks = executor1.submit(process_nifiti_image_1,filepath,outputpath)
        print('task start')
        return redirect(url_for('manage'))
    else: return redirect(url_for('manage'))
    
@app.route('/multiprocess', methods=['POST', 'GET'])
def multiprocess_file():
    if request.method=='POST':
        multiselect = request.form.getlist('multiselect')
        method = request.form['methods']
        #print (method)
        #print (multiselect)
        User = session.get('username')
        files_list = os.listdir(path + User)
        if not method :
            win32api.MessageBox(0,'Please choose your method','alert',win32con.MB_OK)
        if method == '1':
            for i in range(len(files_list)):
                    for j in range(len(multiselect)):    
                        if i+1 == int(multiselect[j]):
                            filename = files_list[i]
                            if filename.rsplit('.', 1)[1] == 'gz':
                                f_new = os.path.join('./users/' + User + '_result/', filename.split('/')[-1].split('.')[0] + '_Procssing_test.txt')
                                f= open(f_new, mode='w', encoding='utf-8').close()
                                filepath = ('./users/' + User + '/'+ filename)
                                outputpath = ('./users/' + User + '_result/'+ filename)
                                tasks = executor1.submit(process_nifiti_image_1,filepath,outputpath)
                                print('task start 1')
                                return redirect(url_for('manage'))
        if method == '2':
            for i in range(len(files_list)):
                    for j in range(len(multiselect)):    
                        if i+1 == int(multiselect[j]):
                            filename = files_list[i]
                            if filename.rsplit('.', 1)[1] == 'gz':
                                f_new = os.path.join('./users/' + User + '_result/', filename.split('/')[-1].split('.')[0] + '_Procssing_FeTS.txt')
                                f= open(f_new, mode='w', encoding='utf-8').close()
                                filepath = ('./users/' + User + '/'+ filename)
                                outputpath = ('./users/' + User + '_result/')
                                tasks = executor2.submit(run_model,filepath,outputpath)
                                print('task start 2')
                                return redirect(url_for('manage'))
                                
    return redirect(url_for('manage'))

@app.route('/multidelete', methods=['POST', 'GET'])
def multidelete_file():
    if request.method=='POST':
        multiselect = request.form.getlist('multiselect')
        print (multiselect)
        User = session.get('username')
        files_list = os.listdir(path + User)
        for i in range(len(files_list)):
                for j in range(len(multiselect)):    
                    if i+1 == int(multiselect[j]):
                        filename = files_list[i]
                        file_path = ('./users/' + User + '/'+filename)
                        os.remove(file_path)
    return redirect(url_for('manage'))
@app.route('/multidownload', methods=['POST', 'GET'])
def multidownload_file():
    if request.method=='POST':
        multiselect = request.form.getlist('multiselect')
        print (multiselect)
        User = session.get('username')
        files_list = os.listdir(path + User)
        dlname = User+'.zip'
        memory_file = BytesIO()
        with zipfile.ZipFile(memory_file, "w", zipfile.ZIP_DEFLATED) as zf:
            for i in range(len(files_list)):
                for j in range(len(multiselect)):    
                    if i+1 == int(multiselect[j]):
                        filename = files_list[i]
                        file_path = ('./users/' + User + '/')
                        with open(os.path.join(file_path, filename), 'rb') as fp:
                            zf.writestr(filename, fp.read())
        memory_file.seek(0)
        return send_file(memory_file, attachment_filename=dlname, as_attachment=True)
    return redirect(url_for('manage'))
@app.route('/multideleteR', methods=['POST', 'GET'])
def multideleteR_file():
    if request.method=='POST':
        multiselect = request.form.getlist('multiselect2')
        print (multiselect)
        User = session.get('username')
        files_list = os.listdir(path + User+ '_result/')
        for i in range(len(files_list)):
                for j in range(len(multiselect)):    
                    if i+1 == int(multiselect[j]):
                        filename = files_list[i]
                        file_path = ('./users/' + User + '_result/'+filename)
                        os.remove(file_path)
    return redirect(url_for('manage'))

@app.route('/multidownloadR', methods=['POST', 'GET'])
def multidownloadR_file():
    if request.method=='POST':
        multiselect = request.form.getlist('multiselect2')
        print (multiselect)
        User = session.get('username')
        files_list = os.listdir(path + User+ '_result/')
        for i in range(len(files_list)):
                for j in range(len(multiselect)):    
                    if i+1 == int(multiselect[j]):
                        filename = files_list[i]
                        file_path = ('./users/' + User + '_result/')
                        send_from_directory(file_path, filename, as_attachment=True)
    return redirect(url_for('manage'))



@app.route('/result/<filename>')
def result_file(filename):
    return redirect(url_for('manage'))
@app.route("/logout",methods=["GET", 'POST'])
def logout():
    session.clear()
    return redirect(url_for('user_login'))

if __name__ == '__main__':

    app.run()