from spire.pdf.common import *
from spire.pdf import *

doc = PdfDocument()
doc.LoadFromFile('ncert-textbook-for-class-11-maths-chapter-11.pdf')

page = doc.Pages[1]

images = []
for image in page.ExtractImages():
    images.append(image)

index = 0
for image in images:
    imageFileName = 'C:/Users/Administrator/Desktop/Extracted/Image-{0:d}.png'.format(index)
    index += 1
    image.Save(imageFileName, ImageFormat.get_Png())
doc.Close()