import cv2
import tensorflow as tf
import os
from tensorflow.keras.preprocessing import image
import numpy as np
from tensorflow.keras.applications.resnet50 import preprocess_input, decode_predictions
from time import time, sleep


def predict(model, path_img):
    IMG_SIZE = 224
    class_names = ['nok', 'ok']

    # Show image to predict - just for visualization
    img = cv2.imread(path_img)
    cv2.imshow('IMAGE TO TEST', img)
    cv2.waitKey(0)

    img = image.load_img(path_img, target_size=(IMG_SIZE, IMG_SIZE))
    img_array = image.img_to_array(img)
    img_batch = np.expand_dims(img_array, axis=0)
    img_preprocessed = preprocess_input(img_batch)

    # Prediction -> higher probability
    prediction = model.predict(img_preprocessed)
    class_predict = class_names[np.argmax(prediction[0])]
    print(prediction)
    if prediction[0][np.argmax(prediction[0])] < 0.9:
        class_predict = 'not_sure'
    else:
        print(class_predict)

    return class_predict


def bin(image):
    img = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 25, 2)
    # _, img = cv2.threshold(image, 180, 255, cv2.THRESH_BINARY)
    return img


def equ(image):
    img = cv2.equalizeHist(image)
    return img


def process(img, path_save, save_name):

    # proc_img = bin(equ(img))
    proc_img = bin(img)
    cv2.imwrite(os.path.join(path_save, save_name), proc_img)
    return proc_img


def newest(path):
    files = os.listdir(path)
    paths = [os.path.join(path, basename) for basename in files]
    return max(paths, key=os.path.getctime)


def feedback(color):

    if color == 'red':
        bgr = (0, 0, 255)
        win_name = 'SURFACE IS DAMAGED'
    elif color == 'green':
        bgr = (255, 0, 0)
        win_name = 'SURFACE IS OK'

    # Create a blank 300x300 black image
    image = np.zeros((800, 1200, 3), np.uint8)
    # Fill image with red color(set each pixel to red)
    image[:] = bgr

    cv2.imshow(win_name, image)
    cv2.waitKey(3000)


def main():

    list_of_files = '../../../imagens/test_images/PointGrey/SpinView_trigger'
    try:
        nr_pics_old = len(os.listdir(list_of_files))
    except:
        nr_pics_old = 0

    # Load tf model
    model = tf.keras.models.load_model('../models/model_2_2')

    while 1:

        sleep(5)

        try:
            nr_pics = len(os.listdir(list_of_files))
        except:
            nr_pics = 0

        if nr_pics == nr_pics_old:
            print('There\'s no new picture yet')
            continue
        else:
            nr_pics_old = nr_pics
            latest_file = newest(list_of_files)

        # Load original image
        path_img = latest_file
        path_save = "images_saved"

        img_original = cv2.imread(path_img, cv2.IMREAD_GRAYSCALE)

        # Divide original image in 4 images of 450 x 450
        img_tl = img_original[0:450, 0:450]  # Image top left
        img_tr = img_original[0:450, 358:]  # Image top right
        img_bl = img_original[158:, 0:450]  # Image bottom left
        img_br = img_original[158:, 358:]  # Image bottom right

        imgs = [img_tl, img_tr, img_bl, img_br]

        try:
            latest_nr = newest(path_save)[13:-4]
            a = int(latest_nr) + 1
        except:
            a = 1

        i = 0
        for img in imgs:
            file_name = str(a) + '.jpg'
            proc_img = process(img, path_save, file_name)

            img_pred = newest(path_save)
            prediction = predict(model, img_pred)
            if prediction == 'nok':
                print('SURFACE IS DAMAGED')
                feedback('red')
                break
            elif prediction == 'not_sure':
                print('Unsure about the class, it is assumed to be ok.')

            # Update variables
            a += 1
            i += 1

            if i == 4:
                print('SURFACE IS OK')
                feedback('green')


if __name__ == '__main__':
    main()
