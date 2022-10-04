import pdfkit

options = {
    'page-size': 'Letter',
    'margin-top': '0.2in',
    'margin-right': '0.0in',
    'margin-bottom': '0.0in',
    'margin-left': '0.2in',
    'zoom': '1.2',
    'no-outline': None
}

pdfkit.from_file(['../html/383.1.html','../html/383.2.html','../html/383.3.html'],"../pdf/383.pdf",options=options)
pdfkit.from_file(['../html/090.1.html','../html/090.2.html','../html/090.3.html'],"../pdf/090.pdf",options=options)
pdfkit.from_file('../html/050.1.html',"../pdf/050.pdf",options=options)
pdfkit.from_file('../html/020.1.html',"../pdf/020.pdf",options=options)
pdfkit.from_file('../html/210.1.html',"../pdf/210.pdf",options=options)
