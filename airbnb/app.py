from flask import Flask, render_template, request, redirect, url_for
import csv
from collections import defaultdict

app = Flask(__name__)

class RevenueManager:
    def __init__(self, filename):
        self.filename = filename
        self.sales_data = defaultdict(list)  # 월별 매출 데이터
        self.booking_data = defaultdict(int)  # 월별 예약 횟수
        self.load_data()  # 프로그램 시작 시 파일에서 데이터를 불러옴

    def load_data(self):
        """CSV 파일에서 데이터를 읽어옴"""
        try:
            with open(self.filename, mode='r', encoding='utf-8-sig') as file:  # 인코딩 수정
                reader = csv.DictReader(file)
                for row in reader:
                    month_str = row['month']  # YYYY-MM-DD 형식
                    full_date = month_str  # YYYY-MM-DD 형식 그대로 사용
                    month = month_str[:7]  # 'YYYY-MM' 형식으로 변환
                    self.sales_data[full_date].append({
                        'payment_method': row['payment_method'],
                        'amount': int(row['amount'])
                    })
                    self.booking_data[month] += 1  # 월별 예약 횟수 증가
        except FileNotFoundError:
            print("No existing CSV file found. A new one will be created upon adding data.")
        except Exception as e:
            print(f"Error loading data: {e}")  # 추가적인 오류 메시지 출력

    def save_data(self):
        """데이터를 CSV 파일로 저장"""
        with open(self.filename, mode='w', encoding='utf-8-sig', newline='') as file:  # 인코딩 수정
            fieldnames = ['month', 'payment_method', 'amount']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for full_date, sales in self.sales_data.items():
                for sale in sales:
                    writer.writerow({
                        'month': full_date,  # 'YYYY-MM-DD' 형식으로 저장
                        'payment_method': sale['payment_method'],
                        'amount': sale['amount']
                    })

    def add_sale(self, date, payment_method, amount):
        """매출 데이터 추가"""
        full_date = date  # 'YYYY-MM-DD' 형식 그대로 사용
        self.sales_data[full_date].append({'payment_method': payment_method, 'amount': amount})
        self.booking_data[full_date[:7]] += 1  # 월별 예약 횟수 증가
        print(f"Added sale: {payment_method}, {amount} to {full_date}")  # 로그 출력
        self.save_data()  # 데이터를 추가할 때마다 파일로 저장

# RevenueManager 객체 생성 (CSV 파일에 저장)
manager = RevenueManager('sales_data.csv')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_sale', methods=['POST'])
def add_sale():
    date = request.form['date']  # 여기서는 'YYYY-MM-DD' 형식으로 받음
    payment_method = request.form['payment_method']
    amount = int(request.form['amount'])
    manager.add_sale(date, payment_method, amount)
    return redirect(url_for('index'))

@app.route('/results', methods=['GET', 'POST'])
def results():
    revenue_data = manager.sales_data

    if not revenue_data:
        return render_template('result.html', revenue_data={}, current_month=None, last_year_month=None, current_sales=0, last_year_sales=0, revenue_increase=0, booking_increase=0)

    if request.method == 'POST':
        # 사용자가 입력한 연도와 월을 가져옴
        year_input = request.form.get('year', type=int)
        month_input = request.form.get('month', type=int)
    else:
        # 기본적으로 가장 최근 날짜의 연도와 월을 사용
        current_month = list(revenue_data.keys())[-1]  # 가장 최근 날짜를 가져옴
        year_input, month_input, _ = map(int, current_month.split('-'))

    month_str = f"{month_input:02d}"  # 월을 두 자리 문자열로 변환
    current_month_str = f"{year_input}-{month_str}"
    last_year_month_str = f"{year_input - 1}-{month_str}"

    # 매출 데이터 계산: 현재 월과 작년 월의 매출 합계
    current_sales = sum(sale['amount'] for date in revenue_data if date.startswith(current_month_str) for sale in revenue_data[date])
    last_year_sales = sum(sale['amount'] for date in revenue_data if date.startswith(last_year_month_str) for sale in revenue_data[date])

    # 매출 증가율 계산
    revenue_increase = ((current_sales - last_year_sales) / last_year_sales) * 100 if last_year_sales else 0

    # 예약 데이터 계산
    current_bookings = manager.booking_data[current_month_str] if current_month_str in manager.booking_data else 0  # 월별 예약 횟수
    last_year_bookings = manager.booking_data.get(last_year_month_str, 0)
    booking_increase = ((current_bookings - last_year_bookings) / last_year_bookings) * 100 if last_year_bookings else 0

    # 결과 전달
    return render_template(
        'result.html',
        revenue_data=revenue_data,
        current_month=current_month_str,
        last_year_month=last_year_month_str if last_year_sales > 0 else None,
        current_sales=current_sales,
        last_year_sales=last_year_sales if last_year_sales > 0 else None,
        revenue_increase=revenue_increase,
        booking_increase=booking_increase
    )

if __name__ == '__main__':
    app.run(debug=True, port=5001)
    # & C:/Users/enjoy/anaconda3/python.exe c:/Users/enjoy/airbnb/app.py