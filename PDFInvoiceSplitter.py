from ctypes import sizeof
import os
from PyPDF2 import PdfFileReader, PdfFileWriter

#returns true if string contains any numerical characters
def has_numbers(inputString):
    return any(char.isdigit() for char in inputString)

#returns true if number is a price (1,889.00)
def is_price(inputString):
    return any(char == "." or char == "," for char in inputString)

#returns true if invoice is valid
def is_valid(invoicesDict, pageNumber): 
    
    #returns false if invoice# is lower than previous invoice#
    if len(invoicesDict) > 0: return invoicesDict[-1][0] < pageNumber

    #returns false if invoice already exist in that certain page number
    for invoice in invoicesDict:
        if invoice[0] == pageNumber: return False

    return True

#Attempt to recover data by renaming word
def attempt_data_recovery(word):
    if int(word) < 100000: return "1" + word

#Print invoices (PageNumber - InvoiceNumber)
def printInvoices(invoicesDict):
    for invoice in invoicesDict:
        print(str(invoice[0]) + " - " + invoice[1])

#Scrap invoice numbers from every pdf page and add to list as a tuple(Page Number, Invoice#)
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

                    #Check if invoice is valid
                    if is_valid(invoicesDict, i + 1): 
                        invoicesDict.append((i + 1, str(word)))

            except IndexError:
                print("Out of Index")
            except TypeError:
                pass
            except ValueError:
                pass

    return invoicesDict

def split_invoicePDF(invoicesDict, path):
    pdfFileObject = open(path, 'rb')
    pdfReader = PdfFileReader(pdfFileObject)
    
    for index in range(len(invoicesDict)):
        writer = PdfFileWriter()

        #Get start and end pages for each invoice
        start = invoicesDict[index][0] - 1
        if index + 3 < len(invoicesDict):
            end = invoicesDict[index + 1][0] - 2
        else: 
            end = pdfReader.getNumPages() - 1

        #Create new pdf file name/page range
        while start <= end:
            writer.addPage(pdfReader.getPage(start))
            start += 1
            output_filename = "{}.pdf".format(
                invoicesDict[index][1]
            )
        
        #Write and save new PDF file
        parentPdfDir = "/".join(pdf_path.rsplit("/")[0:len(pdf_path.rsplit("/")) - 1])
        with open(parentPdfDir + "/" + output_filename, "wb") as out:
            writer.write(out)
#-------------- MAIN ------------------

pdf_path=r"C:/.../PDFInvoice.pdf"

#List of Tuples [(Invoice#, Page#), ...]
invoices = []
invoices = scrap_invoices(invoices, pdf_path)
printInvoices(invoices)
print(len(invoices))

#Extracts out all Invoices into seperate PDF files at the pdf_path parent location
#split_invoicePDF(invoices, pdf_path)
