from flask import Flask, render_template, request, send_file
from utils import convert_pic_to_sketch
import __data__ as data

app = Flask(data.__app_name__)
app.config.update(
    prog=f'{data.__name__} v{data.__version__}',
    author=data.__author__
)


@app.route("/", methods=["POST", "GET"])
def home():
    if request.method == "POST":
        image_file_name = request.files['imagesInput']
        print(image_file_name.read())
        new_image = convert_pic_to_sketch(image_file_name.filename)
        return send_file(new_image,
                         mimetype='image/jpg',
                         attachment_filename=new_image,
                         as_attachment=True)
    return render_template("home.html")


if __name__ == '__main__':
    app.run(debug=True)
