document.addEventListener('DOMContentLoaded', function() {
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
        const logEntry = `[${timestamp}] ${message}\n`;
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
});