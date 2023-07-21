import requests
from flask import Flask, render_template, request
from flask_cors import cross_origin
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq

app = Flask(__name__)


@app.route('/', methods=['GET'])
@cross_origin()
def homepage():
    return render_template('index.html')


@app.route("/review", methods=["POST"])
@cross_origin()
def review():
    if request.method == 'POST':
        try:
            searchstring = request.form['content'].replace(" ", "")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchstring
            flipkart_page = uReq(flipkart_url)
            flipkart_read = flipkart_page.read()
            flipkart_page.close()
            flipkart_bs = bs(flipkart_read, 'html.parser')
            flipkart_boxes = flipkart_bs.find_all("div", {'class': "_1AtVbE col-12-12"})
            del flipkart_boxes[0:3]
            flipkart_box = flipkart_boxes[5]
            flipkart_product_page = "https://www.flipkart.com" + flipkart_box.div.div.div.a['href']
            flipkart_product_page_code = requests.get(flipkart_product_page)
            flipkart_product_page_code.encoding = 'utf-8'
            flipkart_product_page_code_bs = bs(flipkart_product_page_code.text, "html.parser")
            print(flipkart_product_page_code_bs)
            flipkart_reviews = flipkart_product_page_code_bs.find_all("div", {"class": "_16PBlm"})

            filename = searchstring + ".csv"
            fw = open(filename, 'w')
            header = "Product, Price, Rating, Customer Name, Date, Comment header, Comment \n"
            fw.write(header)
            reviews = []
            for review1 in flipkart_reviews:
                try:
                    name = review1.div.div.find_all("p", {"class": "_2sc7ZR _2V5EHH"})[0].text

                except:
                    name = 'Name is not mentioned'

                try:
                    rating = review1.div.div.div.div.text

                except:
                    rating = "Rating in not available"

                try:
                    date = review1.div.find_all("p", {"class": "_2sc7ZR"})[1].text

                except:
                    date = "date is not available"

                try:
                    comment_header = review1.div.div.div.p.text

                except:
                    comment_header = "Comment header is not available"

                try:
                    comment = review1.div.div.find_all("div", {'class': ""})[0].div.text

                except:
                    comment = "Comment is not available"

                try:
                    price = flipkart_product_page_code_bs.find_all("div", {"class": "_30jeq3 _16Jk6d"})[0].text

                except:
                    price = "Price is not available"

                mydict = {"Product": searchstring, "Price": price, "Rating": rating, "Customer Name": name,
                          "Date": date, "Comment Header": comment_header, "Comment": comment}
                reviews.append(mydict)
            return render_template("result.html", reviews=reviews[0:(len(reviews) - 1)])
        except Exception as E:
            print(E)
            return "Something is wrong"
    else:
        return render_template("index.html")


if __name__ == "__main__":
    app.run(port=5001, debug=True)
