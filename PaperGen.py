import cv2
import numpy as np
import random
from PIL import ImageFont, ImageDraw, Image
import lorem

font_size = 90
fonts = [ImageFont.truetype('./font.ttf', font_size),
         ImageFont.truetype('./font2.ttf', font_size)]
colors = [(0, 0, 0), (255, 0, 0)]

print("Hello World!")

# Load the input image
img = cv2.imread('image2.png')

# Convert the image to grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Apply a Gaussian blur to the image
blur = cv2.GaussianBlur(gray, (5, 5), 0)

# Perform Canny edge detection on the blurred image
edges = cv2.Canny(blur, 50, 150, apertureSize=3, L2gradient=False)

# Find the lines in the image using the HoughLinesP transform
lines = cv2.HoughLinesP(edges, rho=1, theta=np.pi/180,
                        threshold=50, minLineLength=50, maxLineGap=10)

height, width = img.shape[:2]
blank_image = np.zeros((height, width, 3), np.uint8)

filtered_lines = []
filtered_vertical_x = []
filtered_mids = []

# Draw the lines on the original image
for line in lines:
    x1, y1, x2, y2 = line[0]
    angle = np.abs(np.arctan2(y2-y1, x2-x1) * 180 / np.pi - 90)
    # check if the angle is less than or equal to 60 degrees from vertical
    if (angle <= 95.0 and angle >= 85.0):
        filtered_lines.append(line)
        filtered_mids.append(int((y1+y2)/2))
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 2)
    elif (angle <= 5.0 and angle >= 0.0):
        filtered_vertical_x.append(int((x1+x2)/2))

mean_x_start = int(sum(filtered_vertical_x)/len(filtered_vertical_x))

filtered_mids.sort()
grouped_mids = []

group = [filtered_mids[0]]
for i in range(1, len(filtered_mids)):
    if filtered_mids[i] - group[-1] <= 30:
        group.append(filtered_mids[i])
    else:
        grouped_mids.append(group)
        group = [filtered_mids[i]]
grouped_mids.append(group)

for item in grouped_mids:
    cv2.line(img, (0, int(sum(item)/len(item))),
             (width, int(sum(item)/len(item))), (0, 255, 0), 2)

pil_image = Image.fromarray(img)
draw = ImageDraw.Draw(pil_image)

index = 0

def write_text(input_text, index, color=(0, 0, 0)):
    counter = 0
    full_text = input_text
    overflow_text = ""
    while full_text != "":
        avg = int(sum(grouped_mids[index])/len(grouped_mids[index]))
        if avg > 100:
            seed = random.randint(0, len(fonts)-1)

            if overflow_text == "":
                text = full_text
            elif full_text != "":
                text = overflow_text
                overflow_text = ""

            text_length = int(draw.textlength(text, font=fonts[seed]))

            while text_length > (width - mean_x_start):
                split_text = text.split()
                overflow_text = split_text[-1]+" "+overflow_text
                split_text.pop()
                text = ' '.join(split_text)
                text_length = int(draw.textlength(text, font=fonts[seed]))

            if overflow_text != "" or counter == 0:
                draw.text(
                    (mean_x_start-random.randint(15, 40), avg),
                    text,
                    font=fonts[seed],
                    fill=color
                )
            else:
                index -= 1
            full_text = full_text.replace(text, "").strip(" ")
        index += 1
        counter += 1
    return index

index = write_text(lorem.paragraph(), index)
index = write_text(lorem.paragraph(), index, (255, 0, 0))
index = write_text(lorem.paragraph(), index, (0, 0, 255))

opencv_image = np.array(pil_image)
final_image = cv2.GaussianBlur(opencv_image, (3, 3), 0)

# Write the new image to a file
cv2.imwrite('linesDetectedBlank.jpg', blank_image)

# Display the result
cv2.imwrite('linesDetected.png', final_image)
