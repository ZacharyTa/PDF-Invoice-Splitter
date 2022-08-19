from ctypes import sizeof
import os
from PyPDF2 import PdfFileReader, PdfFileWriter

#returns true if string contains any numerical characters
def has_numbers(inputString):
    return any(char.isdigit() for char in inputString)

#returns true if number is a price (1,889.00)
def is_price(inputString):

    #return False if string contains alphabet character
    if any(char.isalpha() for char in inputString): return False

    #Return true of false if it contains "." or "$"
    return any(char == "." or char == "$" for char in inputString)

#returns true if invoice is valid
def is_valid(invoicesDict, pageNumber, invoiceNumber): 
    
    try:
        #return false if value less than 6 digits
        if int(invoiceNumber) < 100000: return False

        #return false if value incorrect invoice range
        elif int(invoiceNumber) <= 170000 or int(invoiceNumber) >= 191000: return False

        #returns false if invoice# is lower than previous invoice#
        elif len(invoicesDict) > 0: 
            return invoicesDict[-1][1] <= invoiceNumber

        #returns false if invoice already exist in that certain page number
        for invoice in invoicesDict:
            if invoicesDict[-1] == pageNumber: return False

        return True
    
    except TypeError:
        pass

#Attempt to recover data by renaming word
def attempt_data_recovery(invoicesDict, pageNumber, word):
    try:
        if word.isnumeric(): 

            #Add "1" in front if it'll make the invoice# valid
            if int(word) < 100000 and is_valid(invoicesDict, pageNumber, int(word) + 100000): return "1" + word

            #Remove most significant digit if it'll make the invoice valid
            if int(word) >= 1000000 and is_valid(invoicesDict, pageNumber, word[1:]): return word[1:]

        #removes "'" in word
        if "'" in word:
            tempWords = word.rsplit("'")
            newWord = ""
            for tempWord in tempWords:

                #Only add concatenate elements with only numbers (Exception: and "s" in case it misread "5")
                if tempWord.isnumeric(): newWord += tempWord

                #Add 1 at the end if valid incase last number was misread as character
                elif len(tempWord) == 1 and is_valid(invoicesDict, pageNumber, newWord + "1"): newWord += "1"

            if is_valid(invoicesDict, pageNumber, newWord): 
                return newWord

        else:
            newWord = ""
            for letter in word:
                if letter.isdigit(): newWord += letter
            if is_valid(invoicesDict, pageNumber, newWord): return newWord

        if is_valid(invoicesDict, pageNumber, word.replace("s", "5")): return word.replace("s", "5")


    except TypeError:
        pass

#Print invoices (PageNumber - InvoiceNumber)
def print_Invoices(invoicesDict):
    for invoice in invoicesDict:
        print(str(invoice[0]) + " - " + invoice[1])

#returns most Valid invoice from list "validWords"
def most_valid_Invoice(validWords, invoicesDict):

    if len(invoicesDict) > 0:

        #minInvoice = (difference, invoice#)
        minInvoice = (int(validWords[0]) - int(invoicesDict[-1][1]), validWords[0])
        for tempWord in validWords:
            if (int(tempWord) - int(invoicesDict[-1][1])) < minInvoice[0]: minInvoice = (int(tempWord) - int(invoicesDict[-1][1]), tempWord)
        return str(minInvoice[1])
    else: return validWords[0]

#attempts to reconstruct valid invoice by concatenating numbers after "invoice" ["Invoice", "1", "8'1", "376"] -> "181376"
def invoice_reconstruction(validWords, invoicesDict, pageNumber, words, word):
    indexINV = words.index(word) + 1
    tempWord = ""
    while "t" in words[indexINV] or has_numbers(words[indexINV]):
        if has_numbers(words[indexINV]) and "t" not in words[indexINV]:
            if words[indexINV].isnumeric(): tempWord += words[indexINV]
            else:
                for letter in words[indexINV]:
                    if letter.isdigit(): tempWord += letter
                    elif letter == "s": tempWord += "5"
                    elif letter.isalpha(): tempWord += "1"
        indexINV += 1
    if is_valid(invoicesDict, pageNumber, tempWord): validWords.append(tempWord)

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

        #list of valid words
        validWords = []

        for word in words: 
            try:
                if "bill" in word.lower(): break
                #Invoice number reconstruction attempt after "Invoice"
                if "VO" in word or "vo" in word: invoice_reconstruction(validWords, invoicesDict, i + 1, words, word)

                #Check if string has any numbers
                if has_numbers(word): 

                    #Check string if its a price
                    if not is_price(word):
                        #Splits string if it contains "'" or sees if "5" was misread as "s"
                        if "'" in word or "s" in word: word = attempt_data_recovery(invoicesDict, i + 1, word)

                        #Clean string to only have numbers
                        for letter in word:
                            if not letter.isnumeric(): 
                                word = word.replace(letter, "")

                        #Data Recovery Attempt (If misread first number: r90849 -> 190849)
                        if not is_valid(invoicesDict, i + 1, word): 
                            word = attempt_data_recovery(invoicesDict, i + 1, word)

                        #Check if invoice is valid
                        if is_valid(invoicesDict, i + 1, word): 
                            validWords.append(str(word))

            except IndexError:
                print("Out of Index")
            except TypeError:
                pass
            except ValueError:
                pass

        if i == 0 or len(validWords) == 1: 
            invoicesDict.append(((i + 1), str(validWords[0])))
        elif len(validWords) > 1: 
            if most_valid_Invoice(validWords, invoicesDict) != invoicesDict[-1][1]: invoicesDict.append((i + 1, most_valid_Invoice(validWords, invoicesDict)))
    return invoicesDict

#Splits Invoices into seperate pdfs within original pdf's same directory
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

#Lists pdf names in a given folder directory
def RecursivelyListFileNames(folder, names):
      
  #If path is a a file
  if os.path.isdir(folder) == False: names.append(folder)
    
  else:
    with os.scandir(folder) as folders:
      for folderDir in folders:
        RecursivelyListFileNames(folderDir, names)
#-------------- MAIN ------------------

pdf_path=r"C:/Users/User/Desktop/Test/Image_001.pdf"

#List of Tuples [(Invoice#, Page#), ...]
invoices = []
invoices = scrap_invoices(invoices, pdf_path)
print_Invoices(invoices)
print(len(invoices))

#Extracts out all Invoices into seperate PDF files at the pdf_path parent location
split_invoicePDF(invoices, pdf_path)