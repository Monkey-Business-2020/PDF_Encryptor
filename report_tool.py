#!/usr/bin/python3

from time import sleep
import subprocess, requests, argparse, PyPDF2, os
from termcolor import colored

print("\n")
print("""
  ____  ____  _____   _____                              _            
 |  _ \|  _ \|  ___| | ____|_ __   ___ _ __ _   _ _ __  | |_ ___ _ __ 
 | |_) | | | | |_    |  _| | '_ \ / __| '__| | | | '_ \ | __/ _ \ '__|
 |  __/| |_| |  _|   | |___| | | | (__| |  | |_| | |_) ||  ||  __/ |   
 |_|   |____/|_|     |_____|_| |_|\___|_|   \__, | .__/  \__\___|_|   
                                            |___/|_|                 
Author: Norseman2020
      
This tool helps to encrypt a PDF with a password generated and stored in 1Password and then creates a 1-time link for that password.
""")

def passwordGenny(companyname):
    # Grab Company name from user
    companyName = companyname

    # Generate a password and save it in 1Password
    print(colored("\nGenerating Password...", "green"))
    sleep(1)
    results = subprocess.Popen(['op', 'item', 'create', '--category', 'Password', '--title', f'{companyName} Report', '--vault', 'Fileshare Reports', '--generate-password=16,letters,symbols'], stdout=subprocess.PIPE, text=True)
    output = results.communicate()
    lines = output[0].split('\n')
    password_ID = ""
    password_for_PDF_encryption = ""
    
    for item in lines:
        if item.startswith("ID:"):
            id_value = item.split(":")[1].strip()
            password_ID = id_value

    reveal_password = subprocess.Popen(['op', 'item', 'get', f'{password_ID}', '--reveal'], stdout=subprocess.PIPE, text=True)
    generated_password = reveal_password.communicate()
    text_data = generated_password[0]
    for line in text_data.splitlines():
        if 'password:' in line:
            # Split the line by ':' and strip any leading/trailing spaces to get the password value
            password = line.split(':')[1].strip()
            password_for_PDF_encryption = password

    sleep(0.5)
    print(colored(f"\nGenerated Password & Saved in ", "green") + colored("1Password", "blue") + colored(" as ", "green") + colored(f"{companyName}", "blue"))
    sleep(0.5)
    print(colored(f"\nGenerated Password: {password_for_PDF_encryption}", "green"))
    return password_for_PDF_encryption

def pdfEncryptor(pdfFile, password):
    print(f"\nEncrypting the " + colored(f"{pdfFile}", "yellow") + " file.")
    
    # Open the PDF file in read-binary mode
    with open(pdfFile, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)

        # Create a PDF writer object to write the encrypted PDF
        pdf_writer = PyPDF2.PdfWriter()

        # Add all pages from the original PDF to the writer
        for page_num in range(len(pdf_reader.pages)):
            pdf_writer.add_page(pdf_reader.pages[page_num])

        # Encrypt the PDF with a password
        pdf_writer.encrypt(password)

        # Write the encrypted PDF to the output file
        isolated_pdfFile = os.path.basename(pdfFile)
        filepath = os.path.dirname(pdfFile)
        output_path = os.path.join(filepath, 'encrypted_' + isolated_pdfFile)
        
        with open(output_path, 'wb') as output_pdf:
            print(f"\nSaving to {output_path}")
            pdf_writer.write(output_pdf)
        
        print(f"\nEncrypted PDF: {colored(f'{output_path}', 'yellow')}")

def oneTimeLink(password):
    # Generate a 1-Time link with the generated password as the "note", print out the URL path.
    print(colored("\nGenerating a 1-Time Link...", "white"))
    sleep(1)
    oneTime_url = "https://1ty.me/?mode=ajax&cmd=create_note"
    oneTime_PostData = {"note":f"{password}","email":"","reference":"","newsletter":"","expires_on":"undefined"}
    oneTimeRequest = requests.post(url=oneTime_url, data=oneTime_PostData)
    oneTimeRequest_link = oneTimeRequest.text.split('"')[-2]

    link = "https://1ty.me/" + oneTimeRequest_link
    print("\n1-Time Link: " + colored(f"{link}", "cyan") + "\n")

def zipup(filename, companyname):
    zip_filename = f"{companyname}_Encrypted_Reports.zip"
    print(f"- {filename}.pdf \n\n- {filename}.docx \n\nWill now be encrypted in a pasword protected ZIP.\n")

    # Create a ZIP file
    results = subprocess.Popen(['zip', '-e', f'{zip_filename}', f'{filename}.pdf', f'{filename}.docx', f'{filename}.doc'], stdout=subprocess.PIPE, text=True)
    output = results.communicate()

    print(colored(f"\nEncrypted ZIP file: {zip_filename}\n", "green"))

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", help="This is the PDF file you wish to encrypt.", required=True)
parser.add_argument("-c", "--companyname", help="This is the name to which we save the password in 1Password.", required=True)
parser.add_argument("-p", "--password", help="This is a password you might want to use to encrypt a PDF file.", required=False)
parser.add_argument("-z", "--zip", help="This will zip up the non-encrypted PDF and DOC file and encrypt with the generated password.", action="store_true")
args = parser.parse_args()

if args.password:
    pdfEncryptor(args.password)
    oneTimeLink(args.password)

if args.input:
    onePass_Password = passwordGenny(args.companyname)
    pdfEncryptor(args.input, onePass_Password)
    oneTimeLink(onePass_Password)
    if args.zip:
        filename = args.input.split(".")[0]
        zipup(filename, args.companyname)
    else:
        pass
