import sys, os

def main():
    outfile_path = os.path.join(os.getcwd(),'temp_sgyt')
    if os.path.exists(outfile_path):
        os.remove(outfile_path)
    with open(sys.argv[1], 'rb') as infile, open(outfile_path,'w') as outfile :
        for line in infile:
            if line.strip():
                continue
            else:
                outfile.write(line)
    file_handler = open(outfile_path,'rb')
    file_text = file_handler.read()
    encoded_string = file_text.encode('base64')
    file_handler.close()
    print encoded_string


if __name__ == '__main__':
    main()
