from PIL import ImageFont
from typing import List
import random
import os

class Settings:
  showLines = True
  outputBlank = True
  fontSize = 90
  fonts = []
  headerFonts = []
  subHeaderFonts = []
  colors = []
  randomFontColors = False
  totalPages = 0
  
  def __init__(
    self, 
    showLines: bool, 
    outputBlank: bool, 
    fontSize: int, 
    fonts: List[str],
    randomFontColors: bool = False
  ):
    
    if not os.path.exists("./output"):
      os.mkdir("./output")
    dir_list = os.listdir("./input")
    self.showLines = showLines
    self.outputBlank = outputBlank
    self.fontSize = fontSize
    self.randomFontColors = randomFontColors

    for file in dir_list:
      if file.endswith(".png") and file.startswith("image"):
        self.totalPages += 1

    for font in fonts:
      self.fonts.append(ImageFont.truetype(font, fontSize))
      self.headerFonts.append(ImageFont.truetype(font, fontSize))
      self.subHeaderFonts.append(ImageFont.truetype(font, fontSize))
      
      if randomFontColors:
        self.colors.append((random.randint(0, 128), random.randint(0, 128), random.randint(0, 128)))
      else:
        self.colors.append((0, 0, 0))
        
    
      
    