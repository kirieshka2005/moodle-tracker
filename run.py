from app import create_app

app = create_app()

if __name__ == '__main__':
    print("=" * 45)
    print("  🎯  Moodle Tracker — запуск сервера")
    print("=" * 45)
    print("  Открой в браузере → http://127.0.0.1:5000")
    print("  Для остановки нажми Ctrl+C")
    print("=" * 45)
    app.run(debug=True)
