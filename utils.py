import cv2
import numpy as np


def dodgeV2(image, mask):
    return cv2.divide(image, 255 - mask, scale=256)


SCALE_PERCENT = 0.60


def pic_to_sketch(file_path):
    pic = cv2.imread(file_path)

    width = int(pic.shape[1] * SCALE_PERCENT)
    height = int(pic.shape[0] * SCALE_PERCENT)

    dim = (width, height)
    resized = cv2.resize(pic, dim, interpolation=cv2.INTER_AREA)

    kernel_sharpening = np.array([[-1, -1, -1],
                                  [-1, 9, -1],
                                  [-1, -1, -1]])
    sharpened = cv2.filter2D(resized, -1, kernel_sharpening)

    gray = cv2.cvtColor(sharpened, cv2.COLOR_BGR2GRAY)
    inv = 255 - gray
    gauss = cv2.GaussianBlur(inv, ksize=(15, 15), sigmaX=0, sigmaY=0)

    return dodgeV2(gray, gauss)


if __name__ == '__main__':
    name = input("Enter file name: ")
    new_file = pic_to_sketch(name)
    cv2.imwrite("new_image.jpg", new_file)
