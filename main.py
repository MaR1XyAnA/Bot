#!/usr/bin/env python3
"""
Fishing Bot Application
Main entry point for the fishing bot desktop application.
"""
import sys
import os
import logging
import threading
# Set QT platform to offscreen in Replit environment
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

# --- Исправление ошибки QFontDatabase: Cannot find font directory ---
# Для PyQt5/Qt5: добавляем переменную окружения QT_QPA_FONTDIR с путем к шрифтам
os.environ["QT_QPA_FONTDIR"] = os.path.abspath("fonts")

# Try to import PyQt5, but continue if not available (headless mode)
try:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtGui import QIcon
    qt_available = True
except ImportError:
    qt_available = False
    logging.warning("PyQt5 not available, running in headless mode only")

from flask import Flask, render_template, jsonify, request
from ui.main_window import MainWindow
from utils.logger import setup_logger
from config_manager import ConfigManager
from bot_interface import BotInterface
import threading

# Create Flask app for web-based UI
app = Flask(__name__, static_folder='web/static', template_folder='web/templates')
bot_interface = None
config_manager = None

@app.route('/')
def index():
    """Web UI index page"""
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    """Get bot status"""
    if bot_interface:
        status = "running" if bot_interface.running else "stopped"
        stats = bot_interface.fishing_bot.get_stats() if bot_interface.fishing_bot else {}
        return jsonify({
            "status": status,
            "stats": stats
        })
    return jsonify({"status": "not_initialized"})

@app.route('/api/start', methods=['POST'])
def start_bot():
    """Start the bot"""
    if bot_interface and bot_interface.start_bot():
        return jsonify({"success": True})
    return jsonify({"success": False})

@app.route('/api/stop', methods=['POST'])
def stop_bot():
    """Stop the bot"""
    if bot_interface and bot_interface.stop_bot():
        return jsonify({"success": True})
    return jsonify({"success": False})

def start_qt_app():
    """Start the QT application in a separate thread"""
    # Create QT Application
    app = QApplication(sys.argv)
    app.setApplicationName("Fishing Bot")
    app.setWindowIcon(QIcon("assets/app_icon.svg"))
    
    # Create main window
    window = MainWindow(config_manager)
    window.show()
    
    # Start application event loop
    sys.exit(app.exec_())

def main():
    """Main application entry point"""
    global bot_interface, config_manager
    
    # Setup logging
    setup_logger()
    logging.info("Starting Fishing Bot Application")
    
    # Ensure configuration directory exists
    app_dir = os.path.expanduser("~/.fishing_bot")
    os.makedirs(app_dir, exist_ok=True)
    
    # Initialize configuration
    config_manager = ConfigManager(os.path.join(app_dir, "config.json"))
    
    # Set up bot interface
    bot_interface = BotInterface(config_manager)
    
    # Create necessary web directories
    os.makedirs('web/templates', exist_ok=True)
    os.makedirs('web/static/css', exist_ok=True)
    os.makedirs('web/static/js', exist_ok=True)
    
    # Check if running in a headless environment
    headless = os.environ.get('REPLIT_ENVIRONMENT', False)
    
    if headless:
        # Generate web templates if they don't exist
        create_web_files()
        # Start flask app
        app.run(host='0.0.0.0', port=5000)
    else:
        # Start QT app directly
        start_qt_app()

def create_web_files():
    """Create necessary web files if they don't exist"""
    # Create index.html
    if not os.path.exists('web/templates/index.html'):
        with open('web/templates/index.html', 'w', encoding='utf-8') as f:
            f.write('''<!DOCTYPE html>
<html>
<head>
    <title>Fishing Bot - Веб-интерфейс</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css">
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body data-bs-theme="dark">
    <div class="container mt-4">
        <div class="row">
            <div class="col-12">
                <h1 class="text-center mb-4">Рыболовный Бот</h1>
                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="card-title">Статус</h5>
                    </div>
                    <div class="card-body">
                        <div class="d-flex justify-content-between">
                            <div>
                                <p class="status-label">Статус: <span id="status-value" class="badge bg-secondary">Загрузка...</span></p>
                            </div>
                            <div>
                                <button id="start-btn" class="btn btn-success">Запустить</button>
                                <button id="stop-btn" class="btn btn-danger">Остановить</button>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="row">
                    <div class="col-md-6">
                        <div class="card mb-4">
                            <div class="card-header">
                                <h5 class="card-title">Управление</h5>
                            </div>
                            <div class="card-body">
                                <div class="mb-3">
                                    <label for="cast-interval" class="form-label">Интервал заброса (сек):</label>
                                    <input type="range" class="form-range" id="cast-interval" min="5" max="300" value="30">
                                    <div class="d-flex justify-content-between">
                                        <span>5</span>
                                        <span id="cast-interval-value">30</span>
                                        <span>300</span>
                                    </div>
                                </div>
                                <div class="mb-3">
                                    <label for="detection-method" class="form-label">Метод определения:</label>
                                    <select class="form-select" id="detection-method">
                                        <option value="color">Цвет</option>
                                        <option value="motion">Движение</option>
                                        <option value="sound">Звук</option>
                                    </select>
                                </div>
                                <div class="mb-3">
                                    <label for="sensitivity" class="form-label">Чувствительность:</label>
                                    <input type="range" class="form-range" id="sensitivity" min="0" max="100" value="50">
                                    <div class="d-flex justify-content-between">
                                        <span>0%</span>
                                        <span id="sensitivity-value">50%</span>
                                        <span>100%</span>
                                    </div>
                                </div>
                                <button id="save-settings-btn" class="btn btn-primary">Сохранить настройки</button>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card mb-4">
                            <div class="card-header">
                                <h5 class="card-title">Статистика</h5>
                            </div>
                            <div class="card-body">
                                <p id="session-time">Время сессии: 00:00:00</p>
                                <p id="fish-caught">Поймано рыбы: 0</p>
                                <p id="fish-per-hour">Рыбы в час: 0</p>
                            </div>
                        </div>
                        <div class="card">
                            <div class="card-header">
                                <h5 class="card-title">Информация</h5>
                            </div>
                            <div class="card-body">
                                <p>Версия: <span id="version">1.0.0</span></p>
                                <p>Репозиторий GitHub: <a href="#" id="repo-link">username/fishing-bot</a></p>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="card-title">Журнал активности</h5>
                    </div>
                    <div class="card-body">
                        <div class="log-container">
                            <pre id="log-output" class="form-control"></pre>
                        </div>
                        <button id="clear-log-btn" class="btn btn-secondary mt-2">Очистить журнал</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="/static/js/script.js"></script>
</body>
</html>''')
    
    # Create CSS
    if not os.path.exists('web/static/css/style.css'):
        with open('web/static/css/style.css', 'w', encoding='utf-8') as f:
            f.write('''body {
    padding-bottom: 2rem;
}

.status-label {
    font-size: 1.2rem;
    margin-top: 0.5rem;
}

.log-container {
    max-height: 300px;
    overflow-y: auto;
    background-color: #212529;
    border-radius: 0.25rem;
}

#log-output {
    background-color: #212529;
    color: #f8f9fa;
    font-family: monospace;
    height: 300px;
    white-space: pre-wrap;
    overflow-wrap: break-word;
}''')
    
    # Create JavaScript
    if not os.path.exists('web/static/js/script.js'):
        with open('web/static/js/script.js', 'w', encoding='utf-8') as f:
            f.write('''document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const statusValue = document.getElementById('status-value');
    const startBtn = document.getElementById('start-btn');
    const stopBtn = document.getElementById('stop-btn');
    const castInterval = document.getElementById('cast-interval');
    const castIntervalValue = document.getElementById('cast-interval-value');
    const detectionMethod = document.getElementById('detection-method');
    const sensitivity = document.getElementById('sensitivity');
    const sensitivityValue = document.getElementById('sensitivity-value');
    const saveSettingsBtn = document.getElementById('save-settings-btn');
    const sessionTime = document.getElementById('session-time');
    const fishCaught = document.getElementById('fish-caught');
    const fishPerHour = document.getElementById('fish-per-hour');
    const version = document.getElementById('version');
    const repoLink = document.getElementById('repo-link');
    const logOutput = document.getElementById('log-output');
    const clearLogBtn = document.getElementById('clear-log-btn');

    // Update UI elements when range values change
    castInterval.addEventListener('input', function() {
        castIntervalValue.textContent = this.value;
    });

    sensitivity.addEventListener('input', function() {
        sensitivityValue.textContent = this.value + '%';
    });

    // Start bot
    startBtn.addEventListener('click', function() {
        fetch('/api/start', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    addLogMessage('Бот запущен');
                    updateStatus();
                } else {
                    addLogMessage('Ошибка запуска бота');
                }
            });
    });

    // Stop bot
    stopBtn.addEventListener('click', function() {
        fetch('/api/stop', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    addLogMessage('Бот остановлен');
                    updateStatus();
                } else {
                    addLogMessage('Ошибка остановки бота');
                }
            });
    });

    // Save settings
    saveSettingsBtn.addEventListener('click', function() {
        const settings = {
            cast_interval: parseInt(castInterval.value),
            detection_method: detectionMethod.value,
            sensitivity: parseInt(sensitivity.value)
        };
        
        addLogMessage('Настройки сохранены');
        // Update UI to reflect saved settings
    });

    // Clear log
    clearLogBtn.addEventListener('click', function() {
        logOutput.textContent = '';
        addLogMessage('Журнал очищен');
    });

    // Add log message
    function addLogMessage(message) {
        const now = new Date();
        const timestamp = now.toTimeString().split(' ')[0];
        const logEntry = `[${timestamp}] ${message}\\n`;
        logOutput.textContent += logEntry;
        
        // Auto-scroll to bottom
        logOutput.scrollTop = logOutput.scrollHeight;
    }

    // Update bot status and stats
    function updateStatus() {
        fetch('/api/status')
            .then(response => response.json())
            .then(data => {
                // Update status badge
                if (data.status === 'running') {
                    statusValue.textContent = 'Запущен';
                    statusValue.className = 'badge bg-success';
                    startBtn.disabled = true;
                    stopBtn.disabled = false;
                } else if (data.status === 'stopped') {
                    statusValue.textContent = 'Остановлен';
                    statusValue.className = 'badge bg-danger';
                    startBtn.disabled = false;
                    stopBtn.disabled = true;
                } else if (data.status === 'paused') {
                    statusValue.textContent = 'Приостановлен';
                    statusValue.className = 'badge bg-warning';
                    startBtn.disabled = true;
                    stopBtn.disabled = false;
                } else {
                    statusValue.textContent = 'Не инициализирован';
                    statusValue.className = 'badge bg-secondary';
                }

                // Update stats if available
                if (data.stats) {
                    // Format session time
                    const sessionDuration = data.stats.session_duration || 0;
                    const hours = Math.floor(sessionDuration / 3600);
                    const minutes = Math.floor((sessionDuration % 3600) / 60);
                    const seconds = Math.floor(sessionDuration % 60);
                    const formattedTime = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
                    
                    sessionTime.textContent = `Время сессии: ${formattedTime}`;
                    fishCaught.textContent = `Поймано рыбы: ${data.stats.fish_caught || 0}`;
                    fishPerHour.textContent = `Рыбы в час: ${(data.stats.fish_per_hour || 0).toFixed(1)}`;
                }
            });
    }

    // Initial status update
    updateStatus();
    
    // Add initial log message
    addLogMessage('Веб-интерфейс инициализирован');

    // Poll for status updates every 2 seconds
    setInterval(updateStatus, 2000);
});''')

if __name__ == "__main__":
    main()
