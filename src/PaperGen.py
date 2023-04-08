import cv2
import numpy as np
import random
from PIL import ImageFont, ImageDraw, Image
import lorem

import LineDetection
from Classes.Settings import Settings

############
# SETTINGS #
############
settings = Settings(
    showLines=False,
    outputBlank=True,
    fontSize=115,
    fonts=['./assets/font.ttf', './assets/font2.ttf'],
    randomFontColors=False
)

#############
#  PROGRAM  #
#############

print("Hello World!")

# Load the input images
img = cv2.imread('./input/image2.png')
# Convert the image to grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# Apply a Gaussian blur to the image
blur = cv2.GaussianBlur(gray, (5, 5), 0)
# Perform Canny edge detection on the blurred image
edges = cv2.Canny(blur, 50, 150, apertureSize=3, L2gradient=False)
# Find the lines in the image using the HoughLinesP transform
lines = cv2.HoughLinesP(edges, rho=1, theta=np.pi/180, threshold=50, minLineLength=50, maxLineGap=10)

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
        if settings.showLines:
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 2)
        if settings.outputBlank:
            cv2.line(blank_image, (x1, y1), (x2, y2), (255, 0, 0), 2)
    elif (angle <= 5.0 and angle >= 0.0):
        filtered_vertical_x.append(int((x1+x2)/2))

mean_x_start = int(sum(filtered_vertical_x)/len(filtered_vertical_x))
offset_upper_bound = int(mean_x_start*0.2)
offset_lower_bound = int(mean_x_start*0.08)

filtered_mids.sort()
grouped_mids = []
grouped_lines = []

group = [filtered_mids[0]]
group_lines = [filtered_lines[0]]
for i in range(1, len(filtered_mids)):
    if filtered_mids[i] - group[-1] <= 23:
        group.append(filtered_mids[i])
        group_lines.append(filtered_lines[i])
    else:
        grouped_mids.append(group)
        grouped_lines.append(group_lines)
        group = [filtered_mids[i]]
        group_lines = [filtered_lines[i]]
grouped_mids.append(group)
grouped_lines.append(group_lines)

group_angles = []
for group in grouped_lines:
    angles = []
    for line in group:
        x1, y1, x2, y2 = line[0]
        angles.append(-(np.arctan2(y2-y1, x2-x1) * 180 / np.pi - 0))
    mean = sum(angles)/len(angles)
    group_angles.append(mean)

if settings.showLines or settings.outputBlank:
    for item in grouped_mids:
        if settings.outputBlank:
            cv2.line(blank_image, (0, int(sum(item)/len(item))),
                     (width, int(sum(item)/len(item))), (255, 255, 255), 2)
        if settings.showLines:
            cv2.line(img, (0, int(sum(item)/len(item))),
                     (width, int(sum(item)/len(item))), (0, 255, 0, 0.2), 2)

pil_image = Image.fromarray(img)
draw = ImageDraw.Draw(pil_image)

index = 0


def write_text(input_text, index, color = (0, 0, 0, 220)):
    counter = 0
    full_text = input_text
    overflow_text = ""
    
    while full_text != "":
        avg = int(sum(grouped_mids[index])/len(grouped_mids[index]))
        angle = group_angles[index]
        if avg > 100:
            seed = random.randint(0, len(settings.fonts)-1)
            font = settings.fonts[seed]
            
            text = ""
            if overflow_text == "":
                text = full_text
            elif full_text != "":
                text = overflow_text
                overflow_text = ""

            text_length = int(draw.textlength(text, font=font))

            while text_length > (width - mean_x_start):
                split_text = text.split()
                overflow_text = split_text[-1]+" "+overflow_text
                split_text.pop()
                text = ' '.join(split_text)
                text_length = int(draw.textlength(
                    text, font=font))

            if overflow_text != "" or counter == 0:
                x0, y0, x1, y1 = font.getbbox(text)
                text_width = x1 - x0
                text_height = y1 - y0
                
                image2 = Image.new('RGBA', (text_width, text_height), (0, 0, 128, 0))
                
                draw2 = ImageDraw.Draw(image2)
                draw2.text((0, 0), text=text, font=font, fill=settings.colors[seed] if settings.randomFontColors else color)
                # draw2.line((0, 0, text_width, 0), fill=(0, 255, 0), width=5)
                image2 = image2.rotate(angle*1.1, expand=True)
                
                px, py = (mean_x_start-random.randint(offset_lower_bound, offset_upper_bound)), avg
                sx, sy = image2.size
                y_offset = 10
                pil_image.paste(image2, (px, py-y_offset, px + sx, py-y_offset + sy), image2)

                # draw.text(
                #     (mean_x_start-random.randint(offset_lower_bound,
                #      offset_upper_bound), avg),
                #     text,
                #     font=font,
                #     fill=settings.colors[seed] if settings.randomFontColors else color
                # )
            else:
                index -= 1
            full_text = full_text.replace(text, "").strip(" ")
        index += 1
        counter += 1
    return index

index = write_text(lorem.paragraph(), index, (0, 0, 255))
index = write_text(lorem.paragraph(), index, (255, 0, 0))
index = write_text(lorem.paragraph(), index, (0, 0, 255))
index = write_text(lorem.paragraph(), index, (255, 0, 0))
index = write_text(lorem.paragraph(), index, (0, 0, 255))
index = write_text(lorem.paragraph(), index, (255, 0, 0))

opencv_image = np.array(pil_image)
final_image = cv2.GaussianBlur(opencv_image, (3, 3), 0)

# Write the new image to a file
cv2.imwrite('./output/linesDetectedBlank.jpg', blank_image)

# Display the result
cv2.imwrite('./output/linesDetected.png', final_image)
