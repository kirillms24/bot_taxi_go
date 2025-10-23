from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/support_bot', methods=['GET', 'POST'])
def support_bot():
    if request.method == 'POST':
        user_message = request.form['message']
        # Здесь логика обработки сообщения
        bot_response = process_message(user_message)  # Функция для обработки сообщения
        return jsonify({'response': bot_response})
    return render_template('support_bot.html')

def process_message(message):
    # Простая реализация обработки сообщений
    if 'заказ' in message.lower():
        return 'Для оформления заказа укажите адрес и время.'
    elif 'тарифы' in message.lower():
        return 'Наши тарифы: эконом, комфорт, бизнес.'
    else:
        return 'Я не совсем понимаю ваш запрос. Пожалуйста, уточните.'

if __name__ == '__main__':
    app.run()
