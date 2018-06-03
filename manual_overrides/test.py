import os

file_name = 'logging_level'
file_path = os.path.join(os.getcwd(),file_name)


def main():
    file_handler = open(file_path,'rb')
    for a_line in file_handler.readlines():
        if '#' in a_line:
            print "Ignoring: " + a_line
        elif 'logging_level' in a_line:
            print a_line.split('=')[1].rstrip(' ')



if __name__ == '__main__':
    main()