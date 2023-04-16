from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.exchange-rates.org/history/IDR/USD/T')
soup = BeautifulSoup(url_get.content,"html.parser")

#find your right key here
table = soup.find('tbody')
row = table.find_all('tr', {'class': lambda x: x is None or 'odd' in x})

row_length = len(row)

temp = [] #initiating a list 

for i in range(1, row_length):

    #scrapping process
    #get date     
    date = table.find_all('a', attrs={'class':'w'})[i].text
    
    #get rate
    rate = table.find_all('span', attrs={'class':'w'})[i].text

    temp.append((date, rate)) 
    
temp 

temp = temp[::-1]

#change into dataframe
df = pd.DataFrame(temp, columns = ('date', 'rate'))

#insert data wrangling here
def extract_rate(rate_string):
    return rate_string.split('=')[1].strip()
df['rate'] = df['rate'].apply(extract_rate)
df['rate'] = df['rate'].str.replace('Rp', '').str.replace(",",".")
df['rate'] = df['rate'].astype('float64')
df['date'] = pd.to_datetime(df['date'])

#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = f'{df["rate"].mean().round(3)}' #be careful with the " and ' 

	# generate plot
	plotkurs= df.plot(x='date', y='rate', figsize=(8, 6), grid=True)
        
	#Menambahkan title pada plot
	plt.title('Kurs Mata Uang USD ke IDR', fontsize=14)
	plt.xlabel('Tanggal', fontsize=12)
	plt.ylabel('Nilai Kurs per 1$', fontsize=12)

	#Menampilkan plot kurs 1 USD ke IDR dengan menampilkan 3 angka di belakang koma
	plotkurs.yaxis.set_major_formatter('{:.3f}'.format)

	plt.show()
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result
		)


if __name__ == "__main__": 
    app.run(debug=True)