import base64, sys

def main():
    file_path = str(sys.argv[1])
    file_handler = open(file_path, 'rb')
    file_text = file_handler.read()
    encoded_string = file_text.encode('base64')
    print encoded_string


if __name__ == '__main__':
    main()