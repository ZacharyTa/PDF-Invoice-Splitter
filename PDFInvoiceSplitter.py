from PyPDF2 import PdfFileReader

#returns true if string contains any numerical characters
def has_numbers(inputString):
    return any(char.isdigit() for char in inputString)

#returns true if number is a price (1,889.00)
def is_price(inputString):
    return any(char == "." or char == "," for char in inputString)

#returns true if invoice already exist in that certain page number
def invoice_exist(pageNumber): 
    try:
        if invoices[pageNumber]: 
            return True
    except KeyError:
        return False

#Attempt to recover data by renaming word
def attempt_data_recovery(word):
    if int(word) < 100000: return "1" + word

#Scrap invoice numbers from every pdf page and add to dictionary{"Page Number": Invoice#}
def scrap_invoices(invoicesDict, path):

    pdfFileObject = open(path, 'rb')
    pdfReader = PdfFileReader(pdfFileObject)

    for i in range(0,pdfReader.numPages):
        print(i)
        words = []
        # creating a page object
        pageObj = pdfReader.getPage(i)
        # extracting text from page into list
        words = pageObj.extractText().split()
        for word in words: 
            try:
                #Clean string to only have numbers
                if has_numbers(word): 

                    #Check string if its a price
                    if not is_price(word):
                        for letter in word:
                            if not letter.isnumeric(): word = word.replace(letter, "")

                #Data Recovery Attempt (If misread first number: r90849 -> 190849)
                if int(word) < 100000: word = attempt_data_recovery(word)
                
                #Only Accept number number range 180000-191000
                if int(word) >= 180000 and int(word) <= 191000: 

                    #Check if invoice at page already exist
                    if not invoice_exist(str(i + 1)): invoicesDict[str(i + 1)] = str(word)

            except IndexError:
                print("Out of Index")
            except TypeError:
                pass
            except ValueError:
                pass

    return invoicesDict

#-------------- MAIN ------------------

pdf_path=r"G:Office Share/MISS LE/HD95/Image_001.pdf"

#Dictionary ("Invoice#" : Page#)
invoices = {}
invoices = scrap_invoices(invoices, pdf_path)

for key in invoices:
    print(str(key) + " - " + invoices.get(key))