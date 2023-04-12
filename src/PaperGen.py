import cv2
import numpy as np
import random
from PIL import ImageDraw, Image
import heapq
from Classes.Settings import Settings

############
# SETTINGS #
############
settings = Settings(
    showLines=False,
    outputBlank=True,
    fontSize=100,
    fonts=['./assets/font.ttf', './assets/font2.ttf'],
    randomFontColors=False
)

#############
#  PROGRAM  #
#############

print("Hello World!")

def paper_gen(textFile, pageNumber, actually_overflow):
    if actually_overflow != "":
        textFile.insert(0, actually_overflow)
    
    pageName = f'./input/image{pageNumber % settings.totalPages}.png'
    
    #Simple Functions
    #checks length of String, returns bool True/False
    def length(text, font):
        return int(draw.textlength(text, font=font))

    #Bisection Search
    def bisect_text(string, width, font):
        # check if text fits right away
        if length(string, font) <= width:
            return string, ""
        # Set up variables
        words=string.split()
        start, end = 0, len(words)
        overflow = ''
        # Binary search for split points
        while start < end:
            mid = (start+end)//2
            if length(' '.join(words[:mid]), font) <= width:
                start = mid + 1
            else:
                end = mid 

        # Determine the optimal split point within the chosen range of indices
        split = start
        if split > 0 and length(' '.join(words[:split]), font) > width:
            split -= 1

        # Construct the text and overflow strings
        text = ' '.join(words[:split])
        if split < len(words):
            overflow = ' '.join(words[split:])
        else:
            overflow = ""
        return text, overflow

    # Load the input images
    img = cv2.imread(pageName)
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
    filtered_vertical_lines = []
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
    
        # if angle is almost 0 and the line's x coordinates are in the first 15% of the page
        elif (angle <= 5.0 and angle >= -5.0) and (line[0][0]<(width*0.15) and line[0][2]<(width*0.15)):
            filtered_vertical_lines.append((int((x1+x2)/2), int((y1+y2)/2)))
            if settings.showLines:
                cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
            if settings.outputBlank:
                cv2.line(blank_image, (x1, y1), (x2, y2), (0, 0, 255), 2)

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
    global start; start = 0
    def write_text(input_text, index, color = (0, 0, 0, 220)):
        full_text = input_text
        overflow_text = ""
        text = ""
        last_line = ""
        
        while full_text != "":
            if index >= len(grouped_mids):
                return (999999999, overflow_text, last_line)
            avg = int(sum(grouped_mids[index])/len(grouped_mids[index]))
            angle = group_angles[index]
            # Set mean X start to find the x coordinate of the nearest line vertically in the filtered_lines array
            mean_x_start, mean_y_start = heapq.nsmallest(1, filtered_vertical_lines, key=lambda x: abs(x[1] - avg ))[0]
            if avg > 100:
                seed = random.randint(0, len(settings.fonts)-1)
                font = settings.fonts[seed]
                
                if overflow_text == "":
                    global start; start += 1
                    text = full_text
                elif full_text != "":
                    text = overflow_text
                    overflow_text = ""

                text, overflow_text = bisect_text(text, width - mean_x_start, font)
                
                if text != "":
                    x0, y0, x1, y1 = font.getbbox(text)
                    text_width = x1 - x0
                    text_height = y1 - y0 + 100
                    
                    image2 = Image.new('RGBA', (text_width, text_height), (0, 0, 128, 0))
                    
                    draw2 = ImageDraw.Draw(image2)
                    draw2.text((0, 0), text=text, font=font, fill=settings.colors[seed] if settings.randomFontColors else color)
                    last_line = text
                    # draw2.line((0, 0, text_width, 0), fill=(0, 255, 0), width=5)
                    image2 = image2.rotate(angle*1.1, expand=True)
                    px, py = (mean_x_start+random.randrange(int(mean_x_start*0.05), int(mean_x_start*0.1))), avg
                    sx, sy = image2.size
                    y_offset = -5
                    pil_image.paste(image2, (px, py-y_offset, px + sx, py-y_offset + sy), image2)
                else:
                    index -= 1
                full_text = full_text.replace(text, "").strip(" ")
            index += 1
            
        return (index, text, last_line)

    actual_overflow = ""
    last_line_written = ""
    for text in textFile:
        if index == 999999999:
            break
        elif text.startswith("RED: "):
            text = text.replace("RED: ", "").strip()
            index, actual_overflow, last_line_written = write_text(text, index, (55, 52, 255))
        elif text.startswith("BLUE: "):
            text = text.replace("BLUE: ", "").strip()
            index, actual_overflow, last_line_written = write_text(text, index, (255, 33, 33))
        elif text.startswith("SUMMARY: "):
            text = text.replace("SUMMARY: ", "").strip()
            index, actual_overflow, last_line_written = write_text(text, index, (0, 0, 0, 240))
        elif text != "":
            index, actual_overflow, last_line_written = write_text(text, index, (0, 0, 0, 240))
        
    opencv_image = np.array(pil_image)
    final_image = cv2.GaussianBlur(opencv_image, (3, 3), 0)

    # Write the new image to a file
    cv2.imwrite('./output/linesDetectedBlank.jpg', blank_image)

    # Display the result
    cv2.imwrite(f'./output/output{pageNumber}.png', final_image)
    print("Wrote page", pageNumber)
    
    #print(start, textFile[start-1], actual_overflow.strip())

    newTextFile = textFile[start:]
    if len(newTextFile) == 0:
        return
    paper_gen(newTextFile, pageNumber+1, actual_overflow.strip())
    