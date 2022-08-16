# PDF-Invoice-Splitter
====================    PURPOSE   ========================

Separates a large sorted PDF containing multiple Invoices into individual PDF Invoice files

==================    HOW TO USE    ======================

- Copy and paste PDF path directory into variable, "pdf_file"
> Ex. pdf_path = r"C:/.../PDFInvoice.pdf"
>> NOTE: Use forward slash ("/") instead of back slash ("\")

- Run program
> PDF Files will be extracted within the same parent directory

====================    METHOD    ========================

- Uses PyPDF2 library
> Scraps text from PDF file
>
> Cleans text data into manageable/valid integers
>
> Locate valid Invoice Numbers and its page number
>
> Creates/Writes to new PDF Files for each Invoice

================     POSSIBLE BUGS    ==================
- Possiblilty of inaccurate text scraping
> (Ex. "r23456" instead of "123456")
>> Solution to case 1: Misreads first character 
>>
>> Remove all non-numerical characters
>>
>> If Number < 100000, then add "1" in front of number
>>
>> (NOTE: All invoice numbers have 6 digits)
