from blog import blog, database
from blog.models import Post, FTSPost

def main():
    database.create_tables([Post, FTSPost], safe=True)
    blog.run(debug=True)

if __name__ == '__main__':
    main()