from fastai.vision.all import *
from fastai.vision.widgets import *
labels = pd.read_csv('D:\codes\python\image_main\input\clothing-dataset-full\images.csv')
labels.head()
# Classes and their counts within the dataset
labels['label'].value_counts()
labels.loc[labels['label']=='Not sure','label'] = 'Not_sure'
labels['image'] = labels['image'] + '.jpg'
labels['label_cat'] = labels['label'] + ' ' + labels['kids'].astype(str)
label_df = labels[['image', 'label_cat']]
path = 'D:\codes\python\image_main\input\clothing-dataset-full'
def get_x(r): return path+'/images_original/'+r['image'] # create path to open images in the original folder
def get_y(r): return r['label_cat'].split(' ') # split the labels using space as a delimitter
# Create DataBlock
dblock = DataBlock(blocks = (ImageBlock, MultiCategoryBlock),
                  get_x = get_x, get_y = get_y,
                  item_tfms = RandomResizedCrop(128, min_scale=0.35))  # ensure every item is of the same size
dls = dblock.dataloaders(label_df) # collates items from dataset into minibatches
dls.show_batch(nrows=3, ncols=3)
if __name__ == '__main__':
# Specify the local path where the pre-trained model is saved
    local_model_path = 'D:\\codes\\python\\image_main\\input\\resnet\\resnet18-5c106cde.pth'

    # Load the pre-trained ResNet18 model from torchvision
    model = resnet18(pretrained=False)
    state_dict = torch.load(local_model_path)
    model.load_state_dict(state_dict)

    # Modify the final fully connected layer to match your task
    num_classes = dls.c
    model.fc = nn.Linear(model.fc.in_features, num_classes)

    # Create a learner using the modified model
    learn = Learner(dls, model, metrics=partial(accuracy_multi, thresh=0.2))

    # Fine-tune the model (you can adjust the parameters as needed)
    learn.fine_tune(5, base_lr=3e-3)
    # Get Predictions and target variables
    preds,targs = learn.get_preds()
    xs = torch.linspace(0.01,0.99,50)
    accs = [accuracy_multi(preds, targs, thresh=i, sigmoid=False) for i in xs] # get_preds applies sigmoid activation function
    plt.plot(xs,accs);
    learn.export(Path("D:\codes\python\image_main\output\export.pkl"))
upload = widgets.FileUpload()
out_image = widgets.Output()
prediction = widgets.Label()
run = widgets.Button(description='Classify')

# btn_upload = widgets.FileUpload()
# out_pl = widgets.Output()
# lbl_pred = widgets.Label()
# btn_run = widgets.Button(description='Classify')
def on_click_classify(change):
    img = PILImage.create(upload.data[-1])
    out_image.clear_output()
    with out_image: display(img.to_thumb(128,128))
    pred,pred_idx,probs = learn.predict(img)
    pred0 = pred[0]
    pred1 = pred[1]
    if pred0=='False':
        prediction.value = f'This is a {pred1} for adults.'
    else:
        prediction.value = f'This is a {pred1} for kids.'

run.on_click(on_click_classify)
# Use Virtual Box to encapsulate the iPython widgets
VBox([widgets.Label('Upload a picture of a pice of clothing!'), 
      upload, run, out_image, prediction])