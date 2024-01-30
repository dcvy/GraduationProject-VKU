from fastai.vision.all import *
from fastai.vision.widgets import *
# Load the learner
learn = load_learner(Path("D:\codes\python\image_main\export.pkl"))

# Define the widget components
upload = widgets.FileUpload()
out_image = widgets.Output()
prediction = widgets.Label()
run = widgets.Button(description='Classify')

# Define the on_click_classify function
def on_click_classify(change):
    img = PILImage.create(upload.data[-1])
    out_image.clear_output()
    with out_image: 
        display(img.to_thumb(128, 128))
    pred, pred_idx, probs = learn.predict(img)
    pred0 = pred[0]
    pred1 = pred[1]
    if pred0 == 'False':
        prediction.value = f'This is a {pred1} for adults.'
    else:
        prediction.value = f'This is a {pred1} for kids.'

# Attach the on_click_classify function to the button's click event
run.on_click(on_click_classify)

# Display the widgets
display(widgets.VBox([
    widgets.Label('Upload a picture of a piece of clothing!'), 
    upload, 
    run, 
    out_image, 
    prediction
]))