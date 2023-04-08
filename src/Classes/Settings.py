from PIL import ImageFont
from typing import List
import random

class Settings:
  showLines = True
  outputBlank = True
  fontSize = 90
  fonts = []
  colors = []
  randomFontColors = False
  
  def __init__(
    self, 
    showLines: bool, 
    outputBlank: bool, 
    fontSize: int, 
    fonts: List[str],
    randomFontColors: bool = False
  ):
    self.showLines = showLines
    self.outputBlank = outputBlank
    self.fontSize = fontSize
    self.randomFontColors = randomFontColors
    for font in fonts:
      self.fonts.append(ImageFont.truetype(font, fontSize))
      if randomFontColors:
        self.colors.append((random.randint(0, 128), random.randint(0, 128), random.randint(0, 128)))
      else:
        self.colors.append((0, 0, 0))
      
    