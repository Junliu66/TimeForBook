import os
import csv
import sys
import re

from surprise import Dataset
from surprise import Reader

from collections import defaultdict


class Bookdata:
    bookID_to_name = {}
    name_to_bookID = {}
    ratingsPath = '../BX_CSV_Dump/BX-Book-Ratings.csv'
    bookPath = '../BX_CSV_Dump/BX-Books.csv'

    def loadBookLatestSmall(self):

        os.chdir(os.path.dirname(sys.argv[0]))

        ratingsDataset = 0
        self.bookID_to_name = {}
        self.name_to_bookID = {}

        reader = Reader(line_format='user item rating timestamp', sep=',', skip_lines=1)

        ratingsDataset = Dataset.load_from_file(self.ratingsPath, reader=reader)

        with open(self.bookPath, newline='', encoding='ISO-8859-1') as csvfile:
                bookReader = csv.reader(csvfile)
                next(bookReader)
                for row in bookReader:
                    bookID = int(row[0])
                    bookName = row[1]
                    self.bookID_to_name[bookID] = bookName
                    self.book_to_movieID[bookName] = bookID

        return ratingsDataset

    def getBookName(self, bookID):
        if bookID in self.bookID_to_name:
            return self.bookID_to_name[bookID]
        else:
            return ""