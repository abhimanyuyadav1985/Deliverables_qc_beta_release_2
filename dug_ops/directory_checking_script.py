import sys, os

def main():
    path_name = str(sys.argv[1])
    print os.path.exists(path_name)

if __name__ == '__main__':
    main()