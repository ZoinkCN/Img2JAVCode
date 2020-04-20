from keras.applications.vgg16 import VGG16
from keras.preprocessing import image
from keras.applications.vgg16 import preprocess_input
import numpy as np

def vggFeatGen(img_path):
    model = VGG16(weights='imagenet', include_top=False)

    img = image.load_img(img_path, target_size=(224, 224))
    img = image.img_to_array(img)
    img = np.expand_dims(img, axis=0)
    img = preprocess_input(img)

    features = model.predict(img)
    return features


print(vggFeatGen('01.png'))
