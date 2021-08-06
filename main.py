from flask_cors import CORS
from hashfs import HashFS
import os
from io import StringIO
import json
import hashlib
import flask
# Set the `depth` to the number of subfolders the file's hash should be split when saving.
# Set the `width` to the desired width of each subfolder.
from mpt import MerklePatriciaTrie


# With depth=4 and width=1, files will be saved in the following pattern:
# temp_hashfs/a/b/c/d/efghijklmnopqrstuvwxyz

# With depth=3 and width=2, files will be saved in the following pattern:
# temp_hashfs/ab/cd/ef/ghijklmnopqrstuvwxyz
fs = HashFS('temp_hashfs', depth=4, width=1, algorithm='sha256')


class myHashFs:
    def __init__(self, f, d, w):
        self.f = f
        self.d = d
        self.w = w
        self.hash = hashlib.sha256
        self.data = {}

    def add(self, file_string, fn):
        print(fn)
        add = self.hash(file_string.encode()).hexdigest()
        path, filename, fullpath = self.address_to_path(add)
        if os.path.isfile(fullpath):
            return '-1'
        if not os.path.isdir(fullpath[0:len(self.f) + 4 + self.d * self.w]):
            os.makedirs(path)
        with open(fullpath, 'w') as d:
            d.write(file_string)
        with open('changelog', 'a') as f:
            f.write('file created ' + fn + '\n')
        if fn in self.data:
            i = 0
            while fn + str(i) in self.data:
                i += 1
            fn = fn + str(i)
        self.data[fn] = fullpath
        with open('data', 'a') as f:
            f.write(fullpath + ',' + fn + '\n')
        return path

    def get(self, address):
        path, filename, fullpath = self.address_to_path(address)
        return open(fullpath, 'r').read()

    def address_to_path(self, address):
        add = address
        path = self.f + '/' + add[0:self.w]
        for i in range(self.w, self.d * self.w, self.w):
            path += '/' + add[i:i + self.w]
        filename = add[i + 1:]
        fullpath = path + '/' + filename
        return path, filename, fullpath

    def get_all_names(self):
        self.data = {}
        names = []
        if os.path.isfile('data') and len(open('data', 'r').read()) > 0:
            with open('data', 'r') as f:
                temp = f.read().split('\n')
                print(temp)
                for i in temp:
                    if i == '':
                        break
                    arr = i.split(',')
                    names.append(arr[1])
                    self.data[arr[1]] = arr[0]
            print(self.data)
            with open('changelog', 'a') as f:
                f.write('all filename gotten\n')
            return json.dumps({'data': names})
            string = ''

            for i in names:
                string += f'<a href="http://127.0.0.1:5000/get?name={i}">{i}</a><br>'
            return string
        return '[]'

    def get_file(self, name):
        print(name)
        address = self.data[name]
        with open('changelog', 'a') as f:
            f.write('file accessed ' + name + '\n')
        return json.dumps({'data': open(address, 'r').read()})
        #return f'<textarea name="{name}" id="text">{open(address,"r").read()}</textarea><br>' +\
               #f'<br> <input type="button" onclick="location.href=\'http://127.0.0.1:5000/delete?name={name}\';" value="delete" />'+\
               #f'<br> <input type="button" onclick="var d =document.getElementById("text");var name = d.name; var data = d.value;var xhr = new XMLHttpRequest();xhr.open("POST", "http://127.0.0.1:5000/update", true);xhr.setRequestHeader("Content-Type", "application/json");xhr.send(JSON.stringify('+'{++'));" value="update" />'

    def delete(self, name):
        path = self.data[name]
        del self.data[name]
        os.remove(path)
        os.remove('data')
        with open('data', 'w') as f:
            for i in self.data:
                f.write(self.data[i] + ',' + i + '\n')
            f.close()
        with open('changelog', 'a') as f:
            f.write('file deleted ' + name + '\n')
        return json.dumps({'message': 'success'})


text = 'my name is amk and i am not a terroristasdasdas'
text1 = 'my name is amk and i am not a terrorist'
text2 = 'my name is amk and i am not a terroristasdasdasasdasdd'
mfs = myHashFs('root', 4, 1)
#mfs.add(text, 'f1')
#mfs.add(text1, 'f2')
#mfs.add(text2, 'f3')
mfs.get_all_names()


"""
text = StringIO("my name is amk and i am not a terrorist")
text1 = StringIO("my name is amk and i am not a terroristasdasdas")
# address = fs.put(text)
temp = fs.computehash(text1)
print(temp)
new_address = fs.computehash(text)
if fs.get(new_address) is not None:
    print("file exists")
print(new_address)
"""
from flask import Flask, request

app = Flask(__name__)
cors = CORS(app, resources={r"/upload/*": {"origins": "*"}})


@app.route("/", methods=['Get'])
def hello_world():
    return mfs.get_all_names()


@app.route("/upload", methods=['Post'])
def upload():
    data = json.loads(request.data.decode())
    print(type(data['data']))
    if mfs.add(data['data'], data['name']) == '-1':
        print("oh no")
        return json.dumps({'message': 'file already exists'})
    return json.dumps({'message': 'success'})


@app.route("/update", methods=['Post'])
def update():
    data = json.loads(request.data.decode())
    if data['name'] in mfs.data:
        mfs.delete(data['name'])
        if mfs.add(data['data'], data['name']) == '-1':
            return json.dumps({'message': 'file already exists'})
        return json.dumps({'message': 'success'})
    return json.dumps({'message': 'file does not exist. upload it first'})


@app.route("/get")
def get():
    name = request.args.get('name')
    print(mfs.data)
    if name in mfs.data:
        return mfs.get_file(request.args.get('name'))
    return json.dumps({'message': 'files does not exist'})
    return "<h1>file does not exist</h1>"


@app.route("/delete")
def delete():
    name = request.args.get('name')
    if name in mfs.data:
        return mfs.delete(name)
    return json.dumps({'message': "failiure. try again"})


app.run()



